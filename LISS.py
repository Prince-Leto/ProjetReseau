import socket, sys, difflib
from select import select

import sublime, sublime_plugin

Old = ''

def Changes(Data):
	Last = ''
	Changed = [[], []]
	for i in range(0, int(len(Data)/3)):
		if Data[i*3] == ' ':
			pass
		elif Data[i*3] == '+':
			if Last == '+':
				Changed[0][len(Changed[0]) - 1][1] += Data[i*3 + 2]
			else:
				Changed[0].append([i, Data[i*3 + 2]])
		elif Data[i*3] == '-':
			if Last == '-':
				Changed[1][len(Changed[1]) - 1][1] += Data[i*3 + 2]
			else:
				Changed[1].append([i, Data[i*3 + 2]])
		Last = Data[i*3]
	return Changed

class ListenerCommand(sublime_plugin.EventListener):
	def on_modified(self, view):
		global Old
		d = difflib.Differ()
		Changed = Changes(''.join(d.compare(Old, view.substr(sublime.Region(0, view.size())))))
		Old = view.substr(sublime.Region(0, view.size()))

		Message = ''
		if len(Changed[0]) != 0:
			Message += 'i'
			for Inserted in Changed[0]:
				print(Inserted)
				Message += str(Inserted[0]) + ',' + Inserted[1] + chr(0)
		print(Changed)
		print(Message.encode('utf-8'))
		print(Message.split(chr(0)))

	def on_selection_modified(self, view):
		pass