import beyond.Reaper
import beyond.Reaper.Track
import beyond.Screen


@ProgramStart
class Main(Parallel):

  def Start(o):

    with Reaper as r:

      Project = r.ProjectSelected

      Project.UndoEvent("Modify Effect Envelopes Example")

      for Track in Project.TracksSelected:

        Say("Selected Track:", Track.Name)
        Say()

        Track.Receive()

        for Effect in Track.Effects:

          Say("Effect Name:", Effect.Name)
          Say("Plugin:", Effect.Plugin)
          Say()

          for e in Effect.Elements:
            if e.Name == "PARMENV":
            
              Say("Parameter Number:", e.PARMENV[0])
              Say("Armed:", e.ARM)
              Say("Lane Height:", e.LANEHEIGHT[0])
              Say("Visible:", e.VIS[0])
              Say("All Elements:", e)

              Say("Shifting Envelope Points (PT):")
              for e in e:
                if e.Name == "PT":
                  Say("Time:", e[0], "Value:", e[1])
                  e[0] += 10

              Say()

          Say()


        Track.Send()