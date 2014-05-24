import socket, select, sys

def Encode(Mesage):
	return (Mesage + chr(1)).encode('utf-8')

def Prompt() :
	sys.stdout.write('-> ')
	sys.stdout.flush()

if(len(sys.argv) < 3) :
	print('Usage : python3 Client.py Hostname Port')
	sys.exit()
Host = sys.argv[1]
Port = int(sys.argv[2])

Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Socket.settimeout(2)

try :
	Socket.connect((Host, Port))
except :
	print('Unable to connect')
	sys.exit()

print('Connected to remote host. Start sending messages :')
Prompt()

while True:
	socket_list = [sys.stdin, Socket]
	ready = select.select(socket_list , [], [])

	for sock in ready[0]:
		if sock == Socket:
			data = sock.recv(4096)
			if not data :
				print('\nDisconnected from chat server')
				sys.exit()
			else :
				sys.stdout.write(data.decode("utf-8") + "\n")
				Prompt()

		else :
			Message = sys.stdin.readline()
			if Message[0:1] == 'ß':
				Socket.send(Encode(Message[1:len(Message) - 1] + chr(0)))
			else:
				Socket.send(Encode(Message[0:len(Message) - 1]))

			Prompt()