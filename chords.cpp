// Compile: g++ -std=c++17 main.cpp -o chords
// Run: ./chords

#include <cstdint>
#include <fstream>
#include <vector>

using namespace std;

void vlq(vector<uint8_t>& out, uint32_t v) {
    uint8_t b[4];
    int n = 0;

    b[n++] = v & 0x7F;

    while ((v >>= 7))
        b[n++] = (v & 0x7F) | 0x80;

    while (n) out.push_back(b[--n]);
}

void be(vector<uint8_t>& out, uint32_t v, int n) {
    for (int i = n - 1; i >= 0; --i)
        out.push_back((v >> (i * 8)) & 0xFF);
}

int main() {
    vector<vector<uint8_t>> chords = {
        {50,54,57,61}, {50,53,57,60},
        {47,50,54,57}, {42,45,49,52},
        {42,45,49}, {47,50,54,57},
        {49,54,56}, {49,53,56},
        {42,45,49,52}, {47,50,54,57},
        {49,54,56}, {49,52,56,59},
        {47,50,54,57}, {50,54,57,61},
        {52,57,59}, {52,56,59}
    };

    vector<uint8_t> t = {
        0x00, 0xFF, 0x51, 0x03, 0x09, 0x27, 0xC0
    };

    for (auto& chord : chords) {
        for (auto note : chord) {
            vlq(t, 0);
            t.insert(t.end(), {0x90, note, 90});
        }

        for (int i = 0; i < chord.size(); ++i) {
            vlq(t, i == 0 ? 1920 : 0);
            t.insert(t.end(), {0x80, chord[i], 0});
        }
    }

    t.insert(t.end(), {0x00, 0xFF, 0x2F, 0x00});

    vector<uint8_t> midi = {
        'M','T','h','d', 0,0,0,6,
        0,0, 0,1, 1,0xE0,
        'M','T','r','k'
    };

    be(midi, t.size(), 4);
    midi.insert(midi.end(), t.begin(), t.end());

    ofstream file("chord_progressions.mid", ios::binary);
    file.write(reinterpret_cast<const char*>(midi.data()), midi.size());
}
