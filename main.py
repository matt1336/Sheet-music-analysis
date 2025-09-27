from tkinter import Tk, filedialog
from music21 import converter
import matplotlib.pyplot as plt
import pandas as pd

# pick a MIDI file
Tk().withdraw()
midi_path = filedialog.askopenfilename(
    filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")]
)
score = converter.parse(midi_path)

# build tempo map
def build_tempo_map(s):
    boundaries = s.metronomeMarkBoundaries()
    if not boundaries:
        return [(0, s.highestTime, 120)]
    return [(start, end, mark.number) for start, end, mark in boundaries]

def get_tempo_at_offset(offset, tempo_map):
    for start, end, bpm in tempo_map:
        if start <= offset < end:
            return bpm
    return tempo_map[-1][2]

# extract notes/chords from a hand
def hand_data(part, hand_label, tempo_map):
    rows = []
    for n in part.flatten().notes:
        bpm = get_tempo_at_offset(n.offset, tempo_map)
        dur_sec = (n.quarterLength / bpm) * 60
        if n.isNote:
            rows.append([hand_label, n.nameWithOctave, n.pitch.midi,
                         dur_sec, 1, n.measureNumber, n.volume.velocity, bpm])
        elif n.isChord:
            names = [p.nameWithOctave for p in n.pitches]
            midis = [p.midi for p in n.pitches]
            rows.append([hand_label, names, midis, dur_sec, len(n.pitches),
                         n.measureNumber, n.volume.velocity, bpm])
    return rows

# compute heat per measure
def compute_heat_map(rows):
    heat = {}
    for r in rows:
        measure = r[5]
        dur = r[3]
        heat[measure] = heat.get(measure, 0) + dur
    measures = sorted(heat.keys())
    heat_values = [heat[m] for m in measures]
    return measures, heat_values


tempo_map = build_tempo_map(score)

# extract for both hands if available
all_rows = []
hands = ["Right", "Left"]
for idx, hand in enumerate(hands):
    if idx < len(score.parts):
        rows = hand_data(score.parts[idx], hand, tempo_map)
        all_rows.extend(rows)
        meas, vals = compute_heat_map(rows)
        plt.figure(figsize=(12,4))
        plt.bar(meas, vals, color='orange')
        plt.title(f"{hand} Hand Heat Map")
        plt.xlabel("Measure")
        plt.ylabel("Sum Duration (s)")
        plt.show()

# optional: save table
df = pd.DataFrame(all_rows, columns=["Hand","NoteNames","MIDI",
                                     "Duration(s)","ChordSize","Measure",
                                     "Velocity","BPM"])
df.to_csv("MIDI_full_table.csv", index=False)
print("Data table saved as MIDI_full_table.csv")

