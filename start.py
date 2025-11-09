import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):

    print(f"[RUN] {' '.join(cmd)}")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        sys.exit(result.returncode) 


def build_parser():
    p = argparse.ArgumentParser(
        description="YT → audio → transcription orchestrator"
    )
    p.add_argument(
        "--url",
        required=True,
        help="URL filmu YouTube do pobrania (wymagany)"
    )
    p.add_argument(
        "--outdir",
        default="outputs",
        help="Katalog wyjściowy na pliki wideo/audio/transkrypt (domyślnie: outputs)"
    )
    p.add_argument(
        "--audio-format",
        default="mp3",
        choices=["mp3", "wav", "m4a", "flac", "aac", "opus"],
        help="Docelowy format audio po ekstrakcji"
    )
    p.add_argument(
        "--whisper-model",
        default="base",
        help="Model Whisper: tiny/base/small/medium/large (większe = dokładniejsze, wolniejsze)"
    )
    p.add_argument(
        "--language",
        default=None,
        help="Kod języka (np. 'pl'); None = autodetekcja"
    )
    return p


def ensure_outdir(path_str):
    outdir = Path(path_str)
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def check_cli_exists(name, version_flag="--version"):
    try:
        subprocess.run(
            [name, version_flag],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except Exception:
        return False


def step_download(url, outdir):
    run([sys.executable, "download.py", "--url", url, "--outdir", str(outdir)])

    last_path = outdir / "last_downloaded.txt"

    if not last_path.exists():
        print("[ERROR] Nie znaleziono pliku last_downloaded.txt po pobraniu.")
        sys.exit(1) 

    video_path = last_path.read_text().strip()

    if not Path(video_path).exists():
        print(f"[ERROR] Pobierany plik wideo nie istnieje: {video_path}")
        sys.exit(1)

    return video_path


def step_extract_audio(video_path, outdir, audio_format, copy=False):
    cmd = [sys.executable, "extract_audio.py", "--input", video_path,
           "--outdir", str(outdir), "--audio-format", audio_format]
    
    if copy:
        cmd.append("--copy")

    run(cmd)

    audio_path = outdir / f"audio.{audio_format}"

    if not audio_path.exists():
        print(f"[ERROR] Nie znaleziono wyjściowego audio: {audio_path}")
        sys.exit(1)

    return str(audio_path)


def step_transcribe(audio_path, outdir, model, language):
    cmd = [sys.executable, "transcribe_audio.py", "--audio", audio_path,
           "--model", model, "--outdir", str(outdir)]
    
    if language:
        cmd += ["--language", language]

    run(cmd)

    transcript = outdir / "transcript.txt"

    if not transcript.exists():
        print(f"[ERROR] Brak transcript.txt w {outdir}")
        sys.exit(1)

    return str(transcript)



def main():
    print("YT → Audio → Transkrypcja")
    parser = build_parser()
    args = parser.parse_args()

    outdir = ensure_outdir(args.outdir)

    # Szybkie sanity-checki (opcjonalne, ale pomocne)
    if not check_cli_exists("ffmpeg", "-version"):
        print("Uwaga: ffmpeg nie jest dostępny w PATH. Zainstaluj i dodaj do PATH, inaczej ekstrakcja się nie uda.")
    if not check_cli_exists(sys.executable, "--version"):
        print("Uwaga: problem z interpreterem Pythona?")

    print("[1/3] Pobieranie wideo…")
    video_path = step_download(args.url, outdir)

    print("[2/3] Ekstrakcja audio…")
    audio_path = step_extract_audio(video_path, outdir, args.audio_format, copy=False)

    print("[3/3] Transkrypcja…")
    transcript_path = step_transcribe(audio_path, outdir, args.whisper_model, args.language)

    print(f"Zakończono. Transkrypt: {transcript_path}")


if __name__ == "__main__":
    main()