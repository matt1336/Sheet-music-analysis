from tkinter import Tk, filedialog, messagebox
from music21 import converter
import matplotlib.pyplot as plt
import pandas as pd
import mplcursors  

# Pick a MIDI file
Tk().withdraw()
midi_path = filedialog.askopenfilename(
    filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")]
)
score = converter.parse(midi_path)


# Build tempo map

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


# Extract notes/chords from a hand

def hand_data(part, hand_label, tempo_map):
    rows = []
    for n in part.flatten().notes:
        bpm = get_tempo_at_offset(n.offset, tempo_map)
        dur_sec = (n.quarterLength / bpm) * 60
        chord_size = 1 if n.isNote else len(n.pitches)

        if n.isNote:
            rows.append([
                hand_label,
                n.nameWithOctave,
                n.pitch.midi,
                dur_sec,
                chord_size,
                n.measureNumber,
                n.volume.velocity,
                bpm
            ])
        elif n.isChord:
            names = [p.nameWithOctave for p in n.pitches]
            midis = [p.midi for p in n.pitches]
            rows.append([
                hand_label,
                names,
                midis,
                dur_sec,
                chord_size,
                n.measureNumber,
                n.volume.velocity,
                bpm
            ])
    return rows

# Compute note density per measure

def compute_note_density(rows):
    density = {}
    for r in rows:
        measure = r[5]
        chord_size = r[4]
        density[measure] = density.get(measure, 0) + chord_size
    measures = sorted(density.keys())
    values = [density[m] for m in measures]
    avg = sum(values) / len(values) if values else 0
    return measures, values, avg


# Run data extraction

tempo_map = build_tempo_map(score)
all_rows = []

has_left = len(score.parts) > 1
if not has_left:
    messagebox.showinfo("Info", "Only one part found. Showing a single heat map.")

hands = ["Right", "Left"]
hand_rows = {}
hand_measures = {}
hand_values = {}
hand_avg = {}

for idx, hand in enumerate(hands):
    if idx < len(score.parts):
        rows = hand_data(score.parts[idx], hand, tempo_map)
        all_rows.extend(rows)
        meas, vals, avg = compute_note_density(rows)
        hand_rows[hand] = rows
        hand_measures[hand] = meas
        hand_values[hand] = vals
        hand_avg[hand] = avg


# Plot interactive heat maps

fig, axs = plt.subplots(len(hand_rows), 1, figsize=(14, 4*len(hand_rows)), sharex=True)
if len(hand_rows) == 1:
    axs = [axs]

colors = {"Right": "orange", "Left": "skyblue"}
bars_dict = {}

for ax, hand in zip(axs, hands):
    if hand in hand_rows:
        bars = ax.bar(hand_measures[hand], hand_values[hand], color=colors[hand], alpha=0.7)
        ax.axhline(hand_avg[hand], color='red', linestyle='--', label='Avg Note Density')
        ax.set_ylabel("Note Count")
        ax.set_title(f"{hand} Hand Heat Map")
        ax.legend()
        ax.tick_params(axis='x', labelbottom=True)
        bars_dict[hand] = bars

axs[-1].set_xlabel("Measure")
plt.tight_layout()


# Interactive hover

cursor = mplcursors.cursor([bar for bars in bars_dict.values() for bar in bars], hover=True)
@cursor.connect("add")
def on_add(sel):
    hand = None
    for h, bars in bars_dict.items():
        if sel.artist in bars:
            hand = h
            break
    measure_idx = list(bars_dict[hand]).index(sel.artist)
    measure = hand_measures[hand][measure_idx]
    note_count = hand_values[hand][measure_idx]
    sel.annotation.set_text(f"{hand} Hand\nMeasure {measure}\nNotes: {note_count}")

plt.show()


# Save dataset

df = pd.DataFrame(all_rows, columns=["Hand","NoteNames","MIDI",
                                     "Duration(s)","ChordSize","Measure",
                                     "Velocity","BPM"])
df.to_csv("MIDI_full_table.csv", index=False)
print("Data table saved as MIDI_full_table.csv")
