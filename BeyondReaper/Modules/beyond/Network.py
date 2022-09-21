import beyond
import socket, struct, pickle, io


PacketSize = 1024
TimeOut = 200


class ServerSingle:

	def __init__(o, Address):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind(Address)
			s.listen(5)
			s.settimeout(TimeOut)
			s2, a = s.accept()
			o.Connection = Connection(s2, a)
		except:
			raise
		finally:
			s.close()
			
	def Send(o, d):
		o.Connection.Send(d)
		
	def Receive(o):
		return o.Connection.Receive()
	
	def End(o):
		o.Connection.End()

		
	
class Client():
		
	def __init__(o, Address):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(TimeOut)
		s.connect(Address)
		o.Connection = Connection(s, Address)
		
	def Send(o, d):
		o.Connection.Send(d)
		
	def Receive(o):
		return o.Connection.Receive()

	def End(o):	
		o.Connection.End()
	
	def __enter__(o):
		return o
	
	def __exit__(o, ExceptionType, Exception, Traceback):
		o.End()

		
	
class Connection:
	
	def __init__(o, Socket, Address):
		o.Socket = Socket
		o.Address = Address
	

	def Send(o, d):
	
		o.Socket.settimeout(TimeOut)
	
		b = io.BytesIO()
		b.seek(4)
		pickle.dump(d, b, pickle.HIGHEST_PROTOCOL)
		Size = b.tell()
		b.seek(0)
		b.write(struct.pack("<I", Size))

		b.seek(0)
		
		i = 0
		while i < Size:
			i2 = i + PacketSize
			if i2 > Size: i2 = Size
			o.Socket.send(b.read(i2 - i))
			i = i2
		
		b.close()
		
	
	def Receive(o):
	
		o.Socket.settimeout(TimeOut)
	
		b = io.BytesIO()
		
		b.write(o.Socket.recv(PacketSize))
		i = b.tell()
		if i <= 4:
			b.close()
			return None
		
		b.seek(0)
		Size = struct.unpack("<I", b.read(4))[0]
		b.seek(i)
		
		while i < Size:
			b.write(o.Socket.recv(PacketSize))
			i = b.tell()
				
		b.seek(4)
		d = pickle.load(b)

		b.close()

		return d
	
	
	def End(o):
		o.Socket.close()