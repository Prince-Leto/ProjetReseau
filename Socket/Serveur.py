import socket, os
from select import select
from time import sleep
from threading import Thread

Sockets = []
Files = []
SocketInfos = {}
Buffer = 4096
Port = 5000
MaxModif = 10
TimeMax = 10
Path = os.path.dirname(os.path.realpath(__file__))

Serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
Serveur.bind(('', Port))
Serveur.listen(10)

def Encode(Mesage):
	return (Mesage + chr(1)).encode('utf-8')

def SeparateData(Data):
	Data = Data[:len(Data) - 1]
	return Data.split(chr(1))

def BroadCast(Sock, Message):
	global Sockets, Serveur, Fichiers
	for Socket in Sockets:
		if Socket != Serveur and Socket != Sock and SocketInfos[Sock][0] == SocketInfos[Socket][0] and SocketInfos[Socket][0] != -1:
			try:
				Socket.send(Message)
			except:
				print('Client disconnected')
				Socket.close()
				Sockets.remove(Socket)
				# Should also clean SocketInfos

def LookFiles():
	global Files, Path
	try:
		for FileName in os.listdir(Path + '/LISSData'):
			if os.path.isfile(os.path.join(Path + '/LISSData', FileName)):
				File = open(os.path.join(Path + '/LISSData', FileName), 'r')
				Files.append([FileName, File.read(), 0])
				File.close()
	except:
		os.mkdir(Path + '/LISSData')

LookFiles()

def WriteFile(i):
	global Files
	File = open(os.path.join(Path + '/LISSData', Files[i][0]), 'w')
	File.write(Files[i][1])
	File.close()
	Files[i][2] = 0
	print('File ' + Files[i][0] + ' saved')

def RemoteFiles(Sock):
	global Files
	m = 'f'
	if len(Files) > 0:
		for f in range(len(Files) - 1):
			m += Files[f][0] + ","
		m += Files[len(Files) - 1][0]
	Sock.send(Encode(m))

Sockets.append(Serveur)

class CheckForFileSave(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.daemon = True
		self.start()
	def run(self):
		global Files
		while True:
			for i in range(len(Files)):
				if Files[i][2] != 0:
					WriteFile(i)

			sleep(TimeMax)

print('Serveur started on port ' + str(Port))

CheckForFileSave()

while True:
	read, write, errors = select(Sockets, [], [])

	for Sock in read:
		if Sock == Serveur:
			Sockc, Addr = Serveur.accept()
			Sockets.append(Sockc)
			SocketInfos[Sockc] = [-1, Addr]
			print('Client (%s, %s) connected' % Addr)
			RemoteFiles(Sockc)

		else:
			try:
				Data = Sock.recv(Buffer)
				if Data:
					Data = Data.decode('utf-8')
					print(Data)
					for Data in SeparateData(Data):
						if Data == 'GetFiles':
							RemoteFiles(Sock)
						elif Data[0:1] == 'f':
							SocketInfos[Sock][0] = int(Data[1:])
							Sock.send(Encode('n,' + Files[SocketInfos[Sock][0]][1]))
						elif Data[0:1] == 'c':
							Files.append([Data[1:], '', 0])
							RemoteFiles(Sock)
						elif Data[0:1] == 'k':
							Data = 'k' + str(SocketInfos[Sock][1][1]) + ":" + Data[1:]
							BroadCast(Sock, Encode(Data))
						else:
							Size, Data = Data.split('|', 1)
							# print(Size, Data)
							if int(Size) == len(Files[SocketInfos[Sock][0]][1]): # TODO ; check size
								BroadCast(Sock, Encode(Data))
								Offset = 0
								Data = Data[:len(Data) - 1]
								for Data in Data.split(chr(0)):
									if Data[0:1] == 'i':
										Files[SocketInfos[Sock][0]][2] += 1
										Files[SocketInfos[Sock][0]][1] = Files[SocketInfos[Sock][0]][1][:int(Data[1:].split(",", 1)[0]) - Offset] + Data[1:].split(",", 1)[1] + Files[SocketInfos[Sock][0]][1][int(Data[1:].split(",", 1)[0]) - Offset:]
									if Data[0:1] == 'd':
										Files[SocketInfos[Sock][0]][2] += 1
										Files[SocketInfos[Sock][0]][1] = Files[SocketInfos[Sock][0]][1][:int(Data[1:].split(",", 1)[0]) - Offset] + Files[SocketInfos[Sock][0]][1][int(Data[1:].split(",", 1)[1]) - Offset:]
										Offset += int(Data[1:].split(",", 1)[1]) - int(Data[1:].split(",", 1)[0])
								if Files[SocketInfos[Sock][0]][2] >= MaxModif:
									WriteFile(SocketInfos[Sock][0])
							else:
								print('Conflict in message order. Resending data')
								Sock.send(Encode('n,' + Files[SocketInfos[Sock][0]][1]))
				else:
					print('Client disconnected')
					Sock.close()
					Sockets.remove(Sock)

			except:
				print('Client disconnected')
				Sock.close()
				Sockets.remove(Sock)

Serveur.close()