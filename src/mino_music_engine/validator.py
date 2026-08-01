from dataclasses import dataclass, field

from mino_music_engine.analyzer import TrackInfo


@dataclass
class ValidationResult:
    """Validation result for one album."""

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_album(
    tracks: list[TrackInfo],
    expected_track_count: int = 20,
    minimum_duration_seconds: float = 110.0,
    required_sample_rate_hz: int = 44100,
    required_channels: int = 2,
    minimum_bitrate_kbps: int = 192,
) -> ValidationResult:
    """Validate technical requirements for all album tracks."""

    errors: list[str] = []
    warnings: list[str] = []

    if len(tracks) != expected_track_count:
        errors.append(
            f"Expected {expected_track_count} tracks, "
            f"but found {len(tracks)}."
        )

    seen_names: set[str] = set()

    for position, track in enumerate(tracks, start=1):
        track_name = track.path.name

        normalized_name = track_name.lower().strip()

        if normalized_name in seen_names:
            errors.append(
                f"Track {position:02}: duplicate filename: {track_name}"
            )
        else:
            seen_names.add(normalized_name)

        if not track.path.exists():
            errors.append(
                f"Track {position:02}: file does not exist: {track_name}"
            )

        if track.duration_seconds < minimum_duration_seconds:
            errors.append(
                f"Track {position:02}: too short "
                f"({track.duration_seconds:.1f} seconds): {track_name}"
            )

        if track.sample_rate_hz != required_sample_rate_hz:
            errors.append(
                f"Track {position:02}: sample rate is "
                f"{track.sample_rate_hz} Hz, expected "
                f"{required_sample_rate_hz} Hz: {track_name}"
            )

        if track.channels != required_channels:
            errors.append(
                f"Track {position:02}: has {track.channels} channel(s), "
                f"expected {required_channels}: {track_name}"
            )

        if track.bitrate_kbps < minimum_bitrate_kbps:
            warnings.append(
                f"Track {position:02}: bitrate is "
                f"{track.bitrate_kbps} kbps, below recommended "
                f"{minimum_bitrate_kbps} kbps: {track_name}"
            )

        if track.codec.lower() != "mp3":
            warnings.append(
                f"Track {position:02}: codec is "
                f"{track.codec.upper()}, not MP3: {track_name}"
            )

        if ".mp3.mp3" in normalized_name:
            warnings.append(
                f"Track {position:02}: filename has double extension: "
                f"{track_name}"
            )

    return ValidationResult(
        passed=not errors,
        errors=errors,
        warnings=warnings,
    )