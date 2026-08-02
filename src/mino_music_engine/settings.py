import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EngineSettings:
    """Album and export settings for the Mino Music Engine."""

    album_name: str
    artist: str
    album: str
    genre: str
    year: str
    comment: str
    target_duration_seconds: float
    crossfade_seconds: float
    cover_path: str
    output_filename: str


def load_settings(settings_path: Path) -> EngineSettings:
    """Load and validate settings from JSON."""

    if not settings_path.exists():
        raise FileNotFoundError(
            f"Settings file was not found: {settings_path}"
        )

    try:
        data = json.loads(
            settings_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in settings file: {error}"
        ) from error

    required_fields = [
        "album_name",
        "artist",
        "album",
        "genre",
        "year",
        "comment",
        "target_duration_seconds",
        "crossfade_seconds",
        "cover_path",
        "output_filename",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing_fields:
        raise ValueError(
            "Missing settings: "
            + ", ".join(missing_fields)
        )

    target_duration = float(
        data["target_duration_seconds"]
    )
    crossfade = float(data["crossfade_seconds"])

    if target_duration <= 0:
        raise ValueError(
            "target_duration_seconds must be greater than zero."
        )

    if crossfade < 0:
        raise ValueError(
            "crossfade_seconds cannot be negative."
        )

    return EngineSettings(
        album_name=str(data["album_name"]),
        artist=str(data["artist"]),
        album=str(data["album"]),
        genre=str(data["genre"]),
        year=str(data["year"]),
        comment=str(data["comment"]),
        target_duration_seconds=target_duration,
        crossfade_seconds=crossfade,
        cover_path=str(data["cover_path"]),
        output_filename=str(data["output_filename"]),
    )