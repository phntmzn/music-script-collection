# chiptune_midi_generator.py
# 8-Bit Chiptune MIDI Generator — Python Standard Library Only
#
# Requirements:
#   Python 3.9+
#   No pip installations required.
#
# Generate one track:
#   python3 chiptune_midi_generator.py
#
# Generate 100 tracks:
#   python3 chiptune_midi_generator.py --count 100
#
# Generate indefinitely:
#   python3 chiptune_midi_generator.py --count 0
#
# Faster music:
#   python3 chiptune_midi_generator.py --bpm 180
#
# Longer tracks:
#   python3 chiptune_midi_generator.py --bars 32
#
# Generate 100 tracks at 160 BPM:
#   python3 chiptune_midi_generator.py --count 100 --bpm 160 --bars 16
#
# Output:
#   output_chiptune/chiptune_000001.mid

import argparse
import random
import struct
import time
from pathlib import Path

TICKS_PER_BEAT = 480
OUTPUT_DIR = Path("output_chiptune")


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


def create_track(events):
    """Build a Standard MIDI File track."""
    events.sort(key=lambda item: (item[0], item[1]))

    data = bytearray()
    previous_tick = 0

    for tick, _, event in events:
        data.extend(variable_length(tick - previous_tick))
        data.extend(event)
        previous_tick = tick

    data.extend(b"\x00\xFF\x2F\x00")

    return b"MTrk" + struct.pack(">I", len(data)) + data


def add_note(events, start, duration, pitch, velocity, channel=0):
    """Add a MIDI note-on and note-off."""
    pitch = max(0, min(127, int(pitch)))
    velocity = max(1, min(127, int(velocity)))

    events.append((
        start,
        1,
        bytes([0x90 | channel, pitch, velocity]),
    ))

    events.append((
        start + max(1, duration),
        0,
        bytes([0x80 | channel, pitch, 0]),
    ))


def add_program(events, channel, program):
    """Choose a General MIDI instrument."""
    events.append((
        0,
        0,
        bytes([0xC0 | channel, program]),
    ))


def generate_chiptune(bpm, bars, seed):
    rng = random.Random(seed)
    events = []

    # Tempo metadata.
    tempo = round(60_000_000 / bpm)

    events.append((
        0,
        0,
        b"\xFF\x51\x03" + tempo.to_bytes(3, "big"),
    ))

    # 4/4 time signature.
    events.append((
        0,
        0,
        b"\xFF\x58\x04\x04\x02\x18\x08",
    ))

    # General MIDI patches:
    # 81 = Lead 2 (sawtooth)
    # 89 = Warm Pad
    # 39 = Synth Bass 2
    # 10 = Music Box
    add_program(events, 0, 80)
    add_program(events, 1, 38)
    add_program(events, 2, 10)
    add_program(events, 3, 38)

    beat = TICKS_PER_BEAT
    bar = beat * 4
    eighth = beat // 2
    sixteenth = beat // 4

    # C major scale across multiple octaves.
    scale = [0, 2, 4, 5, 7, 9, 11]
    root = 60

    # Generate a repeating four-bar melodic motif.
    motif = [
        rng.choice(scale) for _ in range(16)
    ]

    for bar_index in range(bars):
        bar_start = bar_index * bar
        section = (bar_index // 4) % 4

        # Main square-wave-style lead melody.
        for step in range(16):
            start = bar_start + step * sixteenth

            degree = motif[(step + bar_index * 3) % len(motif)]

            # Change the melody slightly between sections.
            if section == 1 and rng.random() < 0.35:
                degree = rng.choice(scale)

            if section == 2:
                degree = motif[(step * 2) % len(motif)]

            octave = rng.choice([0, 12, 12, 24])
            pitch = root + degree + octave

            duration = sixteenth * rng.choice([1, 1, 2, 3])

            add_note(
                events,
                start,
                duration,
                pitch,
                rng.randint(85, 120),
                channel=0,
            )

        # Fast arpeggios using chord tones.
        chord_roots = [0, 5, 7, 3]
        chord_root = chord_roots[bar_index % len(chord_roots)]

        chord = [
            root + chord_root,
            root + chord_root + 4,
            root + chord_root + 7,
            root + chord_root + 12,
        ]

        for step in range(16):
            start = bar_start + step * sixteenth

            pitch = chord[step % len(chord)]

            add_note(
                events,
                start,
                sixteenth - 12,
                pitch + 12,
                rng.randint(65, 100),
                channel=2,
            )

        # Bouncy bassline on eighth notes.
        for step in range(8):
            start = bar_start + step * eighth

            bass_pitch = 36 + rng.choice([
                0, 0, 0, 7, 12, 12
            ])

            add_note(
                events,
                start,
                eighth - 20,
                bass_pitch,
                rng.randint(80, 115),
                channel=1,
            )

        # Simple retro drum sounds using General MIDI percussion.
        # Channel 10 is represented by channel index 9.
        for step in range(8):
            start = bar_start + step * eighth

            # Kick on alternating beats.
            if step in [0, 4]:
                add_note(
                    events, start, 60, 36, 95, channel=9
                )

            # Snare on beats 2 and 4.
            if step in [2, 6]:
                add_note(
                    events, start, 60, 38, 85, channel=9
                )

            # Closed hi-hat.
            if rng.random() < 0.75:
                add_note(
                    events,
                    start,
                    40,
                    42,
                    rng.randint(45, 75),
                    channel=9,
                )

        # Occasional high-register game-like accents.
        if bar_index % 4 == 3:
            for step, pitch in enumerate([84, 88, 91, 96]):
                add_note(
                    events,
                    bar_start + step * eighth,
                    eighth // 2,
                    pitch,
                    100,
                    channel=3,
                )

    return create_track(events)


def save_midi(path, bpm, bars, seed):
    """Write a valid Standard MIDI File, format 0."""
    track = generate_chiptune(bpm, bars, seed)

    header = (
        b"MThd"
        + struct.pack(">IHHH", 6, 0, 1, TICKS_PER_BEAT)
    )

    path.write_bytes(header + track)


def main():
    parser = argparse.ArgumentParser(
        description="Generate chiptune MIDI using only Python's standard library."
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of files; 0 generates indefinitely.",
    )

    parser.add_argument(
        "--bpm",
        type=int,
        default=150,
        help="Tempo in beats per minute.",
    )

    parser.add_argument(
        "--bars",
        type=int,
        default=16,
        help="Length of each track in 4/4 bars.",
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
            path = args.output / f"chiptune_{index:06d}.mid"

            save_midi(
                path,
                args.bpm,
                args.bars,
                time.time_ns() + index,
            )

            print(f"Generated: {path}")

            index += 1

    except KeyboardInterrupt:
        print(f"\nStopped. Generated {index - 1} MIDI files.")


if __name__ == "__main__":
    main()


# Example usage:
#
# Generate 100 chiptune tracks:
# python3 chiptune_midi_generator.py --count 100 --bpm 150 --bars 16
#
# Generate indefinitely:
# python3 chiptune_midi_generator.py --count 0 --bpm 180 --bars 8
#
# Generate a longer retro game soundtrack:
# python3 chiptune_midi_generator.py --count 20 --bpm 140 --bars 64
