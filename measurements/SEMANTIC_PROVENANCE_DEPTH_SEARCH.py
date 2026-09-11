#!/usr/bin/env python3
# SEMANTIC_PROVENANCE_DEPTH_SEARCH.py
#
# EXTERNAL RESEARCH / MEASUREMENT INSTRUMENT
# Reads only. Writes one result file beside itself. Touches no EVE surface.
#
# Searches the identified published evidence for the unit and semantic definition of
# the predictor `depth`, and records the search itself so the negative result can be
# checked rather than believed.
#
# WHY THE LOGGING MATTERS. A GitHub repository is mutable. Writing "the repository
# does not contain X" without recording WHICH repository state was examined is the
# same defect this measurement was written to expose. Every remote read below is
# anchored: Zenodo records by DOI and publisher-issued md5, the repository by its
# HEAD commit SHA at measurement time.
#
# SCOPE. This establishes what could or could not be found in the evidence examined.
# It does not establish that no definition exists anywhere.

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "SEMANTIC_PROVENANCE_DEPTH_SEARCH_RESULT.json")

TARGET = "depth"
TERMS = ["depth", "bathym", "unit", "metre", "meter", "centimet", "scal",
         "transform", "predictor", "fixed_var", "substrate", "github", "commit",
         "EMODnet"]

ZENODO = [
    {"key": "D3.13", "record": 21524655, "doi": "10.5281/zenodo.21524655",
     "title": "PROTECT BALTIC - Deliverable 3.13 - Future conditions modelling code",
     "file": "D3.13 Future conditions modelling code (2).pdf",
     "url": "https://zenodo.org/api/records/21524655/files/"
            "D3.13%20Future%20conditions%20modelling%20code%20(2).pdf/content",
     "size": 974356, "md5": "41759bd8e54a9d3d6c771788e8ad1e95"},
    {"key": "D3.2", "record": 17484506, "doi": "10.5281/zenodo.17484506",
     "title": "PROTECT BALTIC Deliverable 3.2 - Environmental predictor layers "
              "modelling code",
     "file": "D3.2_Environmental predictor layers modelling code.pdf",
     "url": "https://zenodo.org/api/records/17484506/files/"
            "D3.2_Environmental%20predictor%20layers%20modelling%20code.pdf/content",
     "size": 1345039, "md5": "4ea3e7803637f3560f28341dace5db93"},
]

REPO = "helcomsecretariat/PROTECT-BALTIC-WP3-SDMs"
REPO_URL = f"https://github.com/{REPO}"
BRANCH = "main"
REPO_PATHS = ["README.md", "predictors/README.md", "predictors/predictor_list.csv"]
REPO_DIRS = ["", "predictors", "predictors/predictors_all"]


def get(url, binary=False, allow_fail=False):
    p = subprocess.run(["curl", "-s", "--max-time", "180", "-w", "\n%{http_code}", url],
                       capture_output=True)
    body, _, code = p.stdout.rpartition(b"\n")
    code = int(code.strip() or 0)
    if code != 200 and not allow_fail:
        raise RuntimeError(f"HTTP {code} for {url}")
    return body, code


def pdf_text(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    pages = [(p.extract_text() or "") for p in r.pages]
    return pages


def search(pages, terms):
    found = {}
    for t in terms:
        hits = []
        for i, page in enumerate(pages):
            for line in page.split("\n"):
                if t.lower() in line.lower():
                    hits.append({"page": i + 1, "line": line.strip()[:200]})
        found[t] = {"count": len(hits), "hits": hits[:5]}
    return found


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = {"record": "SEMANTIC_PROVENANCE_DEPTH_SEARCH_RESULT",
              "target_predictor": TARGET, "measured_utc": ts,
              "search_terms": TERMS, "zenodo": [], "repository": {}}

    # --- published deliverables --------------------------------------------
    for z in ZENODO:
        body, _ = get(z["url"], binary=True)
        md5 = hashlib.md5(body).hexdigest()
        sha = hashlib.sha256(body).hexdigest()
        ok = md5 == z["md5"] and len(body) == z["size"]
        tmp = os.path.join(HERE, f"_tmp_{z['key']}.pdf")
        open(tmp, "wb").write(body)
        try:
            pages = pdf_text(tmp)
        finally:
            os.remove(tmp)
        full = "\n".join(pages)
        entry = dict(z)
        entry.update({
            "md5_measured": md5, "sha256_measured": sha,
            "bytes_measured": len(body),
            "md5_matches_publisher": ok,
            "pages": len(pages), "extracted_chars": len(full),
            "search": search(pages, TERMS),
        })
        del entry["url"]
        result["zenodo"].append(entry)
        hits = entry["search"][TARGET]["count"]
        print(f"{z['key']:6} md5 {'OK' if ok else 'MISMATCH'}  {len(pages)} pages  "
              f"{len(full)} chars  '{TARGET}' hits: {hits}")

    # --- repository, anchored to a commit -----------------------------------
    html, _ = get(f"{REPO_URL}/commits/{BRANCH}")
    m = re.search(rb"/commit/([0-9a-f]{40})", html)
    head = m.group(1).decode() if m else None
    result["repository"] = {
        "url": REPO_URL, "branch": BRANCH, "head_commit": head,
        "head_source": "parsed from the commits page HTML at measurement time",
        "note": "a repository is mutable; this result is only about this commit",
        "files": [], "directories": [],
    }
    print(f"repo   HEAD {head}")

    if head:
        for path in REPO_PATHS:
            url = f"https://raw.githubusercontent.com/{REPO}/{head}/{path}"
            body, code = get(url, allow_fail=True)
            f = {"path": path, "http_status": code}
            if code == 200:
                f["bytes"] = len(body)
                f["sha256"] = hashlib.sha256(body).hexdigest()
                text = body.decode("utf-8", "replace")
                f["search"] = {t: text.lower().count(t.lower()) for t in TERMS}
                if path.endswith(".csv"):
                    lines = text.splitlines()
                    f["csv_header"] = lines[0] if lines else None
                    f["csv_rows"] = max(0, len(lines) - 1)
                    f["csv_rows_matching_target"] = sum(
                        1 for l in lines[1:] if TARGET in l.lower())
            result["repository"]["files"].append(f)
            print(f"       {path:38} HTTP {code}"
                  + (f"  '{TARGET}' {f.get('search', {}).get(TARGET, 0)}"
                     if code == 200 else ""))

        for d in REPO_DIRS:
            html, code = get(f"{REPO_URL}/tree/{head}/{d}".rstrip("/"),
                             allow_fail=True)
            names = sorted(set(re.findall(rb'"name":"([^"]+)"', html)))
            entries = [n.decode() for n in names]
            result["repository"]["directories"].append(
                {"path": d or "/", "http_status": code, "entries": entries,
                 "entries_matching_target": [e for e in entries if TARGET in e.lower()]})
            print(f"       dir {d or '/':34} {len(entries)} names, "
                  f"{len([e for e in entries if TARGET in e.lower()])} match '{TARGET}'")

    # --- classification -----------------------------------------------------
    unit_found = any(
        z["search"]["unit"]["count"] > 0 or z["search"]["metre"]["count"] > 0
        or z["search"]["meter"]["count"] > 0 for z in result["zenodo"])
    result["classification"] = (
        "SEMANTIC RESOLUTION" if unit_found else
        "PROOF OF ABSENCE from the identified published evidence examined")
    result["establishes"] = [
        "which artefacts were searched, at which identity, with which terms",
        "the number of matches per term in each artefact",
        "the repository state examined, by commit SHA",
    ]
    result["does_not_establish"] = [
        "that no definition of the predictor exists anywhere - only that none was "
        "found in the evidence examined",
        "that the repository lacked such a definition at any other commit",
        "anything about sources not identified from the publication metadata",
    ]

    body = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    open(OUT, "wb").write(body.encode("utf-8"))
    back = open(OUT, "rb").read()
    print()
    print("classification  " + result["classification"])
    print("result  %s" % OUT)
    print("  sha256 %s" % hashlib.sha256(back).hexdigest())
    print("  bytes  %d" % len(back))


if __name__ == "__main__":
    main()
