# Spectrogram viewer, player and clip validator
Python Tkinter app to plot and validate spectrograms

Two modes:

* Single file: allows for plotting and playing a spectrogram for a single file
* Multiple file: select a folder to browse all audio files in the folder. Optionally can play a clip and validate it: move file to TruePos, FalsePos or Uncertain folders. This is designed assuming all clips in a folder are supposed to be a particular class. Instead can be customised to add species-specific buttons (three shown) 

### Requires

* Built under Python 3.8
* tkinter, librosa, numpy, math, pathlib, os, matplotlib, winsound

### Limitations and known issues

* Currently limited to showing clips of no more than 10s duration
* Currently limited to read clips at 22050 kHz and frequency axis hard-coded. I may add a config screen to modify this. Window size, hop length etc also currently fixed

![Screenshot](https://github.com/BritishTrustForOrnithology/spectrogram_viewer/blob/main/images/screengrab.jpg)


### Recent bug fixes

* 18/06/2022: File array now updates when a file is moved, so the Previous File button works properly


Simon Gillings
BTO