# midi_generator.py
# Standard-Library-Only MIDI Generator
#
# Requirements:
#   Python 3.9+
#   No pip installations required.
#
# Generate one MIDI file:
#   python3 midi_generator.py
#
# Generate 100 MIDI files:
#   python3 midi_generator.py --count 100
#
# Generate MIDI files indefinitely:
#   python3 midi_generator.py --count 0
#
# Change tempo:
#   python3 midi_generator.py --bpm 140
#
# Change length:
#   python3 midi_generator.py --bars 16
#
# Combine options:
#   python3 midi_generator.py --count 50 --bpm 150 --bars 8
#
# Output:
#   output/track_000001.mid

import argparse
import random
import struct
import time
from pathlib import Path


OUTPUT_DIR = Path("output")
TICKS_PER_BEAT = 480


def variable_length(value):
    """Encode an integer as a MIDI variable-length quantity."""
    value = max(0, int(value))
    buffer = value & 0x7F

    while value >> 7:
        value >>= 7
        buffer <<= 8
        buffer |= ((value & 0x7F) | 0x80)

    result = bytearray()

    while True:
        result.append(buffer & 0xFF)

        if buffer & 0x80:
            buffer >>= 8
        else:
            break

    return bytes(result)


def make_event(delta, event):
    return variable_length(delta) + event


def make_track(events):
    """Create a MIDI track from absolute-tick events."""
    events.sort(key=lambda item: item[0])

    track_data = bytearray()
    previous_tick = 0

    for tick, event in events:
        delta = tick - previous_tick
        track_data.extend(make_event(delta, event))
        previous_tick = tick

    # End-of-track meta event
    track_data.extend(b"\x00\xFF\x2F\x00")

    return b"MTrk" + struct.pack(">I", len(track_data)) + track_data


def note_events(events, start, duration, pitch, velocity, channel=0):
    """Add MIDI note-on and note-off events."""
    pitch = max(0, min(127, pitch))
    velocity = max(1, min(127, velocity))

    events.append((
        start,
        bytes([0x90 | channel, pitch, velocity])
    ))

    events.append((
        start + max(1, duration),
        bytes([0x80 | channel, pitch, 0])
    ))


def generate_track(bpm, bars, seed):
    """Generate a randomized techno-style MIDI track."""
    rng = random.Random(seed)

    events = []

    # Tempo in microseconds per quarter note.
    microseconds_per_beat = round(60_000_000 / bpm)

    events.append((
        0,
        b"\xFF\x51\x03"
        + microseconds_per_beat.to_bytes(3, "big")
    ))

    # 4/4 time signature.
    events.append((
        0,
        b"\xFF\x58\x04\x04\x02\x18\x08"
    ))

    # GM program change: synth bass.
    events.append((
        0,
        bytes([0xC0, 38])
    ))

    beats_per_bar = 4
    total_beats = bars * beats_per_bar
    bar_ticks = beats_per_bar * TICKS_PER_BEAT

    # A minor pentatonic scale.
    scale = [0, 3, 5, 7, 10]
    root = 45

    # Bass: one note per beat.
    for beat in range(total_beats):
        pitch = root + rng.choice(scale)

        # Occasional octave variation.
        if rng.random() < 0.15:
            pitch += 12

        start = beat * TICKS_PER_BEAT

        note_events(
            events,
            start,
            TICKS_PER_BEAT - 30,
            pitch,
            rng.randint(80, 115),
            channel=0,
        )

    # Arpeggio: eighth notes.
    for step in range(total_beats * 2):
        start = step * (TICKS_PER_BEAT // 2)

        degree = rng.choice(scale)
        octave = rng.choice([12, 24, 36])
        pitch = 60 + degree + octave

        note_events(
            events,
            start,
            TICKS_PER_BEAT // 3,
            pitch,
            rng.randint(65, 105),
            channel=1,
        )

    # Drums on MIDI channel 10 (zero-based channel 9).
    # GM drum pitches: kick 36, snare 38, closed hi-hat 42.
    for bar in range(bars):
        bar_start = bar * bar_ticks

        for beat in range(4):
            start = bar_start + beat * TICKS_PER_BEAT

            # Four-on-the-floor kick.
            note_events(
                events, start, 100, 36, 115, channel=9
            )

            # Snare on beats 2 and 4.
            if beat in (1, 3):
                note_events(
                    events, start, 100, 38, 100, channel=9
                )

        # Eighth-note hi-hats.
        for step in range(8):
            start = bar_start + step * (TICKS_PER_BEAT // 2)

            note_events(
                events,
                start,
                60,
                42,
                rng.randint(55, 90),
                channel=9,
            )

    return make_track(events)


def save_midi(path, bpm, bars, seed):
    """Write a complete Standard MIDI File, format 0."""
    track = generate_track(bpm, bars, seed)

    header = (
        b"MThd"
        + struct.pack(">IHHH", 6, 0, 1, TICKS_PER_BEAT)
    )

    path.write_bytes(header + track)


def main():
    parser = argparse.ArgumentParser(
        description="Generate MIDI using only Python's standard library."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of files; use 0 to generate indefinitely.",
    )

    parser.add_argument(
        "--bpm",
        type=int,
        default=140,
        help="Tempo in beats per minute.",
    )

    parser.add_argument(
        "--bars",
        type=int,
        default=8,
        help="Number of 4/4 bars per MIDI file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory.",
    )

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be zero or greater.")

    if not 20 <= args.bpm <= 300:
        parser.error("--bpm must be between 20 and 300.")

    if not 1 <= args.bars <= 1024:
        parser.error("--bars must be between 1 and 1024.")

    args.output.mkdir(parents=True, exist_ok=True)

    index = 1

    try:
        while args.count == 0 or index <= args.count:
            path = args.output / f"track_{index:06d}.mid"

            seed = time.time_ns() + index

            save_midi(
                path,
                args.bpm,
                args.bars,
                seed,
            )

            print(f"Generated: {path}")

            index += 1

    except KeyboardInterrupt:
        print(f"\nStopped. Generated {index - 1} MIDI files.")


if __name__ == "__main__":
    main()


# Example usage:
#
#   python3 midi_generator.py --count 100 --bpm 145 --bars 8
#
#   python3 midi_generator.py --count 0 --bpm 130 --bars 16
#
#   python3 midi_generator.py --count 10 --output my_midi

### Run it on macOS

**1. Save the script** as `midi_generator.py`.

**2. Open Terminal** in the folder containing the script.

**3. Generate 100 MIDI files:**

```bash
python3 midi_generator.py --count 100 --bpm 140 --bars 8
