# ZIP_INVENTORY_20309312 — PROVENANCE NOTE

```
EXTERNAL RESEARCH / MEASUREMENT ARTEFACT
NOT EVE PRODUCT STATE · NOT GOVERNANCE EVIDENCE · NOT AUTHORITY
NOT A SIGNED H · NOT ACCEPTED BASELINE STATE

No EVE product, governance, evidence, baseline, pointer or DUR-3 surface was
modified. This tree lies outside the DUR-3 walked roots and is not captured by any
snapshot.
```

Path note: the issued order wrote `D:\EVE11_research\BALTIC_PROOF\measurements\`.
Measured, the MCP filesystem roots are `D:\EVE11` and `F:\lab`; a sibling directory
`D:\EVE11_research` lies outside both and cannot be written. The owner's locked
separation is `D:\EVE11\_research\`, and these artefacts are written there.

---

## 0. MATERIALIZATION STATUS

```
MATERIALIZED   YES

inventory      D:\EVE11\_research\BALTIC_PROOF\measurements\ZIP_INVENTORY_20309312.json
written        2026-09-09 16:38:46 +0200
byte count     4 041 369
sha256         4227f14a154db244864de2bad2b71f2d5871878267b65d67e502760edebe90da
entry count    5 697
file count     5 672
builder        sha256 86e49789fec83540af766aa77a10bb22e4141520025ce31b71a78d1ce515ff01

category recount from the entries array, not read from the stored accounting block
    25   directory entries
 4 410   product rasters
 1 260   .tif.aux.xml sidecars
     2   CSV files
         sum 5 697

all 5 697 member_path values          unique
all 5 697 local_header_offset values  unique
disk artefact vs independently built reference artefact   BYTE-IDENTICAL
```

**These values were measured on the materialized artefact read back from disk, not
taken from the builder's stdout.** The builder prints a sha256 computed over the
buffer it was about to write, which is the process's statement about itself; the
figures above come from re-reading the finished file. The file count is a count of
entries whose `is_directory` is false, not the total minus the directory entries.

---

## 1. WHAT THIS INVENTORY IS

A complete, per-entry inventory of the ZIP central directory of the published
PROTECT BALTIC WP3 SDM archive. It records what the archive itself declares about
each of its members: path, type, sizes, CRC32, local-header offset and the
remaining central-directory header fields.

It is an inventory of the container's own bookkeeping. It is not an integrity
statement about any member's bytes.

---

## 2. SOURCE ARCHIVE IDENTITY

```
zenodo record id       20309312
version DOI            10.5281/zenodo.20309312
concept DOI            10.5281/zenodo.20309311
record title           D3.6 - Region-wide distribution models of aquatic species
                       in the Baltic Sea
creator                Baltic Marine Environment Protection Commission
record version         1
publication date       2026-06-23
licence                cc-by-4.0

archive filename       PROTECT-BALTIC-WP3-SDMs.zip
archive size           5 584 303 765 bytes
archive md5            d713b61ae9fe125a6711ea5b0574930e   (publisher-issued)
content URL            https://zenodo.org/api/records/20309312/files/
                       PROTECT-BALTIC-WP3-SDMs.zip/content
```

The md5 above is the publisher's. It is quoted, not endorsed: md5 is not
collision-resistant, and it covers the archive as a whole, not any member.

---

## 3. HOW IT WAS MEASURED

Derived from the archive's **own ZIP central directory**, read over **HTTP range
requests**. The archive was never downloaded in full: 5.58 GB stayed on the server
and roughly 0.9 MB was read.

```
range support          server answered 206 Partial Content, accept-ranges: bytes
zip64                  yes
EOCD location          zip64 end-of-central-directory locator (PK\x06\x07) found in
                       the final 70 000 bytes; the 32-bit EOCD carried 0xFFFFFFFF
                       for the central-directory offset, so the zip64 record was
                       consulted
central directory      offset 5 583 450 702, size 852 965 bytes
central directory hash sha256 8ae075754c9f98d9f18cdd032cce8b7f8522280386397c2b83c27d1671a883a8
declared entry count   5 697 (zip64 EOCD)
parser                 struct.unpack('<HHHHHHIIIHHHHHII') over each PK\x01\x02
                       header; zip64 extra field 0x0001 consulted wherever a 32-bit
                       size or offset field held 0xFFFFFFFF
filename encoding      utf-8
```

Measurement time: **2026-09-09, approximately 14:07 UTC**. Basis: the Zenodo `Date`
response header observed on the range-support probe in the same sequence read
`Wed, 09 Sep 2026 14:08:04 GMT`, and the central-directory read preceded it by under
a minute. The minute is therefore approximate and is recorded as approximate; the
date is measured.

Observed operational property: Zenodo intermittently answers a large range read with
`504 Gateway Timeout`. This occurred twice during measurement. The builder retries
with a linear backoff and fails closed rather than returning a partial directory.

---

## 4. ACCOUNTING — ENTRIES, NOT FILES

```
5 697   central-directory ENTRIES
   25   directory entries
4 410   product rasters        (630 species × 7 product classes)
1 260   .tif.aux.xml sidecars  (630 × binary_strict + binary_confidence)
    2   CSV files              (WP3_species_list.csv, WP3_species_review.csv)
```

`25 + 4 410 + 1 260 + 2 = 5 697`.

**5 697 is a count of entries, not of files.** A directory entry is not a file. The
file count is 5 672. Any external statement should use the category totals above
rather than the raw entry count.

---

## 5. CRC32 IS NOT A HASH

Every entry carries a CRC32 because the ZIP format stores one. CRC-32 is a 32-bit
cyclic redundancy check designed to detect accidental corruption in transmission and
storage. It is not a cryptographic hash and must never be used as one: collisions
are trivially constructible, so a CRC32 match does not establish that a member's
bytes are unaltered by an adversary.

Where a cryptographic identity for a member is required, it must be computed
independently by extracting the member and taking sha256 over the inflated bytes.
The source measurement report records three such per-member sha256 values, computed
that way and marked DERIVED.

The inventory carries this distinction in its own `field_semantics.crc32` field so
that it travels with the data rather than only with this note.

---

## 6. THE INVENTORY ARTEFACT AND HOW TO MATERIALISE IT

*This section describes the CONSTRUCTION PATH. For the current state of the
artefact, see section 0: the inventory is materialized.*

The inventory serialises to **4 041 369 bytes**, which exceeds what the filesystem
channel available to this session can write in a single operation. It was therefore
**not written directly**; instead a deterministic builder was written to disk beside
this note, and the expected output is pinned here. That statement records how the
artefact came to exist. It is not a statement that the artefact is absent.

```
builder      D:\EVE11\_research\BALTIC_PROOF\measurements\ZIP_INVENTORY_20309312_BUILD.py
             sha256 86e49789fec83540af766aa77a10bb22e4141520025ce31b71a78d1ce515ff01
             9 177 bytes

expected output
             ZIP_INVENTORY_20309312.json
             sha256 4227f14a154db244864de2bad2b71f2d5871878267b65d67e502760edebe90da
             4 041 369 bytes
             5 697 entries; 25 / 4 410 / 1 260 / 2 by category
```

To materialise it:

```
D:\EVE11\venv_gpu\Scripts\python.exe ^
  D:\EVE11\_research\BALTIC_PROOF\measurements\ZIP_INVENTORY_20309312_BUILD.py ^
  D:\EVE11\_research\BALTIC_PROOF\measurements\ZIP_INVENTORY_20309312.json
```

The script prints the byte count and sha256 of what it wrote. **Both must equal the
pinned values above.** If either differs, the inventory is not the measured one and
must not be used.

The builder is standard library only, writes exactly one file, reads nothing from
any EVE surface, and fails closed before writing if the central directory's length,
its sha256, or the entry count departs from the pinned values. An offline mode
(`--cd <file>`) parses a previously captured central directory instead of fetching.

Determinism was established by measurement, not assumed: three runs produced
byte-identical output, sha256 `4227f14a…` each time, two of them from the exact
script bytes now on disk.

This arrangement is stronger than a copy in one respect and weaker in another.
Stronger: the artefact is reproducible from the published source by a pinned rule
that anyone can re-run, and a divergence is detected rather than inherited. Weaker:
until the command is run, the inventory exists as a pinned expectation on this disk
and not as bytes. That command was run on 2026-09-09 at 16:38:46 +0200 and the
expectation was met exactly; the weakness above is historical and is retained
because it explains why the pins exist.

---

## 6A. OBSERVED TRANSPORT EVENT DURING ACQUISITION

Recorded as provenance of how the source was reached, not as a property of the
artefact.

```
attempt 1   HTTP 504 Gateway Time-out    (Zenodo)
attempt 2   HTTP 502 Bad Gateway         (Zenodo)
attempt 3   succeeded
```

Two transient gateway failures were observed while acquiring the central directory
during the materializing run. A later retry succeeded. Content identity was checked
only after successful retrieval: the retrieved bytes were length-checked and
sha256-checked against the pinned central-directory identity before any parsing, and
the builder writes nothing if either check fails.

No identity verdict was produced by either failed attempt. A transport failure says
nothing about the archive or about any member of it, and the builder does not let it
try.

Scope of this record: an **observed failure-path event during a research pass**. It
was not a designed negative test, it was not run under any governed gate, and it
establishes nothing beyond what was seen. It is written down because the sequence
actually occurred against a live external source and is useful input to a later
state model, not because it verifies anything.

---

## 7. WHAT THIS ARTEFACT DOES NOT CLAIM

```
no cryptographic integrity claim over any archive member
no claim that the archive is immutable — Zenodo version-record immutability is
   their stated policy and is UNMEASURED here
no endorsement by HELCOM, the Protect Baltic project, Zenodo or the dataset authors
no claim about the scientific validity or correctness of any product
no EVE accepted state, no governance authority, no baseline membership
```

---

## 8. RELATED ARTEFACTS

```
D:\EVE11\_research\BALTIC_PROOF\BALTIC_PROOF_001_SOURCE_MEASUREMENT.md
   sha256 cbc14137651fe7c8c11781a7039802c8b931575970f013408d4627a9c15b90dd
   43 636 bytes
   The source measurement pass this inventory belongs to. Section 3 of that report
   describes the product structure the inventory enumerates; section 13-C describes
   why per-member identity matters.
```
