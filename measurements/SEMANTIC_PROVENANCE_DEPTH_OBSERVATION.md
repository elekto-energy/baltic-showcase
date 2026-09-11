# Semantic Provenance — `depth`

```
EXTERNAL RESEARCH / OBSERVATION
Written 2026-09-11. Status changed from OPEN to PROOF OF ABSENCE the same day,
after the search recorded in SEMANTIC_PROVENANCE_DEPTH_SEARCH.py was run.

STATUS: PROOF OF ABSENCE from the identified published evidence examined.

This does NOT state that no definition exists. It states that the unit and semantic
definition could not be established from the identified published evidence that was
actually examined, and it records exactly which evidence that was.
```

## Observation

For the BALTIC-CHAIN cell, the published GeoTIFF exposes:

```
band name      depth
raster value   3852.9119
unit           not identified in the examined GDAL_METADATA
cell           row 3387, column 2035
artefact       fixed_var_stack.tif, Zenodo 21523969
```

The value is reproducibly retrievable from the published artefact. Its semantic
interpretation could not be established from the evidence examined.

## Search chain, in the order followed

```
GeoTIFF fixed_var_stack.tif
   ↓  band name present, no unit
D3.13  "Future conditions modelling code"
   ↓  no match
D3.2   "Environmental predictor layers modelling code"
   ↓  no match
published repository, at commit 2ded2551
   ↓  README, predictors/README, predictor_list.csv
predictors/predictors_all/depth.tif
   ↓  present as an INPUT raster; no code identified that creates or defines it
END OF IDENTIFIED CHAIN
```

Reproducible with `SEMANTIC_PROVENANCE_DEPTH_SEARCH.py`, which records artefact
identities, the repository commit, every search term, every match count and the HTTP
status of every path requested.

## Negative observations, with the identity each was measured against

**1 · `fixed_var_stack.tif`** — Zenodo 21523969, 258 767 525 B,
md5 `fec2be03c56e63c4b55048f904d9c589`

```
all 16 band names present as DESCRIPTION items in GDAL_METADATA
no unit, scale, datum or definition accompanies any band
```

**2 · D3.13** — Zenodo 21524655, 974 356 B, md5 `41759bd8e54a9d3d6c771788e8ad1e95`,
md5 verified at measurement time. 5 pages, 4 212 characters extracted.

```
"depth"      0        "unit"       0        "bathym"     0
"metre"      0        "meter"      0        "centimet"   0
"transform"  0        "predictor"  0        "substrate"  0
"scal"       0        "EMODnet"    0        "commit"     0
"github"     1  — prose mention, no URL
```

The deliverable describes a Zonation 5 hotspot prioritisation workflow. It is not the
document in which a predictor layer would be defined.

**3 · D3.2** — Zenodo 17484506, 1 345 039 B, md5 `4ea3e7803637f3560f28341dace5db93`,
md5 verified at measurement time. 5 pages, 3 590 characters extracted.

```
"depth"      0        "unit"       0        "bathym"     0
"metre"      0        "meter"      0        "substrate"  0
"EMODnet"    0        "transform"  0
"github"     1  — prose mention, no URL
"scal"       2  — "Baltic scale", "downscaled to a common"
```

This is the deliverable whose title names the environmental predictor layers. It
contains no unit or definition for any predictor.

**4 · Repository** — `github.com/helcomsecretariat/PROTECT-BALTIC-WP3-SDMs`,
branch `main`, HEAD `2ded2551c8a85745d9fd82242bee94457bdd5ede` at measurement time.

```
README.md                        HTTP 200 · "depth" 0 · links to Zenodo 20309312
                                 and to a GitHub Pages viewer
predictors/README.md             HTTP 404
predictors/predictor_list.csv    HTTP 200 · columns: species_group, predictor
                                 44 rows · 7 rows contain "depth"
                                 NO unit column, NO definition column
predictors/predictors_all/       69 entries · 4 contain "depth"
                                 depth.tif is present as a raster INPUT
```

**No code that creates or defines `depth` was identified in the repository at this
commit.** The only R file in `predictors/` is `vif_test.R`, a collinearity test. The
predictor rasters are inputs to this repository, not outputs of it.

The same HEAD commit `2ded2551` was recorded in
`BALTIC_PROOF_001_SOURCE_MEASUREMENT.md` on 2026-09-09, so the repository is
unchanged between the two measurements.

## Result

```
identity      verified      artefact bound by DOI, size and publisher md5
bytes         verifiable    retrieved by HTTP range, CRC32 checked after inflate
cell          verified      grid geometry identical across the three artefacts
value         verified      3852.9119, reproduced by two independent runs
name          verified      "depth", from the artefact's own GDAL_METADATA
meaning       NOT ESTABLISHED from the identified published evidence examined
```

## Scope of this result

```
ESTABLISHED
  which artefacts were searched, at which identity, with which terms
  that no unit or definition for `depth` was found in any of them
  the repository state examined, by commit SHA

NOT ESTABLISHED
  that no definition exists - a definition may exist in a source not identified
      from the publication metadata examined here
  that the repository lacked such a definition at any other commit
  what the value 3852.9119 represents

NOTED, NOT CONCLUDED
  D3.6 lists EMODnet among its related identifiers, and EMODnet bathymetry is
  normally expressed in metres. That reference is not bound to this predictor, and
  3852.9 metres is not a plausible Baltic depth - the deepest point of the Baltic
  Sea is 459 m. The candidate external source therefore does not explain the value,
  and no inference is drawn from it.
```

## Reach of the predictor

```
predictor_list.csv identifies `depth` as a predictor for all three species groups
represented in that file.
```

This is stated at the level the file supports. It does not establish how any
individual model uses the variable, or that any particular model output depends on
the unit being known.

## Separate finding — not evidence for this result

Recorded apart because the Proof of Absence above stands without it, and because a
reasonable objection exists to it.

```
Two deliverables titled "modelling code" — D3.13 and D3.2 — each contain exactly one
PDF and no code artefact. Both state that supporting files are available through the
project's GitHub repository. Neither record carries a related identifier to that
repository, and no commit identity appears anywhere in the publication metadata
examined.
```

The objection: a deliverable titled "modelling code" need not package the code
itself. That objection is reasonable and does not affect the result above, which is
why the two are kept apart.

## Related observations from the same cell, also unresolved

Overlapping or non-exclusive class representations are ordinary in substrate
modelling. These are recorded as open, not as defects.

```
substrate_soft 51.5483 · substrate_sand 39.3058 · substrate_coarse 50.7417
substrate_hard 48.5833
    these do not sum to a single whole; whether they are percentages, scores or
    probabilities of separate classes is not established

substrate_hard_binary 1.0 and substrate_soft_binary 1.0 in the same cell,
substrate_mixed_binary 0.0
    whether these flags are mutually exclusive is not established
```

## Method note

The retrieved values are environmentally plausible for a Baltic coastal cell and
provide a useful sanity check. **Spatial identity is established independently, from
the matching grid geometry** — identical CRS code, dimensions, pixel size and origin
across the three artefacts. Plausibility is not the evidence for the binding.

## Why this file exists

A reading can be syntactically correct and semantically wrong. Earlier in this
measurement the same raster row was read without undoing TIFF `Predictor = 2`, which
produced eleven plausible-looking zeros that were differences rather than values.

The same risk applies to this file. Writing "the repository does not contain a
definition" without recording which repository state was examined would repeat, in
our own work, the defect this measurement describes. That is why the commit SHA is
recorded and why the search is a script rather than a claim.

```
No assumption should be made that 3852.9119 represents metres, centimetres or any
other unit until independently established from evidence.
```
