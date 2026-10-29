# deathcore_midi_generator.py
# Deathcore MIDI Generator — Python Standard Library Only
#
# No pip installations required.
#
# Generate one track:
#   python3 deathcore_midi_generator.py
#
# Generate 100 tracks:
#   python3 deathcore_midi_generator.py --count 100
#
# Generate indefinitely:
#   python3 deathcore_midi_generator.py --count 0
#
# Faster deathcore:
#   python3 deathcore_midi_generator.py --bpm 220
#
# Longer compositions:
#   python3 deathcore_midi_generator.py --bars 64
#
# Generate 50 long tracks at 200 BPM:
#   python3 deathcore_midi_generator.py --count 50 --bpm 200 --bars 32
#
# Output:
#   output_deathcore/deathcore_000001.mid

import argparse
import random
import struct
import time
from pathlib import Path

TICKS_PER_BEAT = 480
OUTPUT_DIR = Path("output_deathcore")

# General MIDI program numbers are zero-based.
# These are approximate instrument choices; your DAW determines the sound.
GUITAR_DISTORTION = 30
GUITAR_MUTED = 29
BASS = 33


def vlq(value):
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


def midi_track(events):
    """Build a MIDI track from absolute-tick events."""
    events.sort(key=lambda item: (item[0], item[1]))

    data = bytearray()
    previous_tick = 0

    for tick, _, event in events:
        data.extend(vlq(tick - previous_tick))
        data.extend(event)
        previous_tick = tick

    data.extend(b"\x00\xFF\x2F\x00")

    return b"MTrk" + struct.pack(">I", len(data)) + data


def add_note(events, start, duration, pitch, velocity, channel=0):
    """Add a MIDI note-on and note-off."""
    pitch = max(0, min(127, int(pitch)))
    velocity = max(1, min(127, int(velocity)))

    events.append((
        start, 1,
        bytes([0x90 | channel, pitch, velocity])
    ))

    events.append((
        start + max(1, duration), 0,
        bytes([0x80 | channel, pitch, 0])
    ))


def add_program(events, channel, program):
    events.append((
        0, 0,
        bytes([0xC0 | channel, program])
    ))


def generate_deathcore(bpm, bars, seed):
    rng = random.Random(seed)

    events = []

    microseconds = round(60_000_000 / bpm)

    # Tempo.
    events.append((
        0, 0,
        b"\xFF\x51\x03" + microseconds.to_bytes(3, "big")
    ))

    # 4/4 time signature.
    events.append((
        0, 0,
        b"\xFF\x58\x04\x04\x02\x18\x08"
    ))

    # Tracks share one MIDI channel per instrument part.
    add_program(events, 0, GUITAR_DISTORTION)
    add_program(events, 1, GUITAR_MUTED)
    add_program(events, 2, BASS)

    beat = TICKS_PER_BEAT
    bar = beat * 4
    sixteenth = beat // 4
    eighth = beat // 2

    # Low-register pitches approximate a downtuned guitar.
    root = 26

    # Chromatic and dissonant intervals for deathcore riffs.
    riff_notes = [0, 0, 0, 1, 3, 5, 6, 7, 10, 12]

    for bar_index in range(bars):
        bar_start = bar_index * bar

        section = (bar_index // 4) % 4

        # Section 0: chugging riff.
        # Section 1: faster tremolo.
        # Section 2: breakdown.
        # Section 3: blast-beat section.

        if section == 2:
            # Half-time breakdown with syncopated chugs.
            positions = [0, 3, 6, 8, 11, 14]
            duration = sixteenth * 2

            for step in positions:
                start = bar_start + step * sixteenth

                # Root chug.
                add_note(
                    events,
                    start,
                    duration,
                    root,
                    rng.randint(105, 127),
                    channel=1,
                )

                # Occasional dissonant power interval.
                if rng.random() < 0.45:
                    add_note(
                        events,
                        start,
                        duration,
                        root + rng.choice([6, 7, 12]),
                        rng.randint(90, 115),
                        channel=0,
                    )

            # Slow half-time snare on beat 3.
            add_note(
                events,
                bar_start + 2 * beat,
                100,
                38,
                127,
                channel=9,
            )

        elif section == 1:
            # Tremolo-picked sixteenth-note guitar.
            for step in range(16):
                start = bar_start + step * sixteenth
                pitch = root + rng.choice(riff_notes)

                add_note(
                    events,
                    start,
                    sixteenth - 8,
                    pitch,
                    rng.randint(85, 118),
                    channel=0,
                )

                # Double-kick pattern.
                add_note(
                    events,
                    start,
                    55,
                    36,
                    rng.randint(105, 127),
                    channel=9,
                )

                # Blast-beat snare accents.
                if step % 2 == 1:
                    add_note(
                        events,
                        start,
                        45,
                        38,
                        rng.randint(95, 125),
                        channel=9,
                    )

                # Fast cymbal hits.
                add_note(
                    events,
                    start,
                    40,
                    49,
                    rng.randint(85, 115),
                    channel=9,
                )

        elif section == 3:
            # Blast beats with alternating kick/snare accents.
            for step in range(16):
                start = bar_start + step * sixteenth

                pitch = root + rng.choice([0, 1, 3, 6, 7, 12])

                add_note(
                    events,
                    start,
                    sixteenth - 10,
                    pitch,
                    rng.randint(85, 120),
                    channel=0,
                )

                add_note(
                    events,
                    start,
                    50,
                    36,
                    120,
                    channel=9,
                )

                if step % 2 == 0:
                    add_note(
                        events,
                        start,
                        40,
                        38,
                        115,
                        channel=9,
                    )

                add_note(
                    events,
                    start,
                    40,
                    51,
                    95,
                    channel=9,
                )

        else:
            # Main chug riff with syncopation.
            positions = [0, 2, 3, 6, 8, 10, 11, 14]

            for step in positions:
                start = bar_start + step * sixteenth

                pitch = root + rng.choice([0, 0, 0, 1, 6, 7, 12])

                add_note(
                    events,
                    start,
                    sixteenth * rng.choice([1, 2, 3]),
                    pitch,
                    rng.randint(100, 127),
                    channel=1,
                )

                # Add higher guitar accents.
                if rng.random() < 0.3:
                    add_note(
                        events,
                        start,
                        sixteenth * 2,
                        pitch + 12,
                        rng.randint(85, 110),
                        channel=0,
                    )

            # Standard kick pattern.
            for step in [0, 4, 8, 12]:
                add_note(
                    events,
                    bar_start + step * sixteenth,
                    55,
                    36,
                    120,
                    channel=9,
                )

            # Snare on beats 2 and 4.
            for step in [4, 12]:
                add_note(
                    events,
                    bar_start + step * sixteenth,
                    60,
                    38,
                    115,
                    channel=9,
                )

            # Cymbal accents.
            for step in [0, 8]:
                add_note(
                    events,
                    bar_start + step * sixteenth,
                    60,
                    49,
                    105,
                    channel=9,
                )

        # Bass follows the low guitar root.
        add_note(
            events,
            bar_start,
            bar - 30,
            root - 12,
            110,
            channel=2,
        )

        # Add occasional low-frequency accents.
        if rng.random() < 0.5:
            add_note(
                events,
                bar_start + 3 * beat,
                beat // 2,
                root - 12,
                115,
                channel=2,
            )

    return midi_track(events)


def save_midi(path, bpm, bars, seed):
    track = generate_deathcore(bpm, bars, seed)

    header = (
        b"MThd"
        + struct.pack(">IHHH", 6, 0, 1, TICKS_PER_BEAT)
    )

    path.write_bytes(header + track)


def main():
    parser = argparse.ArgumentParser(
        description="Generate deathcore MIDI with Python's standard library."
    )

    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--bpm", type=int, default=200)
    parser.add_argument("--bars", type=int, default=16)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR)

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be >= 0.")

    if not 20 <= args.bpm <= 300:
        parser.error("--bpm must be between 20 and 300.")

    if not 1 <= args.bars <= 1024:
        parser.error("--bars must be between 1 and 1024.")

    args.output.mkdir(parents=True, exist_ok=True)

    index = 1

    try:
        while args.count == 0 or index <= args.count:
            path = args.output / f"deathcore_{index:06d}.mid"

            save_midi(
                path,
                args.bpm,
                args.bars,
                time.time_ns() + index,
            )

            print(f"Generated: {path}")

            index += 1

    except KeyboardInterrupt:
        print(f"\nStopped after {index - 1} MIDI files.")


if __name__ == "__main__":
    main()


# Example:
# python3 deathcore_midi_generator.py --count 100 --bpm 220 --bars 32
#
# Generate indefinitely:
# python3 deathcore_midi_generator.py --count 0 --bpm 200 --bars 16
#
# IMPORTANT:
# MIDI instrument patches determine the sound. Load a distorted guitar
# VST, bass instrument, and drum kit in your DAW for a deathcore sound.
