import beyond
import sys


MainModule = sys.modules["__main__"]
RunningInside = hasattr(MainModule, "obj")



if RunningInside:


  SayOutputClear = False

  def SayOutput(Text):
    global SayOutputClear
    if not SayOutputClear:
      MainModule.RPR_ShowConsoleMsg("")
      SayOutputClear = True
    MainModule.RPR_ShowConsoleMsg(Text)

  beyond.Text.SayOutputs.append(SayOutput)



  ModuleClass = type(beyond)
  Omnipresent.ReaperImportOriginal = Omnipresent.__import__
  def Import(name, globals = None, locals = None, fromlist = (), level = 0):
    if name.startswith("beyond"):
      return ModuleClass(name)
    else:
      return ReaperImportOriginal(name, globals, locals, fromlist, level)
  Omnipresent.__import__ = Import

  @Omnipresent
  def ProgramStart(E):

    Omnipresent.__import__ = ReaperImportOriginal
    import os.path, subprocess, beyond.Reaper.Settings
  
    p = sys.path[0]
    p = os.path.normpath(p)
    f = MainModule.obj.co_filename
    f = os.path.join(p, f)

    if not os.path.isfile(Settings.Python):
      Say("Cannot find Python:", Settings.Python)

    if not os.path.isfile(f):
      Say("Cannot find Program:", f)

    subprocess.Popen([Settings.Python, f])

  Omnipresent.ProgramStartDirect = ProgramStart
  Omnipresent.Parallel = object
  Omnipresent.Screen = object
  Omnipresent.Reaper = sys.modules["beyond.Reaper"]


else:


  import socket, struct

  def OSCMessage(*l):
    Data = b""
    for e in l:
      t = type(e)
      if t is bytes:
        d = e
        d += b"\0" * (4 - len(d) % 4)
      elif t is str:
        d = e.encode("utf-8")
        d += b"\0" * (4 - len(d) % 4)
      elif t is int:
        d = struct.pack(">i", e)
      elif t is float:
        d = struct.pack(">f", e)
      Data += d
    # Say("Data:", Data)
    return Data

  def OSCSendAction(Address, Action):
    if type(Action) is int:
      Data = OSCMessage("/action", ",i", Action)
    else:
      Data = OSCMessage("/action/str", ",s", Action)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(Data, Address)
    s.close()

  
  import beyond.Class
  import beyond.Network
  import beyond.Reaper.Settings

  class Reaper(Class):

    __PropertiesNative__ = "Depth", "Server", "Execute", "OnConnectExecute", "OnDisconnectHandlers", "RunningInside"

    def __Object__(c):
      o = c.Base()
      o.RunningInside = False
      o.Depth = 0
      o.OnConnectExecute = None
      o.OnDisconnectHandlers = set()
      o.StringLimit = 4 * 1024 ** 2

    def __enter__(o):
      if o.Depth == 0:
        # Say("REAPER Start:")
        try:
          OSCSendAction(Settings.Reaper_OSC_Address, Settings.Reaper_RemoteControl_CommandID)
          o.Server = beyond.Network.ServerSingle(Settings.External_Program_Address)
        except Exception as E:
          Say()
          Say("Cannot Connect to Reaper:") 
          Say("Is Reaper running and /Modules/beyond/Reaper/Settings.py correct?:")
          Say("  Reaper_RemoteControl_CommandID:", Settings.Reaper_RemoteControl_CommandID)
          Say("  Reaper_OSC_Address:", Settings.Reaper_OSC_Address)
          Say()
          raise E
      o.Depth += 1
      if o.OnConnectExecute is not None:
        try: o.Execute(o.OnConnectExecute)
        except: pass
      return o

    def __exit__(o, ExceptionType, Exception, Traceback):
      o.Depth -= 1
      if o.Depth == 0 or Exception is not None:
        # Say("REAPER End:")

        o.Depth = 1
        for h in o.OnDisconnectHandlers:
          try: h._ReaperDisconnect()
          except: pass
        o.Depth = 0

        try:
          o.Server.Send(('Active = False',))
        except: pass
        o.Server.End()

    def Execute(o, *l):
      if o.Depth == 0:
        with o:
          o.Server.Send(l)
          r = o.Server.Receive()
      else:
        o.Server.Send(l)
        r = o.Server.Receive()
      if isinstance(r, Exception):
        Say("\nFrom Reaper:", r)
        raise Exception("Reaper Exception: " + str(r))
      return r

    def __PropertiesDynamic__(o, p):
      p.Base()
      if p.Get and not p.Exists:
        Prefix, n = beyond.Text.SplitStart(p.Name, "_")
        if Prefix.isupper(): n = p.Name
        else: n = "RPR_" + p.Name
        c = 'l = ' + n + '(*l[1:])'
        p.Value = lambda *l: o.Execute(c, *l)
        p.Exists = True

    @Property
    def StringLimit(o, p):
      p.Base()
      if p.Set and p.Value > 4 * 1024 ** 2:
        # Say("StringLimit Set:", p.Value)
        o.Execute('sys.modules["reaper_python"].rpr_packs = lambda v: create_string_buffer(str(v).encode(), ' + str(p.Value) + ')')
        

  Omnipresent.Reaper = Reaper()



  # import weakref
  Proxies = {}#weakref.WeakValueDictionary()

  class Proxy(Class):

    __PropertiesNative__ = "Address"

    def __Object__(c, Address = None):
      if Address is not None:
        c.Object = Proxies.get(Address, None)
        c.New = False
      if c.Object is None:
        o = c.Base()
        o.Address = Address
        Proxies[Address] = o
        c.New = True