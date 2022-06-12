# -*- coding: utf-8 -*-
"""
App to view Spectrograms

Simon Gillings
June 2022

This layout is based on the following post which shows how to use frames as pages:
https://stackoverflow.com/questions/14817210/using-buttons-in-tkinter-to-navigate-to-different-pages-of-the-application


@author: simon.gillings
"""


import tkinter as tk
from tkinter import filedialog as fd  # needed for file dialogues
#from tkinter import ttk

# for the audio and spectrogram
import librosa
import numpy as np
from math import floor  # for working out x axis

# for folders and paths
#import os, glob, pathlib
import pathlib

# for plotting within tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Actions():
    def __init__(self, parent):
        # this allows referencing objects in the parent class, i.e. in one of the page classes
        self.parent = parent

        # Config settings
        self.maxduration = 4.0  # Maximum clip duration to allow a spectrogram to be shown
        self.fileopentypes = (
            ('Wav files', '*.wav'),
            ('All files', '*.*')
        )

        # Internal dynamic parameters
        self.current_file = tk.StringVar()
        self.current_folder = tk.StringVar()
        self.num_files = tk.IntVar()
        self.duration = tk.DoubleVar()

    # method to select a single file, and if selected, open it
    def select_file(self):
        audio_file = fd.askopenfilename(
            title='Open a file',
            filetypes=self.fileopentypes)
        if len(audio_file) > 0:
            print(audio_file)
            self.current_file.set(audio_file)
            # print(self.current_file.get())
            self.open_audio_file(file=audio_file)

    # method to select a folder, and if selected, collect list of files
    def select_folder(self):
        folder = fd.askdirectory(title='Select a folder')
        if len(folder) > 0:
            self.current_folder.set(folder)
            
            # get list of audio files in folder
            filetypes = ['.wav', '.WAV', '.mp3', '.MP3']
            self.audio_files = []
            for filetype in filetypes:
                self.audio_files.extend(
                    [filename for filename in pathlib.Path(folder).rglob('*' + filetype)])

            #how many files
            self.num_files.set(len(self.audio_files))

            #show the first file
            self.file_counter = 0
            audio_file = self.audio_files[self.file_counter]
            self.current_file.set(audio_file)
            self.open_audio_file(file=audio_file)

    def file_forward(self):
        self.file_counter = self.file_counter + 1
        audio_file = self.audio_files[self.file_counter]
        self.current_file.set(audio_file)
        self.open_audio_file(file=audio_file)

    def file_backward(self):
        self.file_counter = self.file_counter - 1
        audio_file = self.audio_files[self.file_counter]
        self.current_file.set(audio_file)
        self.open_audio_file(file=audio_file)

    def open_audio_file(self, file):
        print("Open file")
        x, sr = librosa.load(file, mono=True, sr=22050)
        dur = librosa.get_duration(y=x, sr=sr)
        self.duration.set(dur)
        if self.duration.get() > self.maxduration:
            tk.messagebox.showerror(
                title='Error', message='File is too long!')
        # print(dur)
        if self.duration.get() <= self.maxduration:
            self.create_spectrogram(x, sr)

    # method to plot a spectrogram
    def create_spectrogram(self, x, sr):
        # Get the audio data and prepare
        #x, sr = librosa.load(file, sr = 22050, mono = True)
        D = librosa.amplitude_to_db(np.abs(librosa.stft(x)), ref=np.max)
        # determine x scale
        print(D.shape)
        xsteps = D.shape[1] / self.duration.get()
        print(xsteps)
        # adding the subplot
        self.parent.ax.clear()
        # plt.rcParams['toolbar'] = 'None' # Remove tool bar (upper bar)
        self.parent.ax.pcolormesh(D)
        #self.parent.ax.axes.set_xticks(D.shape[1] * np.linspace(0,1,self.duration.get()+1))
        #self.parent.ax.axes.set_xticklabels(np.linspace(0, 4, 5))
        labs = np.unique(np.append(np.linspace(0, floor(self.duration.get()), floor(
            self.duration.get())+1), self.duration.get()))
        print(labs)
        self.parent.canvas.draw()


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()

# Class for allowing a single clip to be plotted


class Page_single(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # MAIN PAGE STRUCTURE
        # frames
        actionsframe = tk.Frame(self, bg='white')
        actionsframe.pack(side="top", fill="x", expand=False)
        infoframe1 = tk.Frame(self, bg='white')
        infoframe1.pack(side="top", fill="x", expand=False)
        infoframe2 = tk.Frame(self, bg='white')
        infoframe2.pack(side="top", fill="x", expand=False)
        specframe = tk.Frame(self, bg='white')
        specframe.pack(side="top", fill="both", expand=True)

        # The plotting canvas
        fig = plt.figure(figsize=(10, 6))
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=specframe)
        self.canvas.get_tk_widget().grid(column=0, row=5)
        self.canvas.draw()

        # MAIN ACTIONS
        # instance of Actions to be able to call actions
        actions = Actions(self)

        # buttons
        button_select_file = tk.Button(
            actionsframe, text="Select audio file", command=lambda: actions.select_file())
        button_select_file.pack(side="left", anchor='nw', padx=5, pady=5)
        # labels
        label_Filename = tk.Label(infoframe1, text='File:', bg='white')
        label_Filename.pack(side="left", anchor='nw', padx=10, pady=2)
        label_filename = tk.Label(
            infoframe1, textvariable=actions.current_file, bg='white')
        label_filename.pack(side="left", pady=2)
        label_Duration = tk.Label(infoframe2, text='Length(s):', bg='white')
        label_Duration.pack(side="left", anchor='nw', padx=10, pady=2)
        label_duration = tk.Label(
            infoframe2, textvariable=actions.duration, bg='white')
        label_duration.pack(side="left", pady=2)


# Class for page allowing iteration over clips in a folder
class Page_multiple(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # MAIN PAGE STRUCTURE
        # frames
        actionsframe = tk.Frame(self, bg='white')
        actionsframe.pack(side="top", fill="x", expand=False)
        infoframe1 = tk.Frame(self, bg='white')
        infoframe1.pack(side="top", fill="x", expand=False)
        infoframe2 = tk.Frame(self, bg='white')
        infoframe2.pack(side="top", fill="x", expand=False)
        infoframe3 = tk.Frame(self, bg='white')
        infoframe3.pack(side="top", fill="x", expand=False)
        infoframe4 = tk.Frame(self, bg='white')
        infoframe4.pack(side="top", fill="x", expand=False)
        specframe = tk.Frame(self, bg='white')
        specframe.pack(side="top", fill="both", expand=True)

        # The plotting canvas
        fig = plt.figure(figsize=(10, 6))
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=specframe)
        self.canvas.get_tk_widget().grid(column=0, row=5)
        self.canvas.draw()

        # MAIN ACTIONS
        # instance of Actions to be able to call actions
        actions = Actions(self)

        # label = tk.Label(self, text="Multiple file method")
        # label.pack(side="top", fill="both", expand=True)
        button_select_folder = tk.Button(
            actionsframe, text="Select folder", command=lambda: actions.select_folder())
        button_select_folder.pack(side="left", anchor='nw', padx=5, pady=5)
        button_backward = tk.Button(actionsframe, text="Previous file", command=lambda: actions.file_backward())
        button_backward.pack(side="left", anchor='nw', padx=5, pady=5)
        button_forward = tk.Button(actionsframe, text="Next file", command=lambda: actions.file_forward())
        button_forward.pack(side="left", anchor='nw', padx=5, pady=5)

        # labels
        label_Folder = tk.Label(infoframe1, text='Folder:', bg='white')
        label_Folder.pack(side="left", anchor='nw', padx=10, pady=2)
        label_folder = tk.Label(
            infoframe1, textvariable=actions.current_folder, bg='white')
        label_folder.pack(side="left", pady=2)
        label_NumFiles = tk.Label(infoframe2, text='Num files:', bg='white')
        label_NumFiles.pack(side="left", anchor='nw', padx=10, pady=2)
        label_numfiles = tk.Label(
            infoframe2, textvariable=actions.num_files, bg='white')
        label_numfiles.pack(side="left", pady=2)
        label_Filename = tk.Label(infoframe3, text='File:', bg='white')
        label_Filename.pack(side="left", anchor='nw', padx=10, pady=2)
        label_filename = tk.Label(
            infoframe3, textvariable=actions.current_file, bg='white')
        label_filename.pack(side="left", pady=2)
        label_Duration = tk.Label(infoframe4, text='Length(s):', bg='white')
        label_Duration.pack(side="left", anchor='nw', padx=10, pady=2)
        label_duration = tk.Label(
            infoframe4, textvariable=actions.duration, bg='white')
        label_duration.pack(side="left", pady=2)


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        #actions = Actions(self)

        p1 = Page_single(self)
        p2 = Page_multiple(self)

        buttonframe = tk.Frame(self, bg='black')
        container = tk.Frame(self, bg='white')
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(buttonframe, text="Single file", command=p1.show)
        b2 = tk.Button(buttonframe, text="Multiple files", command=p2.show)
        b3 = tk.Button(buttonframe, text="Quit", command=p2.show)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")

        p1.show()


if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.title('Polyglotta Toolbox')
    root.wm_geometry("1200x800")

    root.mainloop()
