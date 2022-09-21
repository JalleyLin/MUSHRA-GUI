import beyond.Reaper
import beyond.Reaper.Item
import beyond.Screen


@ProgramStart
class Main(Parallel):

  def Start(o):

    with Reaper as r:

      for Item in r.ProjectSelected.ItemsSelected:

        T = Item.TakeActive

        Say(T.Name, T.Address)

        Say(r.RPR_MIDI_GetTextSysexEvt(T.Address, 0, 0, 0, 0, 0, 0, 0))      