import beyond.Reaper
import beyond.File
import beyond.Elements


class Project(beyond.Reaper.Proxy, beyond.Elements.Elements):
	
	def __Object__(c):
		o = c.Base()
		if c.New:
			Reaper.OnDisconnectHandlers.add(o)
			o._UndoEventName = ""

	def UndoEvent(o, Name):
		if o._UndoEventName == "":
			o._UndoEventName = Name
			Reaper.Undo_BeginBlock2(o.Address)

	def _ReaperDisconnect(o):
		if o._UndoEventName != "":
			Reaper.Undo_EndBlock2(o.Address, o._UndoEventName, -1)
			o._UndoEventName = ""

Reaper.Project = Project



@Property
def ProjectSelected(o, p):
	a, _, f, _ = Reaper.EnumProjects(-1, "", 512)
	p.Value = Project(a)
	p.Value.File = File(f)

type(Reaper).ProjectSelected = ProjectSelected