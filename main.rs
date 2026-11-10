// Compile: cargo run --release
// Output: chord_progressions.mid

use midly::{num::*, *};

fn main() {
    let chords: Vec<Vec<u8>> = vec![
        vec![50, 54, 57, 61],       // Dmaj7
        vec![50, 53, 57, 60],       // Dm7
        vec![47, 50, 54, 57],       // Bm7
        vec![42, 45, 49, 52],       // F#m7
        vec![42, 45, 49],           // F#m
        vec![47, 50, 54, 57],       // Bm7
        vec![49, 54, 56],           // C#sus4
        vec![49, 53, 56],           // C#
        vec![42, 45, 49, 52],       // F#m7
        vec![47, 50, 54, 57],       // Bm7
        vec![49, 54, 56],           // C#sus4
        vec![49, 52, 56, 59],       // C#m7
        vec![47, 50, 54, 57],       // Bm7
        vec![50, 54, 57, 61],       // Dmaj7
        vec![52, 57, 59],           // Esus4
        vec![52, 56, 59],           // E
    ];

    let mut track = vec![TrackEvent {
        delta: u28::new(0),
        kind: TrackEventKind::Meta(MetaMessage::Tempo(u24::new(600_000))),
    }];

    for chord in chords {
        for &note in &chord {
            track.push(TrackEvent {
                delta: u28::new(0),
                kind: TrackEventKind::Midi {
                    channel: u4::new(0),
                    message: MidiMessage::NoteOn {
                        key: u7::new(note),
                        vel: u7::new(90),
                    },
                },
            });
        }

        for (i, &note) in chord.iter().enumerate() {
            track.push(TrackEvent {
                delta: u28::new(if i == 0 { 1920 } else { 0 }),
                kind: TrackEventKind::Midi {
                    channel: u4::new(0),
                    message: MidiMessage::NoteOff {
                        key: u7::new(note),
                        vel: u7::new(0),
                    },
                },
            });
        }
    }

    track.push(TrackEvent {
        delta: u28::new(0),
        kind: TrackEventKind::Meta(MetaMessage::EndOfTrack),
    });

    Smf {
        header: Header {
            format: Format::SingleTrack,
            timing: Timing::Metrical(u15::new(480)),
        },
        tracks: vec![track],
    }
    .save("chord_progressions.mid")
    .unwrap();

    println!("MIDI generated!");
}
