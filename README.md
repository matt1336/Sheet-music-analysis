# Piano MIDI Analyzer

Extracts note/chord information from MIDI files and generates a heat map of note density for each hand. Also saves a CSV dataset of the score for analysis or AI applications.

## How to run

1. Install dependencies: `pip install music21 pandas matplotlib`
2. Run `main.py` and select a MIDI file.
3. The heat map will display, and a CSV file `MIDI_full_table.csv` will be saved.

## Example Output

- Heat map per hand
- CSV table with columns: Hand, NoteNames, MIDI, Duration(s), ChordSize, Measure, Velocity, BPM

## Note
- MIDI files like to occasionally not specify left and right hand notes. In these cases, the program will only show one heat map and table for the "Right" hand — essentially it will combine the right and left into one hand.
