#!/usr/bin/env python3
# ZIP_INVENTORY_20309312_BUILD.py
#
# EXTERNAL RESEARCH / MEASUREMENT ARTEFACT
# NOT EVE PRODUCT STATE - NOT GOVERNANCE EVIDENCE - NOT AUTHORITY
# NOT A SIGNED H - NOT ACCEPTED BASELINE STATE
#
# Deterministic regeneration of ZIP_INVENTORY_20309312.json from the published
# archive's own ZIP central directory, read over HTTP range requests.
# Standard library only. Writes exactly one file. Reads nothing from EVE surfaces.
#
# Expected outputs are pinned below. If any pin fails the script exits non-zero
# and writes nothing.

import hashlib
import json
import struct
import sys
import time
import urllib.request

URL = "https://zenodo.org/api/records/20309312/files/PROTECT-BALTIC-WP3-SDMs.zip/content"
ARCHIVE_BYTES = 5584303765
CD_OFFSET = 5583450702
CD_SIZE = 852965
CD_SHA256 = "8ae075754c9f98d9f18cdd032cce8b7f8522280386397c2b83c27d1671a883a8"
EXPECTED_ENTRIES = 5697
MEASURED_UTC = "2026-09-09T14:07Z"

# usage: build [<output path>] [--cd <local central-directory file>]
ARGV = sys.argv[1:]
LOCAL_CD = None
if "--cd" in ARGV:
    k = ARGV.index("--cd")
    LOCAL_CD = ARGV[k + 1]
    ARGV = ARGV[:k] + ARGV[k + 2:]
OUT = ARGV[0] if ARGV else "ZIP_INVENTORY_20309312.json"


def fetch(a, b, tries=6):
    # Zenodo intermittently answers a large range read with 504. Observed
    # 2026-09-09. Retry with a linear backoff; fail closed if it never succeeds.
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                URL, headers={"Range": "bytes=%d-%d" % (a, b)})
            return urllib.request.urlopen(req, timeout=300).read()
        except Exception as exc:  # noqa: BLE001 - reported, not swallowed
            last = exc
            sys.stderr.write("range read attempt %d failed: %r\n" % (attempt + 1, exc))
            time.sleep(6 + 6 * attempt)
    raise SystemExit("range read failed after %d attempts: %r" % (tries, last))


def load_central_directory(local_path=None):
    if local_path:
        with open(local_path, "rb") as fh:
            return fh.read()
    return fetch(CD_OFFSET, CD_OFFSET + CD_SIZE - 1)


def classify(path, is_dir):
    if is_dir:
        return "directory"
    if path.endswith(".tif.aux.xml"):
        return "sidecar_aux_xml"
    if path.endswith(".tif"):
        return "product_raster"
    if path.endswith(".csv"):
        return "csv"
    return "other"


def parse(cd):
    out = []
    i = 0
    while i < len(cd):
        if cd[i:i + 4] != b"PK\x01\x02":
            raise SystemExit("central directory signature lost at offset %d" % i)
        (vmade, vneed, flags, method, mtime, mdate, crc, csize, usize,
         nlen, elen, clen, disk, iattr, eattr, off) = struct.unpack(
            "<HHHHHHIIIHHHHHII", cd[i + 4:i + 46])
        name = cd[i + 46:i + 46 + nlen].decode("utf-8")
        extra = cd[i + 46 + nlen:i + 46 + nlen + elen]
        zip64 = False
        if csize == 0xFFFFFFFF or usize == 0xFFFFFFFF or off == 0xFFFFFFFF:
            zip64 = True
            j = 0
            while j + 4 <= len(extra):
                hid, hsz = struct.unpack("<HH", extra[j:j + 4])
                body = extra[j + 4:j + 4 + hsz]
                k = 0
                if hid == 0x0001:
                    if usize == 0xFFFFFFFF:
                        usize, = struct.unpack("<Q", body[k:k + 8]); k += 8
                    if csize == 0xFFFFFFFF:
                        csize, = struct.unpack("<Q", body[k:k + 8]); k += 8
                    if off == 0xFFFFFFFF:
                        off, = struct.unpack("<Q", body[k:k + 8]); k += 8
                j += 4 + hsz
        is_dir = name.endswith("/")
        out.append({
            "member_path": name,
            "entry_type": classify(name, is_dir),
            "is_directory": is_dir,
            "compression_method": method,
            "compressed_size_bytes": csize,
            "uncompressed_size_bytes": usize,
            "crc32": "%08x" % crc,
            "local_header_offset": off,
            "zip64_extra_used": zip64,
            "version_made_by": vmade,
            "version_needed": vneed,
            "general_purpose_flags": flags,
            "dos_mod_date": mdate,
            "dos_mod_time": mtime,
            "internal_attributes": iattr,
            "external_attributes": eattr,
            "disk_number_start": disk,
            "extra_field_length": elen,
            "file_comment_length": clen,
        })
        i += 46 + nlen + elen + clen
    return out


def main():
    cd = load_central_directory(LOCAL_CD)
    if len(cd) != CD_SIZE:
        raise SystemExit("central directory length %d != %d" % (len(cd), CD_SIZE))
    got = hashlib.sha256(cd).hexdigest()
    if got != CD_SHA256:
        raise SystemExit("central directory sha256 %s != pinned %s" % (got, CD_SHA256))

    entries = parse(cd)
    if len(entries) != EXPECTED_ENTRIES:
        raise SystemExit("entry count %d != %d" % (len(entries), EXPECTED_ENTRIES))

    counts = {}
    for e in entries:
        counts[e["entry_type"]] = counts.get(e["entry_type"], 0) + 1

    doc = {
        "record_kind": "external_research_measurement_artefact",
        "classification": [
            "EXTERNAL RESEARCH / MEASUREMENT ARTEFACT",
            "NOT EVE PRODUCT STATE",
            "NOT GOVERNANCE EVIDENCE",
            "NOT AUTHORITY",
            "NOT A SIGNED H",
            "NOT ACCEPTED BASELINE STATE",
        ],
        "subject": "ZIP central-directory inventory of the published PROTECT BALTIC WP3 SDM archive",
        "source_archive": {
            "zenodo_record_id": 20309312,
            "version_doi": "10.5281/zenodo.20309312",
            "concept_doi": "10.5281/zenodo.20309311",
            "record_title": "D3.6 - Region-wide distribution models of aquatic species in the Baltic Sea",
            "record_version": "1",
            "record_publication_date": "2026-06-23",
            "record_licence": "cc-by-4.0",
            "archive_filename": "PROTECT-BALTIC-WP3-SDMs.zip",
            "archive_size_bytes": ARCHIVE_BYTES,
            "archive_md5_publisher_issued": "d713b61ae9fe125a6711ea5b0574930e",
            "archive_content_url": URL,
        },
        "measurement": {
            "measured_utc": MEASURED_UTC,
            "derived_from": "the archive's own ZIP central directory",
            "transport": "HTTP range requests (server returned 206; accept-ranges: bytes)",
            "archive_downloaded_in_full": False,
            "central_directory_offset": CD_OFFSET,
            "central_directory_size_bytes": CD_SIZE,
            "central_directory_sha256": CD_SHA256,
            "zip64": True,
            "eocd_locator": "zip64 end of central directory located via PK\\x06\\x07 in the final 70000 bytes",
            "parser": "struct.unpack('<HHHHHHIIIHHHHHII') over each PK\\x01\\x02 header; zip64 extra field 0x0001 consulted where a 32-bit field is 0xFFFFFFFF",
            "filename_encoding": "utf-8",
            "serialisation": "json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True) + trailing newline, LF line endings",
        },
        "field_semantics": {
            "crc32": "CRC-32 as published in the archive's central directory. A 32-bit cyclic redundancy check for error detection. NOT a cryptographic hash and never to be used as one. Collisions are trivially constructible; a CRC32 match does not establish that bytes are unaltered by an adversary.",
            "compressed_size_bytes": "size of the deflated member data inside the archive",
            "uncompressed_size_bytes": "size of the member after inflation",
            "local_header_offset": "byte offset of the member's PK\\x03\\x04 local header within the archive; member data begins after the local header plus its own filename and extra-field lengths",
            "compression_method": "8 = deflate, 0 = stored",
            "dos_mod_date": "raw MS-DOS date field, not decoded here",
            "dos_mod_time": "raw MS-DOS time field, not decoded here",
        },
        "accounting": {
            "central_directory_entries_total": len(entries),
            "by_entry_type": counts,
            "note": "The total counts ENTRIES in the central directory, not files. Directory entries are not files.",
        },
        "not_claimed": [
            "no cryptographic integrity claim over any member is made by this inventory",
            "no endorsement by HELCOM, the Protect Baltic project, Zenodo or the dataset authors",
            "no claim about the scientific validity or correctness of any product",
            "no claim that the archive is immutable; Zenodo version-record immutability is unmeasured here",
        ],
        "entries": entries,
    }

    text = json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    data = text.encode("utf-8")
    with open(OUT, "wb") as fh:
        fh.write(data)
    print("wrote      %s" % OUT)
    print("bytes      %d" % len(data))
    print("sha256     %s" % hashlib.sha256(data).hexdigest())
    print("entries    %d" % len(entries))
    for k in sorted(counts):
        print("  %-16s %d" % (k, counts[k]))


if __name__ == "__main__":
    main()
