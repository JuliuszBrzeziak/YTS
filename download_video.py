#!/usr/bin/env python3
# download_audio.py
import argparse
from pathlib import Path
import yt_dlp

def main():
    parser = argparse.ArgumentParser(description="Pobieranie tylko audio z YouTube w formacie MP3")
    parser.add_argument("--url", "-u", required=True, help="URL filmu YouTube")
    parser.add_argument("--outdir", default="outputs", help="Katalog wyjściowy (domyślnie 'outputs')")
    parser.add_argument("--mode", default="bestaudio", help="Tryb pobierania (domyślnie 'bestaudio')")
    args = parser.parse_args()



    print(args.url)   # Hardcoded URL
    print(args.mode)  # bestaudio

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Szablon nazwy pliku: np. outputs/TytułFilmu.mp3
    outtmpl = str(outdir / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",  # pobierz tylko najlepszy strumień audio
        "outtmpl": outtmpl,
        "quiet": False,
        "noprogress": False,
        # postprocessing — konwersja do MP3
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
    }

    print(f"\n Pobieranie audio z: {args.url}\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([args.url])

    print(f"\nZakończono! Plik zapisany w: {outdir.resolve()}\n")


if __name__ == "__main__":
    main()
