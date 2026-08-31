#!/usr/bin/env python3
"""Package results/ into a zip you can upload to Gradescope.

    python3 make_submission.py

Checks what you are about to hand in before zipping it: every file present, valid
JSON, and no `None` left over from the notebook's stubs. Finding a missing part
here takes a second; finding it from a Gradescope score takes a submission.
"""

import argparse
import json
import os
import sys
import zipfile

REPO = os.path.dirname(os.path.abspath(__file__))

# Each entry: filename, the part it comes from, and the shape it should have.
# "shape" is a callable returning None when the file looks right, or a complaint.
MODELS = 4


def models_dict(n_per_model=None):
    def check(obj):
        if not isinstance(obj, dict):
            return f"expected an object keyed by model name, got {type(obj).__name__}"
        if len(obj) != MODELS:
            return f"expected {MODELS} models, found {len(obj)}: {sorted(obj)}"
        if n_per_model is not None:
            for model, values in obj.items():
                if not isinstance(values, list) or len(values) != n_per_model:
                    return f"expected {n_per_model} values for {model}, found {len(values) if isinstance(values, list) else type(values).__name__}"
        return None
    return check


def per_class(n):
    def check(obj):
        if not isinstance(obj, dict):
            return f"expected an object keyed by class name, got {type(obj).__name__}"
        if len(obj) != n:
            return f"expected {n} entries, found {len(obj)}"
        return None
    return check


def list_of(n, inner=None):
    def check(obj):
        if not isinstance(obj, list) or len(obj) != n:
            return f"expected a list of {n}, found {len(obj) if isinstance(obj, list) else type(obj).__name__}"
        if inner:
            for i, item in enumerate(obj):
                problem = inner(item)
                if problem:
                    return f"entry {i}: {problem}"
        return None
    return check


def language_dict(n_per_language):
    def check(obj):
        if not isinstance(obj, dict):
            return f"expected an object keyed by language, got {type(obj).__name__}"
        for language, values in obj.items():
            if not isinstance(values, list) or len(values) != n_per_language:
                return f"expected {n_per_language} values for {language}, found {len(values) if isinstance(values, list) else type(values).__name__}"
        return None
    return check


REQUIRED = [
    ("accuracies.json",                 "1.2", models_dict()),
    ("best_model_prec.json",            "1.3", per_class(20)),
    ("best_model_rec.json",             "1.4", per_class(20)),
    ("f1s.json",                        "1.5", models_dict()),
    ("language_wers.json",              "2.1", language_dict(20)),
    ("language_wer_cis.json",           "2.2", language_dict(2)),
    ("ngram_precisions_cs.json",        "3.1", models_dict(25)),
    ("brevity_penalties_cs.json",       "3.2", models_dict(25)),
    ("bleu_scores_cs.json",             "3.3", models_dict(25)),
    ("bleu_scores_zh.json",             "3.3", models_dict(25)),
    ("bleu_scores_gu.json",             "3.3", models_dict(25)),
    ("head_to_head_judgements.json",    "4.1", list_of(10, per_class(12))),
    ("attribute_preds.json",            "4.2", list_of(10, list_of(MODELS))),
    ("new_head_to_head_judgements.json","4.4", list_of(10, per_class(12))),
]


def count_blanks(obj):
    """How many None values are left anywhere in a nested json structure."""
    if isinstance(obj, dict):
        return sum(count_blanks(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_blanks(v) for v in obj)
    return 1 if obj is None else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", default=os.path.join(REPO, "results"))
    parser.add_argument("--out", default=os.path.join(REPO, "submission.zip"))
    parser.add_argument("--pdf", default=os.path.join(REPO, "HW1.pdf"),
                        help="PDF export of the notebook, included if it exists")
    args = parser.parse_args()

    if not os.path.isdir(args.results):
        sys.exit(f"no results directory at {args.results} -- run the notebook first")

    ready, problems = [], []
    print(f"{'part':>5}  {'file':<34} status")
    print("-" * 72)
    for name, part, shape in REQUIRED:
        path = os.path.join(args.results, name)
        if not os.path.exists(path):
            print(f"{part:>5}  {name:<34} MISSING -- run the cell that saves it")
            problems.append(name)
            continue
        try:
            with open(path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"{part:>5}  {name:<34} NOT VALID JSON ({e})")
            problems.append(name)
            continue

        blanks = count_blanks(data)
        complaint = shape(data)
        if blanks:
            print(f"{part:>5}  {name:<34} {blanks} unfilled null(s) -- Part {part} is not implemented yet")
            problems.append(name)
        elif complaint:
            print(f"{part:>5}  {name:<34} unexpected shape: {complaint}")
            problems.append(name)
        else:
            print(f"{part:>5}  {name:<34} ok")
        ready.append(path)

    pdf = args.pdf if os.path.exists(args.pdf) else None
    print("-" * 72)
    if pdf:
        print(f"{'':>5}  {os.path.basename(pdf):<34} ok ({os.path.getsize(pdf) / 1024:.0f} KB)")
    else:
        print(f"{'':>5}  {'HW1.pdf':<34} not found -- export the notebook to PDF for the written part")

    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in ready:
            z.write(path, os.path.basename(path))
        if pdf:
            z.write(pdf, os.path.basename(pdf))

    print(f"\nwrote {args.out} ({os.path.getsize(args.out) / 1024:.0f} KB, {len(ready) + bool(pdf)} files)")
    if problems:
        print(f"\n{len(problems)} file(s) above still need work. The zip was written anyway, so you "
              f"can submit partial progress, but those parts will not score.")
    else:
        print("\nEverything checks out. Upload this to Gradescope.")


if __name__ == "__main__":
    main()
