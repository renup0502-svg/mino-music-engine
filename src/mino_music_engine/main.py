import sys
from pathlib import Path

from mino_music_engine.analyzer import (
    TrackInfo,
    analyze_track,
    format_duration,
)
from mino_music_engine.duration_engine import build_extended_track_plan
from mino_music_engine.mixer import create_crossfade_mix
from mino_music_engine.reporter import create_reports
from mino_music_engine.scanner import find_audio_tracks
from mino_music_engine.validator import validate_album



TARGET_DURATION_SECONDS = 7200.0
CROSSFADE_SECONDS = 6.0


def get_project_paths() -> tuple[Path, Path]:
    """Return the project root and music folder."""

    project_root = Path(__file__).resolve().parents[2]
    music_folder = project_root / "assets" / "music"

    return project_root, music_folder


def analyze_music_folder(music_folder: Path) -> list[TrackInfo]:
    """Scan and analyze every supported audio track."""

    print()
    print("Mino Music Engine")
    print("=" * 72)
    print(f"Music folder: {music_folder}")
    print()

    try:
        tracks = find_audio_tracks(music_folder)
    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")
        return []

    if not tracks:
        print("No audio tracks were found.")
        return []

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

    return track_infos


def run_validation(track_infos: list[TrackInfo]) -> bool:
    """Validate the album and return True when it passes."""

    print()
    print("ALBUM VALIDATION")
    print("=" * 72)

    validation = validate_album(track_infos)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")

    if validation.errors:
        for error in validation.errors:
            print(f"ERROR: {error}")

        print()
        print("Album validation failed.")
        return False

    raw_duration = sum(track.duration_seconds for track in track_infos)

    print("Album validation passed.")
    print(f"Validated tracks: {len(track_infos)}")
    print(f"Raw duration: {format_duration(raw_duration)}")

    return True


def validate_command() -> None:
    """Validate tracks without creating an export."""

    _, music_folder = get_project_paths()
    track_infos = analyze_music_folder(music_folder)

    if track_infos:
        run_validation(track_infos)


def build_command() -> None:
    """Validate and build the complete two-hour album."""

    project_root, music_folder = get_project_paths()
    track_infos = analyze_music_folder(music_folder)

    if not track_infos:
        return

    if not run_validation(track_infos):
        return

    extended_tracks = build_extended_track_plan(
        tracks=track_infos,
        target_duration_seconds=TARGET_DURATION_SECONDS,
        crossfade_seconds=CROSSFADE_SECONDS,
    )

    print()
    print("TWO-HOUR PLAYLIST PLAN")
    print("=" * 72)
    print(f"Planned track uses: {len(extended_tracks)}")
    print("Target duration: 02:00:00")

    output_path = (
        project_root
        / "exports"
        / "Rain Valley - Autumn Stories - 2 Hours - Normalized.mp3"
    )

    try:
        final_duration = create_crossfade_mix(
            tracks=extended_tracks,
            output_path=output_path,
            crossfade_seconds=CROSSFADE_SECONDS,
            target_duration_seconds=TARGET_DURATION_SECONDS,
        )
    except (ValueError, RuntimeError) as error:
        print(f"Export error: {error}")
        return

        print()
    print("=" * 72)
    print("Two-hour export completed.")
    print(f"Final duration: {format_duration(final_duration)}")
    print(f"Output: {output_path}")


def print_help() -> None:
    """Show available commands."""

    print()
    print("Mino Music Engine")
    print("=" * 40)
    print("Available commands:")
    print()
    print("  uv run mino-music-engine validate")
    print("      Analyze and validate tracks only.")
    print()
    print("  uv run mino-music-engine build")
    print("      Create the complete two-hour album.")
    print()


def main() -> None:
    """Run the requested command."""

    command = (
        sys.argv[1].lower()
        if len(sys.argv) > 1
        else "help"
    )

    if command == "validate":
        validate_command()
    elif command == "build":
        build_command()
    elif command in {"help", "--help", "-h"}:
        print_help()
    else:
        print(f"Unknown command: {command}")
        print_help()


if __name__ == "__main__":
    main()