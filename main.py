# -*- coding: utf-8 -*-
"""
App to view Spectrograms

Select Single File to view/play a single audio file
Select Multiple Files to browse through audio files in a folder. Optionally move 
files to True (TruePos), False (FalsePos) or Uncertain (Uncertain) folders. 
Optionally also add species-specific buttons for files to be relabelled as 
something completely different 

When moving files, don't use back button as haven't added functionality to 
rebuild array of files once a file has been moved.

Simon Gillings
June 2022

Tips on multiple 'page' layout from::
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
import os

# for plotting within tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# for the audio player - note needs playsound 1.2.2
import winsound
#from playsound import playsound #pip install playsound==1.2.2 #using winsound as playsound keeps locking files

class Actions():
    def __init__(self, parent):
        # this allows referencing objects in the parent class, i.e. in one of the page classes
        self.parent = parent

        # Config settings
        self.maxduration = 10.0  # Maximum clip duration to allow a spectrogram to be shown
        self.fileopentypes = (
            ('Wav files', '*.wav'),
            ('All files', '*.*')
        )

        # Internal dynamic parameters
        self.file_counter = tk.IntVar()
        self.file_counter_text = tk.StringVar()
        self.file_counter_text.set('File ' + str(self.file_counter.get()))
        self.file_counter_display = tk.IntVar()
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
            #print(audio_file)
            self.current_file.set(audio_file)
            # print(self.current_file.get())
            self.open_audio_file(file=audio_file)

    # method to select a folder, and if selected, collect list of files
    def select_folder(self):
        folder = fd.askdirectory(title='Select a folder')
        if len(folder) > 0:
            self.current_folder.set(folder)
            
            # get list of audio files in folder
            filetypes = ['.wav', '.mp3']
            self.audio_files = []
            for filetype in filetypes:
                self.audio_files.extend(
                    [filename for filename in pathlib.Path(folder).rglob('*' + filetype)])

            #how many files
            self.num_files.set(len(self.audio_files))

            #show the first file
            self.file_counter.set(0)
            audio_file = self.audio_files[self.file_counter.get()]
            self.file_counter_text.set('File ' + str(self.file_counter.get()+1))
            self.current_file.set(audio_file)
            self.open_audio_file(file=audio_file)

    def file_jump(self, jump: int=1):
        self.file_counter.set(self.file_counter.get() + jump)
        if self.file_counter.get()<0:
            tk.messagebox.showwarning(title='Out of range', message="Tried to jump beyond list. Set to 1st file")
            self.file_counter.set(0)
        if self.file_counter.get() >= self.num_files.get():
            tk.messagebox.showwarning(title='Out of range', message="Tried to jump beyond list. Set to last file")
            self.file_counter.set(self.num_files.get())
        
        #self.file_counter_display.set(self.file_counter.get() + 1)
        self.file_counter_text.set('File ' + str(self.file_counter.get()+1))
        audio_file = self.audio_files[self.file_counter.get()]
        self.current_file.set(audio_file)
        self.open_audio_file(file=audio_file)


    def open_audio_file(self, file):
        #print("Open file")
        x, sr = librosa.load(file, mono=True, sr=22050)
        dur = round(librosa.get_duration(y=x, sr=sr), 1)
        self.duration.set(dur)
        if self.duration.get() > self.maxduration:
            tk.messagebox.showerror(
                title='Error', message='File is too long!')
        # print(dur)
        if self.duration.get() <= self.maxduration:
            self.create_spectrogram(x, sr)

    # method to plot a spectrogram
    def create_spectrogram(self, x, sr):
        """
        Create a spectrogram and send to the canvas

        Parameters
        ----------
        x : audio data
        sr : sample rate of the audio

        Returns
        -------
        None.

        """
        # Get the audio data and prepare
        #x, sr = librosa.load(file, sr = 22050, mono = True)
        D = librosa.amplitude_to_db(np.abs(librosa.stft(x, n_fft = 1024, hop_length=256, win_length=1024)), ref=np.max)
        # determine x scale
        #print(D.shape)
        #xsteps = D.shape[1] / self.duration.get()
        #print(xsteps)
        # adding the subplot
        self.parent.ax.clear()
        # plt.rcParams['toolbar'] = 'None' # Remove tool bar (upper bar)
        self.parent.ax.pcolormesh(D)
        #self.parent.ax.axes.set_xticks(D.shape[1] * np.linspace(0,1,self.duration.get()+1))
        #self.parent.ax.axes.set_xticklabels(np.linspace(0, 4, 5))
        self.parent.ax.axes.set_xticks([0, D.shape[1]])
        self.parent.ax.axes.set_xticklabels([0, round(self.duration.get(),1)])
        self.parent.ax.axes.set_yticks([0,100,200,300,400,500])
        self.parent.ax.axes.set_yticklabels([0,2000,4000,6000,8000,10000])
        # labs = np.unique(np.append(np.linspace(0, floor(self.duration.get()), floor(
        #     self.duration.get())+1), self.duration.get()))
        # #print(labs)
        self.parent.canvas.draw()

    def play(self):
        """
        Play an audio file
        """
        winsound.PlaySound(self.current_file.get(), winsound.SND_ALIAS)

        # playsound locks files and causes problems when moving
        # playsound(self.current_file.get())
    


    def make_folder(self, foldername):
        """
        Make a folder to move verified clips to
        """
        path = os.path.join(self.current_folder.get(), foldername)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    # def make_folder_FP(self):
    #     """
    #     Make a folder to move False Positive clips to
    #     """
    #     path_FP = os.path.join(self.current_folder.get(), 'FP')
    #     if not os.path.exists(path_FP):
    #         os.mkdir(path_FP)
    #     return path_FP

    # def make_folder_QQ(self):
    #     """
    #     Make a folder to move Uncertain clips to
    #     """
    #     path_QQ = os.path.join(self.current_folder.get(), 'QQ')
    #     if not os.path.exists(path_QQ):
    #         os.mkdir(path_QQ)
    #     return path_QQ
    

    def identification_move(self, response):
        #make the folder to hold the validated clip depending on response
        path = self.make_folder(foldername = response)
        #name for file when moved
        file_target = os.path.join(path, os.path.split(self.current_file.get())[1])
        os.rename(self.current_file.get(), file_target)

        # TO DO need to remove file from list as no longer in top level folder
        
        #increment counter
        self.file_jump(1)

    # def identification_false(self):
    #     #make the folder to hold the false positive
    #     path_FP = self.make_folder('FP')
    #     #name for file when moved
    #     file_target = os.path.join(path_FP, os.path.split(self.current_file.get())[1])
    #     os.rename(self.current_file.get(), file_target)

    #     # TO DO need to remove file from list as no longer in top level folder
        
    #     #increment counter
    #     self.file_jump(1)
        
    # def identification_uncertain(self):
    #     #make the folder to hold the false positive
    #     path_QQ = self.make_folder('QQ')
    #     #name for file when moved
    #     file_target = os.path.join(path_QQ, os.path.split(self.current_file.get())[1])
    #     os.rename(self.current_file.get(), file_target)

    #     #TO DO need to remove file from list as no longer in top level folder
        
    #     #increment counter
    #     self.file_jump(1)
        

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        #colours
        self.blue = '#004488'
        self.bluel = '#6699CC'
        self.red = '#994455'
        self.redl = '#EE99AA'
        self.yellow = '#997700'
        self.yellowl = '#EECC66'
        

    def show(self):
        self.lift()

# Class for allowing a single clip to be plotted


class Page_single(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # MAIN PAGE STRUCTURE
        # frames
        frame_file = tk.Frame(self, bg='white')
        frame_file.pack(side="top", fill="x", expand=False)
        frame_actions = tk.Frame(self, bg='white')
        frame_actions.pack(side="top", fill="x", expand=False)
        infoframe2 = tk.Frame(self, bg='white')
        infoframe2.pack(side="top", fill="x", expand=False)
        frame_spec = tk.Frame(self, bg='white')
        frame_spec.pack(side="top", fill="both", expand=True)
        # frame_response = tk.Frame(self, bg='white')
        # frame_response.pack(side="top", fill="x", expand=False)


        # The plotting canvas
        fig = plt.figure(figsize=(10, 6))
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=frame_spec)
        self.canvas.get_tk_widget().grid(column=0, row=5)
        self.canvas.draw()

        # MAIN ACTIONS
        # instance of Actions to be able to call actions
        actions = Actions(self)

        # buttons
        button_select_file = tk.Button(frame_file, text="Select audio file", command=lambda: actions.select_file(), font=("Arial", 12))
        button_select_file.pack(side="left", padx=5, pady=5)
      
        button_play = tk.Button(frame_actions, text="Play", command=lambda: actions.play(), bg = self.blue, fg='white', font=("Arial", 12))
        button_play.pack(side="left", padx=400, pady=5)
        
        # labels
        # label_filename = tk.Label(frame_file, text='File:', bg='white')
        # label_filename.pack(side="left", padx=10, pady=2)
        value_filename = tk.Label(frame_file, textvariable=actions.current_file, bg='white', fg=self.blue, font=("Arial", 12))
        value_filename.pack(side="left", pady=2)
        # label_Duration = tk.Label(infoframe2, text='Length(s):', bg='white')
        # label_Duration.pack(side="left", anchor='nw', padx=10, pady=2)
        # label_duration = tk.Label(infoframe2, textvariable=actions.duration, bg='white')
        # label_duration.pack(side="left", pady=2)


# Class for page allowing iteration over clips in a folder
class Page_multiple(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # MAIN PAGE STRUCTURE
        # frames
        frame_folder = tk.Frame(self, bg='white')
        frame_folder.pack(side="top", fill="x", expand=False)
        frame_file1 = tk.Frame(self, bg='white')
        frame_file1.pack(side="top", fill="x", expand=False)
        frame_file2 = tk.Frame(self, bg='white')
        frame_file2.pack(side="top", fill="x", expand=False)
        frame_actions = tk.Frame(self, bg='white')
        frame_actions.pack(side="top", fill="x", expand=False)
        frame_response = tk.Frame(self, bg='white')
        frame_response.pack(side="top", fill="x", expand=False)
        frame_spec = tk.Frame(self, bg='white')
        frame_spec.pack(side="top", fill="both", expand=False)

        # The plotting canvas
        fig = plt.figure(figsize=(10, 6))
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=frame_spec)
        self.canvas.get_tk_widget().grid(column=0, row=5)
        self.canvas.draw()

        # MAIN ACTIONS
        # instance of Actions to be able to call actions
        actions = Actions(self)

        # label = tk.Label(self, text="Multiple file method")
        # label.pack(side="top", fill="both", expand=True)
        button_select_folder = tk.Button(frame_folder, text="Select folder", command=lambda: actions.select_folder(), font=("Arial", 12))
        button_select_folder.pack(side="left", anchor='nw', padx=5, pady=5)
        
        button_backward = tk.Button(frame_actions, text="Previous file", command=lambda: actions.file_jump(-1), font=("Arial", 12))
        button_backward.pack(side="left", padx=(150,15), pady=5)
        button_play = tk.Button(frame_actions, text="Play", command=lambda: actions.play(), bg = self.blue, fg='white', font=("Arial", 12))
        button_play.pack(side="left", padx=5, pady=5)
        button_forward = tk.Button(frame_actions, text="Next file", command=lambda: actions.file_jump(1), font=("Arial", 12))
        button_forward.pack(side="left", padx=15, pady=5)

        button_true = tk.Button(frame_response, text="Correct", command=lambda: actions.identification_move('TruePos'), bg = self.bluel, font=("Arial", 12))
        button_true.pack(side="left", padx=(150,15), pady=5)
        button_false = tk.Button(frame_response, text="Incorrect", command=lambda: actions.identification_move('FalsePos'), bg = self.redl, font=("Arial", 12))
        button_false.pack(side="left", padx=5, pady=5)
        button_quarantine = tk.Button(frame_response, text="Uncertain", command=lambda: actions.identification_move('Uncertain'), bg=self.yellowl, font=("Arial", 12))
        button_quarantine.pack(side="left", padx=15, pady=5)

        button_TO = tk.Button(frame_response, text="Tawny Owl", command=lambda: actions.identification_move('TO'), bg=self.yellowl, font=("Arial", 12))
        button_TO.pack(side="left", padx=10, pady=5)
        button_TO = tk.Button(frame_response, text="Thrush Nightingale", command=lambda: actions.identification_move('FN'), bg=self.yellowl, font=("Arial", 12))
        button_TO.pack(side="left", padx=10, pady=5)
        button_TO = tk.Button(frame_response, text="Grey Heron", command=lambda: actions.identification_move('H_'), bg=self.yellowl, font=("Arial", 12))
        button_TO.pack(side="left", padx=10, pady=5)
        
        
        
        

        # labels
        value_folder = tk.Label(frame_folder, textvariable=actions.current_folder, bg='white', fg=self.blue, font=("Arial", 12))
        value_folder.pack(side="left", pady=2)
        value_numfiles = tk.Label(frame_folder, textvariable=actions.num_files, bg='white', fg=self.blue, font=("Arial", 12))
        value_numfiles.pack(side="left", pady=2)
        label_numfiles = tk.Label(frame_folder, text='files', bg='white', fg=self.blue, font=("Arial", 12))
        label_numfiles.pack(side="left", pady=2)
        
        value_counter = tk.Label(frame_file1, textvariable=actions.file_counter_text, bg='white', font=("Arial", 12))
        value_counter.pack(side="left", padx=10, pady=2)
        value_filename = tk.Label(frame_file1, textvariable=actions.current_file, bg='white', fg=self.blue, font=("Arial", 12))
        value_filename.pack(side="left", pady=2)
        
        #label_duration = tk.Label(frame_file2, text='Length(s):', bg='white')
        #label_duration.pack(side="left", padx=10, pady=2)
        #value_duration = tk.Label(frame_file2, textvariable=actions.duration, bg='white', fg='blue')
        #value_duration.pack(side="left", pady=2)


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        #actions = Actions(self)

        p1 = Page_single(self)
        p2 = Page_multiple(self)

        buttonframe = tk.Frame(self, bg='grey')
        buttonframe.pack(side="top", fill="x", expand=False)
        container = tk.Frame(self, bg='white')
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(buttonframe, text="Single file", command=p1.show, font=("Arial", 12))
        b2 = tk.Button(buttonframe, text="Multiple files", command=p2.show, font=("Arial", 12))
        b3 = tk.Button(buttonframe, text="Quit", command=root.destroy, font=("Arial", 12))

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
