from pathlib import Path

AUDIO_EXTS = (".wav", ".m4a", ".mp3", ".ogg", ".opus", ".flac", ".aac", ".mp4")


def find_audio(directory, clip_id):
    for ext in AUDIO_EXTS:
        p = Path(directory) / f"{clip_id}{ext}"
        if p.exists():
            return p
    return None
