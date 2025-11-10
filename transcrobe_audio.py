#!/usr/bin/env python3
# transcribe_audio.py
import argparse
from pathlib import Path
import whis
import time
from tqdm import tqdm

def build_parser():
    p = argparse.ArgumentParser(description="Transkrypcja audio na tekst (Whisper)")
    p.add_argument("--audio", required=True, help="Ścieżka do pliku audio (np. .mp3, .wav, .m4a, .opus)")
    p.add_argument("--model", default="base", help="tiny/base/small/medium/large/large-v2/large-v3")
    p.add_argument("--language", default=None, help="Kod ISO-639-1, np. 'pl' (autodetekcja gdy None)")
    p.add_argument("--outdir", default="outputs", help="Katalog wyjściowy")
    # Przydatne opcje jakości/szybkości:
    p.add_argument("--vad", action="store_true", help="Włącz prostą VAD (segmentacja ciszy) przez split_on_silence")
    p.add_argument("--timestamps", action="store_true", help="Zapisz również znaczniki czasowe segmentów")
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Ładowanie modelu Whisper: {args.model}")
    model = whis.load_model(args.model)

    # Opcje transkrypcji
    transcribe_kwargs = {}
    if args.language:
        transcribe_kwargs["language"] = args.language
    # Umiarkowane zwiększenie jakości kosztem czasu:
    print(f"Ustawienia transkrypcji: VAD={args.vad}, Timestamps={args.timestamps}")
    transcribe_kwargs.update(dict(beam_size=5, best_of=5))

    # Główna transkrypcja
    print(f"Transkrypcja: {args.audio}")
    duration = whis.audio.load_audio(args.audio).shape[0] / whis.audio.SAMPLE_RATE
    with tqdm(total=duration, desc="Transkrypcja w toku", unit="sekundy") as pbar:
        def progress_callback(progress):
            pbar.update(progress - pbar.n)

        # result = model.transcribe(args.audio, **transcribe_kwargs, progress_callback=progress_callback)
        result = model.transcribe(args.audio, **transcribe_kwargs)


    # Zapis prostego tekstu
    (outdir / "transcript.txt").write_text(result.get("text", "").strip() + "\n", encoding="utf-8")
    print(f"Zapisano: {outdir / 'transcript.txt'}")

    # Opcjonalnie: segmenty i timestampy
    if args.timestamps:
        from json import dumps
        segments = result.get("segments", [])
        # Minimalny JSON z [start, end, text]
        data = [
            {"start": round(seg.get("start", 0.0), 3),
             "end": round(seg.get("end", 0.0), 3),
             "text": seg.get("text", "").strip()}
            for seg in segments
        ]
        (outdir / "transcript_segments.json").write_text(dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Zapisano: {outdir / 'transcript_segments.json'}")

if __name__ == "__main__":
    main()
