from mido import MidiFile, MidiTrack, Message

# 0 based
MIDI_CHANNEL=0

# ALL changes are 0 based
Nirvana_Scene_Controller_USA_PATCH = 12

MIDI_CONTROL=34

SCENE_1 = 0
SCENE_2 = 1
SCENE_3 = 2

BPM=120
filename='output.mid'

def setAfxPatch(ticksPerBeat:int, bpm:int, relativeTime:float, track:MidiTrack, patchNumber:int):
    # Program Change at 1 minute 11 seconds (71 seconds) on channel 3, with Bank 4
    programChangeTicks = int(relativeTime * ticksPerBeat * (bpm / 60))
    
    # Set Bank Select MSB and LSB for bank 4 before program change
    track.append(Message('control_change', control=0, value=3, time=programChangeTicks, channel=MIDI_CHANNEL))   # Bank Select MSB to 4
    # AxeFx does not need LSB
    # track.append(Message('control_change', control=32, value=0, time=0, channel=MIDI_CHANNEL))                   # Bank Select LSB to 0

    # Program Change immediatly after the CC.
    track.append(Message('program_change', program=patchNumber, time=0, channel=MIDI_CHANNEL))

def switchAfxScene(ticksPerBeat:int, bpm:int, relativeTime:float, track:MidiTrack, sceneNumber:int):
    # Calculate ticks for each event based on BPM
    # Time in seconds = (ticks / TICKS_PER_BEAT) * (60 / BPM)
    # Therefore, ticks = time_in_seconds * TICKS_PER_BEAT * (BPM / 60)
    
    controlChangeTicks = int(relativeTime * ticksPerBeat * (bpm / 60))
    track.append(Message('control_change', control=MIDI_CONTROL, value=sceneNumber, time=controlChangeTicks, channel=MIDI_CHANNEL))

# Set up basic MIDI parameters
midiFile = MidiFile()
track = MidiTrack()
midiFile.tracks.append(track)

# Define ticks per beat, assuming the default 480 TPB in mido
TICKS_PER_BEAT = midiFile.ticks_per_beat

setAfxPatch(ticksPerBeat=TICKS_PER_BEAT, bpm=BPM, relativeTime=0, track=track, patchNumber=Nirvana_Scene_Controller_USA_PATCH)

switchAfxScene(ticksPerBeat=TICKS_PER_BEAT, bpm=BPM, relativeTime=2, track=track, sceneNumber=SCENE_2)

switchAfxScene(ticksPerBeat=TICKS_PER_BEAT, bpm=BPM, relativeTime=2, track=track, sceneNumber=SCENE_1)
switchAfxScene(ticksPerBeat=TICKS_PER_BEAT, bpm=BPM, relativeTime=2, track=track, sceneNumber=SCENE_3)

midiFile.save(filename)
print(f'MIDI file saved as {filename}')

