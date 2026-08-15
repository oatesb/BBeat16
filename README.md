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


dir *.wav | % { ren $_ $_.Name.Substring(2) }; del .\wav;ls

I have some music stems that I need to search for in one folder and then renamed and moved to another folder that we will create.  Make a powershell that does the following.  Ask for a search string.  Then in the hard coded source folder search for all files that have that name, and store that file name in memory replacing all the '_' in the name with ' '.  Now we need to make a folder in the hard coded Destination Foler.  The folder name will be the searched file name upto the '('.  The file name will be the text between the 2 parens.  Then extention will be the same extension at the end of the folder.  Another rule for the file name is to remove 'Custom Backing Track' from the file name.  If that would be an empty string then title it misc## with an incrementing number at the end.

sourceDir:
C:\Users\oates\Downloads

destinationDir:
C:\Guitar\RipX\Audacity


sample files found in the sourceDir:
Green_Day_Jesus_of_Suburbia(Acoustic_Guitar_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Backing_Vocals_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Bass_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Click_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Drum_Kit_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Electric_Guitar_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Lead_Electric_Guitar_Custom_Backing_Track).mp3
Green_Day_Jesus_of_Suburbia(Lead_Vocal_Custom_Backing_Track).mp3

Example folder created:
C:\Guitar\RipX\Audacity\Green Day Jesus of Suburbia

Example of the files created in 'C:\Guitar\RipX\Audacity\Green Day Jesus of Suburbia':
Acoustic Guitar.mp3
Backing_Vocals.mp3
misc01.mp3
