
from dataclasses import dataclass
import json
from pathlib import Path
import traceback
from typing import Dict

from mido import Message, MidiFile, MidiTrack

@dataclass
class AfxPatch():
    midiChannel:int
    patchBank:int
    sceneMidiCC:int = 34

@dataclass
class Ve500():
    midiChannel:int
    patchBank:int

@dataclass
class Song():
    
    midiFile:MidiFile
    track:MidiTrack
    axFx:AfxPatch
    ve500:Ve500
    fileName:Path
    bpm:int = 120

    def _getTicksPerBeat(self) -> int:
        return self.midiFile.ticks_per_beat
    
    def _calculateTicks(self, seconds:int) -> int:
        return int(seconds * self._getTicksPerBeat() * (self.bpm / 60))
    
    # VE500
    def setVe500Patch(self, seconds:float, patchNumber:int):
        ticks = self._calculateTicks(seconds=seconds)

        self.track.append(Message('control_change', control=0, value=self.ve500.patchBank, time=ticks, channel=self.ve500.midiChannel - 1))
        self.track.append(Message('program_change', program=patchNumber -1, time=5, channel=self.ve500.midiChannel - 1))

    # The Assign FX to toggle needs to set the value on and off real fast for some reason so call both 50ms apart.
    def sendVe500CcToggle(self, seconds:float, ccNumber:int):
        self.sendCcandValue(seconds=seconds, channel=self.ve500.midiChannel, ccNumber=ccNumber, ccValue=127)
        self.sendCcandValue(seconds=0.05, channel=self.ve500.midiChannel, ccNumber=ccNumber, ccValue=0)

    def sendVe500CcOn(self, seconds:float, ccNumber:int):
        self.sendCcandValue(seconds=seconds, channel=self.ve500.midiChannel, ccNumber=ccNumber, ccValue=0)

    def sendVe500CcOff(self, seconds:float, ccNumber:int):
        self.sendCcandValue(seconds=seconds, channel=self.ve500.midiChannel, ccNumber=ccNumber, ccValue=127)

    # General
    def sendCcandValue(self, seconds:float, channel:int, ccNumber:int, ccValue):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=ccNumber, value=ccValue, time=ticks, channel=channel - 1))

    # AxFx    
    def setAfxPatch(self, seconds:float, patchNumber:int):
        
        ticks = self._calculateTicks(seconds=seconds)
        
        # Set Bank Select MSB and LSB for bank 4 before program change
        self.track.append(Message('control_change', control=0, value=self.axFx.patchBank, time=ticks, channel=self.axFx.midiChannel - 1))
        # AxeFx does not need LSB
        # track.append(Message('control_change', control=32, value=0, time=0, channel=MIDI_CHANNEL))                

        # Program Change immediatly after the CC by a few ticks.
        self.track.append(Message('program_change', program=patchNumber, time=5, channel=self.axFx.midiChannel - 1))

    def switchAfxScene(self, seconds:float, sceneNumber:int):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=self.axFx.sceneMidiCC, value=sceneNumber - 1, time=ticks, channel=self.axFx.midiChannel - 1))

    def sendAfxCcOff(self, seconds:float, cc:int):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=cc, value=0, time=ticks, channel=self.axFx.midiChannel - 1))

    def sendAfxCcOn(self, seconds:float, cc:int):
        ticks = self._calculateTicks(seconds=seconds)
        self.track.append(Message('control_change', control=cc, value=127, time=ticks, channel=self.axFx.midiChannel - 1))

    def saveMidiFile(self):
        self.midiFile.save(self.fileName)
        print(f"Created Midi: {self.fileName.absolute()}")

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
        afx = self.jsonData['AFX']
        ve500Data = self.jsonData['VE500']

        fileName = Path(songData['fileName'])
        bpm = songData['bpm']

        ve500 = Ve500(
            midiChannel=ve500Data['midiChannel'],
            patchBank=ve500Data['patchBank'],
        )

        axFx = AfxPatch(
            midiChannel=afx['midiChannel'],
            patchBank=afx['patchBank'],
            sceneMidiCC=afx['sceneMidiCC']
        )

        midiFile = MidiFile()
        track = MidiTrack()
        track.name = "track_0"
        midiFile.tracks.append(track)
        song = Song(
            midiFile=midiFile,
            track=track,
            axFx=axFx,
            ve500=ve500,
            fileName=fileName,
            bpm=bpm
        )
        return song

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
            elif event['event'] == 'sendAfxCcOff':
                self.song.sendAfxCcOff(seconds=secondsDelta, cc=event['data'])
            elif event['event'] == 'sendAfxCcOn':
                self.song.sendAfxCcOn(seconds=secondsDelta, cc=event['data'])
            elif event['event'] == 'setVe500Patch':
                self.song.setVe500Patch(seconds=secondsDelta, patchNumber=event['data'])
            elif event['event'] == 'sendVe500CcOn':
                self.song.sendVe500CcOn(seconds=secondsDelta, ccNumber=event['cc'])
            elif event['event'] == 'sendVe500CcOff':
                self.song.sendVe500CcOff(seconds=secondsDelta, ccNumber=event['cc'])
            elif event['event'] == 'sendVe500CcToggle':
                self.song.sendVe500CcToggle(seconds=secondsDelta, ccNumber=event['cc'])
            elif event['event'] == 'sendCcandValue':
                self.song.sendCcandValue(
                    seconds=secondsDelta,
                    channel=event['channel'],
                    ccNumber=event['cc'],
                    ccValue=event['value'])
            else:
                raise KeyError(f"Can't find function {event['event']}")

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
                stackTrace = traceback.format_exc()
                print(f"Failed to process {file.name}: {e}")
                print(stackTrace)
    