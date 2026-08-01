from dataclasses import dataclass
from pathlib import Path

from mino_music_engine.analyzer import TrackInfo


@dataclass
class PlaylistItem:
    """One track placed inside the final playlist."""

    track_number: int
    path: Path
    duration_seconds: float
    start_seconds: float


def build_playlist(track_infos: list[TrackInfo]) -> list[PlaylistItem]:
    """
    Build a playlist using the tracks in their existing order.

    The first version uses every track exactly once.
    """

    playlist: list[PlaylistItem] = []
    current_start = 0.0

    for position, track_info in enumerate(track_infos, start=1):
        item = PlaylistItem(
            track_number=position,
            path=track_info.path,
            duration_seconds=track_info.duration_seconds,
            start_seconds=current_start,
        )

        playlist.append(item)
        current_start += track_info.duration_seconds

    return playlist