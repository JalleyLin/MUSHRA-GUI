import beyond.Elements
import base64, io



class Element(beyond.Elements.Element):
	
	__PropertiesNative__ = "Name", "_ValuesSerialized", "_Serialize", "_Deserialize", "_List"

	def __Object__(c, Name, ValuesSerial):
		o = c.Base()
		o.Name = Name
		o.ValuesSerial = ValuesSerial

		
	def _Serialize(o, s, Full = True):

		Previous = False

		if Full and o.Name != "":
			s += o.Name
			Previous = True
							
		if o._ValuesSerialized:
			if Previous: s += " "
			s += o.ValuesSerial

		else:

			ValuesStart = s.tell() + (1 if Previous else 0)

			for e in o._List:

				if Previous: s += " "
				
				c = type(e)
				
				if c is int:
					s += str(e)
				
				elif c is float:
					s += str(e)
				
				elif c is ID:
					s += "{"
					s += str(e)
					s += "}"

				elif c is str:
					
					q = 0
					
					for c in e:
						if c == '"': q |= 1
						elif c == "'" : q |= 2
						elif c == "`" : q |= 4
						if q == 7: break
							
					if q & 1 == 0: q = '"'
					elif q & 2 == 0: q = "'"
					elif q & 4 == 0: q = "`"
					else:
						q = "`"
						e = e.replace(q, "'")
						
					s += q
					s += e
					s += q
				
				elif c is bool:
					s += str(int(e))

				elif c is Word:
					s += str(e)

				else:
					s += "-"

				Previous = True

			End = s.tell()
			s.seek(ValuesStart)
			o.ValuesSerial = s.read()
			s.seek(End)

		if Full:
			s += "\r\n"


	def _Deserialize(o):

		o._List = []

		ValuesSerial = o.ValuesSerial
		Start = i = 0
		EndQuote = ""
		
		def Add():
			e = ValuesSerial[Start:i]
			if EndQuote == "}": o._List.append(ID(e))
			elif EndQuote != "": o._List.append(e)
			elif Start < i:
				e = beyond.Text.ToNumber(e)
				if type(e) is str: o._List.append(Word(e))
				else: o._List.append(e)
			return i + 1
				
		for c in ValuesSerial:
			if EndQuote == "":
				if c in "\"'`":
					EndQuote = c
					Start = i + 1
				elif c == "{":
					EndQuote = "}"
					Start = i + 1					
				elif c in " \r\t":
					if Start < i: Start = Add()
					else: Start = i + 1	
			elif c == EndQuote:
				Start = Add()
				EndQuote = ""
			i += 1
		Add()

		o._ValuesSerialized = False

	
	@Property
	def ValuesSerial(o, p):
		if p.Get:
			if o._ValuesSerialized:
				p.Base()
			else:
				s = beyond.Text.Stream()
				o._Serialize(s, False)
				p.Value = s.Complete()
		elif p.Set:
			o._ValuesSerialized = True
			p.Base()


	def __getitem__(o, Index):
		if o._ValuesSerialized: o._Deserialize()
		return o._List.__getitem__(Index)

	def __setitem__(o, Index, Value):
		if o._ValuesSerialized: o._Deserialize()
		if Index >= len(o):
			for i in range(Index - len(o) + 1): o._List.append(None)
		o._List.__setitem__(Index, Value)

	def __delitem__(o, Index):
		if o._ValuesSerialized: o._Deserialize()
		o._List.__delitem__(Index)

	def __len__(o):
		if o._ValuesSerialized: o._Deserialize()
		return o._List.__len__()

	def __iter__(o):
		if o._ValuesSerialized: o._Deserialize()
		return o._List.__iter__()

	def __reversed__(o):
		if o._ValuesSerialized: o._Deserialize()
		return o._List.__reversed__()



class ID(str):
	pass

class Word(str):
	pass	

WordBlank = Word()




class Elements(beyond.Elements.Elements):
	
	__PropertiesNative__ = "Binary", "BinaryBase64", "_Serialize", "_Deserialize"
	
	def __Object__(c, Serial = None):
		o = c.Base()
		if Serial is None: o.Binary = None	
		else: o.Serial = Serial
		o.BinaryBase64 = True

		
	def _Serialize(o, s):
		s += "<"
		for e in o: e._Serialize(s)
		if o.Binary is not None: 
			if o.BinaryBase64:
				s += base64.encodebytes(o.Binary).decode("utf-8")
			else:
				for l in o.Binary.decode("utf-8").split("\n"):
					s += "|" + l + "\n"
		s += ">\r\n"
	
	
	def _Deserialize(o, Text, Start = 0):

		o.Clear()
		o.Binary = None
		
		i = SpaceStart = Start

		List, Name, Data = range(3)
		State = List
		EndQuote = ""
	
		def Add():
			if State == Name or State == Data:

				if Start < SpaceStart:
					n = Text[Start:SpaceStart]
					d = Text[SpaceStart + 1:i].rstrip()
				else:
					n = Text[Start:i]
					d = ""

				if n[0] in "0123456789.-":
					o.Add(Element("", Text[Start:i]))
					return List
				else:
					o.Add(Element(n, d))
					return List

			else: return State


		while i < len(Text):
		
			c = Text[i]
			
			if c in " \r\t\n\"'`<>":

				if c in "\"'`":
					if EndQuote == "":
						EndQuote = c
					elif c == EndQuote:
						EndQuote = ""

				elif EndQuote != "":
					pass
			
				elif c in " \r\t":
					if State == Name:
						SpaceStart = i
						State = Data

				elif c in "\n":
					State = Add()
					
					if len(o) == 1:
						l = Text[i + 1: Text.find("\n", i + 1)]
						if len(l) > 1:
							# Say("bc:", l)
							if l[0] == "|":
								o.BinaryBase64 = False
								s = io.StringIO()
								i += 1
								Start = i
								while Text[Start] == "|":
									Start += 1
									i = Text.find("\n", Start) + 1
									s.write(Text[Start:i])
									# Say("   ___:", i, Text[Start:i])
									Start = i
								o.Binary = s.getvalue().encode("utf-8")
								s.close()
								# Say("  BN:", i, o.Binary)
								i -= 1
								# i = Text.find(">", i)
								# Say(Text[i], i)
								# break

							elif l[-1] == "=" or l.strip().find(" ") == -1:
								# Say("  BB:", o.Name, Text[i+1:i+10])
								o.BinaryBase64 = True
								Start = i + 1
								i = Text.find(">", Start)
								d = Text[Start:i]
								d = d.encode("utf-8")
								# d = d.rstrip()
								# l = len(d)
								# f = d.rfind(b"==", 0, l - 1 if d.endswith(b"==") else l + 1)
								if True: #f != -1 and l - f > 2:
									# Say("By lines:")
									b = io.BytesIO() 
									for l in d.split(b"\n"):
										b.write(base64.decodebytes(l))
									o.Binary = b.getvalue()
									b.close()
								# else:
									# o.Binary = base64.decodebytes(d)
								break
					
				elif c in "<":
					State = Add()
					e = Elements()
					i = e._Deserialize(Text, i + 1)
					o.Add(e)
						
				elif c in ">":
					Add()
					break

			elif State == Name or EndQuote != "":
				pass
			elif State == List:
				State = Name
				Start = i
					
			i += 1
		
		return i


	@Property
	def Serial(o, p):
		if p.Get:
			s = beyond.Text.Stream()
			o._Serialize(s)
			p.Value = s.Complete()
		elif p.Set:
			o._Deserialize(p.Value)


	def __PropertiesDynamic__(o, p):
		Old = p.BaseGet()
		e = Old.Value if isinstance(Old.Value, beyond.Elements.Element) else None
		if Old.Exists and e is None:
			if p.Get: p.Value = Old.Value
			else: p.Base()
		else:
			if p.Get:
				if e is None: p.Exists = False
				elif isinstance(e, Elements): p.Value = e
				elif len(e) == 1: p.Value = e[0]
				elif len(e) == 0: p.Value = WordBlank
				else: p.Value = e
			elif p.Set:
				if isinstance(p.Value, beyond.Elements.Element): 
					if e is None:
						p.Value.Name = p.Name
						o.Add(p.Value)
					else:
						p.Base()
				else:
					if e is None: e = o.Add(Element(p.Name, ""))
					e[0] = p.Value
			elif p.Delete:
				p.Base()



	def Set(o, Name, Value, Index = 0):
		if isinstance(Value, beyond.Elements.Element):
			super().Set(Name, Value)
		else:
			e = super().Get(Name)
			if e is None: e = o.Add(Element(Name, ""))
			e[Index] = Value
		return Value



	@Property
	def Name(o, p):
		p.Base()
		if len(o) == 0:
			if p.Get: p.Value = ""
			elif p.Set: o.Add(Element(p.Value, ""))
		else:
			if p.Get: p.Value = o[0].Name
			elif p.Set: o[0].Name = p.Value
			
	
	
	def ReceiveFile(o, File):
		# TimerStart("ReceiveFile")
		o.Serial = File.Binary.decode("utf-8")
		# TimerEnd()
		return o


	def SendFile(o, File):
		File.Binary = o.Serial.encode("utf-8")
		return o



	def Say(o, s):
			
		s += "(Elements)"

		Seperator = "\n  "

		for e in o:
			if type(e) is Element:
				s += Seperator
				s += e.Name
				s += ": "
				s += e.ValuesSerial
			elif type(e) is Elements:
				s += Seperator
				s += "<"
				s += e.Name
				s += ">..."
				s += str(len(e))
		
		if o.Binary is not None:
			s += Seperator
			s += "+ Binary: "
			s += str(len(o.Binary))
	
		return "\n"

		


class Proxy(beyond.Reaper.Proxy):

	__PropertiesNative__ = "_InfoGet", "_InfoSet", "_InfoGetSetString", "_GetSet"

	def __Object__(c):
		o = c.Base()
		if c.New:
			o.Elements = beyond.Reaper.Elements.Elements()
			o.Connected = True

	@Property
	def Connected(o, p):
		p.Base()
		if p.Get: p.Value = p.Value and o.Address is not None

	def _GetSet(o, ElementName, ElementIndex, InfoName, DefaultValue, Set, SetValue):
		if Set:
			if ElementName is not None: o.Elements.Set(ElementName, SetValue, ElementIndex)
			if InfoName is not None and o.Connected:
				if InfoName[0] == "P": type(o)._InfoGetSetString(o.Address, InfoName, str(SetValue), True)
				else: type(o)._InfoSet(o.Address, InfoName, SetValue)
		else:
			if InfoName is not None and o.Connected:
				if InfoName[0] == "P": Value = type(o)._InfoGetSetString(o.Address, InfoName, "", False)[3]
				else: Value = type(o)._InfoGet(o.Address, InfoName)
				Value = type(DefaultValue)(Value)
				if ElementName is not None: o.Elements.Set(ElementName, Value, ElementIndex)
				return Value
			elif ElementName is not None and o.Elements.Has(ElementName):
				return type(DefaultValue)(o.Elements.Get(ElementName)[ElementIndex])
			else:
				return DefaultValue

