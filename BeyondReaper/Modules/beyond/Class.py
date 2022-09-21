import beyond
import types



class MetaClass(type):

  def __new__(Class, Name , Bases, Dictionary):
    # Say(Name, Bases)

    if "__PropertiesDynamic__" in Dictionary:
      Found = False
      for c in Bases: 
        if hasattr(c, "__PropertiesDynamic__"): 
          Found = True
          break
      if not Found:
        Bases = list(Bases)
        Bases.insert(0, PropertiesDynamic)
        Bases = tuple(Bases)

    p = _PropertiesNativeGet(Dictionary)
    for c in Bases: p |= _PropertiesNativeGet(c.__dict__)
    if len(p) > 0: Dictionary["__PropertiesNative__"] = p

    Class = super().__new__(Class, Name, Bases, Dictionary)
    return Class


  def __call__(Class, *l, **d):
    c = ObjectConstructor()
    c.Object = None
    c.ClassChain = Class.mro()
    c.ClassIndex = 0
    c.ParameterList = l
    c.ParameterDictionary = d
    return c.Base()



def _PropertiesNativeGet(d):
  p = d.get("__PropertiesNative__", None)
  if p is None: p = ()
  elif type(p) is str: p = (p,)
  p = set(p)
  return p



class ObjectConstructor():

  def BaseFirst(c):
    Class = c.ClassChain[0]
    i = Class.__init__
    if i is object.__init__ or i.__code__.co_argcount == 1:
      c.Object = type.__call__(Class)
    else:
      c.Object = type.__call__(Class, *c.ParameterList, **c.ParameterDictionary)
    return c.Object

  def Base(c):
    while c.ClassIndex <= len(c.ClassChain):
      Class = c.ClassChain[c.ClassIndex]
      c.ClassIndex += 1
      e = Class.__dict__.get("__Object__", None)
      if e is not None:
        # Say("__Object__:", Class.__name__, Class.__module__)
        if e.__code__.co_argcount == 1:
          e(c)
        else:
          e(c, *c.ParameterList, **c.ParameterDictionary)
        return c.Object


@Omnipresent
class Class(metaclass = MetaClass):
  def __Object__(c):
    c.BaseFirst()



@Omnipresent
class Property(property):
  
  def __init__(o, Function):

    o.Function = Function

    def Get(o):
      p = PropertyAccess()
      p.Object = o
      p.ClassChain = type(o).mro()
      p.ClassIndex = 0
      p.ClassSearch = True
      p.Name = Function.__name__
      p.Get = True
      p.Set = False
      p.Delete = False
      p.Exists = True
      p.Value = None
      p.Base()
      if not p.Exists: raise AttributeError(str(p) + ": Does not exist")
      return p.Value
    
    def Set(o, Value):
      p = PropertyAccess()
      p.Object = o
      p.ClassChain = type(o).mro()
      p.ClassIndex = 0
      p.ClassSearch = True
      p.Name = Function.__name__
      p.Get = False
      p.Set = True
      p.Delete = False
      p.Exists = True
      p.Value = Value
      p.Base()
      if not p.Exists: raise AttributeError(str(p) + ": Does not exist")
      return Value

    def Delete(o):
      p = PropertyAccess()
      p.Object = o
      p.ClassChain = type(o).mro()
      p.ClassIndex = 0
      p.ClassSearch = True
      p.Name = Function.__name__
      p.Get = False
      p.Set = False
      p.Delete = True
      p.Exists = True
      p.Value = None
      p.Base()
      if not p.Exists: raise AttributeError(str(p) + ": Does not exist")

    super().__init__(Get, Set, Delete)



class PropertiesDynamic():

  __PropertiesNative__ = set()

  def __getattribute__(o, Name):
    c = type(o)
    if Name.startswith("__") or Name in c.__PropertiesNative__: return super().__getattribute__(Name)
    else:
      p = PropertyAccess()
      p.Object = o
      p.ClassChain = c.mro()
      p.ClassIndex = 0
      p.ClassSearch = True
      p.Name = Name
      p.Get = True
      p.Set = False
      p.Delete = False
      p.Exists = True
      p.Value = None
      p.Base()
      if not p.Exists: raise AttributeError(str(p) + ": Does not exist")
      return p.Value

  def __setattr__(o, Name, Value):
    c = type(o)
    if Name.startswith("__") or Name in c.__PropertiesNative__: super().__setattr__(Name, Value)
    else:
      p = PropertyAccess()
      p.Object = o
      p.ClassChain = c.mro()
      p.ClassIndex = 0
      p.ClassSearch = True
      p.Name = Name
      p.Get = False
      p.Set = True
      p.Delete = False
      p.Exists = True
      p.Value = Value
      p.Base()
      if not p.Exists: raise AttributeError(str(p) + ": Does not exist")

  def __delattr__(o, Name):
    c = type(o)
    if Name.startswith("__") or Name in c.__PropertiesNative__: super().__delattr__(Name)
    else:
      p = PropertyAccess()
      p.Object = o
      p.ClassChain = c.mro()
      p.ClassIndex = 0
      p.ClassSearch = True
      p.Name = Name
      p.Get = False
      p.Set = False
      p.Delete = True
      p.Exists = True
      p.Value = None
      p.Base()
      if not p.Exists: raise AttributeError(str(p) + ": Does not exist")



class PropertyAccess:

  def BaseFirst(p):
    try:
      if p.Get: p.Value = p.Object.__dict__[p.Name]
      elif p.Set: p.Object.__dict__[p.Name] = p.Value
      elif p.Delete: del p.Object.__dict__[p.Name]
      p.Exists = True
    except KeyError:
      p.Exists = False  


  def Base(p):

    while p.ClassIndex <= len(p.ClassChain):

      if p.ClassIndex == len(p.ClassChain): p.BaseFirst()
      else:

        c = p.ClassChain[p.ClassIndex]

        if p.ClassSearch:
          e = c.__dict__.get(p.Name, None)
          if e is not None:
            p.ClassSearch = False
            if type(e) is Property:
              # Say(c.__name__ + " Property:")
              R = e.Function(p.Object, p)
              if type(R) is types.GeneratorType: p.Value = R
            elif type(e) is types.FunctionType:
              p.Value = types.MethodType(e, p.Object)
            else:
              p.Value = e
            break

        e = c.__dict__.get("__PropertiesDynamic__", None)
        if e is not None:
          p.ClassIndex += 1
          p.ClassSearch = True
          # Say(c.__name__ + " PropertiesDynamic:")
          R = e(p.Object, p)
          if type(R) is types.GeneratorType: p.Value = R
          break

      p.ClassIndex += 1
      p.ClassSearch = True


  def BaseGet(p, Name = None):
    p2 = PropertyAccess()
    p2.Object = p.Object
    p2.ClassChain = p.ClassChain
    p2.ClassIndex = p.ClassIndex
    p2.ClassSearch = p.ClassSearch
    p2.Name = p.Name if Name is None else Name
    p2.Get = True
    p2.Set = False
    p2.Delete = False
    p2.Exists = True
    p2.Value = None
    p2.Base()
    return p2


  def SameAs(p, Name):
    p.Name = Name
    getattr(type(p.Object), Name).Function(p.Object, p)


  def __str__(p):
    s = "Property "
    if p.Get: s += "Get"
    elif p.Set: s += "Set"
    elif p.Delete: s += "Delete"
    s += ' "' + p.Name + '"'
    return s