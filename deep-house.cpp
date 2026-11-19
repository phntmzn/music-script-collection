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
#include <random>
#include <cstdint>
#include <array>
#include <iomanip>
#include <sstream>

using namespace std;
namespace fs = std::filesystem;

constexpr int BPM = 122;
constexpr int PPQ = 480;
constexpr int BAR = PPQ * 4;
constexpr int TOTAL = 1000;

struct Key {
    string name;
    string folder;
    int root;
    int signature;
};

struct Chord {
    string name;
    int degree;
    vector<int> intervals;
};

struct Event {
    int tick;
    int priority;
    vector<unsigned char> data;
};

// 12 minor keys and their MIDI key signatures.
vector<Key> keys = {
    {"A Minor",       "A_Minor",       9,   0},
    {"Bb Minor",      "Bb_Minor",     10,  -5},
    {"B Minor",       "B_Minor",      11,   2},
    {"C Minor",       "C_Minor",       0,  -3},
    {"C# Minor",      "CSharp_Minor",  1,   4},
    {"D Minor",       "D_Minor",       2,  -1},
    {"Eb Minor",      "Eb_Minor",      3,  -6},
    {"E Minor",       "E_Minor",       4,   1},
    {"F Minor",       "F_Minor",       5,  -4},
    {"F# Minor",      "FSharp_Minor",  6,   3},
    {"G Minor",       "G_Minor",       7,  -2},
    {"Ab Minor",      "Ab_Minor",      8,  -7}
};

const int scale[] = {
    0, 2, 3, 5, 7, 8, 10
};

vector<Chord> chordTypes = {
    {"m9",    0, {0, 3, 7, 10, 14}},
    {"m7b5",  1, {0, 3, 6, 10}},
    {"maj9",  2, {0, 4, 7, 11, 14}},
    {"m9",    3, {0, 3, 7, 10, 14}},
    {"m7",    4, {0, 3, 7, 10}},
    {"maj9",  5, {0, 4, 7, 11, 14}},
    {"7",     6, {0, 4, 7, 10}}
};

const vector<vector<int>> progressions = {
    {0, 5, 2, 6},
    {0, 3, 5, 4},
    {0, 6, 3, 4},
    {5, 3, 0, 6},
    {0, 2, 5, 3},
    {0, 3, 6, 5},
    {0, 5, 3, 4},
    {0, 4, 3, 6},
    {5, 0, 6, 3},
    {0, 1, 5, 6},
    {0, 3, 2, 6},
    {5, 6, 0, 3}
};

// Letter names and the natural pitch class of each.
const string letterNames = "CDEFGAB";
const int naturalPc[] = {0, 2, 4, 5, 7, 9, 11};

string chordName(const Key& key, int degree) {

    int pc = (key.root + scale[degree]) % 12;

    // Spell the root by letter, so each scale degree keeps its
    // letter name (Cb rather than B, Fb rather than E).
    int tonic = static_cast<int>(letterNames.find(key.name[0]));
    int letter = (tonic + degree) % 7;

    int accidental = (pc - naturalPc[letter] + 12) % 12;

    if (accidental > 6)
        accidental -= 12;

    string root(1, letterNames[letter]);

    if (accidental > 0)
        root += string(accidental, '#');
    else if (accidental < 0)
        root += string(-accidental, 'b');

    return root + chordTypes[degree].name;
}

// MIDI variable-length quantity.
void vlq(vector<unsigned char>& out, int value) {

    unsigned char buffer[4];
    int count = 0;

    buffer[count++] = value & 0x7F;

    while ((value >>= 7)) {
        buffer[count++] = (value & 0x7F) | 0x80;
    }

    while (count--) {
        out.push_back(buffer[count]);
    }
}

// Write big-endian integer.
void write32(ofstream& file, uint32_t value) {

    unsigned char bytes[] = {
        (unsigned char)(value >> 24),
        (unsigned char)(value >> 16),
        (unsigned char)(value >> 8),
        (unsigned char)value
    };

    file.write((char*)bytes, 4);
}

// Generate one MIDI file.
void generate(
    const Key& key,
    const vector<int>& progression,
    int index
) {

    vector<Event> events;

    // Tempo metadata.
    int tempo = 60000000 / BPM;

    events.push_back({
        0, 0,
        {0xFF, 0x51, 0x03,
         (unsigned char)(tempo >> 16),
         (unsigned char)(tempo >> 8),
         (unsigned char)tempo}
    });

    // Key signature metadata.
    events.push_back({
        0, 1,
        {0xFF, 0x59, 0x02,
         (unsigned char)(int8_t)key.signature,
         0x01}
    });

    // Time signature: 4/4.
    events.push_back({
        0, 2,
        {0xFF, 0x58, 0x04, 4, 2, 24, 8}
    });

    // Track name.
    string trackName = key.name + " Deep House";

    vector<unsigned char> trackMeta = {
        0xFF, 0x03,
        (unsigned char)trackName.size()
    };

    trackMeta.insert(
        trackMeta.end(),
        trackName.begin(),
        trackName.end()
    );

    events.push_back({0, 3, trackMeta});

    string progressionName;

    // Generate four chords.
    for (int bar = 0; bar < 4; ++bar) {

        int degree = progression[bar];

        string name = chordName(key, degree);

        if (bar)
            progressionName += "-";

        progressionName += name;

        int start = bar * BAR;
        int end = start + BAR - 120;

        // Chord marker metadata.
        vector<unsigned char> marker = {
            0xFF, 0x06,
            (unsigned char)name.size()
        };

        marker.insert(
            marker.end(),
            name.begin(),
            name.end()
        );

        events.push_back({start, 3, marker});

        int root = 48 + (key.root + scale[degree]) % 12;

        for (int interval : chordTypes[degree].intervals) {

            int note = root + interval;

            // Note on.
            events.push_back({
                start, 5,
                {0x90, (unsigned char)note, 88}
            });

            // Note off.
            events.push_back({
                end, 4,
                {0x80, (unsigned char)note, 0}
            });
        }
    }

    // Sort events chronologically.
    stable_sort(
        events.begin(),
        events.end(),
        [](const Event& a, const Event& b) {
            if (a.tick != b.tick)
                return a.tick < b.tick;

            return a.priority < b.priority;
        }
    );

    vector<unsigned char> track;

    int previous = 0;

    for (const auto& event : events) {

        vlq(track, event.tick - previous);

        track.insert(
            track.end(),
            event.data.begin(),
            event.data.end()
        );

        previous = event.tick;
    }

    // End of track.
    track.insert(
        track.end(),
        {0x00, 0xFF, 0x2F, 0x00}
    );

    // Create key folder.
    fs::path folder =
        fs::path("DeepHouseMIDI") / key.folder;

    fs::create_directories(folder);

    // Filename.
    ostringstream filename;

    filename
        << "DeepHouse_"
        << setw(4) << setfill('0') << index
        << "_" << progressionName
        << ".mid";

    fs::path output = folder / filename.str();

    ofstream file(output, ios::binary);

    if (!file) {
        cerr << "Error creating: " << output << endl;
        return;
    }

    // MIDI header: format 0, one track, 480 PPQ.
    file.write("MThd", 4);
    write32(file, 6);

    unsigned char header[] = {
        0, 0,
        0, 1,
        (unsigned char)(PPQ >> 8),
        (unsigned char)PPQ
    };

    file.write((char*)header, 6);

    // MIDI track.
    file.write("MTrk", 4);
    write32(file, track.size());

    file.write(
        (char*)track.data(),
        track.size()
    );

    file.close();

    cout << index << "/1000  "
         << key.name << "  "
         << progressionName << endl;
}

int main() {

    fs::create_directories("DeepHouseMIDI");

    random_device rd;
    mt19937 rng(rd());

    uniform_int_distribution<int> keyDist(
        0, keys.size() - 1
    );

    uniform_int_distribution<int> progressionDist(
        0, progressions.size() - 1
    );

    cout << "\nGENERATING 1000 DEEP HOUSE MIDI FILES\n\n";

    for (int i = 1; i <= TOTAL; ++i) {

        const Key& key = keys[keyDist(rng)];

        const auto& progression =
            progressions[progressionDist(rng)];

        generate(key, progression, i);
    }

    cout << "\n================================\n";
    cout << "1000 MIDI FILES GENERATED\n";
    cout << "Location: DeepHouseMIDI/\n";
    cout << "Tempo: 122 BPM\n";
    cout << "Time Signature: 4/4\n";
    cout << "Keys: 12 Minor Keys\n";
    cout << "================================\n";

    return 0;
}
