# classical_midi_generator.py
# Classical Music MIDI Generator — Python Standard Library Only
#
# Requirements:
#   Python 3.9+
#   No pip installations required.
#
# Generate one composition:
#   python3 classical_midi_generator.py
#
# Generate 100 compositions:
#   python3 classical_midi_generator.py --count 100
#
# Generate indefinitely:
#   python3 classical_midi_generator.py --count 0
#
# Slow classical music:
#   python3 classical_midi_generator.py --bpm 70
#
# Longer compositions:
#   python3 classical_midi_generator.py --bars 64
#
# Select a style:
#   python3 classical_midi_generator.py --style baroque
#   python3 classical_midi_generator.py --style romantic
#   python3 classical_midi_generator.py --style orchestral
#
# Output:
#   output_classical/classical_000001.mid

import argparse
import random
import struct
import time
from pathlib import Path

TICKS_PER_BEAT = 480
OUTPUT_DIR = Path("output_classical")

# General MIDI program numbers are zero-based.
PIANO = 0
VIOLIN = 40
VIOLA = 41
CELLO = 42
CONTRABASS = 43
FLUTE = 73
OBOE = 68


def variable_length(value):
    """Encode an integer as a MIDI variable-length quantity."""
    value = max(0, int(value))
    buffer = value & 0x7F

    while value >> 7:
        value >>= 7
        buffer = (buffer << 8) | ((value & 0x7F) | 0x80)

    result = bytearray()

    while True:
        result.append(buffer & 0xFF)

        if buffer & 0x80:
            buffer >>= 8
        else:
            break

    return bytes(result)


def make_track(events):
    """Build a MIDI track from absolute-tick events."""
    events.sort(key=lambda item: (item[0], item[1]))

    data = bytearray()
    previous_tick = 0

    for tick, _, event in events:
        data.extend(variable_length(tick - previous_tick))
        data.extend(event)
        previous_tick = tick

    data.extend(b"\x00\xFF\x2F\x00")

    return b"MTrk" + struct.pack(">I", len(data)) + data


def add_note(events, start, duration, pitch, velocity, channel):
    """Add a MIDI note-on and note-off event."""
    pitch = max(0, min(127, int(pitch)))
    velocity = max(1, min(127, int(velocity)))

    events.append((
        start,
        2,
        bytes([0x90 | channel, pitch, velocity]),
    ))

    events.append((
        start + max(1, duration),
        1,
        bytes([0x80 | channel, pitch, 0]),
    ))


def add_program(events, channel, program):
    events.append((
        0,
        0,
        bytes([0xC0 | channel, program]),
    ))


def add_tempo(events, bpm):
    microseconds = round(60_000_000 / bpm)

    events.append((
        0,
        0,
        b"\xFF\x51\x03" + microseconds.to_bytes(3, "big"),
    ))

    # 4/4 time signature.
    events.append((
        0,
        0,
        b"\xFF\x58\x04\x04\x02\x18\x08",
    ))


def generate_classical(bpm, bars, style, seed):
    rng = random.Random(seed)
    events = []

    add_tempo(events, bpm)

    # Instruments on separate MIDI channels.
    add_program(events, 0, PIANO)
    add_program(events, 1, VIOLIN)
    add_program(events, 2, CELLO)
    add_program(events, 3, FLUTE)

    beat = TICKS_PER_BEAT
    bar = beat * 4
    eighth = beat // 2

    # Diatonic scales, represented as semitone offsets.
    major = [0, 2, 4, 5, 7, 9, 11]
    minor = [0, 2, 3, 5, 7, 8, 10]

    scale = minor if style == "romantic" else major

    # Chord progression degrees.
    if style == "baroque":
        progression = [0, 4, 5, 3, 0, 3, 4, 0]
    elif style == "romantic":
        progression = [0, 5, 3, 4, 0, 5, 4, 0]
    else:
        progression = [0, 3, 4, 0, 5, 3, 4, 0]

    root = 60

    # Melodic contour.
    melody = [0, 2, 4, 2, 5, 4, 2, 0]

    for bar_index in range(bars):
        start = bar_index * bar
        chord_degree = progression[
            (bar_index // 2) % len(progression)
        ]

        chord_root = scale[chord_degree % len(scale)]

        # Basic triad: root, third, fifth.
        chord = [
            root + chord_root,
            root + scale[(chord_degree + 2) % len(scale)],
            root + scale[(chord_degree + 4) % len(scale)],
        ]

        # Piano accompaniment.
        if style == "baroque":
            # Broken chords in eighth notes.
            arp = [
                chord[0] - 12,
                chord[1] - 12,
                chord[2] - 12,
                chord[1] - 12,
                chord[0] - 12,
                chord[1] - 12,
                chord[2] - 12,
                chord[1] - 12,
            ]

            for step, pitch in enumerate(arp):
                add_note(
                    events,
                    start + step * eighth,
                    eighth - 20,
                    pitch,
                    rng.randint(55, 85),
                    channel=0,
                )

        elif style == "romantic":
            # Full chord attacks with sustained notes.
            for pitch in chord:
                add_note(
                    events,
                    start,
                    bar - 30,
                    pitch - 12,
                    rng.randint(45, 75),
                    channel=0,
                )

            # Additional arpeggiated movement.
            for step in range(8):
                pitch = chord[step % 3] + 12

                add_note(
                    events,
                    start + step * eighth,
                    eighth - 15,
                    pitch,
                    rng.randint(40, 70),
                    channel=0,
                )

        else:
            # Classical Alberti-bass-inspired accompaniment.
            pattern = [
                chord[0] - 12,
                chord[2] - 12,
                chord[1] - 12,
                chord[2] - 12,
            ]

            for step, pitch in enumerate(pattern):
                add_note(
                    events,
                    start + step * beat,
                    beat - 30,
                    pitch,
                    rng.randint(50, 78),
                    channel=0,
                )

        # Violin melody.
        for beat_index in range(4):
            note_index = (bar_index * 2 + beat_index) % len(melody)

            degree = (
                melody[note_index]
                + rng.choice([-1, 0, 0, 1])
            )

            pitch = root + 12 + scale[degree % len(scale)]

            # Occasional leaps.
            if rng.random() < 0.2:
                pitch += rng.choice([-7, 5, 7, 12])

            duration = beat * rng.choice([1, 1, 2])

            add_note(
                events,
                start + beat_index * beat,
                duration,
                pitch,
                rng.randint(55, 90),
                channel=1,
            )

        # Cello bass line.
        bass_pitch = 36 + chord_root

        add_note(
            events,
            start,
            beat * 2 - 20,
            bass_pitch,
            rng.randint(50, 80),
            channel=2,
        )

        add_note(
            events,
            start + beat * 2,
            beat * 2 - 20,
            bass_pitch + rng.choice([0, 7, 12]),
            rng.randint(45, 75),
            channel=2,
        )

        # Flute counter-melody, more common in orchestral style.
        if style == "orchestral" or rng.random() < 0.35:
            for step in range(2):
                pitch = (
                    root + 24
                    + scale[rng.randrange(len(scale))]
                )

                add_note(
                    events,
                    start + step * beat * 2,
                    beat * 2 - 40,
                    pitch,
                    rng.randint(35, 65),
                    channel=3,
                )

    return make_track(events)


def save_midi(path, bpm, bars, style, seed):
    track = generate_classical(bpm, bars, style, seed)

    header = (
        b"MThd"
        + struct.pack(">IHHH", 6, 0, 1, TICKS_PER_BEAT)
    )

    path.write_bytes(header + track)


def main():
    parser = argparse.ArgumentParser(
        description="Classical MIDI generator using only the standard library."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of files; use 0 for indefinite generation.",
    )

    parser.add_argument(
        "--bpm",
        type=int,
        default=90,
        help="Tempo in beats per minute.",
    )

    parser.add_argument(
        "--bars",
        type=int,
        default=32,
        help="Length in 4/4 bars.",
    )

    parser.add_argument(
        "--style",
        choices=["classical", "baroque", "romantic", "orchestral"],
        default="classical",
        help="Composition style.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory.",
    )

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be >= 0")

    if not 20 <= args.bpm <= 300:
        parser.error("--bpm must be between 20 and 300")

    if not 1 <= args.bars <= 1024:
        parser.error("--bars must be between 1 and 1024")

    args.output.mkdir(parents=True, exist_ok=True)

    index = 1

    try:
        while args.count == 0 or index <= args.count:
            path = args.output / f"classical_{index:06d}.mid"

            save_midi(
                path,
                args.bpm,
                args.bars,
                args.style,
                time.time_ns() + index,
            )

            print(f"Generated: {path}")

            index += 1

    except KeyboardInterrupt:
        print(f"\nStopped after generating {index - 1} files.")


if __name__ == "__main__":
    main()


# Examples:
#
# Classical:
# python3 classical_midi_generator.py --count 10 --style classical
#
# Baroque:
# python3 classical_midi_generator.py --count 10 --style baroque --bpm 110
#
# Romantic:
# python3 classical_midi_generator.py --count 10 --style romantic --bpm 70
#
# Orchestral:
# python3 classical_midi_generator.py --count 10 --style orchestral --bars 64
#
# Generate indefinitely:
# python3 classical_midi_generator.py --count 0 --style baroque
