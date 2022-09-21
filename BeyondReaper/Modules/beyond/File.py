import beyond.Class
import os, os.path, sys, imp, subprocess


@Omnipresent
class File():

	def __init__(o, Path):
		o.Path = Path
	
	@Property
	def Path(o, p):
		if p.Get:
			p.Value = os.path.join(o.ParentPath, o.NameVersion + o.Extension)

		elif p.Set:

			o.ParentPath, n = os.path.split(p.Value)
			n, o.Extension = os.path.splitext(n)

			o.Version = 0
			i = n.rfind(" V")
			if i != -1:
				try:
					o.Version = int(n[i + 2:])
					n = n[0:i]
				except: pass
				
			o.Name = n
	

	@Property
	def NameVersion(o, p):
		p.Value = o.Name
		if o.Version > 0: p.Value += " V" + str(o.Version)
		
	@Property
	def Parent(o, p):
		p.Value = File(o.ParentPath)
		if p.Value.Name == "": p.Value = None

	def __truediv__(o, Name):
		return File(os.path.join(o.Path, Name))
	
	def __iter__(o):
		for n in os.listdir(o.Path):
			yield File(os.path.join(o.ParentPath, n))

	def __hash__(o):
		return o.Path.__hash__()

	def __eq__(o, o2):
		return o.Path == o2.Path

	def __str__(o):
		return '"' + o.Path + '"'


	@Property	
	def IsFile(o, p):
		p.Value = os.path.isfile(o.Path)
		
	@Property
	def IsDirectory(o, p):
		p.Value = os.path.isdir(o.Path)
		
	@Property
	def Binary(o, p):
		if p.Get:
			with open(o.Path, "rb") as f: p.Value = f.read()
		elif p.Set:
			with open(o.Path, "wb") as f: f.write(p.Value)
		
		
	def LastVersion(o):
		for f in o.Parent: 
			if f.Name == o.Name and f.Version > o.Version: o.Version = f.Version
	
	def NextVersion(o):
		o.LastVersion()
		o.Version += 1
	
	
	def ParentFind(o, Name):
		f = File(os.path.join(o.Path if o.IsDirectory else o.ParentPath, Name))
		# Say(f)
		if f.IsFile or f.IsDirectory: return f
		else:
			p = o.Parent
			if p is None: return None
			else: return p.ParentFind(Name)
					

	@Property
	def DirectoryExisting(o, p):
		if o.IsDirectory:
			p.Value = o
		else:
			p = o.Parent
			if p is None: p.Value = None
			else: p.Value = File(o.ParentPath).DirectoryExisting


	def Show(o, Default = None):
		if o.IsFile:
			subprocess.Popen('explorer /select,"' + o.Path + '"')
		elif o.IsDirectory:
			subprocess.Popen('explorer "' + o.Path + '"')
		else:	
			f = o.DirectoryExisting
			if f: f.Show()
			elif Default: Default.Show()


	def Import(o):
		S = sys.dont_write_bytecode
		sys.dont_write_bytecode = True
		if o.ParentPath not in sys.path: sys.path.append(o.ParentPath)
		M = imp.load_source(o.Name, o.Path)
		sys.dont_write_bytecode = S
		return M

	def Execute(o):
		Source = o.Binary.decode("utf-8")
		c = compile(Source, o.Path, 'exec')
		if o.ParentPath not in sys.path: sys.path.append(o.ParentPath)
		g = sys._getframe(1).f_globals
		exec(c, g, g)


def _Import(o):
	File.__module__ = "beyond"
	beyond.File = File

Omnipresent.ProgramDirectory = File(sys.path[0])