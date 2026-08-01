import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TrackInfo:
    """Technical information about one audio track."""

    path: Path
    duration_seconds: float
    codec: str
    bitrate_kbps: int
    sample_rate_hz: int
    channels: int


def analyze_track(track_path: Path) -> TrackInfo:
    """Read technical audio information using ffprobe."""

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,bit_rate:"
        "stream=codec_name,sample_rate,channels,bit_rate",
        "-of",
        "json",
        str(track_path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "ffprobe was not found. Check your FFmpeg installation."
        ) from error
    except subprocess.CalledProcessError as error:
        message = error.stderr.strip() or "Unknown ffprobe error."
        raise RuntimeError(
            f"Could not analyze {track_path.name}: {message}"
        ) from error

    data = json.loads(result.stdout)

    audio_streams = [
        stream
        for stream in data.get("streams", [])
        if stream.get("codec_name")
    ]

    if not audio_streams:
        raise RuntimeError(
            f"No valid audio stream found in {track_path.name}."
        )

    stream = audio_streams[0]
    format_data = data.get("format", {})

    bitrate_value = (
        stream.get("bit_rate")
        or format_data.get("bit_rate")
        or 0
    )

    return TrackInfo(
        path=track_path,
        duration_seconds=float(format_data.get("duration", 0)),
        codec=str(stream.get("codec_name", "unknown")),
        bitrate_kbps=round(int(bitrate_value) / 1000),
        sample_rate_hz=int(stream.get("sample_rate", 0)),
        channels=int(stream.get("channels", 0)),
    )


def format_duration(seconds: float) -> str:
    """Convert seconds into MM:SS format."""

    total_seconds = round(seconds)
    minutes, remaining_seconds = divmod(total_seconds, 60)

    return f"{minutes:02}:{remaining_seconds:02}"