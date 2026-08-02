import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from mino_music_engine.analyzer import (
    TrackInfo,
    format_duration,
)


def create_reports(
    output_folder: Path,
    album_name: str,
    playlist: list[TrackInfo],
    duration_seconds: float,
    crossfade_seconds: float,
) -> None:
    """
    Generate production reports.
    """

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------
    # Album JSON
    # -----------------------------

    album = {
        "album": album_name,
        "duration": format_duration(duration_seconds),
        "tracks": len(playlist),
        "crossfade_seconds": crossfade_seconds,
        "generated": datetime.now().isoformat(),
    }

    (
        output_folder / "album_report.json"
    ).write_text(
        json.dumps(
            album,
            indent=4,
        ),
        encoding="utf-8",
    )

    # -----------------------------
    # Playlist CSV
    # -----------------------------

    with open(
        output_folder / "playlist.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Order",
                "Track",
                "Duration",
            ]
        )

        for index, track in enumerate(
            playlist,
            start=1,
        ):
            writer.writerow(
                [
                    index,
                    track.path.stem,
                    format_duration(
                        track.duration_seconds
                    ),
                ]
            )

    # -----------------------------
    # Track Usage
    # -----------------------------

    counter = Counter(
        track.path.stem
        for track in playlist
    )

    with open(
        output_folder / "track_usage.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "Track",
                "Times Used",
            ]
        )

        for name, count in sorted(counter.items()):
            writer.writerow(
                [
                    name,
                    count,
                ]
            )

    # -----------------------------
    # Build Log
    # -----------------------------

    (
        output_folder / "build_log.txt"
    ).write_text(
        f"""
Album: {album_name}

Generated:
{datetime.now()}

Tracks:
{len(playlist)}

Duration:
{format_duration(duration_seconds)}

Crossfade:
{crossfade_seconds} sec

Status:
SUCCESS
""".strip(),
        encoding="utf-8",
    )