import beyond.Reaper.Project
import beyond.Reaper.Effects
from beyond.Reaper.Elements import *


class Item(Proxy, beyond.Elements.Elements):
  
  def __Object__(c):
    o = c.Base()
    if c.New:
      o.HeaderElements = Elements()
      o.ExtraElements = Elements()
      o.ExtraElements.Name = "Extra"

  def Clear(o):
    super().Clear()
    o.HeaderElements.Clear()
    o.Elements.Clear()


  def Receive(o):
    with Reaper as r:
      s = r.GetItemStateChunk(o.Address, "", r.StringLimit, False)[2]
    # Say(s)
    o.Elements = Elements(s).ITEM
    o.ReceiveElements()


  def Send(o):
    o.SendElements()
    s = o.Elements.Serial
    with Reaper as r:
      # r.Execute('l = RPR_GetSetItemState2(l[1], l[2], l[3], False)[0]', o.Address, s, len(s))
      r.SetItemStateChunk(o.Address, s, False)


  def ReceiveElements(o):

    super().Clear()
    o.HeaderElements.Clear()
    Target = o.HeaderElements
    if o.Connected:
      with Reaper as r:
        i = 0
        for e in o.Elements:
          if e.Name == "TAKE" or (Target is o.HeaderElements and e.Name == "NAME"):
            a = r.GetTake(o.Address, i)
            i += 1
            Target = o.Add(Take(a)).Elements
            Target.Clear()
          Target.Add(e)
    else:
      for e in o.Elements:
        if e.Name == "TAKE" or (Target is o.HeaderElements and e.Name == "NAME"):
          Target = o.Add(Take()).Elements
        Target.Add(e)

    if len(o) > 0:
      AnyActive = False
      for t in o:
        if not t.Elements.Has("TAKE"): t.Elements.TAKE = WordBlank
        elif t.Elements.TAKE == "SEL": 
          AnyActive = True
          break
      if not AnyActive: o[0].Elements.TAKE = Word("SEL")
    
    try:
      s = o.HeaderElements.NOTES.Binary.decode("utf-8")
      e = Elements(s)
      if e.Has("Extra"): o.ExtraElements = e.Extra 
      else: o.ExtraElements.Set("Notes", s)
    except: pass



  def SendElements(o):

    o.Elements.Clear()

    for e in o.HeaderElements: o.Elements.Add(e)

    for t in o:
      for e in t.Elements: o.Elements.Add(e)

    if o.Elements.Has("TAKE"): del o.Elements.TAKE

    if len(o.ExtraElements) > 1:
      if not o.HeaderElements.Has("NOTES"):
        o.HeaderElements.Set("NOTES", Elements()).BinaryBase64 = False
        o.Elements.Add(o.HeaderElements.NOTES)
      o.Elements.NOTES.Binary = o.ExtraElements.Serial.encode("utf-8")

  


  def ReceiveFile(o, File):
    s = File.Binary.decode("utf-8")
    o.Elements = Elements(s).ITEM
    o.ReceiveElements()

  def SendFile(o, File):
    o.SendElements()
    s = o.Elements.Serial
    File.Binary = s.encode("utf-8")






  _InfoGet = Reaper.GetMediaItemInfo_Value
  _InfoSet = Reaper.SetMediaItemInfo_Value

  @Property
  def Name(o, p):
    if p.Get: p.Value = o.TakeActive.Name
    elif p.Set: o.TakeActive.Name = p.Value
    

  @Property
  def Selected(o, p): 
    p.Value = o._GetSet("SEL", 0, "B_UISEL", False, p.Set, p.Value)
  
  @Property
  def TakeActive(o, p):
    if p.Get:
      if o.Connected:
        a = Reaper.GetActiveTake(o.Address)
        p.Value = Take(a)
      else:
        for t in o:
          if t.Elements.TAKE == "SEL": 
            p.Value = t
            break
    elif p.Set:
      Found = False
      for t in o:
        if p.Value is t and not Found:
          t.Elements.TAKE = Word("SEL")
          Found = True
        else:
          t.Elements.TAKE = WordBlank
      if Found:
        if o.Connected:
          with Reaper as r:
            r.SetActiveTake(p.Value.Address)
            r.MarkTrackItemsDirty(r.GetMediaItemTrack(o.Address), o.Address)
            r.UpdateItemInProject(o.Address)
      else:
        t = o.Add(p.Value.Copy())
        t.Address = None


Reaper.Item = Item

@Property
def ItemsSelected(o, p):
  with Reaper as r:
    for i in range(r.CountSelectedMediaItems(o.Address)):
      a = r.GetSelectedMediaItem(o.Address, i)
      yield Item(a)

Reaper.Project.ItemsSelected = ItemsSelected

@Property
def Items(o, p):
  with Reaper as r:
    for i in range(r.CountMediaItems(o.Address)):
      a = r.GetMediaItem(o.Address, i)
      yield Item(a)

Reaper.Project.Items = Items



class Take(Proxy, beyond.Elements.Element):

  def __Object__(c):
    o = c.Base()
    if c.New:
      o.Effects = Reaper.Effects()

  _InfoGet = Reaper.GetMediaItemTakeInfo_Value
  _InfoSet = Reaper.SetMediaItemTakeInfo_Value
  _InfoGetSetString = Reaper.GetSetMediaItemTakeInfo_String

  @Property
  def Name(o, p):
    p.Value = o._GetSet("NAME", 0, "P_NAME", "", p.Set, p.Value)
    if p.Set: p.Base()

  @Property
  def Active(o, p):
    if p.Get: p.Value = o == o.Container.TakeActive
    elif p.Set: o.Container.TakeActive = o