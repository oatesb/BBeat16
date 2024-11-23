
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict

from mido import Message, MidiFile, MidiTrack

@dataclass
class AfxPatch():
    midiChannel:int
    patchBank:int
    sceneMidiControlNumber:int = 34

@dataclass
class Song():
    
    midiFile:MidiFile
    track:MidiTrack
    patch:AfxPatch
    fileName:Path
    bpm:int = 120

    def _getTicksPerBeat(self) -> int:
        return self.midiFile.ticks_per_beat
    
    def _calculateTicks(self, seconds:int) -> int:
        return int(seconds * self._getTicksPerBeat() * (self.bpm / 60))
    
    def setAfxPatch(self, seconds:float, patchNumber:int):
        
        ticks = self._calculateTicks(seconds=seconds)
        
        # Set Bank Select MSB and LSB for bank 4 before program change
        self.track.append(Message('control_change', control=0, value=self.patch.patchBank, time=ticks, channel=self.patch.midiChannel - 1))
        # AxeFx does not need LSB
        # track.append(Message('control_change', control=32, value=0, time=0, channel=MIDI_CHANNEL))                

        # Program Change immediatly after the CC by a few ticks.
        self.track.append(Message('program_change', program=patchNumber, time=5, channel=self.patch.midiChannel - 1))

    def switchAfxScene(self, seconds:float, sceneNumber:int):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=self.patch.sceneMidiControlNumber, value=sceneNumber - 1, time=ticks, channel=self.patch.midiChannel - 1))

    def ccOff(self, seconds:float, cc:int):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=cc, value=0, time=ticks, channel=self.patch.midiChannel - 1))

    def ccOn(self, seconds:float, cc:int):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=cc, value=127, time=ticks, channel=self.patch.midiChannel - 1))

    def saveMidiFile(self):
        self.midiFile.save(self.fileName)

class SongGenerator:
    def __init__(self, jsonData: Dict):
        self.jsonData = jsonData
        self.song = self._createSong()

    def _parseTime(self, timeStr: str) -> float:
        """
        Convert 'MM:SS.xx' time format to total seconds as a float with 2 decimal precision.
        """
        try:
            minutes, seconds = timeStr.split(':')
            minutes = int(minutes)
            seconds = float(seconds)  # Handle fractional seconds directly
            totalSeconds = minutes * 60 + seconds
            return round(totalSeconds, 2)
        except ValueError:
            raise ValueError(f"Invalid time format: {timeStr}")
    

    def _createSong(self) -> Song:
        """Initialize the Song instance from JSON data."""
        songData = self.jsonData['song']
        patchData = self.jsonData['patch']

        fileName = Path(songData['fileName'])
        bpm = songData['bpm']

        patch = AfxPatch(
            midiChannel=patchData['midiChannel'],
            patchBank=patchData['patchBank'],
            sceneMidiControlNumber=patchData['sceneMidiControlNumber']
        )

        midiFile = MidiFile()
        track = MidiTrack()
        track.name = "track_0"
        midiFile.tracks.append(track)

        return Song(midiFile=midiFile, track=track, patch=patch, fileName=fileName, bpm=bpm)

    def processEvents(self):
        """Process each event from JSON, calling the appropriate Song method."""
        lastEventTime = 0  # Track time of the last event in seconds

        for event in self.jsonData['events']:
            eventTime = self._parseTime(event['time'])
            secondsDelta = eventTime - lastEventTime
            lastEventTime = eventTime  # Update last event time

            if event['event'] == 'setAfxPatch':
                self.song.setAfxPatch(seconds=secondsDelta, patchNumber=event['data'])
            elif event['event'] == 'switchAfxScene':
                self.song.switchAfxScene(seconds=secondsDelta, sceneNumber=event['data'])
            elif event['event'] == 'ccOff':
                self.song.ccOff(seconds=secondsDelta, cc=event['data'])
            elif event['event'] == 'ccOn':
                self.song.ccOn(seconds=secondsDelta, cc=event['data'])

        self.song.saveMidiFile()

    @staticmethod
    def loadFromFile(filePath: str) -> "SongGenerator":
        """Load JSON data from a file and initialize SongGenerator."""
        with open(filePath, 'r') as file:
            jsonData = json.load(file)
        return SongGenerator(jsonData=jsonData)


class SongBatchProcessor:
    def __init__(self, folderPath: str):
        self.folderPath = Path(folderPath)

    def processAllSongs(self):
        """Process all JSON song files in the specified folder."""
        for file in self.folderPath.glob("*.json"):
            print(f"Processing {file.name}...")

            try:
                songGenerator = SongGenerator.loadFromFile(file)
                songGenerator.processEvents()
                print(f"Successfully created MIDI for {file.name}.")
            except Exception as e:
                print(f"Failed to process {file.name}: {e}")
    