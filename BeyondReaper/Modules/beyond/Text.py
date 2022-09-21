import sys, io, time



class Stream(io.StringIO):

  def __iadd__(o, t):
    o.write(t)
    return o
  
  def Complete(o):
    t = o.getvalue()
    o.close()
    return t


    



SayOutputs = []


def SayFormat(*l):
  
  s = Stream()

  Seperator = ""
  
  for e in l: 
    
    s += Seperator
    
    c = e.__class__
    if c is str:
      if e.endswith(":"):
        s += e
        Seperator = " "
      else:
        s += '"'
        s += e
        s += '"'
        Seperator = ", "
    
    elif c is int or c is float or c is bool:
      s += str(e)
      Seperator = ", "
    
    elif hasattr(e, "Say") and e.Say != Say:
      Seperator = e.Say(s)
    
    elif isinstance(e, Exception):
      s += "\n== Exception ===========\n"
      t = getattr(e, "Traceback", None)
      if t is None:
        import traceback
        t = traceback.extract_tb(e.__traceback__)
      for File, LineNumber, Name, Line in t:
        s += '\nFile "'
        s += File
        s += '", line '
        s += str(LineNumber)
        s += ', in '
        s += Name
        s += '\n '
        s += str(Line)
        s += '\n'
      s += '\n'
      s += str(e)
      s += '\n'
        # Say('File "' + File + '", line ' + str(LineNumber) + ':')
        # Say(Name + '():', Line)
      s += "\n========================\n"
      Seperator = "\n"

    else:
      s += str(e)
      s += " ("
      s += c.__name__
      s += ")"
      Seperator = ", "
    
  s += "\n"
  
  return s.Complete()

  

@Omnipresent  
def Say_(*l):
  if sys.stdout is not None:
    sys.stdout.write(SayFormat(*l))
    sys.stdout.flush()


@Omnipresent  
def Say(*l):
  t = SayFormat(*l)
  if sys.stdout is not None:
    sys.stdout.write(t)
    sys.stdout.flush()
  for Output in SayOutputs: Output(t)


@Omnipresent  
def Saydir(o):
  for e in dir(o):
    Say(e + ":", getattr(o, e))




def ToNumber(t):
  try:
    if "." in t: return float(t)
    else: return int(t)
  except: return t
  

def SplitStart(t, Seperator):
  t = t.partition(Seperator)
  if t[1] == "" and t[2] == "": return "", t
  else: return t[0], t[2]

def SplitEnd(t, Seperator):
  t = t.rpartition(Seperator)
  if t[0] == "" and t[1] == "": return t[2], ""
  else: return t[0], t[2]

def Join(Start, Seperator, End):
  return Start if End == "" else Start + Seperator + End



@Omnipresent
def TimerStart(Name):
  global TimerStart_, TimerName
  TimerStart_ = time.clock()
  TimerName = Name

@Omnipresent  
def TimerEnd():
  Say(TimerName + ":", round(time.clock() - TimerStart_, 4))