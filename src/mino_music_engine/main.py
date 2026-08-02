import sys
from pathlib import Path

from mino_music_engine.analyzer import (
    TrackInfo,
    analyze_track,
    format_duration,
)
from mino_music_engine.chapters import generate_chapters
from mino_music_engine.duration_engine import (
    build_extended_track_plan,
)
from mino_music_engine.metadata import embed_metadata
from mino_music_engine.mixer import create_crossfade_mix
from mino_music_engine.reporter import create_reports
from mino_music_engine.scanner import find_audio_tracks
from mino_music_engine.settings import (
    EngineSettings,
    load_settings,
)
from mino_music_engine.validator import validate_album


def get_project_root() -> Path:
    """Return the project root folder."""

    return Path(__file__).resolve().parents[2]


def read_settings(
    project_root: Path,
) -> EngineSettings | None:
    """Load engine settings and show readable errors."""

    settings_path = (
        project_root
        / "config"
        / "settings.json"
    )

    try:
        return load_settings(settings_path)
    except (FileNotFoundError, ValueError) as error:
        print(f"Settings error: {error}")
        return None


def analyze_music_folder(
    music_folder: Path,
) -> list[TrackInfo]:
    """Scan and analyze every music track."""

    print()
    print("Mino Music Engine")
    print("=" * 72)
    print(f"Music folder: {music_folder}")
    print()

    try:
        tracks = find_audio_tracks(music_folder)
    except (
        FileNotFoundError,
        NotADirectoryError,
    ) as error:
        print(f"Error: {error}")
        return []

    if not tracks:
        print("No audio tracks were found.")
        return []

    print(f"Found {len(tracks)} audio track(s).")
    print("Analyzing tracks...")
    print()

    track_infos: list[TrackInfo] = []

    for position, track in enumerate(
        tracks,
        start=1,
    ):
        try:
            info = analyze_track(track)
        except RuntimeError as error:
            print(
                f"{position:02}. ERROR - {error}"
            )
            continue

        track_infos.append(info)

        print(
            f"{position:02}. {track.name}"
            f" | {format_duration(info.duration_seconds)}"
            f" | {info.bitrate_kbps} kbps"
        )

    return track_infos


def run_validation(
    track_infos: list[TrackInfo],
) -> bool:
    """Validate all source tracks."""

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

    raw_duration = sum(
        track.duration_seconds
        for track in track_infos
    )

    print("Album validation passed.")
    print(f"Validated tracks: {len(track_infos)}")
    print(
        f"Raw duration: "
        f"{format_duration(raw_duration)}"
    )

    return True


def validate_command() -> None:
    """Analyze and validate without exporting."""

    project_root = get_project_root()
    music_folder = (
        project_root
        / "assets"
        / "music"
    )

    track_infos = analyze_music_folder(
        music_folder
    )

    if track_infos:
        run_validation(track_infos)


def build_command() -> None:
    """Create the complete publish-ready album."""

    project_root = get_project_root()
    settings = read_settings(project_root)

    if settings is None:
        return

    music_folder = (
        project_root
        / "assets"
        / "music"
    )

    cover_file = (
        project_root
        / settings.cover_path
    )

    if not cover_file.exists():
        print(
            f"Cover image was not found: "
            f"{cover_file}"
        )
        return

    track_infos = analyze_music_folder(
        music_folder
    )

    if not track_infos:
        return

    if not run_validation(track_infos):
        return

    extended_tracks = build_extended_track_plan(
        tracks=track_infos,
        target_duration_seconds=(
            settings.target_duration_seconds
        ),
        crossfade_seconds=(
            settings.crossfade_seconds
        ),
    )

    print()
    print("PLAYLIST PLAN")
    print("=" * 72)
    print(
        f"Planned track uses: "
        f"{len(extended_tracks)}"
    )
    print(
        f"Target duration: "
        f"{format_duration(settings.target_duration_seconds)}"
    )

    reports_folder = (
        project_root
        / "reports"
    )

    chapters_path = (
        reports_folder
        / "chapters.txt"
    )

    try:
        chapter_lines = generate_chapters(
            tracks=extended_tracks,
            output_path=chapters_path,
            crossfade_seconds=(
                settings.crossfade_seconds
            ),
            target_duration_seconds=(
                settings.target_duration_seconds
            ),
        )
    except ValueError as error:
        print(f"Chapter error: {error}")
        return

    print(
        f"Chapters generated: "
        f"{len(chapter_lines)}"
    )

    exports_folder = (
        project_root
        / "exports"
    )

    working_output = (
        exports_folder
        / "working-mix.mp3"
    )

    final_output = (
        exports_folder
        / settings.output_filename
    )

    try:
        final_duration = create_crossfade_mix(
            tracks=extended_tracks,
            output_path=working_output,
            crossfade_seconds=(
                settings.crossfade_seconds
            ),
            target_duration_seconds=(
                settings.target_duration_seconds
            ),
        )
    except (ValueError, RuntimeError) as error:
        print(f"Audio export error: {error}")
        return

    print()
    print("Embedding metadata and cover artwork...")

    try:
        embed_metadata(
            input_file=working_output,
            output_file=final_output,
            title=settings.album_name,
            artist=settings.artist,
            album=settings.album,
            genre=settings.genre,
            year=settings.year,
            comment=settings.comment,
            cover_file=cover_file,
        )
    except (
        FileNotFoundError,
        RuntimeError,
    ) as error:
        print(f"Metadata error: {error}")
        return

    try:
        create_reports(
            output_folder=reports_folder,
            album_name=settings.album_name,
            playlist=extended_tracks,
            duration_seconds=final_duration,
            crossfade_seconds=(
                settings.crossfade_seconds
            ),
        )
    except OSError as error:
        print(
            f"Report generation error: "
            f"{error}"
        )
        return

    try:
        working_output.unlink(missing_ok=True)
    except OSError as error:
        print(
            f"Warning: temporary file "
            f"could not be deleted: {error}"
        )

    print()
    print("=" * 72)
    print("BUILD COMPLETED SUCCESSFULLY")
    print("=" * 72)
    print(
        f"Album: {settings.album_name}"
    )
    print(
        f"Duration: "
        f"{format_duration(final_duration)}"
    )
    print(
        f"Final audio: {final_output}"
    )
    print(
        f"Chapters: {chapters_path}"
    )
    print(
        f"Reports: {reports_folder}"
    )


def print_help() -> None:
    """Show available commands."""

    print()
    print("Mino Music Engine")
    print("=" * 40)
    print("Available commands:")
    print()
    print(
        "  uv run mino-music-engine validate"
    )
    print(
        "      Analyze and validate tracks only."
    )
    print()
    print(
        "  uv run mino-music-engine build"
    )
    print(
        "      Create the publish-ready album."
    )


def main() -> None:
    """Run the selected command."""

    command = (
        sys.argv[1].lower()
        if len(sys.argv) > 1
        else "help"
    )

    if command == "validate":
        validate_command()
    elif command == "build":
        build_command()
    elif command in {
        "help",
        "--help",
        "-h",
    }:
        print_help()
    else:
        print(
            f"Unknown command: {command}"
        )
        print_help()


if __name__ == "__main__":
    main()