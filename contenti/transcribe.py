"""Stage 2 — transcribe downloaded videos with faster-whisper.

faster-whisper decodes audio from the video file directly (via PyAV), so no
separate ffmpeg extraction step is required, though having ffmpeg installed
helps with odd containers.
"""

from __future__ import annotations

from contenti.store import (
    Item,
    find_video,
    load_items,
    save_meta,
    transcript_path,
)


def transcribe_dir(
    data_dir: str,
    model_size: str = "small",
    language: str | None = None,
    device: str = "auto",
    compute_type: str = "default",
    overwrite: bool = False,
) -> int:
    from faster_whisper import WhisperModel

    items = load_items(data_dir)
    if not items:
        raise SystemExit(f"[transcribe] no downloaded items found in {data_dir}")

    print(f"[transcribe] loading model '{model_size}' (device={device})...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    done = 0
    for item in items:
        out_txt = transcript_path(item.dir)
        if out_txt.exists() and not overwrite:
            print(f"[transcribe] {item.shortcode}: already transcribed, skipping")
            continue

        video = find_video(item.dir)
        if not video:
            print(f"[transcribe] {item.shortcode}: no video file, skipping")
            continue

        print(f"[transcribe] {item.shortcode}: transcribing {video.name}...")
        segments, info = model.transcribe(str(video), language=language, vad_filter=True)
        text = " ".join(seg.text.strip() for seg in segments).strip()

        out_txt.write_text(text, encoding="utf-8")
        item.language = info.language or ""
        if item.duration is None:
            item.duration = float(getattr(info, "duration", 0.0)) or None
        save_meta(item)
        done += 1
        preview = (text[:80] + "...") if len(text) > 80 else text
        print(f"[transcribe] {item.shortcode}: [{info.language}] {preview}")

    print(f"[transcribe] done: {done} new transcripts")
    return done
