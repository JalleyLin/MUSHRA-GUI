# import beyond
import beyond.File
import io, pickle



class State:

	def Apply(o, Target):

		d = {}
		
		for e, v in o.Elements.items():
			if v.__class__ is State and hasattr(Target, e): 
				v.Apply(getattr(Target, e))
			else:
				d[e] = v
		
		Target.StateSet(d)

def _Import(o):
	State.__module__ = "beyond"
	beyond.State = State


class Statable:

	def __reduce__(o):
		F = o.StateGet
		if hasattr(F, "Parallel"): e = F(WaitReturn = True)
		else: e = F()
		return State, (), {"ClassName": o.__class__.__name__, "Elements": e}

		
	def StateGet(o):
		return o.__dict__
		
	def StateSet(o, d):
		o.__dict__.update(d)
		
	def StateSave(o, Stream):
		if type(Stream) is File:
			Stream = open(Stream.Path, "wb")
			pickle.dump(o, Stream, pickle.HIGHEST_PROTOCOL)
			Stream.close()
		else:
			pickle.dump(o, Stream, pickle.HIGHEST_PROTOCOL)

	def StateLoad(o, Stream):
		if type(Stream) is File:
			Stream = open(Stream.Path, "rb")
			s = pickle.load(Stream)
			Stream.close()
		else:
			s = pickle.load(Stream)
		s.Apply(o)

beyond.Statable = Statable