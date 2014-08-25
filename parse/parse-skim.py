#!/usr/bin/python

from statemachine import StateMachine
import sys, string, json

output = {'QUOTES' : [], 'NOTES' : []}

def error(c):
	fp, l = c
	sys.stderr.write('Unidentifiable line:\n'+ l)

def eof(c):
	print json.dumps(output, sys.stdout)

def parse(c):
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		if line[:1] == '*': return section(line), (fp, line)
		else: continue	

def highlight(c):
	fp, l = c
	p = page(l)
	text = fp.readline()
	output['QUOTES'].append({'pp' : p, 'quote' : text.strip()})
	return parse(c)

def anchored_note(c):
	fp, l = c
	p = page(l)
	text = fp.readline()
	fp.readline()
	note = fp.readline()	
	output['QUOTES'].append({'pp' : p, 'quote' : text.strip()})
	output['NOTES'].append({'pp' : p, 'note' : note.strip()})
	return parse(c)

def box(c):
	fp, l = c
	p = page(l)
	text = fp.readline()	
	output['QUOTES'].append({'pp' : p, 'quote' : text.strip()})
	return parse(c)

def text_note(c):
	fp, l = c
	p = page(l)
	text = fp.readline()
	output['NOTES'].append({'pp' : p, 'note' : text.strip()})
	return parse(c)

## helper fncts
def section(line):
	line = string.upper(line)
	if string.find(line, 'HIGHLIGHT') >= 0: return highlight
	elif string.find(line, 'ANCHORED NOTE') >= 0: return anchored_note
	elif string.find(line, 'BOX') >= 0: return box
	elif string.find(line, 'TEXT NOTE') >= 0: return text_note
	else: return parse

def page(line):	
	return line.rstrip('\n').split(',')[1][-1]

if __name__ == '__main__':
	m = StateMachine();
	m.add_state(parse)
	m.add_state(highlight)
	m.add_state(anchored_note)
	m.add_state(box)
	m.add_state(text_note)
	m.add_state(error, end_state=1)
	m.add_state(eof, end_state=1)
	m.set_start(parse)
	m.run((sys.stdin, ''))

