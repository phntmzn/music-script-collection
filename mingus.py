# death_metal_core.py
# Death Metal Chord Progressions — F# Minor
# Dark, dissonant, chromatic, brutal.

progressions = {
    "Brutal Death Metal": [
        ["F5", "G5", "F#5", "C5"],
        ["F#5", "A5", "C5", "B5"],
        ["F#5", "D5", "C#5", "G5"],
        ["F#5", "E5", "D#5", "C5"],
        ["F#5", "Bb5", "C5", "F#5"],
    ],

    "Technical Death Metal": [
        ["F#5", "G5", "A#5", "C5", "F#5"],
        ["F#5", "E5", "Bb5", "A5", "C#5"],
        ["F#5", "C5", "D5", "G5", "F#5"],
        ["F#5", "F5", "A5", "C5", "B5"],
        ["F#5", "D#5", "G5", "C5", "F#5"],
    ],

    "Blackened Death Metal": [
        ["F#5", "G5", "D5", "C#5"],
        ["F#5", "A5", "G5", "D#5"],
        ["F#5", "C5", "Bb5", "G5"],
        ["F#5", "E5", "G5", "A#5"],
        ["F#5", "D5", "C5", "F#5"],
    ],

    "Deathcore": [
        ["F#5", "G5", "F5", "C5"],
        ["F#5", "C5", "Bb5", "C#5"],
        ["F#5", "D5", "G5", "F5"],
        ["F#5", "F5", "G5", "C5"],
        ["F#5", "A5", "Bb5", "C5"],
    ],

    "Dissonant Death Metal": [
        ["F#5", "G5", "F5", "E5"],
        ["F#5", "C5", "B5", "Bb5"],
        ["F#5", "D#5", "G5", "F5"],
        ["F#5", "A#5", "C5", "E5"],
        ["F#5", "G5", "C5", "F#5"],
    ],

    "Slamming Brutality": [
        ["F#5", "F#5", "G5", "F#5"],
        ["F#5", "C5", "F#5", "Bb5"],
        ["F#5", "D5", "C5", "F#5"],
        ["F#5", "G5", "F5", "F#5"],
        ["F#5", "C5", "B5", "F#5"],
    ],

    "Chromatic Riffs": [
        ["F#5", "G5", "G#5", "A5"],
        ["F#5", "F5", "E5", "D#5"],
        ["F#5", "C5", "B5", "Bb5"],
        ["F#5", "G5", "F5", "E5"],
        ["F#5", "D5", "C#5", "C5"],
    ],

    "Doom Death Metal": [
        ["F#m", "D5", "C#5", "F#m"],
        ["F#m", "G5", "D5", "C#5"],
        ["F#m", "Bb5", "G5", "F#m"],
        ["F#m", "E5", "D5", "C#5"],
    ],

    "Grindcore": [
        ["F#5", "C5", "F#5", "G5"],
        ["F#5", "Bb5", "C5", "F#5"],
        ["F#5", "F5", "C5", "B5"],
        ["F#5", "G5", "C5", "F#5"],
    ],

    "Progressive Death Metal": [
        ["F#5", "A5", "C#5", "G5"],
        ["D5", "F#5", "C5", "A#5"],
        ["F#5", "E5", "G5", "C#5"],
        ["Bb5", "C5", "F#5", "G5"],
    ],
}


def print_progressions():
    print("=" * 65)
    print("       DEATH METAL CORE | F# MINOR")
    print("=" * 65)

    for style, sequences in progressions.items():
        print(f"\n[{style}]")

        for i, progression in enumerate(sequences, 1):
            print(f"{i:02d}. " + " | ".join(progression))


if __name__ == "__main__":
    print_progressions()