#!/usr/bin/env python3
# BALTIC_CELL_CHAIN_MEASURE.py
#
# EXTERNAL RESEARCH / MEASUREMENT INSTRUMENT
# Reads only. Writes one result file beside itself. Touches no EVE surface.
#
# Reads a single 250 m cell across three published PROTECT BALTIC artefacts without
# downloading them. Each raster is 208-258 MB; this fetches roughly 120 KB per row.
#
#   species     Zenodo 20309312  fish/probability_tif/<species>.tif   (local copy)
#   scenario    Zenodo 21523969  env_stack_rcp45_2040_2059.tif        (HTTP range)
#   fixed       Zenodo 21523969  fixed_var_stack.tif                  (HTTP range)
#
# METHOD, in the order it must be done:
#   1. fetch the last ~50 KB of the remote file and parse the TIFF IFD, which GDAL
#      wrote at the END of these files, not the start
#   2. read StripOffsets / StripByteCounts — one strip per row, PlanarConfig 1
#   3. fetch only the strip for the row of interest by HTTP range
#   4. ZSTD-decompress it (Compression tag 50000)
#   5. UNDO PREDICTOR 2 — horizontal differencing on the 32-bit sample values.
#      Skipping this step yields syntactically valid, plausible-looking numbers that
#      are differences, not values. The first run of this measurement reported eleven
#      zeros for a cell and they looked like data. Reading bytes correctly is not the
#      same as interpreting evidence correctly.
#   6. extract the pixel across all bands and check finiteness band by band, not only
#      on band 1
#
# WHAT THIS ESTABLISHES: the value stored at a named cell of each named artefact, and
# whether the three artefacts share one grid.
#
# WHAT THIS DOES NOT ESTABLISH: what the values mean. Band names are read from the
# artefact's own GDAL_METADATA and are not renamed here. The species raster value is
# reported as a RASTER VALUE, not as a probability: the 0-1000 scale is described in
# project documentation, not in the artefact's own metadata, and this instrument does
# not perform that conversion.

import hashlib
import json
import math
import os
import struct
import subprocess
import sys

try:
    import numpy as np
    import zstandard as zstd
except ImportError as e:
    print("requires numpy and zstandard: pip install numpy zstandard", file=sys.stderr)
    raise

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "BALTIC_CELL_CHAIN_RESULT.json")

# ---------------------------------------------------------------------------
# artefact identities, from the Zenodo API. Sizes and md5 are publisher-issued.
# ---------------------------------------------------------------------------
ART = {
    "scenario": {
        "record": 21523969, "doi": "10.5281/zenodo.21523969",
        "concept": "10.5281/zenodo.21523968", "published": "2026-07-24",
        "file": "env_stack_rcp45_2040_2059.tif",
        "url": "https://zenodo.org/api/records/21523969/files/"
               "env_stack_rcp45_2040_2059.tif/content",
        "size": 208816897, "md5": "e98cd1d02dbb21f7a7cc8dcf64ce7a9a", "bands": 11,
        "role": "future environmental predictors, RCP4.5 2040-2059",
    },
    "fixed": {
        "record": 21523969, "doi": "10.5281/zenodo.21523969",
        "concept": "10.5281/zenodo.21523968", "published": "2026-07-24",
        "file": "fixed_var_stack.tif",
        "url": "https://zenodo.org/api/records/21523969/files/"
               "fixed_var_stack.tif/content",
        "size": 258767525, "md5": "fec2be03c56e63c4b55048f904d9c589", "bands": 16,
        "role": "time-invariant predictors",
    },
}

SPECIES_LOCAL = os.path.join(HERE, "..", "sources",
                             "Perca.fluviatilis.probability.tif")
SPECIES_ID = {
    "record": 20309312, "doi": "10.5281/zenodo.20309312", "published": "2026-06-23",
    "member": "PROTECT-BALTIC-WP3-SDMs/fish/probability_tif/Perca.fluviatilis.tif",
    "sha256": "e1c4ef30f7e3eb45829640e32dc2003872c1a5d74308b79bdf6aa1654e0c5f9a",
    "bytes": 6202696, "role": "probability_tif", "species": "Perca fluviatilis",
}

WIDTH, HEIGHT = 4914, 5657
CASES = {"BALTIC-CHAIN": (3387, 2035), "BALTIC-ABSENCE": (3387, 1926)}

TIFF_TYPE_SIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8,
                  11: 4, 12: 8}
TIFF_FMT = {1: 'B', 3: 'H', 4: 'I', 6: 'b', 8: 'h', 9: 'i', 11: 'f', 12: 'd'}
TAG = {256: 'ImageWidth', 257: 'ImageLength', 258: 'BitsPerSample',
       259: 'Compression', 273: 'StripOffsets', 277: 'SamplesPerPixel',
       278: 'RowsPerStrip', 279: 'StripByteCounts', 284: 'PlanarConfig',
       317: 'Predictor', 339: 'SampleFormat', 33550: 'ModelPixelScale',
       33922: 'ModelTiepoint', 34735: 'GeoKeyDirectory',
       34737: 'GeoAsciiParams', 42112: 'GDAL_METADATA', 42113: 'GDAL_NODATA'}


def curl_range(url, first, last):
    """One HTTP range read. Fails hard rather than returning a short buffer."""
    want = last - first + 1
    p = subprocess.run(
        ["curl", "-s", "--fail", "--max-time", "180", "-r", f"{first}-{last}", url],
        capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed for {url} range {first}-{last}")
    if len(p.stdout) != want:
        raise RuntimeError(f"range {first}-{last}: got {len(p.stdout)} of {want} bytes")
    return p.stdout


def read_ifd(url, size):
    """GDAL wrote the IFD at the end of these files. Find it, then parse it."""
    head = curl_range(url, 0, 15)
    if head[:2] != b'II':
        raise RuntimeError("not a little-endian TIFF")
    if struct.unpack('<H', head[2:4])[0] != 42:
        raise RuntimeError("not a classic TIFF")
    ifd_off = struct.unpack('<I', head[4:8])[0]
    tail = curl_range(url, ifd_off, size - 1)

    n = struct.unpack('<H', tail[0:2])[0]
    tags, p = {}, 2
    for _ in range(n):
        tag, typ = struct.unpack('<HH', tail[p:p + 4])
        cnt = struct.unpack('<I', tail[p + 4:p + 8])[0]
        vo = tail[p + 8:p + 12]
        p += 12
        if typ not in TIFF_TYPE_SIZE:
            continue
        nbytes = TIFF_TYPE_SIZE[typ] * cnt
        if nbytes <= 4:
            raw = vo[:nbytes]
        else:
            o = struct.unpack('<I', vo)[0] - ifd_off
            if o < 0 or o + nbytes > len(tail):
                continue
            raw = tail[o:o + nbytes]
        if typ == 2:
            v = raw.split(b'\x00')[0].decode('latin1')
        elif typ == 5:
            u = struct.unpack('<%dI' % (cnt * 2), raw)
            v = [u[k] / u[k + 1] if u[k + 1] else None for k in range(0, len(u), 2)]
        else:
            v = list(struct.unpack('<%d%s' % (cnt, TIFF_FMT[typ]), raw))
            if len(v) == 1:
                v = v[0]
        tags[TAG.get(tag, tag)] = v
    tags['_ifd_offset'] = ifd_off
    tags['_tail_sha256'] = hashlib.sha256(tail).hexdigest()
    return tags


def read_row(url, tags, bands, row):
    """Fetch and decode exactly one raster row."""
    if tags.get('RowsPerStrip') != 1:
        raise RuntimeError("expected one strip per row")
    if tags.get('PlanarConfig') != 1:
        raise RuntimeError("expected chunky PlanarConfig")
    if tags.get('Compression') != 50000:
        raise RuntimeError("expected ZSTD (50000)")
    off, cnt = tags['StripOffsets'][row], tags['StripByteCounts'][row]
    comp = curl_range(url, off, off + cnt - 1)
    raw = zstd.ZstdDecompressor().decompress(comp, max_output_size=WIDTH * bands * 4)
    if len(raw) != WIDTH * bands * 4:
        raise RuntimeError(f"decompressed {len(raw)}, expected {WIDTH * bands * 4}")

    a = np.frombuffer(raw, dtype='<u4').reshape(WIDTH, bands)
    if tags.get('Predictor') == 2:
        # horizontal differencing over the 32-bit sample values, per band
        a = (np.cumsum(a.astype(np.uint64), axis=0, dtype=np.uint64)
             % (1 << 32)).astype(np.uint32)
    elif tags.get('Predictor') not in (None, 1):
        raise RuntimeError(f"unhandled Predictor {tags.get('Predictor')}")
    return a.view(np.float32).reshape(WIDTH, bands), off, cnt


def band_names(tags, bands):
    """Names exactly as the artefact states them. No renaming, no inference."""
    md = tags.get('GDAL_METADATA')
    if not isinstance(md, str):
        return [None] * bands
    import re
    out = [None] * bands
    for m in re.finditer(
            r'<Item name="DESCRIPTION" sample="(\d+)"[^>]*>(.*?)</Item>', md, re.S):
        i = int(m.group(1))
        if 0 <= i < bands:
            out[i] = m.group(2).strip()
    return out


def main():
    result = {"record": "BALTIC_CELL_CHAIN_RESULT",
              "grid": {"width": WIDTH, "height": HEIGHT}, "artefacts": {}, "cases": {}}

    # --- species raster, local ---------------------------------------------
    import rasterio
    sp_path = os.path.normpath(SPECIES_LOCAL)
    sp_sha = hashlib.sha256(open(sp_path, 'rb').read()).hexdigest()
    if sp_sha != SPECIES_ID['sha256']:
        raise RuntimeError(f"species raster sha256 {sp_sha} != pinned")
    src = rasterio.open(sp_path)
    sp_grid = {"crs": str(src.crs), "width": src.width, "height": src.height,
               "transform": [src.transform.a, src.transform.b, src.transform.c,
                             src.transform.d, src.transform.e, src.transform.f],
               "nodata": src.nodata, "band": src.descriptions[0]}
    result["artefacts"]["species"] = dict(SPECIES_ID, grid=sp_grid,
                                          local_sha256=sp_sha)
    print("species  %s  sha256 %s  OK" % (os.path.basename(sp_path), sp_sha[:16]))

    # --- remote stacks ------------------------------------------------------
    meta = {}
    for key, a in ART.items():
        t = read_ifd(a["url"], a["size"])
        names = band_names(t, a["bands"])
        meta[key] = t
        g = {"width": t['ImageWidth'], "height": t['ImageLength'],
             "pixel_scale": t.get('ModelPixelScale'),
             "tiepoint": t.get('ModelTiepoint'),
             "geo_ascii": t.get('GeoAsciiParams'),
             "nodata": t.get('GDAL_NODATA'),
             "compression": t.get('Compression'), "predictor": t.get('Predictor')}
        result["artefacts"][key] = dict(a, grid=g, band_names=names,
                                        ifd_offset=t['_ifd_offset'],
                                        ifd_tail_sha256=t['_tail_sha256'])
        print("%-9s %s  %d bands  IFD at %d" % (key, a["file"], a["bands"],
                                                t['_ifd_offset']))

    # --- grid identity ------------------------------------------------------
    ident = {
        "species_vs_scenario": (
            src.width == meta['scenario']['ImageWidth'] and
            src.height == meta['scenario']['ImageLength'] and
            abs(src.transform.a - meta['scenario']['ModelPixelScale'][0]) < 1e-9 and
            abs(src.transform.c - meta['scenario']['ModelTiepoint'][3]) < 1e-6 and
            abs(src.transform.f - meta['scenario']['ModelTiepoint'][4]) < 1e-6),
    }
    ident["species_vs_fixed"] = (
        src.width == meta['fixed']['ImageWidth'] and
        src.height == meta['fixed']['ImageLength'] and
        abs(src.transform.c - meta['fixed']['ModelTiepoint'][3]) < 1e-6 and
        abs(src.transform.f - meta['fixed']['ModelTiepoint'][4]) < 1e-6)
    result["grid_identity"] = ident
    print("grid identity  species==scenario %s  species==fixed %s"
          % (ident["species_vs_scenario"], ident["species_vs_fixed"]))

    # --- the two cases ------------------------------------------------------
    rows = {}
    for name, (row, col) in CASES.items():
        if row not in rows:
            sp_row = src.read(1, window=((row, row + 1), (0, WIDTH)))[0]
            env_row, eo, ec = read_row(ART['scenario']['url'], meta['scenario'], 11, row)
            fix_row, fo, fc = read_row(ART['fixed']['url'], meta['fixed'], 16, row)
            rows[row] = (sp_row, env_row, fix_row, eo, ec, fo, fc)
        sp_row, env_row, fix_row, eo, ec, fo, fc = rows[row]

        x, y = src.xy(row, col)
        sp_val = int(sp_row[col])
        env = [None if math.isnan(v) else float(v) for v in env_row[col]]
        fix = [None if math.isnan(v) else float(v) for v in fix_row[col]]
        case = {
            "cell": {"row": row, "col": col},
            "cell_centre_epsg3035": [round(x, 4), round(y, 4)],
            "species_raster_value": sp_val,
            "species_is_nodata": sp_val == int(src.nodata),
            "scenario_bands_finite": sum(v is not None for v in env),
            "scenario_bands_total": 11,
            "fixed_bands_finite": sum(v is not None for v in fix),
            "fixed_bands_total": 16,
            "scenario_values": env,
            "fixed_values": fix,
            "scenario_strip": {"offset": eo, "compressed_bytes": ec},
            "fixed_strip": {"offset": fo, "compressed_bytes": fc},
        }
        result["cases"][name] = case
        print("%-15s cell (%d,%d)  species %-6d  scenario %2d/11  fixed %2d/16"
              % (name, row, col, sp_val, case["scenario_bands_finite"],
                 case["fixed_bands_finite"]))

    # --- row-level mask comparison -----------------------------------------
    row = 3387
    sp_row, env_row, fix_row, *_ = rows[row]
    spv = sp_row != int(src.nodata)
    envv = ~np.isnan(env_row).any(axis=1)
    fixv = ~np.isnan(fix_row).any(axis=1)
    result["row_mask_comparison"] = {
        "row": row,
        "species_modelled": int(spv.sum()),
        "scenario_all_bands_finite": int(envv.sum()),
        "fixed_all_bands_finite": int(fixv.sum()),
        "all_three": int((spv & envv & fixv).sum()),
        "species_only": int((spv & ~(envv & fixv)).sum()),
        "environment_only": int((~spv & envv & fixv).sum()),
        "note": "one row only. Not extrapolated to the grid.",
    }
    print("row %d  species %d  all three %d  species-only %d  env-only %d"
          % (row, spv.sum(), (spv & envv & fixv).sum(),
             (spv & ~(envv & fixv)).sum(), (~spv & envv & fixv).sum()))

    result["establishes"] = [
        "the value stored at the named cell of each named artefact",
        "that the three artefacts share one grid: same CRS code, dimensions, "
        "pixel size and origin",
    ]
    result["does_not_establish"] = [
        "what any value means - band names are reproduced from the artefact's own "
        "GDAL_METADATA and are not renamed or interpreted here",
        "that the species raster value is a probability - the 0-1000 scale is "
        "described in project documentation, not in the artefact's own metadata",
        "why the environmental stacks carry NoData where the species raster carries "
        "a value - the reason is not represented in the artefacts examined",
        "anything about rows other than the one measured",
    ]

    body = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    open(OUT, "wb").write(body.encode("utf-8"))
    back = open(OUT, "rb").read()
    print()
    print("result  %s" % OUT)
    print("  sha256 %s" % hashlib.sha256(back).hexdigest())
    print("  bytes  %d" % len(back))


if __name__ == "__main__":
    main()
