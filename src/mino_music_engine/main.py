from pathlib import Path

from mino_music_engine.analyzer import (
    TrackInfo,
    analyze_track,
    format_duration,
)
from mino_music_engine.mixer import create_crossfade_mix
from mino_music_engine.playlist import build_playlist
from mino_music_engine.scanner import find_audio_tracks
from mino_music_engine.validator import validate_album


def main() -> None:
    """Run the Mino Music Engine."""

    project_root = Path(__file__).resolve().parents[2]
    music_folder = project_root / "assets" / "music"

    print()
    print("Mino Music Engine")
    print("=" * 72)
    print(f"Music folder: {music_folder}")
    print()

    try:
        tracks = find_audio_tracks(music_folder)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
        return

    if not tracks:
        print("No audio tracks were found.")
        print("Add files to assets/music.")
        return

    print(f"Found {len(tracks)} audio track(s).")
    print("Analyzing tracks...")
    print()

    track_infos: list[TrackInfo] = []

    for position, track in enumerate(tracks, start=1):
        try:
            info = analyze_track(track)
        except RuntimeError as error:
            print(f"{position:02}. ERROR - {error}")
            continue

        track_infos.append(info)

        print(
            f"{position:02}. {track.name}"
            f" | {format_duration(info.duration_seconds)}"
            f" | {info.bitrate_kbps} kbps"
        )

    if not track_infos:
        print()
        print("No valid tracks could be analyzed.")
        return

    print()
    print("ALBUM VALIDATION")
    print("=" * 72)

    validation = validate_album(track_infos)

    if validation.warnings:
        print("Warnings:")

        for warning in validation.warnings:
            print(f"  WARNING: {warning}")

        print()

    if validation.errors:
        print("Errors:")

        for error in validation.errors:
            print(f"  ERROR: {error}")

        print()
        print("Album validation failed.")
        print("Fix the errors before creating a mix.")
        return

    print("Album validation passed.")
    print(f"Validated tracks: {len(track_infos)}")

    playlist = build_playlist(track_infos)

    print()
    print("PLAYLIST PLAN")
    print("=" * 72)

    for item in playlist:
        print(
            f"{item.track_number:02}. "
            f"Start: {format_duration(item.start_seconds)}"
            f" | Duration: {format_duration(item.duration_seconds)}"
            f" | {item.path.name}"
        )

    total_duration = sum(
        item.duration_seconds
        for item in playlist
    )

    print()
    print("=" * 72)
    print(f"Total tracks: {len(playlist)}")
    print(f"Total duration: {format_duration(total_duration)}")
    print("Playlist created successfully.")

    preview_tracks = track_infos[:3]

    print()
    print("CROSSFADE COMPARISON")
    print("=" * 72)
    print("Creating 4-second, 6-second, and 8-second previews.")

    preview_settings = [
        (4.0, "crossfade-4s.mp3"),
        (6.0, "crossfade-6s.mp3"),
        (8.0, "crossfade-8s.mp3"),
    ]

    for crossfade_seconds, filename in preview_settings:
        preview_output = project_root / "exports" / filename

        try:
            preview_duration = create_crossfade_mix(
                tracks=preview_tracks,
                output_path=preview_output,
                crossfade_seconds=crossfade_seconds,
            )
        except (ValueError, RuntimeError) as error:
            print(f"Crossfade error: {error}")
            return

        print()
        print(f"Created: {filename}")
        print(f"Duration: {format_duration(preview_duration)}")
        print(f"File: {preview_output}")

    print()
    print("All comparison previews created successfully.")