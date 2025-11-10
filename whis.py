import whisper

# Wczytanie modelu (możesz zmienić na tiny, base, small, medium, large)
model = whisper.load_model("small")

# Transkrypcja nagrania
result = model.transcribe("./outputs/audio.mp3", language="pl")

# Wyświetlenie tekstu
print("📜 Rozpoznany tekst:")
print(result["text"])
