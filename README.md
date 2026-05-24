# contenti

Download an Instagram account's videos, transcribe the audio, and produce an
LLM-written analysis of the account's content strategy.

The pipeline has three stages that you can run together or separately:

1. **download** — pull every video (Reel/video post) from a profile via
   [`instaloader`](https://instaloader.github.io/), saving the media plus
   metadata (caption, date, likes, views, hashtags).
2. **transcribe** — turn the spoken audio into text with
   [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper).
3. **analyze** — distil each video's "essence" and generate a Markdown report
   about the account using the Anthropic API.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`ffmpeg` is recommended (helps with some video containers):

```bash
# macOS:  brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
```

## Authentication & API keys

- **Instagram**: anonymous scraping is heavily rate-limited. Log in once to
  create a reusable session, then pass `--login`:

  ```bash
  instaloader -l YOUR_INSTAGRAM_USERNAME      # creates a session file
  ```

- **Analysis**: set your Anthropic key:

  ```bash
  export ANTHROPIC_API_KEY=sk-ant-...
  # optional: export CONTENTI_MODEL=claude-sonnet-4-6
  ```

> **Note:** Only download content you are allowed to. Scraping at scale may
> conflict with Instagram's Terms of Service — use this on your own account
> or with permission, for research/analysis purposes.

## Usage

Full pipeline for one account:

```bash
python -m contenti run kirills_finance --login YOUR_IG_USERNAME --limit 30
```

Or stage by stage:

```bash
python -m contenti download kirills_finance --login YOUR_IG_USERNAME --limit 30
python -m contenti transcribe data/kirills_finance --model small --lang ru
python -m contenti analyze   data/kirills_finance --report-lang Russian
```

The report lands at `data/<username>/report.md`, with per-video metadata and
transcripts kept alongside each video under `data/<username>/<shortcode>/`.

## Useful flags

| Flag | Stage | Meaning |
|------|-------|---------|
| `--limit N` | download | stop after N videos |
| `--login USER` | download | use a saved instaloader session |
| `--model SIZE` | transcribe | `tiny`…`large-v3` (default `small`) |
| `--lang ru` | transcribe | force language instead of auto-detect |
| `--device cuda` | transcribe | run whisper on GPU |
| `--report-lang` | analyze | language of the written report |
| `--max-videos N` | analyze | cap how many videos go to the LLM |

## Why a tool instead of a one-off

This was built to run wherever Instagram is reachable. Sandboxed/cloud
environments often block `instagram.com`, so the pipeline is packaged as a
reusable CLI you point at any public account.
