# Measurements

The files behind the claim on [baltic.eveverified.com](https://baltic.eveverified.com) that
**506 of 630 species have identical uncompressed size and CRC32 between the `binary_tif` and
`binary_envelope_tif` product families** in the Protect Baltic WP3 SDMs archive.

They are here so the number can be checked rather than taken on trust.

---

## Files

```
ZIP_INVENTORY_20309312_BUILD.py        builds the inventory from the published archive
ZIP_INVENTORY_20309312.json            the inventory it produces      4 041 369 B
ZIP_INVENTORY_20309312_PROVENANCE.md   how the inventory was obtained
PRODUCT_ROLE_COLLISION_MEASURE.py      the measurement
PRODUCT_ROLE_COLLISION_RESULT.json     its output                       118 144 B
```

Measured identities, so a clone can be compared against what was published:

```
ZIP_INVENTORY_20309312.json         sha256 4227f14a154db244864de2bad2b71f2d5871878267b65d67e502760edebe90da
PRODUCT_ROLE_COLLISION_RESULT.json  sha256 4fbdcbc945a2d5b866e8a802b70446678739087cb05e911362b1593c8971218d
```

This directory carries a `.gitattributes` with `* -text`, so git performs no line-ending
conversion. Without it a checkout on Windows would change the bytes and the hashes above
would no longer reproduce.

---

## Reproducing it

The measurement reads the inventory and needs nothing else:

```
python PRODUCT_ROLE_COLLISION_MEASURE.py
```

It prints the inventory identity it used, the counts per product family, and writes
`PRODUCT_ROLE_COLLISION_RESULT.json`. Compare that file's sha256 with the value above.

To rebuild the inventory from the source rather than trusting the copy here, run
`ZIP_INVENTORY_20309312_BUILD.py`. It reads the ZIP central directory of the published
archive over HTTP byte range — it does not download the 5.58 GB archive. The provenance
file records exactly what was requested and how the response was verified.

Source: Zenodo record [20309312](https://doi.org/10.5281/zenodo.20309312), CC-BY-4.0.

---

## What the measurement establishes, and what it does not

**Establishes:** for 506 of the 630 species, the two product families hold entries with the
same uncompressed size and the same CRC32 in the archive's own central directory.

**Does not establish byte identity.** CRC32 is 32 bits. Identical size and CRC32 across two
entries indicates identical content strongly, but it is not proof. Full byte identity was
verified only for the species inspected individually.

The measurement says nothing about whether either product family is correct, or about which
of them a given downstream use should have cited. It is a statement about identity, not
about role — which is the point being made on the showcase page: where two artefacts carry
the same content hash, that hash cannot tell you which role each one played.

---

This is independent research using publicly available Protect Baltic WP3 data. It is not part
of the Protect Baltic project and does not represent SLU, HELCOM or project partners.
