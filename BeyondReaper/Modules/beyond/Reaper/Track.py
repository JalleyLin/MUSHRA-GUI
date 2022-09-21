import beyond.Reaper.Project
import beyond.Reaper.Effects
from beyond.Reaper.Elements import *




class Track(Proxy, beyond.Elements.Elements):


	def __Object__(c):
		o = c.Base()
		if c.New:
			o.Effects = Reaper.Effects()
			o.ExtraElements = Elements()
			o.ExtraElements.Name = "Extra"

			
	def Receive(o):
		with Reaper as r:
			r.StringLimit = 16 * 1024 ** 2
			s = r.GetTrackStateChunk(o.Address, "", r.StringLimit, False)[2]
		# Say("s:", s)
		o.Elements = Elements(s).TRACK
		o.ReceiveElements()


	def Send(o):
		
		o.Effects.HeaderElements.SHOW = 0
		
		for f in o.Effects:
			for e in f.Elements:
				if e.Name == "FLOAT": e.Name = "FLOATPOS"
		
		o.SendElements()
		s = o.Elements.Serial

		with Reaper as r:
			r.StringLimit = len(s)
			r.SetTrackStateChunk(o.Address, s, False)



	def ReceiveElements(o):
		o.Effects.Clear()
		if o.Elements.Has("FXCHAIN"):
			o.Effects.Elements = o.Elements.FXCHAIN
			o.Effects.ReceiveElements()
			try:
				s = o.Effects[0].Elements.COMMENT.Binary.decode("utf-8")
				e = Elements(s)
				if e.Has("Extra"): o.ExtraElements = e.Extra 
				else: o.ExtraElements.Set("Notes", s)			
			except: pass	

	
	def SendElements(o):
		if len(o.Effects) == 0 and o.Elements.Has("FXCHAIN"):
			del o.Elements.FXCHAIN
		else:
			if len(o.ExtraElements) > 1:
				o.Effects[0].Elements.Set("COMMENT", Elements()).Binary = o.ExtraElements.Serial.encode("utf-8")
			o.Elements.FXCHAIN = o.Effects.Elements
			o.Effects.SendElements()


	
	def ReceiveFile(o, File):
		# TimerStart("ReceiveFile")
		s = File.Binary.decode("utf-8")
		o.Elements = Elements(s).TRACK
		o.ReceiveElements()
		# TimerEnd()
		
	def SendFile(o, File):
		o.SendElements()
		s = o.Elements.Serial
		File.Binary = s.encode("utf-8")



			



	_InfoGet = Reaper.GetMediaTrackInfo_Value
	_InfoSet = Reaper.SetMediaTrackInfo_Value
	_InfoGetSetString = Reaper.GetSetMediaTrackInfo_String

	@Property
	def Selected(o, p): p.Value = o._GetSet("SEL", 0, "I_SELECTED", False, p.Set, p.Value)
	
	@Property
	def Name(o, p): p.Value = o._GetSet("NAME", 0, "P_NAME", "", p.Set, p.Value)

	@Property
	def FolderDelta(o, p): p.Value = o._GetSet("ISBUS", 1, "I_FOLDERDEPTH", 0, p.Set, p.Value)


Reaper.Track = Track




@Property
def Project_TracksSelected(o, p):
	with Reaper as r:
		
		t = o.TrackMaster
		if t.Selected: yield t

		for i in range(r.CountSelectedTracks(o.Address)):
			a = r.GetSelectedTrack(o.Address, i)
			yield Track(a)

Reaper.Project.TracksSelected = Project_TracksSelected


@Property
def Project_TrackMaster(o, p):
	p.Value = Track(Reaper.GetMasterTrack(o.Address))

Reaper.Project.TrackMaster = Project_TrackMaster


@Property
def Project_TracksAll(o, p):
	with Reaper as r:
	  for i in range(r.CountTracks(o.Address)):
	    a = r.GetTrack(o.Address, i)
	    yield Track(a)

Reaper.Project.TracksAll = Project_TracksAll


def Project_Receive(o):
  Target = o
  Target.Clear()
  for t in o.TracksAll:
    Target.Add(t)
    d = t.FolderDelta
    if d == 1:
    	Target = t
    	Target.Clear()
    elif d < 0:
      for c in range(-d): Target = Target.Container

def Project_Receive2(o):
  
  l = Reaper.Execute("""
ProjectAddress = l[1]
l = []
for i in range(RPR_CountTracks(ProjectAddress)):
  t = RPR_GetTrack(ProjectAddress, i)
  d = int(RPR_GetMediaTrackInfo_Value(t, "I_FOLDERDEPTH"))
  l.append((t, d))
  """, o.Address)

  Target = o
  Target.Clear() 
  for t, d in l:
    t = Track(t)
    Target.Add(t)
    if d == 1:
    	Target = t
    	Target.Clear()
    elif d < 0:
      for c in range(-d): Target = Target.Container

Reaper.Project.Receive = Project_Receive2