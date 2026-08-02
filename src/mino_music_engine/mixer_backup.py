import subprocess
from pathlib import Path

from mino_music_engine.analyzer import TrackInfo


import subprocess
from pathlib import Path

from mino_music_engine.analyzer import TrackInfo


def create_crossfade_mix(
    tracks: list[TrackInfo],
    output_path: Path,
    crossfade_seconds: float = 6.0,
    target_duration_seconds: float | None = None,
) -> float:
    """
    Join tracks using FFmpeg crossfades.

    When target_duration_seconds is supplied, trim the final output
    precisely to that duration.
    """

    if len(tracks) < 2:
        raise ValueError(
            "At least two tracks are required."
        )

    for track in tracks:
        if track.duration_seconds <= crossfade_seconds:
            raise ValueError(
                f"{track.path.name} is too short for a "
                f"{crossfade_seconds}-second crossfade."
            )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = ["ffmpeg", "-y"]

    for track in tracks:
        command.extend(["-i", str(track.path)])

    filter_parts: list[str] = []

    for index in range(len(tracks)):
        filter_parts.append(
            f"[{index}:a]"
            "aformat="
            "sample_fmts=fltp:"
            "sample_rates=44100:"
            "channel_layouts=stereo,"
            "asetpts=N/SR/TB"
            f"[a{index}]"
        )

    previous_label = "a0"

    for index in range(1, len(tracks)):
        output_label = f"mix{index}"

        filter_parts.append(
            f"[{previous_label}][a{index}]"
            f"acrossfade=d={crossfade_seconds}:"
            "c1=qsin:c2=qsin"
            f"[{output_label}]"
        )

        previous_label = output_label

    calculated_duration = (
        sum(track.duration_seconds for track in tracks)
        - crossfade_seconds * (len(tracks) - 1)
    )

    final_duration = calculated_duration

    if target_duration_seconds is not None:
        final_duration = min(
            calculated_duration,
            target_duration_seconds,
        )

    fade_out_seconds = 4.0
    fade_out_start = max(
        0.0,
        final_duration - fade_out_seconds,
    )

    filter_parts.append(
        f"[{previous_label}]"
        f"atrim=end={final_duration:.3f},"
        "asetpts=N/SR/TB,"
        "afade=t=in:st=0:d=2,"
        f"afade=t=out:"
        f"st={fade_out_start:.3f}:"
        f"d={fade_out_seconds}"
        "[final_audio]"
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[final_audio]",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )

    print()
    print("Creating crossfade mix...")
    print(
        f"Tracks in plan: {len(tracks)}"
    )
    print(
        f"Crossfade duration: "
        f"{crossfade_seconds} seconds"
    )
    print(
        f"Target duration: "
        f"{final_duration:.1f} seconds"
    )
    print(f"Output: {output_path}")
    print()

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
            "FFmpeg could not create the mix."
        ) from error

    return final_duration