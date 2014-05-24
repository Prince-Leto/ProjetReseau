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
			for i in range(len(Changed[0]) - 1):
				Message += str(Changed[0][i][0]) + ',' + Changed[0][i][1] + chr(0)
			Message += str(Changed[0][len(Changed[0]) - 1][0]) + ',' + Changed[0][len(Changed[0]) - 1][1]
		if len(Changed[0]) != 0 and len(Changed[1]) != 0:
			Message += chr(0)
		if len(Changed[1]) != 0:
			Message += 'd'
			for i in range(len(Changed[1]) - 1):
				Message += str(Changed[1][i][0]) + ',' + Changed[1][i][1] + chr(0)
			Message += str(Changed[1][len(Changed[1]) - 1][0]) + ',' + Changed[1][len(Changed[1]) - 1][1]


			# for Inserted in Changed[0]:
			# 	Message += str(Inserted[0]) + ',' + Inserted[1] + chr(0)
		print(Message.encode('utf-8'))
		# print(Message.split(chr(0)))

	def on_selection_modified(self, view):
		pass