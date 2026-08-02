from mino_music_engine.analyzer import TrackInfo


def build_extended_track_plan(
    tracks: list[TrackInfo],
    target_duration_seconds: float,
    crossfade_seconds: float,
) -> list[TrackInfo]:
    """
    Repeat and rotate album tracks until the target duration is reached.

    Each new pass starts from a different position so the album does not
    obviously restart from Track 1 every time.
    """

    if not tracks:
        raise ValueError("No tracks were provided.")

    if target_duration_seconds <= 0:
        raise ValueError("Target duration must be greater than zero.")

    if crossfade_seconds < 0:
        raise ValueError("Crossfade duration cannot be negative.")

    extended_tracks: list[TrackInfo] = []
    estimated_duration = 0.0
    pass_number = 0
    rotation_step = 7

    while estimated_duration < target_duration_seconds:
        start_index = (
            pass_number * rotation_step
        ) % len(tracks)

        rotated_tracks = (
            tracks[start_index:]
            + tracks[:start_index]
        )

        for track in rotated_tracks:
            extended_tracks.append(track)

            if len(extended_tracks) == 1:
                estimated_duration += track.duration_seconds
            else:
                estimated_duration += (
                    track.duration_seconds
                    - crossfade_seconds
                )

            if estimated_duration >= target_duration_seconds:
                return extended_tracks

        pass_number += 1

    return extended_tracks