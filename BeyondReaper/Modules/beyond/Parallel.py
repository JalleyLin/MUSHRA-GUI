import beyond
import beyond.State
import threading, queue, time, types, sys



Parallels = {}
ParallelsLock = threading.Lock()


@Omnipresent
class Parallel(beyond.Statable):


	def __init__(o, Parent = None, Stay = False, **d):
				
		o.__dict__["Parent"] = Parent
		o.__dict__.update(d)
						
		o.Queue = queue.Queue()
		o.Active = True

		o.Thread = t = Parallel.Thread()
		t.name = o.__class__.__name__
		t.Parallel = o
		
		with ParallelsLock: Parallels[t] = o
		
		o.Start()
		t.start()
		if not Stay: o.End()
			

	class Thread(threading.Thread):
		def	run(o):
			o = o.Parallel
			while o.Active: o.Yield()
			with ParallelsLock: del Parallels[o.Thread]
			# Say_("Parallel Exit:", o.Thread.name)
		
	
	def Yield(o, Duration = None):
		if Duration is not None: WaitEnd = time.clock() + Duration
		while True:
			Now = time.clock()
			if not o.Active or (Duration is not None and Now >= WaitEnd):
				break
			elif not o.Queue.empty():
				l, d = o.Queue.get()
				Execute(*l, **d)
			else:
				time.sleep(0.001)

				
	def End(o):
		if o.Active:
			o.Active = False
			o.Free()

	def Execute(__o__, *l, **d):
		if __o__.Thread is threading.currentThread():
			Execute(*l, **d)
		else:
			__o__.Queue.put((l, d))
		
	def ExecuteWaitReturn(__o__, ___Function___, *l, **d):
		# Say_("ExecuteWaitReturn:", ___Function___)
		if __o__.Thread is threading.currentThread():
			return ___Function___(*l, **d)
		else:
			Ready = threading.Event()
			Return = []
			# __o__.Queue.put((('Return.append(Function(*l, **d))\nReady.set()',), {"Return": Return, "Ready": Ready, "Function": ___Function___, "l": l, "d": d}))
			__o__.Execute('Return.append(Function(*l, **d))\nReady.set()', Return = Return, Ready = Ready, Function = ___Function___, l = l, d = d)
			while not Ready.isSet() and __o__.Active: Ready.wait(.01)
			return Return[0] if len(Return) == 1 else None
			
	
	
		
	def StateGet(o):
		d = o.__dict__.copy()
		del d["Thread"]
		del d["Queue"]
		del d["Active"]
		del d["Parent"]
		return d

	def StateSet(o, d):
		for e, v in d.items(): setattr(o, e, v)

			
		
	def Start(o):
		pass

	# def Pulse(o):
	# 	pass

	def Free(o):
		pass


		
	_DirectAttributes = set(("Thread", "Queue", "Active", "Execute", "ExecuteWaitReturn"))	
	
	def __getattribute__(o, Name):
		# Say_("Get:", Name)
		A = object.__getattribute__(o, Name)
		if Name[0] == "_" or Name in Parallel._DirectAttributes or o.Thread is threading.currentThread():
			return A
		else:
			if hasattr(A, "__call__"):
				# Say_("Parallel Function Get:", Name)
				def f(*l, **d):
					if d.pop("WaitReturn", False):
						return o.ExecuteWaitReturn(A, *l, **d)
					else:
						o.Execute(A, *l, **d)
				f.Parallel = o
				return f
			else:
				# Say_("Parallel Get:", Name)
				return o.ExecuteWaitReturn(object.__getattribute__, o, Name)

	def __setattr__(o, Name, Value):
		# Say_("Set:", Name, Value)
		if Name[0] == "_" or Name in Parallel._DirectAttributes or o.Thread is threading.currentThread():
			object.__setattr__(o, Name, Value)
		else:
			# Say_("Parallel Set:", Name, Value)
			o.Execute(object.__setattr__, o, Name, Value)
				
				


# @Omnipresent
# def ParallelReceiver(Function):
	# return lambda *l, **d: l[0].Execute(Function, *l, **d)



@Omnipresent
def BaseReceiver(Function):
	return lambda *l, **d: Base.Execute(Function, *l, **d)



def Execute(*l, **d):
  try:
    if l[0].__class__ is str: exec(l[0], globals(), d)
    else: l[0](*l[1:], **d)
  except Exception as e: Say(e)




def Current():
	t = threading.currentThread()
	with ParallelsLock: p = Parallels[t]
	return p


class Base(Parallel):

	def __init__(o):
		o.Queue = queue.Queue()
		o.Active = o._Active = True
		o.Thread = threading.currentThread()
		Parallels[o.Thread] = o
		o.PulseRate = 60
		o.Pulses = []

		
	def Start(o, e = None):

		if e is None: pass
		elif isinstance(e, type): e()
		elif type(e) is types.FunctionType:
			class p(Parallel):
				def Start(o):
					e()
			p()
		else:
			raise Exception("Unable to start: " + str(e))
		
		while o.Active:
			
			o.Yield(1 / o.PulseRate)	
			
			for f in o.Pulses: f()
			
			with ParallelsLock: 
				if len(Parallels) == 1: break
			
			
	def End(o):
		if o._Active:
			o._Active = False
			
			# Say("e N d +++++++++++++++++++:")

			while True:
				
				with ParallelsLock: 
					if len(Parallels) == 1: break
					l = Parallels.copy().values()
				
				for p in l: p.End()
				
				o.Yield(.1)
			
			o.Active = False

			# import os
			# os._exit(1)		
		
		
Omnipresent.Base = Base = Base()



@Omnipresent
def ProgramStart(e):
	if e.__module__ == "__main__": 
		Base.Start(e)
	else: 
		return e