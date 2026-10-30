# death_metal_notes.py
# Death Metal Progressions — F# Minor
# Requires: python3 -m pip install mingus

from mingus.core import chords
from mingus.containers import Note, NoteContainer

progressions = {
    "Brutal Death Metal": [
        ["F#m", "G", "F#", "C"],
        ["F#m", "A", "C", "B"],
        ["F#m", "D", "C#", "G"],
    ],

    "Technical Death Metal": [
        ["F#m", "G", "A#", "C", "F#m"],
        ["F#m", "E", "Bb", "A", "C#"],
        ["F#m", "C", "D", "G", "F#m"],
    ],

    "Blackened Death Metal": [
        ["F#m", "G", "D", "C#"],
        ["F#m", "A", "G", "D#"],
        ["F#m", "C", "Bb", "G"],
    ],

    "Deathcore": [
        ["F#m", "G", "F", "C"],
        ["F#m", "C", "Bb", "C#"],
        ["F#m", "D", "G", "F"],
    ],

    "Dissonant Death Metal": [
        ["F#m", "G", "F", "E"],
        ["F#m", "C", "B", "Bb"],
        ["F#m", "D#", "G", "F"],
    ],

    "Slamming Brutality": [
        ["F#m", "F#m", "G", "F#m"],
        ["F#m", "C", "F#m", "Bb"],
        ["F#m", "D", "C", "F#m"],
    ],

    "Grindcore": [
        ["F#m", "C", "F#m", "G"],
        ["F#m", "Bb", "C", "F#m"],
        ["F#m", "F", "C", "B"],
    ],

    "Progressive Death Metal": [
        ["F#m", "A", "C#", "G"],
        ["D", "F#m", "C", "A#"],
        ["F#m", "E", "G", "C#"],
    ],
}


def get_notes(chord_name):
    try:
        notes = chords.from_shorthand(chord_name)
        return notes
    except Exception:
        return ["Invalid chord"]


def print_progressions():
    print("=" * 75)
    print("       DEATH METAL CORE — F# MINOR")
    print("=" * 75)

    for style, sequences in progressions.items():

        print(f"\n{'#' * 75}")
        print(f"STYLE: {style}")
        print(f"{'#' * 75}")

        for index, progression in enumerate(sequences, 1):

            print(f"\nProgression {index}")
            print("-" * 50)

            for chord_name in progression:

                notes = get_notes(chord_name)

                print(f"\nChord: {chord_name}")
                print(f"Notes: {' - '.join(notes)}")


if __name__ == "__main__":
    print_progressions()