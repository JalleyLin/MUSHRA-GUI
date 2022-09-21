import beyond.Reaper
import beyond.Reaper.Track
import beyond.Screen


@ProgramStart
class Main(Parallel):

	def Start(o):

		with Reaper as r:

			Project = r.ProjectSelected

			Project.UndoEvent("Modify Selected Tracks Example")

			for Track in Project.TracksSelected:

				Say("Selected Track:", Track.Name)
				Say()

				Track.Receive()

				Say("Pythonized Track Elements:", Track.Elements)
				Say()

				Track.Elements.VOLPAN[0] *= .9
				Track.Elements.VOLPAN[1] += .1

				Say("Effects:")
				for e in Track.Effects:
					Say(e.Name, "Active:", e.Active, "Online:", e.Online)
					e.Active = not e.Active

				Track.Name +=	"!"

				Track.Send()