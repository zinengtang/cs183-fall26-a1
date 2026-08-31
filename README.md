# Assignment 1: Evaluating Language Technologies

All the work happens in `HW1.ipynb`. Set up with one of the two below, then run
the notebook from the top.

## Colab setup

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/zinengtang/cs183-fall26-a1/blob/main/HW1.ipynb)


1. Click the badge.
2. **Runtime → Change runtime type → GPU**.
3. Run the first cell. Say yes when it asks to mount Google Drive.
4. Wait for `Ready.`, then run the rest of the notebook.

## Prefer your own machine?

Install [ollama](https://ollama.com/download), clone this repo, then from it:

```bash
conda create -y -n ugrad-nlp python=3.10 jupyter jupyterlab && conda activate ugrad-nlp
pip install -r requirements.txt
ollama pull llama3.2:1b && ollama pull llama3.2 && ollama pull gemma3:1b && ollama pull gemma3:4b && ollama pull qwen3:8b
jupyter lab
```

Mac also needs `brew install ffmpeg`. Nothing times out on you this way, and the
cache survives without Drive. Worth it if you have ~13GB free.

**That is the whole setup.** Everything below is reference: read it when
something breaks, or when you reach Part 4 on Colab.

---

## When you reach Part 4 on Colab

Part 4 uses `qwen3:8b` as the judge, a 5.2GB download the notebook pulls when
you get there rather than during setup. It fits a free Colab GPU runtime with
room to spare.

Part 4 makes 280 calls to it, which takes roughly half an hour. Colab
disconnects idle sessions, so keep the tab in front of you while it runs.
Your generations are cached in Drive as they finish, so a disconnect costs you
time rather than work.

## If you cannot get ollama working

`inference_cache_reference/` holds the generations we got from the four models
for Parts 1, 3 and 4.0. Copying them across makes the notebook use those instead
of calling ollama:

```bash
cp inference_cache_reference/*.json inference_cache/
```

Do this only if you genuinely cannot run the models, and say so in your writeup.
Prompting them yourself is one of the things the assignment is for, and it is
also the only way Part 4 works. There are no cached judge verdicts, so 4.1, 4.2
and 4.4 still need a running ollama either way.

## If something breaks

**`Cannot connect to host localhost:11434`**. ollama is not running. Start
`ollama serve` locally, or re-run the first cell on Colab.

**Every prediction is an empty string**. That model was never pulled. Check
with `ollama list`.

**Part 1 accuracies look far too low**. Model output is raw text, not a clean
label, and most answers end in a newline. Part 1.0 gives you
`normalize_prediction`; use it everywhere you compare a prediction to a label.

**Colab threw away my work**. Run `ls -l inference_cache`; it should show a symlink
into Drive. If you skipped the first cell, it won't, and nothing was saved.

## How long it takes

| | |
| --- | --- |
| Setup | ~13GB of models, 10 to 20 min |
| Part 1 | 800 calls to the small models |
| Part 2 | minutes; the transcripts ship with the repo, so no audio is downloaded |
| Part 3 | 300 calls to the small models |
| Part 4 | 280 calls to the 8B judge, about half an hour |

Generations are cached in `inference_cache/` as they finish, so an interrupted
run resumes instead of starting over.

## Submitting

Run this when you are done:

```bash
python3 make_submission.py
```

It checks every file the notebook was supposed to write: all present, valid
JSON, nothing left unimplemented. Then it packs them into `submission.zip` for
you. Anything still missing is listed with the part it belongs to.

What ends up in the zip:

* The fourteen json files the notebook writes into `results/`.
* `HW1.pdf`, if you have exported the notebook. Every starred question is graded
  from this, so check that your plots actually rendered before you export.

