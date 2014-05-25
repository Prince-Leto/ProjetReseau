import socket, difflib
from select import select

import sublime, sublime_plugin

Sockets = []
Old = []
Vues = []
Cursors = []
OCursors = []
DataReceived = 0
Realoding = False
Started = False

Buffer = 4096

# Encode messages before sending
def Encode(Mesage):
	return (Mesage + chr(1)).encode('utf-8')

# Separate messages that can be received in one time
def SeparateData(Data):
	Data = Data[:len(Data) - 1]
	return Data.split(chr(1))

# Send a request for the list of files available
class RemoteFileCommand(sublime_plugin.TextCommand):
	global Sockets, Vues
	def run(self, edit):
		try:
			Sockets[Vues.index(self.view)].send(Encode('GetFiles'))
		except ValueError:
			sublime.error_message('This file is not connected.')

# Create a new file on the serveur
class CreateFileCommand(sublime_plugin.TextCommand):
	def run(self, view):
		global Sockets, Vues
		def onDone(m):
			global Sockets, Vues
			try:
				index = Vues.index(sublime.active_window().active_view()) # Bad... But we cannot get parameters and I don't want an other global variable
				if ',' in m:
					sublime.error_message('File name not permited.')
				else:
					Sockets[index].send(Encode('c' + m))
			except ValueError:
				sublime.error_message('This file is not connected.')
		sublime.active_window().show_input_panel('Name', '', onDone, None, None)

# Insert some text
class InsertionCommand(sublime_plugin.TextCommand):
	def run(self, edit, Data):
		status = self.view.is_read_only()
		self.view.set_read_only(False)
		self.view.insert(edit, int(Data.split(',', 1)[0]), Data.split(',', 1)[1])
		self.view.set_read_only(status)

# Delete some text
class DeletionCommand(sublime_plugin.TextCommand):
	def run(self, edit, Data):
		status = self.view.is_read_only()
		self.view.set_read_only(False)
		self.view.erase(edit, sublime.Region(int(Data.split(',', 1)[0]), int(Data.split(',', 1)[1])))
		self.view.set_read_only(status)

# Erase all the content
class EraseCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		status = self.view.is_read_only()
		self.view.set_read_only(False)
		self.view.erase(edit, sublime.Region(0, self.view.size()))
		self.view.set_read_only(status)

# Infinite loop to listen for sockets
def Loop():
	global Sockets, Vues, DataReceived, OCursors, Old
	while True:
		Ready = select(Sockets, [], [])
		for Sock in Ready[0]:
			Data = Sock.recv(Buffer)
			if not Data:
				sublime.error_message('Connection lost.')
				Sock.close()
				index = Sockets.index(Sock)
				del Sockets[index]
				del Vues[index]
				del Cursors[index]
			else:
				try:
					index = Sockets.index(Sock)
					Data = Data.decode('utf-8')
					for Data in SeparateData(Data):
						if Data[0:1] == 'f':
							if Data != 'f':
								def onDone(i):
									global client
									if i != -1:
										Sockets[index].send(Encode('f' + str(i)))
								sublime.active_window().show_quick_panel(Data[1:].split(','), onDone)
							else:
								sublime.error_message('No file available on server.')
						elif Data[0:1] == 'n': # If we have to replace all the content
							DataReceived = 0
							OCursors[index] = [] # Should receive other's cursors from server
							if Vues[index].size() > 0:
								DataReceived += 1
								Vues[index].run_command('erase')
							if Data[1:].split(',', 1)[1] != '':
								DataReceived += 1
								Vues[index].run_command('insertion', {'Data': '0' + Data[1:]})
							Old[index][0] = Vues[index].substr(sublime.Region(0, Vues[index].size()))
							Old[index][1] = Vues[index].size()
						elif Data[0:1] == 'k':
							Addr = Data[1:].split(':')[0]
							Key = Data[1:].split(':')[1].split('|')
							for i in range(len(Key)):
								Key[i] = sublime.Region(int(Key[i].split(',')[0]), int(Key[i].split(',')[1]))
							OCursors[index] = Key
							Vues[index].add_regions(Addr, Key, 'string', 'dot', sublime.DRAW_EMPTY)
							Over = False
							for K in OCursors[index]:
								for L in Cursors[index]:
									for l_other in Vues[index].lines(K):
										for l_me in Vues[index].lines(L):
											if l_me == l_other:
												Over = True

							Vues[index].set_read_only(Over)

						else:
							Data = Data[:len(Data) - 1]
							Offset = 0
							for Data in Data.split(chr(0)):
								DataReceived = 1
								if Data[0:1] == 'i':
									Vues[index].run_command('insertion', {'Data': Data[1:]})
								elif Data[0:1] == 'd':
									Vues[index].run_command('deletion', {'Data': Data[1:]})

				except ValueError:
					pass

class ConnectFileCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global Cursors, OCursors, Old, Vues, Started, Sockets
		def onDone(Message):
			global Cursors, OCursors, Old, Vues, Started, Sockets
			try:
				Host, Port = Message.split(':', 1)
				Port = int(Port)
				Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				Vue = self.view
				Vues.append(Vue)
				Cursors.append(list(Vue.sel()))
				OCursors.append([])
				Old.append(['', 0])

				try:
					Sock.connect((Host, Port))
					Sockets.append(Sock)
					if not Started:
						Started = True
						sublime.set_timeout_async(Loop, 0)
				except:
					sublime.error_message('Unable to connect.')
			except:
				sublime.error_message('Please enter hostname:port.')

		sublime.active_window().show_input_panel('Hostname:port', '', onDone, None, None)

class AppendFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		global Cursors, OCursors, Old, Vues, Started, Sockets
		def onDone(Message):
			global Cursors, OCursors, Old, Vues, Started, Sockets
			try:
				Host, Port = Message.split(':', 1)
				Port = int(Port)
				Sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				Vue = self.window.new_file()
				Vues.append(Vue)
				Cursors.append(list(Vue.sel()))
				OCursors.append([])
				Old.append(['', 0])

				try:
					Sock.connect((Host, Port))
					Sockets.append(Sock)
					if not Started:
						Started = True
						# sublime.set_timeout_async(Loop, 0)
				except:
					sublime.error_message('Unable to connect.')
			except:
				sublime.error_message('Please enter hostname:port.')

		self.window.show_input_panel('Hostname:port', '', onDone, None, None)

def Changes(DataDiff):
	Last = ''
	Indice = 0
	Buffer = ''
	Message = ''
	for i in range(0, int(len(DataDiff)/3)):
		if Last != DataDiff[i*3]:
			if Last == '+':
				Message += 'i' + str(Indice) + ',' + Buffer + chr(0)
			elif Last == '-':
				Message += 'd' + str(Indice) + ',' + str(len(Buffer) + Indice) + chr(0)
			Buffer = DataDiff[i*3 + 2]
			Indice = i
		else:
			Buffer += DataDiff[i*3 + 2]
		Last = DataDiff[i*3]
	if Last == '+':
		Message += 'i' + str(Indice) + ',' + Buffer + chr(0)
	elif Last == '-':
		Message += 'd' + str(Indice) + ',' + str(len(Buffer) + Indice) + chr(0)
	return Message

class ListenerCommand(sublime_plugin.EventListener):
	def on_modified(self, view):
		global Old, Sockets, Vues, DataReceived, Cursors
		try:
			index = Vues.index(view)
			if DataReceived == 0:
				d = difflib.Differ()
				Message = str(Old[index][1]) + '|' + Changes(''.join(d.compare(Old[index][0], view.substr(sublime.Region(0, view.size())))))
				Old[index][0] = view.substr(sublime.Region(0, view.size()))
				Old[index][1] = view.size()
				try:
					Sockets[index].send(Encode(Message))
				except:
					sublime.error_message('Connection lost.')
					Sockets[index].close()
					del Sockets[index]
					del Vues[index]
					del Cursors[index]

			else:
				DataReceived -= 1

		except ValueError:
			pass

	def on_selection_modified(self, view):
		global Sockets, Vues, Cursors, OCursors
		try:
			index = Vues.index(view)
			Cursors[index] = list(view.sel())
			m = ''
			for i in range(len(view.sel()) - 1):
				m += str(view.sel()[i].begin()) + ',' + str(view.sel()[i].end()) + '|'
			m += str(view.sel()[len(view.sel()) - 1].begin()) + ',' + str(view.sel()[len(view.sel()) - 1].end())
			try:
				Sockets[index].send(Encode('k' + m))
			except:
				sublime.error_message('Connection lost.')
				Sockets[index].close()
				del Sockets[index]
				del Vues[index]
				del Cursors[index]

			Over = False

			for K in OCursors[index]:
				for L in Cursors[index]:
					for l_other in view.lines(K):
						for l_me in view.lines(L):
							if l_me == l_other:
								Over = True
			if Over and len(Cursors[index]) == 1 and Cursors[index][0].end() == Cursors[index][0].begin() and (Cursors[index][0].begin() == view.size() or Cursors[index][0].begin() == 0):
				view.run_command('insertion', {'Data': str(Cursors[index][0].begin()) + ',' + '\n'})
				Old[index][0] = Vues[index].substr(sublime.Region(0, Vues[index].size()))
				Old[index][1] = Vues[index].size()

			view.set_read_only(Over)

		except ValueError:
			pass

	def on_close(self, view):
		global Vues, Sockets, Cursors
		try:
			index = Vues.index(view)
			Sockets[index].close()
			del Sockets[index]
			del Vues[index]
			del Cursors[index]
		except ValueError:
			pass