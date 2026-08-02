# Mino Music Engine

A modular Python command-line application for validating audio collections, generating playlist plans, and creating seamless crossfade previews using FFmpeg.

## Project Overview

Mino Music Engine was built to solve a practical music-production problem: combining multiple MP3 tracks into smooth listening sessions while checking that the source files are valid and consistently organised.

The application scans an audio folder, analyses track metadata, validates the album, creates a playlist plan, and generates multiple crossfade comparison files.

## Key Features

- Scans a local music directory for supported audio files
- Analyses track duration and bitrate
- Validates album structure before processing
- Reports validation errors and warnings
- Builds a numbered playlist plan
- Calculates total playlist duration
- Creates 4-second, 6-second, and 8-second crossfade previews
- Uses FFmpeg for audio processing
- Uses configuration files for reusable settings
- Excludes source audio and generated exports from Git tracking

## Successful Test Run

The application was tested with:

- 20 MP3 tracks
- 192 kbps audio
- Total playlist duration of approximately 56 minutes
- Three generated crossfade previews

Generated outputs:

```text
crossfade-4s.mp3
crossfade-6s.mp3
crossfade-8s.mp3