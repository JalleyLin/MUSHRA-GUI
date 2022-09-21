import sys, builtins

Version = 27

class Omnipresent():
  def __call__(o, e):
    setattr(builtins, e.__name__, e)
    return e
  def __getattribute__(o, Name): return getattr(builtins, Name)
  def __setattr__(o, Name, Value): setattr(builtins, Name, Value)
  def __delattr__(o, Name): delattr(builtins, Name)
builtins.Omnipresent = Omnipresent()
del Omnipresent


ImportOriginal = Omnipresent.__import__
def Import(name, globals = None, locals = None, fromlist = (), level = 0):
  r = ImportOriginal(name, globals, locals, fromlist, level)
  if name.startswith("beyond."):
    m = sys.modules[name]
    if hasattr(m, "_Import"): m._Import(m)
  return r
Omnipresent.__import__ = Import


@Omnipresent
def ProgramStartDirect(e):
  if e.__module__ == "__main__": e()
  else: return e


import beyond.Text