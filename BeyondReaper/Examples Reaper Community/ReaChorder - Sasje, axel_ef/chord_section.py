# from reaper_python import *
import debug
from rs_midi import RSMidi
from random import choice
import reaChord_data
import tkinter
from tkinter import ttk
from rs_statemanager import RSStateManager

class ChordSection(RSStateManager):
    '''
    Copius chord tomfoolery
    '''

    #rc = reaChord_functions.RC() # comment out - just for autocomplete

    def __init__(self, parent, rc):
        '''

        '''
        debug.msg("Chords __init__  Enter")

        #default settings
        self.settings = {
            "draw": 1, "channel": 1, "velocity": 96, "highlight": 1, "invert_above": 6
        }
        self.stateManager_Start("ChordSection", self.settings)
        self.parent = parent
        self.rc = rc
        self.init_widgets()
        debug.msg("Chords __init__  Exit")




    def draw(self, midiTake, song, sectionLength):
        #song dictionary contains full Structure and chords for the sections
        # ie Verse and Chorus at the moment.
        if not(self.drawOrNot.get()):  return
        currentPos = 0

        for i, sect in enumerate(song["Structure"]):
            chords = song[str(sect)]
            chordLength = sectionLength / len(chords)
            for i, chord in enumerate(chords):
                self.drawChord(midiTake, chord, currentPos, chordLength, i)
                currentPos += chordLength
##        return currentPos



    def drawChord(self,midiTake, chord, currentPos, chordLength, chordIndex): #velocity,x,position,startPosition,rd,chordattack,selectNote):
        debug.msg('drawChord - Enter')

        # alwaysRootPosition:
        #   True = always draw chords in root position, False = randomize between root position and second inversion
        alwaysRootPosition = False

##        if chordIndex == 0:   # todo: "smooth chord progr."
##        firstChord = chord
        if not alwaysRootPosition:
            randomChPosL = ["rootPosition", "inversion2nd"] # ["rootPosition", "inversion1st", "inversion2nd"]
            chordPos = choice(randomChPosL)
        else:
            chordPos = "rootPosition"

        velocity = self.velocity.get()
        chordattack = self.chordAttack.get()
        selectNote = self.highlight.get()
        step = 0
        debug.msg(chordattack)
        if chordattack == 'Fast': step=120 #fast
        elif chordattack == 'Slow': step=480 #slow
        channel = self.settings["channel"]
        noteOffset = -12

        # root position
        if chordPos == "rootPosition":
            note1Pitch = int(self.rc.ChordDict[chord][0]) + noteOffset
            note2Pitch = int(self.rc.ChordDict[chord][1]) + noteOffset
            note3Pitch = int(self.rc.ChordDict[chord][2]) + noteOffset

        # first inversion
        if chordPos == "inversion1st":
            note1Pitch = int(self.rc.ChordDict[chord][1]) + noteOffset - 12
            note2Pitch = int(self.rc.ChordDict[chord][2]) + noteOffset - 12
            note3Pitch = int(self.rc.ChordDict[chord][0]) + noteOffset

        # second inversion
        if chordPos == "inversion2nd":
            note1Pitch = int(self.rc.ChordDict[chord][2]) + noteOffset - 12
            note2Pitch = int(self.rc.ChordDict[chord][0]) + noteOffset
            note3Pitch = int(self.rc.ChordDict[chord][1]) + noteOffset

        debug.msg("wtf2")

        RSMidi.addNote(midiTake, channel, int(velocity), int(currentPos),\
                            note1Pitch, int(chordLength), selectNote)
        RSMidi.addNote(midiTake, channel, int(velocity), int(currentPos+step),\
                            note2Pitch, int(chordLength)-step, selectNote)
        RSMidi.addNote(midiTake, channel, int(velocity), int(currentPos+(step*2)),\
                            note3Pitch, int(chordLength)-(step*2), selectNote)

        debug.msg('drawChord - Exit')
        return currentPos



    def init_widgets(self):
        # Widget Initialization

        self._label_1 = tkinter.Label(self.parent,
            text = "Draw:",bg="#E8E8E8",
        )
        self._label_2 = tkinter.Label(self.parent,
            text = "Highlight:",bg="#E8E8E8",
        )
        self._label_3 = tkinter.Label(self.parent,
            text = "Channel:",bg="#E8E8E8",
        )
        self._label_4 = tkinter.Label(self.parent,
            text = "Velocity:",bg="#E8E8E8",
        )
        self._label_5 = tkinter.Label(self.parent,
            text = "Attack:",bg="#E8E8E8",
        )
        
        

        self.drawOrNot = self.newControlIntVar("draw", 1)
        self.cDrawOrNot = tkinter.Checkbutton(self.parent, variable=self.drawOrNot,bg="#E8E8E8")
        
        self.highlight = self.newControlIntVar("highlight", 1)
        self.cHighlight = tkinter.Checkbutton(self.parent, variable=self.highlight,bg="#E8E8E8")

        self.channel = self.newControlIntVar("channel", 1)
        self.sChannel = tkinter.Scale(self.parent, from_=1, to=16, resolution=1, showvalue=0, orient="horizontal",\
                                      variable=self.channel)
        self.scaleTxt1 = ttk.Label(self.parent, textvariable=self.channel)
              
        self.velocity = self.newControlIntVar("velocity", 96)
        self.sVelocity = tkinter.Scale(self.parent, from_=1, to=127, resolution=1, showvalue=0, orient="horizontal",\
                                       variable=self.velocity)
        self.scaleTxt2 = ttk.Label(self.parent, textvariable=self.velocity)
        
        self.chordAttack = self.newControlStrVar("chordattack", self.rc.ChordAttack[1])
        self.cbChordAttack = ttk.Combobox(self.parent, values=self.rc.ChordAttack, state='readonly', width=13,\
                                          textvariable=self.chordAttack)
        #self.cbChordAttack.current(0)

        # Geometry Management

        self._label_1.grid(
            in_    = self.parent,
            column = 1,
            row    = 1,
            columnspan = 1,
            ipadx = 10,
            ipady = 5,
            padx = 0,
            pady = 5,
            rowspan = 1,
            sticky = "w"
        )
        self._label_2.grid(
            in_    = self.parent,
            column = 1,
            row    = 2,
            columnspan = 1,
            ipadx = 10,
            ipady = 5,
            padx = 0,
            pady = 5,
            rowspan = 1,
            sticky = "w"
        )
        self._label_3.grid(
            in_    = self.parent,
            column = 1,
            row    = 3,
            columnspan = 1,
            ipadx = 10,
            ipady = 5,
            padx = 0,
            pady = 5,
            rowspan = 1,
            sticky = "w"
        )
        self._label_4.grid(
            in_    = self.parent,
            column = 1,
            row    = 4,
            columnspan = 1,
            ipadx = 10,
            ipady = 5,
            padx = 0,
            pady = 5,
            rowspan = 1,
            sticky = "w"
        )
        self._label_5.grid(
            in_    = self.parent,
            column = 1,
            row    = 5,
            columnspan = 1,
            ipadx = 10,
            ipady = 0,
            padx = 0,
            pady = 10,
            rowspan = 1,
            sticky = "w"
        )
        self.scaleTxt1.grid(
            in_    = self.parent,
            column = 2,
            row    = 3,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 2,
            pady = 0,
            rowspan = 1,
            sticky = "e"
        )
        self.scaleTxt2.grid(
            in_    = self.parent,
            column = 2,
            row    = 4,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 2,
            pady = 0,
            rowspan = 1,
            sticky = "e"
        )

        self.cDrawOrNot.grid(
            in_    = self.parent,
            column = 2,
            row    = 1,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 0,
            pady = 0,
            rowspan = 1,
            sticky = "w"
        )
        self.cHighlight.grid(
            in_    = self.parent,
            column = 2,
            row    = 2,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 0,
            pady = 0,
            rowspan = 1,
            sticky = "w"
        )
        self.sVelocity.grid(
            in_    = self.parent,
            column = 2,
            row    = 4,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 0,
            pady = 0,
            rowspan = 1,
            sticky = "w"
        )
        self.cbChordAttack.grid(
            in_    = self.parent,
            column = 2,
            row    = 5,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 0,
            pady = 0,
            rowspan = 1,
            sticky = "w"
        )

        self.sChannel.grid(
            in_    = self.parent,
            column = 2,
            row    = 3,
            columnspan = 1,
            ipadx = 0,
            ipady = 0,
            padx = 0,
            pady = 0,
            rowspan = 1,
            sticky = "w"
        )
        self.parent.grid_rowconfigure(1, weight = 0, minsize = 22, pad = 0)
        self.parent.grid_rowconfigure(2, weight = 0, minsize = 22, pad = 0)
        self.parent.grid_rowconfigure(3, weight = 0, minsize = 22, pad = 0)
        self.parent.grid_rowconfigure(4, weight = 0, minsize = 22, pad = 0)
        self.parent.grid_rowconfigure(5, weight = 0, minsize = 22, pad = 0)
        self.parent.grid_rowconfigure(6, weight = 0, minsize = 22, pad = 0)
        self.parent.grid_columnconfigure(1, weight = 0, minsize = 80, pad = 0)
        self.parent.grid_columnconfigure(2, weight = 0, minsize = 135, pad = 0)




    def msg(self, m):
        if (reaChord_data.debug):
            Reaper.ShowConsoleMsg(str(m)+'\n')