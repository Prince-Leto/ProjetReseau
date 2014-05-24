import socket, sys, difflib
from select import select

import sublime, sublime_plugin

Sockets = []
Old = []
Vues = []
Cursors = []
OCursors = []
DataReceived = 0
Started = False

Buffer = 4096

def Encode(Mesage):
	return Mesage.encode('utf-8')

def Loop():
	global Sockets, Vues, DataReceived, OCursors
	while True:
		Ready = select(Sockets, [], [])
		for Sock in Ready[0]:
			Data = Sock.recv(Buffer).decode('utf-8')
			if not Data:
				sublime.error_message('Connection lost.')
				Sock.close()
				index = Sockets.index(Sock)
				del Sockets[index]
				del Infos[index]
				del Cursors[index]
			else:
				try:
					index = Sockets.index(Sock)
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
				OCursors.append([]) # Should receive other's cursors from server
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
				OCursors.append([]) # Should receive other's cursors from server
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
		global Old, Sockets, Vues, DataReceived
		if DataReceived == 0:
			try:
				index = Vues.index(view)
				d = difflib.Differ()
				Message = str(Old[index][1]) + '|' + Changes(''.join(d.compare(Old[index][0], view.substr(sublime.Region(0, view.size()))))) + chr(1)
				Old[index][0] = view.substr(sublime.Region(0, view.size()))
				Old[index][1] = view.size()
				Sockets[index].send(Encode(Message))

			except ValueError:
				pass

		else:
			DataReceived -= 1

	def on_selection_modified(self, view):
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