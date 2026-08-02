import subprocess
from pathlib import Path


def embed_metadata(
    input_file: Path,
    output_file: Path,
    title: str,
    artist: str,
    album: str,
    genre: str,
    year: str,
    comment: str,
    cover_file: Path | None = None,
) -> None:
    """Embed MP3 metadata and optional album artwork."""

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input audio was not found: {input_file}"
        )

    if cover_file is not None and not cover_file.exists():
        raise FileNotFoundError(
            f"Cover image was not found: {cover_file}"
        )

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_file),
    ]

    if cover_file is not None:
        command.extend(
            [
                "-i",
                str(cover_file),
                "-map",
                "0:a",
                "-map",
                "1:v",
                "-c:a",
                "copy",
                "-c:v",
                "mjpeg",
                "-id3v2_version",
                "3",
                "-metadata:s:v",
                "title=Album cover",
                "-metadata:s:v",
                "comment=Cover (front)",
            ]
        )
    else:
        command.extend(
            [
                "-map",
                "0:a",
                "-c:a",
                "copy",
            ]
        )

    command.extend(
        [
            "-metadata",
            f"title={title}",
            "-metadata",
            f"artist={artist}",
            "-metadata",
            f"album={album}",
            "-metadata",
            f"genre={genre}",
            "-metadata",
            f"date={year}",
            "-metadata",
            f"comment={comment}",
            str(output_file),
        ]
    )

    try:
        subprocess.run(
            command,
            check=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "FFmpeg was not found."
        ) from error
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "FFmpeg could not embed metadata or artwork."
        ) from error