https://mido.readthedocs.io/en/stable/installing.html


Use the midieditor tool to make midi tracks

always one track
midi channel 0

to select a preset
    event 1: bank select
        CC: control 0, Value 0-3.  (usually 3)
    event 2: Program Change a few ticks after
        Program: 12, Channel 0


To select a Scene
    event 1: CC
        Control 34; Value 0-7 [0 based]


Leslie
    event 1: CC
        Control 69; Value 0 OFF 127 ON




Popular Scenes Bank 3
Metallica       19
AIC             21
Nirvana         15
Acoustic        24
Bass            25
Nirvana DFS     14
Nirvana Scene Controller USA    12
FW6             30
