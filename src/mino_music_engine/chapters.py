import re
from pathlib import Path

from mino_music_engine.analyzer import TrackInfo


def clean_track_title(path: Path) -> str:
    """Remove file extension and leading track number."""

    title = path.stem

    title = re.sub(
        r"^\s*\d+\s*-\s*",
        "",
        title,
    )

    return title.strip()


def format_chapter_time(seconds: float) -> str:
    """Convert seconds to YouTube chapter timestamp format."""

    total_seconds = max(0, int(seconds))

    hours, remaining = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remaining, 60)

    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    return f"{minutes:02}:{seconds:02}"


def generate_chapters(
    tracks: list[TrackInfo],
    output_path: Path,
    crossfade_seconds: float,
    target_duration_seconds: float,
) -> list[str]:
    """Generate chapter timestamps for the final playlist."""

    if not tracks:
        raise ValueError("No tracks were provided for chapters.")

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    chapter_lines: list[str] = []
    current_start = 0.0

    for position, track in enumerate(tracks, start=1):
        if current_start >= target_duration_seconds:
            break

        timestamp = format_chapter_time(current_start)
        title = clean_track_title(track.path)

        chapter_lines.append(
            f"{timestamp} {title}"
        )

        current_start += track.duration_seconds

        if position < len(tracks):
            current_start -= crossfade_seconds

    output_path.write_text(
        "\n".join(chapter_lines) + "\n",
        encoding="utf-8",
    )

    return chapter_lines