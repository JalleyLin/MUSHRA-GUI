import beyond.Class
import weakref



class Element(Class):
	
	__PropertiesNative__ = "Containers", "_Include", "_Exclude", "Copy"

	def __Object__(c):
		o = c.Base()
		o.Containers = weakref.WeakKeyDictionary()
		
	def __hash__(o):
		return id(o)

	def _Include(o, e):
		# Say("Include:", id(e))
		o.Containers.setdefault(e, 0)
		o.Containers[e] += 1

	def _Exclude(o, e):
		# Say("Exclude:", id(e))
		o.Containers[e] -= 1
		if o.Containers[e] <= 0: del o.Containers[e]

	@Property
	def Container(o, p):
		if len(o.Containers) == 1:
			for e in o.Containers: p.Value = e
		elif len(o.Containers) == 0:
			raise Exception("No Containers")
		else:
			raise Exception("Multipe Containers")

	def Copy(o, Copies = {}):
		# Say("Copy:", o)
		Copy = o.__class__.__new__(o.__class__)
		Copies[o] = Copy
		Copy.Containers = weakref.WeakKeyDictionary()
		for Name, Value in o.__dict__.items():
			if isinstance(Value, Element):
				if Value in Copies: e = Copies[Value]
				else: e = Value.Copy(Copies)
				Copy.__dict__[Name] = e
				e._Include(Copy)
			elif Name != "Containers":
				Copy.__dict__[Name] = Value
		return Copy


	@Property
	def Name(o, p):
		p.Base()
		if p.Set:
			for e in o.Containers: e._ElementRenamed(o)
		elif not p.Exists:
			p.Value = ""
			p.Exists = True
	
	@Property
	def Index(o, p):
		p.Value = o.Container._List.index(o)		


	def __PropertiesDynamic__(o, p):
		Old = p.BaseGet()
		if p.Get:
			p.Exists = Old.Exists
			p.Value = Old.Value
		else:
			if isinstance(Old.Value, Element): Old.Value._Exclude(o)
			if p.Set and isinstance(p.Value, Element): p.Value._Include(o)
			p.Base()



	
class Elements(Element):
	
	__PropertiesNative__ = "_List", "_Dictionary", "_DictionaryReady", "Get", "Set", "Add", "Remove", "Clear", "Has", "_ElementRenamed"
	
	def __Object__(c):
		o = c.Base()
		o._List = []
		o._Dictionary = {}
		o._DictionaryReady = True


	def Copy(o, Copies = {}):
		# Say("C:", o)
		Copy = super().Copy(Copies)
		Copy._List = []
		for e in o._List:
			if e in Copies: e = Copies[e]
			else: e = e.Copy(Copies)
			Copy._List.append(e)
			e._Include(Copy)
		Copy._Dictionary = {}
		Copy._DictionaryReady = False
		return Copy


	def Get(o, Name):
		d = o._Dictionary
		if not o._DictionaryReady:
			d.clear()
			for e in o._List: d.setdefault(e.Name, e)
			o._DictionaryReady = True
		return d.get(Name, None)

	def Set(o, Name, e):
		e.Name = Name
		Old = o.Get(Name)
		if Old is None: o.Add(e)
		else:
			Old._Exclude(o)
			o._List[o._List.index(Old)] = e
			o._Dictionary[Name] = e
			e._Include(o)

	def Add(o, e, Index = None):
		if Index is None: o._List.append(e)
		else: o._List.insert(Index, e)
		o._DictionaryReady = False
		e._Include(o)
		return e

	def Remove(o, e):
		e._Exclude(o)
		o._List.__delitem__(o._List.index(e))
		o._DictionaryReady = False
		return e

	def Clear(o):
		for e in o._List: e._Exclude(o)
		del o._List[:]
		o._Dictionary.clear()
		o._DictionaryReady = True

	def Has(o, Name):
		return o.Get(Name) is not None

	def _ElementRenamed(o, e):
		o._DictionaryReady = False


	
	def __PropertiesDynamic__(o, p):
		Old = p.BaseGet()
		if Old.Exists:
			if p.Get: p.Value = Old.Value
			else: p.Base()
		else:
			e = Elements.Get(o, p.Name)
			if e is None:
				if p.Get: p.Exists = False
				else: p.Base()
			else:
				if p.Get:
					p.Value = e
				elif p.Set:
					e._Exclude(o)
					p.Value.Name = p.Name
					o._List[o._List.index(e)] = p.Value
					o._Dictionary[p.Name] = p.Value
					p.Value._Include(o)
				elif p.Delete:
					o.Remove(e)


	def __getitem__(o, Index):
		return o._List.__getitem__(Index)

	def __setitem__(o, Index, e):
		o._List[Index]._Exclude(o)
		o._List.__setitem__(Index, e)
		o._DictionaryReady = False
		e._Include(o)

	def __delitem__(o, Index):
		o._List[Index]._Exclude(o)
		o._List.__delitem__(Index)
		o._DictionaryReady = False

	def __len__(o):
		return o._List.__len__()

	def __iter__(o):
		return o._List.__iter__()

	def __reversed__(o):
		return o._List.__reversed__()


