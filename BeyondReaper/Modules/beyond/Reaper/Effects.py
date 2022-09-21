from beyond.Reaper.Elements import *


class Effects(beyond.Elements.Elements):
	
	def __Object__(c):
		o = c.Base()
		o.HeaderElements = Elements()
		o.Elements = Elements()


	def ReceiveElements(o):
		
		o.Clear()
		o.HeaderElements.Clear()

		Target = o.HeaderElements
		for e in o.Elements:

			if e.Name == "BYPASS":
				f = o.Add(Effect())
				Target = f.Elements
			Target.Add(e)

		for e in o:
			e.ReceiveElements()
	
	
	def SendElements(o):

		o.Elements.Clear()
	
		if len(o) > 0:
			
			for e in o.HeaderElements: o.Elements.Add(e)

			for f in o:
				f.SendElements()
				for e in f.Elements: o.Elements.Add(e)

		
Reaper.Effects = Effects



		
class Effect(beyond.Elements.Element):
	
	def __Object__(c):
		o = c.Base()
		o.Elements = Elements()
		o.Parameters = Parameters()
		o.PluginType = ""
		o.Plugin = ""


	def ReceiveElements(o):

		for e in o.Elements:
			if e.__class__ is Elements: 
				o.PluginType = e.Name
				break

		o.Plugin = o.PluginElements[0][0]
		
		e = o.Elements
		o.Active = True if e.BYPASS[0] == 0 else False
		o.Online = True if e.BYPASS[1] == 0 else False
		
		if o.PluginType == "VST":
			o.Name = o.PluginElements[0][3]
		elif o.PluginType == "JS":
			o.Name = o.PluginElements[0][1]
			o.Parameters.Clear()
			for e in o.Elements.JS[1]:
				if type(e) == float:
					p = o.Parameters.Add(Parameter())
					p.Value = e

	
	def SendElements(o):
		
		o.PluginElements[0][0] = o.Plugin
		
		e = o.Elements
		e.BYPASS[0] = 0 if o.Active else 1
		e.BYPASS[1] = 0 if o.Online else 1

		if o.PluginType == "VST":
			o.PluginElements[0][3] = o.Name	
		if o.PluginType == "JS":
			o.PluginElements[0][1] = o.Name	
			e = o.Elements.JS[1]
			i = 0
			for p in o.Parameters:
				e[i] = p.Value
				i += 1

		if not o.Elements.Has("COMMENT"): o.Elements.Set("COMMENT", Elements())	


	
	@Property
	def PluginElements(o, p):
		p.Value = o.Elements.Get(o.PluginType)


		


class Parameters(beyond.Elements.Elements):
		
		
	def Receive(o, Names = False):
		
		TrackAddress = o.Container.Container.Container.Address
		EffectIndex = o.Container.Index
		
		o.Clear()

		l = Reaper.Execute("""
			
TrackAddress, EffectIndex, Names = l[1:]
n = ""
l = []

for p in range(RPR_TrackFX_GetNumParams(TrackAddress, EffectIndex) - 2):
	if Names: n = RPR_TrackFX_GetParamName(TrackAddress, EffectIndex, p, "", 128)[4]
	r = RPR_TrackFX_GetParamEx(TrackAddress, EffectIndex, p, 0, 0, 0)
	l.append((n, r[0], r[4], r[5], r[6]))
	
""", TrackAddress, EffectIndex, Names)
				
		for e in l:
			p = Parameter()
			p.Name, p.Value, p.Minimum, p.Maximum, p.Default = e
			o.Add(p)

	
		
	def Send(o):
		
		TrackAddress = o.Container.Container.Container.Address
		EffectIndex = o.Container.Index
		
		Values = []
		for p in o: Values.append(p.Value)

		Reaper.Execute("""
		
TrackAddress, EffectIndex, Values = l[1:]
i = 0

for v in Values: 
	RPR_TrackFX_SetParam(TrackAddress, EffectIndex, i, v)
	i += 1

l = []

""", TrackAddress, EffectIndex, Values)
	
	
		
class Parameter(beyond.Elements.Element):
	pass
