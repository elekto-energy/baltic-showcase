#!/usr/bin/env python3
# PRODUCT_ROLE_COLLISION_MEASURE.py
#
# EXTERNAL RESEARCH / MEASUREMENT INSTRUMENT
# Reads only. Writes one result file beside itself. Touches no EVE surface.
#
# Question: for how many species do two DECLARED product roles carry the same
# content, as far as the archive's own central directory can establish?
#
# Method: read ZIP_INVENTORY_20309312.json, which was built from the central
# directory of PROTECT-BALTIC-WP3-SDMs.zip. For every species, compare crc32 and
# uncompressed size across all seven product families. Report every family pair
# that coincides.
#
# WHAT THIS ESTABLISHES: identical uncompressed size and identical CRC32 in the
# archive metadata. CRC32 is 32 bits, so this is a very strong indication of
# identical content, NOT a proof of byte identity. Full byte identity has been
# established only for the members actually retrieved and hashed.
#
# WHAT THIS DOES NOT ESTABLISH: why the collision occurs. Envelope masking is a
# plausible cause and is a hypothesis, not something bound here to published code.

import hashlib
import json
import os
import sys
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
INVENTORY = os.path.join(HERE, "ZIP_INVENTORY_20309312.json")
OUT = os.path.join(HERE, "PRODUCT_ROLE_COLLISION_RESULT.json")

EXPECTED_INVENTORY_SHA256 = "4227f14a"  # prefix only; full value printed at runtime


def main():
    if not os.path.isfile(INVENTORY):
        print("inventory not found: %s" % INVENTORY, file=sys.stderr)
        raise SystemExit(2)

    raw = open(INVENTORY, "rb").read()
    inv_sha = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw.decode("utf-8"))

    entries = [e for e in data["entries"]
               if not e.get("is_directory") and e["member_path"].endswith(".tif")]

    # (group, species) -> {family: (crc32, uncompressed_size)}
    by_species = defaultdict(dict)
    families = set()
    for e in entries:
        parts = e["member_path"].replace("PROTECT-BALTIC-WP3-SDMs/", "").split("/")
        if len(parts) != 3:
            continue
        group, family, filename = parts
        species = filename[:-4]
        families.add(family)
        by_species[(group, species)][family] = (e["crc32"], e["uncompressed_size_bytes"])

    pair_counts = Counter()
    collisions = []
    for (group, species), fams in by_species.items():
        seen = defaultdict(list)
        for fam, key in fams.items():
            seen[key].append(fam)
        for key, fam_list in seen.items():
            if len(fam_list) > 1:
                pair = tuple(sorted(fam_list))
                pair_counts[pair] += 1
                collisions.append({
                    "group": group, "species": species,
                    "families": list(pair),
                    "crc32": key[0], "uncompressed_size_bytes": key[1]})

    result = {
        "record": "PRODUCT_ROLE_COLLISION_RESULT",
        "measured_from": {
            "file": os.path.basename(INVENTORY),
            "sha256": inv_sha,
            "bytes": len(raw),
            "source_archive": data.get("source_archive", {}),
        },
        "scope": {
            "raster_entries_considered": len(entries),
            "species": len(by_species),
            "product_families": sorted(families),
        },
        "coinciding_family_pairs": [
            {"families": list(p), "species_count": n}
            for p, n in pair_counts.most_common()
        ],
        "establishes":
            "identical uncompressed size and identical CRC32 in the archive's own "
            "central directory for the listed species and family pairs",
        "does_not_establish": [
            "byte identity - CRC32 is 32 bits and this is an indication, not a proof",
            "the cause of the collision - envelope masking is a hypothesis, not bound "
            "here to published code or method description",
            "anything about product roles other than that two declared roles carry "
            "the same content for these species",
        ],
        "collisions": sorted(collisions, key=lambda c: (c["group"], c["species"])),
    }

    body = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    with open(OUT, "wb") as fh:
        fh.write(body.encode("utf-8"))

    back = open(OUT, "rb").read()

    print("inventory  %s" % os.path.basename(INVENTORY))
    print("  sha256   %s" % inv_sha)
    print("  bytes    %d" % len(raw))
    print()
    print("raster entries considered  %d" % len(entries))
    print("species                    %d" % len(by_species))
    print("product families           %d  %s" % (len(families), ", ".join(sorted(families))))
    print()
    print("coinciding family pairs, counted over species:")
    if not pair_counts:
        print("  none")
    for p, n in pair_counts.most_common():
        print("  %-45s %d of %d species" % (" == ".join(p), n, len(by_species)))
    print()
    print("result   %s" % OUT)
    print("  sha256 %s" % hashlib.sha256(back).hexdigest())
    print("  bytes  %d" % len(back))
    print()
    print("Establishes identical size and CRC32 in the archive metadata.")
    print("Does NOT establish byte identity: CRC32 is 32 bits.")


if __name__ == "__main__":
    main()
