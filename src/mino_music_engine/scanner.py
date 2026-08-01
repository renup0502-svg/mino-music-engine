from pathlib import Path


SUPPORTED_AUDIO_FORMATS = {
    ".mp3",
    ".wav",
    ".flac",
    ".m4a",
    ".aac",
    ".ogg",
}


def find_audio_tracks(music_folder: Path) -> list[Path]:
    """Find supported audio files and return them in filename order."""

    if not music_folder.exists():
        raise FileNotFoundError(
            f"Music folder does not exist: {music_folder}"
        )

    if not music_folder.is_dir():
        raise NotADirectoryError(
            f"The music path is not a folder: {music_folder}"
        )

    tracks = [
        file
        for file in music_folder.iterdir()
        if file.is_file()
        and file.suffix.lower() in SUPPORTED_AUDIO_FORMATS
    ]

    return sorted(
        tracks,
        key=lambda track: track.name.lower(),
    )