import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EngineSettings:
    """Configuration values used by the Mino Music Engine."""

    album_name: str
    crossfade_seconds: float
    fade_curve: str
    opening_fade_seconds: float
    ending_fade_seconds: float
    output_bitrate: str
    sample_rate: int
    channels: int


def load_settings(settings_path: Path) -> EngineSettings:
    """Load engine settings from a JSON file."""

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

    return EngineSettings(
        album_name=str(data["album_name"]),
        crossfade_seconds=float(data["crossfade_seconds"]),
        fade_curve=str(data["fade_curve"]),
        opening_fade_seconds=float(
            data["opening_fade_seconds"]
        ),
        ending_fade_seconds=float(
            data["ending_fade_seconds"]
        ),
        output_bitrate=str(data["output_bitrate"]),
        sample_rate=int(data["sample_rate"]),
        channels=int(data["channels"]),
    )