import beyond.Reaper
import beyond.Reaper.Item
import beyond.Screen


@ProgramStart
class Main(Parallel):

  def Start(o):

    with Reaper as r:

      Project = r.ProjectSelected

      Project.UndoEvent("Modify Selected Items MIDI Example")

      for Item in Project.ItemsSelected:

        Item.Receive()

        Take = Item.TakeActive
        Say("Item Take:", Take.Name)

        if Take.Elements.Has("SOURCE"):
        
          Say("Take Elements SOURCE:", Take.Elements.SOURCE)
          Say()

          Say("Modifying MIDI Elements in SOURCE:")

          for e in Take.Elements.SOURCE:
            if e.Name == "e" or e.Name == "E":

              TimeDelta = e[0]
              b1 = int(str(e[1]), 16)
              b2 = int(str(e[2]), 16)
              b3 = int(str(e[3]), 16)
              Flags = e[4] if len(e) == 5 else 0

              Say("Time Delta:", TimeDelta, "Bytes:", b1, b2, b3, "Flags:", Flags)

              if b1 == 0x90 or b1 == 0x80: # Note Channel 1 ?
                b2 += 1 # Transpose
                if b2 > 127: b2 == 127

              e[0] = TimeDelta
              e[1] = beyond.Reaper.Elements.Word("%0.2X" % b1)
              e[2] = beyond.Reaper.Elements.Word("%0.2X" % b2)
              e[3] = beyond.Reaper.Elements.Word("%0.2X" % b3)
              e[4] = Flags
              if Flags == 0: del e[4]

        Item.Send()