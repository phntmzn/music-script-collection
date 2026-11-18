// Compile:
// g++ -std=c++17 deep_house.cpp -o deep_house
//
// Run:
// ./deep_house

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <algorithm>
#include <cstdint>

using namespace std;
namespace fs = std::filesystem;

struct Chord {
    string name;
    vector<int> notes;
};

int main() {

    // D minor key signature
    const int BPM = 122;
    const int PPQ = 480;
    const int BAR = PPQ * 4;

    // Dm - Dm9 - Bbmaj7 - Fmaj7 - Cadd9
    vector<Chord> chords = {
        {"Dm",     {50, 53, 57}},
        {"Dm9",    {50, 53, 57, 60, 64}},
        {"Bbmaj7", {46, 50, 53, 57}},
        {"Fmaj7",  {41, 45, 48, 52}},
        {"Cadd9",  {48, 52, 55, 62}}
    };

    // Create output folder
    fs::path folder = "DeepHouseMIDI/D_Minor";

    fs::create_directories(folder);

    string filename =
        "Dm - Dm9 - Bbmaj7 - Fmaj7 - Cadd9.mid";

    fs::path output = folder / filename;

    // MIDI events: absolute tick, priority, message
    struct Event {
        int tick;
        int priority;
        vector<unsigned char> data;
    };

    vector<Event> events;

    // Tempo: 122 BPM
    int tempo = 60000000 / BPM;

    events.push_back({
        0, 0,
        {0xFF, 0x51, 0x03,
         (unsigned char)(tempo >> 16),
         (unsigned char)(tempo >> 8),
         (unsigned char)tempo}
    });

    // Key signature: D minor = 1 flat, minor
    events.push_back({
        0, 1,
        {0xFF, 0x59, 0x02, 0xFF, 0x01}
    });

    // Time signature: 4/4
    events.push_back({
        0, 2,
        {0xFF, 0x58, 0x04, 0x04, 0x02, 0x18, 0x08}
    });

    // Generate chord progression
    for (int bar = 0; bar < chords.size(); ++bar) {

        int start = bar * BAR;
        int end = start + BAR;

        cout << chords[bar].name << " ";

        for (int note : chords[bar].notes) {

            events.push_back({
                start, 4,
                {0x90, (unsigned char)note, 90}
            });

            events.push_back({
                end, 3,
                {0x80, (unsigned char)note, 0}
            });
        }
    }

    // Sort events by timestamp
    stable_sort(events.begin(), events.end(),
        [](const Event& a, const Event& b) {
            return a.tick < b.tick;
        }
    );

    vector<unsigned char> track;

    // Variable-length MIDI encoding
    auto vlq = [&](int value) {

        unsigned char buffer[4];
        int count = 0;

        buffer[count++] = value & 0x7F;

        while ((value >>= 7)) {
            buffer[count++] = (value & 0x7F) | 0x80;
        }

        while (count--) {
            track.push_back(buffer[count]);
        }
    };

    int previous = 0;

    for (const auto& event : events) {

        vlq(event.tick - previous);

        track.insert(
            track.end(),
            event.data.begin(),
            event.data.end()
        );

        previous = event.tick;
    }

    // End of track
    track.insert(track.end(), {
        0x00, 0xFF, 0x2F, 0x00
    });

    // Write MIDI file
    ofstream out(output, ios::binary);

    if (!out) {
        cerr << "Could not create MIDI file.\n";
        return 1;
    }

    // MIDI header
    out.write("MThd", 4);

    unsigned char header[] = {
        0, 0, 0, 6,
        0, 0, 0, 1,
        (unsigned char)(PPQ >> 8),
        (unsigned char)PPQ
    };

    out.write((char*)header, sizeof(header));

    // MIDI track
    out.write("MTrk", 4);

    uint32_t size = track.size();

    unsigned char length[] = {
        (unsigned char)(size >> 24),
        (unsigned char)(size >> 16),
        (unsigned char)(size >> 8),
        (unsigned char)size
    };

    out.write((char*)length, 4);
    out.write((char*)track.data(), track.size());

    out.close();

    cout << "\n\nKey: D Minor";
    cout << "\nTempo: " << BPM << " BPM";
    cout << "\nTime Signature: 4/4";
    cout << "\nSaved: " << output << endl;

    return 0;
}
