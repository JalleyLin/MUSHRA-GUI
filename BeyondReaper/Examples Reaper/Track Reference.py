import beyond.Reaper
import beyond.Reaper.Track
import beyond.Screen


@ProgramStart
class Main(Parallel):

  def Start(o):

    with Reaper as r:

      Project = r.ProjectSelected

      Project.UndoEvent("Track Reference Example")

      Project.Receive() # Quickly Receive the Track Hierarchy

      for t in Project:
        Say(":", t.Name)
        for t in t:
          Say("  :", t.Name, t.Index)

      # Say("Track by Name Path:", Project.Drums.Overhead.Selected) # Put in the Names from your Project
      # Say("by Any Name Path:", Project.Drums.Get("Overhead Left").Selected)

      Say()
      Say("Master Track Selected?:", Project.TrackMaster.Selected)

      Say()
      Say("Flip the Selection of all Tracks:")
      for t in Project.TracksAll:
        Say(t.Name, t.Address)
        t.Selected = not t.Selected

      # Project.TracksAll is a fast Python Generator, great for breakable iterations, searches, etc..
      # Here is how to convert it into a regular list
      l = list(Project.TracksAll)
      Say("Track Count:", len(l))

      Say()
      if len(Project) >= 1:

        t = Project[0]
        Say("First Track in Hierarchy:", t.Name)
        if len(t) >= 2: Say("Second Child:", t[1].Name)
        
        Say()
        a = r.GetTrack(Project.Address, 0) # Directly From Reaper API
        t = r.Track(a) # Make it into a beyond.Reaper Track
        t.Receive()
        t2 = r.Track(a) # This will recall the previously created Track with the same Address!
        # t2.Receive() # Not needed, t2 is t :-)
        Say("Tracks Created with the Same Address are the Same Objects:", t2 is t)
        Say("t2:", t2.Elements)