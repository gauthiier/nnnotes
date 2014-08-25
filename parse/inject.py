#!/usr/bin/env python
from statemachine import StateMachine
import sys, os, string, json, shutil, codecs

quote_nbr = sys.maxint
fileout = ''
fileref = ''
notes = []
quotes = []

def error(c):
	fp, l = c
	sys.stderr.write('Unidentifiable line:\n'+ l)

def eof(c):
	print "eof"
	return

def parse(c):
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		if line[:2] == '##': return section(line), (fp, line)
		else: 
			emit_line(line)
			continue

def QUOTES(c):
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: 
			emit_remaining_quotes()
			return eof, (fp, line)
		elif string.find(string.upper(line), 'PAGE') >= 0: return process_quote, (fp, line)
		elif line[:2] == '##': 
			emit_remaining_quotes()
			return section(line), (fp, line)
		else:
			emit_line(line)
			continue

def NOTES(c):	
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: 
			emit_line('\n')
			emit_remaining_notes()
			return eof, (fp, line)
		elif string.find(string.upper(line), 'NOTE') >= 0: return process_note, (fp, line)
		elif line[:2] == '##': 
			emit_line('\n')
			emit_remaining_notes()			
			return section(line), (fp, line)		
		else:
			emit_line(line) 
			continue

def process_quote(c):
	fp, l = c
	ppnbr = int(string.rsplit(l)[-1])
	for i in quotes.keys():
		if int(i) < ppnbr:
			emit_quotes(quotes[i])
	emit_line(l)
	return QUOTES(c)

def process_note(c):
	fp, l = c
	emit_line(l)
	return NOTES(c)


####################

def section(line):
	emit_line(line)
	line = string.upper(line)
	if string.find(line, 'NOTES') >= 0: 
		if not notes:
			return parse
		return NOTES
	elif string.find(line, 'QUOTES') >= 0: 
		if not quotes:
			return parse		
		return QUOTES
	elif string.find(line, 'REFERENCE') >= 0: return parse
	else: return parse

def emit_remaining_quotes():
	rest = []
	for i in quotes:
		rest.extend(quotes[i])	
	emit_quotes(rest)

def emit_quotes(list):
	while list:
		emit_quote(list.pop())

def emit_quote(data):
	emit_line("page " + data['pp'] + "\n\n")
	emit_line(">" + data['quote'] + "\n")
	emit_line('\n')

def emit_remaining_notes():
	rest = []
	for i in notes:
		rest.extend(notes[i])	
	for j in rest:
		emit_note(j)

def emit_note(data):
	emit_line("note: " + data['pp'] + "\n\n")
	emit_line(data['note'] + "\n" )
	emit_line('\n')

def emit_line(l):
	#l = l.encode('utf-8')
	fileout.write(l)

def reoder(q):
	out = {}
	while q:
		i = q.pop()
		if i['pp'] in out.keys():
			out[i['pp']].append(i)
		else:
			out[i['pp']] = [i]
	return out

def open_file(p):
	if not os.path.exists(p):
		sys.exit('File %s does not exists... Aborting.' % p)
	return codecs.open(p, 'rb', 'utf-8')

def open_fileoutput(p):
	if not os.path.exists(p):
		sys.exit('File %s does not exists... Aborting.' % p)
	return codecs.open(p, 'r+', 'utf-8')

def backupfile(p):
	if not os.path.exists(p):
		sys.exit('File %s does not exists... Aborting.' % p)
	bak = p + '.bak'
	shutil.copy2(p, bak)
	return codecs.open(bak, 'r', 'utf-8')


if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit('No input file... Aborting.')
	# fp1 should be the incoming .mmd file
	fileref = backupfile(sys.argv[1])
	fileout = open_fileoutput(sys.argv[1])
	fileout.seek(0)
	if len(sys.argv) < 3:
		fp2 = sys.stdin
	else:
		fp2 = open_file(sys.argv[2])

	# fp2 should be the incoming (json) data to inject in fp1
	data = json.load(fp2)
	fp2.close()

	print data

	if not data['QUOTES'] and not data['NOTES']:
		print "Document up-to-date."
		fileout.close()
		sys.exit(0)

	quotes = reoder(data['QUOTES'])
	notes = reoder(data['NOTES'])

	m = StateMachine();
	m.add_state(parse)
	m.add_state(NOTES)
	m.add_state(QUOTES)
	m.add_state(process_quote)
	m.add_state(process_note)
	m.add_state(error, end_state=1)
	m.add_state(eof, end_state=1)
	m.set_start(parse)
	m.run((fileref, ''))

	fileout.close()
	fileref.close()


