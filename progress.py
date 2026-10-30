# chord_progressions.py
# Generate MIDI files using Python standard library only.

import struct
from pathlib import Path

p = [
    ["Dmaj7", "Dm7", "Bm7", "F#m7"],
    ["F#m", "Bm7", "C#sus4", "C#"],
    ["F#m7", "Bm7", "C#sus4", "C#m7"],
    ["Bm7", "Dmaj7", "Esus4", "E"]
]

NOTES = {
    "C": 0, "C#": 1, "D": 2, "D#": 3,
    "E": 4, "F": 5, "F#": 6, "G": 7,
    "G#": 8, "A": 9, "A#": 10, "B": 11
}

CHORDS = {
    "maj7": [0, 4, 7, 11],
    "m7": [0, 3, 7, 10],
    "m": [0, 3, 7],
    "sus4": [0, 5, 7],
}

def chord_notes(chord):
    for quality in sorted(CHORDS, key=len, reverse=True):
        if chord.endswith(quality):
            root = chord[:-len(quality)]
            return [48 + NOTES[root] + interval
                    for interval in CHORDS[quality]]

    raise ValueError(f"Unknown chord: {chord}")


def vlq(value):
    buffer = value & 0x7F

    while (value := value >> 7):
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


def make_midi(progression, filename):
    events = []
    ticks_per_beat = 480
    duration = ticks_per_beat * 4

    for bar, chord in enumerate(progression):
        start = bar * duration
        end = start + duration

        for note in chord_notes(chord):
            events.append((start, bytes([0x90, note, 90])))
            events.append((end, bytes([0x80, note, 0])))

    events.sort(key=lambda x: x[0])

    track = bytearray()
    previous = 0

    for tick, event in events:
        track.extend(vlq(tick - previous))
        track.extend(event)
        previous = tick

    track.extend(b"\x00\xFF\x2F\x00")

    header = struct.pack(
        ">IHHH", 6, 0, 1, ticks_per_beat
    )

    midi_track = b"MTrk" + struct.pack(">I", len(track)) + track

    Path(filename).write_bytes(b"MThd" + header + midi_track)


output = Path("output")
output.mkdir(exist_ok=True)

for i, progression in enumerate(p, 1):
    filename = output / f"progression_{i}.mid"
    make_midi(progression, filename)
    print(f"Created: {filename}")

print("Finished generating MIDI files.")