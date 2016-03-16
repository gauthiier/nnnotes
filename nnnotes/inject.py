#!/usr/bin/env python

# reads (1) a formatted md file, (2) json formatted index
# and injects (sorts and appends) in the md file the information 
# contained in the index

from statemachine import StateMachine
import sys, os, string, json, shutil, codecs, traceback

quote_nbr = sys.maxint
fileout = ''
fileref = ''
notes = []
quotes = []
notes_cnt = 0

def error(c):
	fp, l = c
	sys.stderr.write('Unidentifiable line:\n'+ l)

def eof(c):
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
		elif is_quote_identifier(line): return process_quote, (fp, line)
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
		elif is_note_identifier(line): return process_note, (fp, line)
		elif line[:2] == '##': 
			emit_line('\n')
			emit_remaining_notes()			
			return section(line), (fp, line)		
		else:
			emit_line(line) 
			continue

def process_quote(c):
	fp, l = c
	ppnbr = int(extract_identifier(l))
	for i in quotes.keys():
		if i < ppnbr:
			emit_quotes(quotes[i])
	emit_line(l)
	return QUOTES(c)

def process_note(c):
	global notes_cnt
	fp, l = c
	cnt = int(extract_identifier(l))
	if(cnt > notes_cnt):
		notes_cnt = cnt
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

def is_quote_identifier(line):
	l = line.strip().upper()
	return l.startswith("<!--") and l.find("PAGE") >= 0

def is_note_identifier(line):
	l = line.strip().upper()
	return l.startswith("<!--") and l.find("NOTE") >= 0		

def extract_identifier(line):
	t = line.strip().replace('<!--', '').replace('-->', '')
	return t.strip().rsplit()[-1]

def emit_remaining_quotes():
	rest = []
	for i in quotes:
		rest.extend(quotes[i])	
	for j in rest:
		emit_quote(j)
	#emit_quotes(rest)

def emit_quotes(list):
	while list:
		emit_quote(list.pop())

def emit_quote(data):
	emit_line("<!--page " + data['pp'] + "-->\n\n")
	emit_line(">\"" + data['quote'] + "\" p." + data['pp'] + "\n")
	emit_line('\n')

def emit_remaining_notes():

	print "emit_remaining_notes"

	rest = []
	for i in notes:
		rest.extend(notes[i])	
	for j in rest:
		emit_note(j)

def emit_note(data):
	global notes_cnt
	notes_cnt += 1
	emit_line("<!--note " + str(notes_cnt) + "-->\n\n")
	emit_line(str(notes_cnt) + ". " + data['note'] + "\n\n" )

def emit_line(l):
	#l = l.encode('utf-8')
	fileout.write(l)

def reoder(q):
	out = {}
	while q:
		ip = q.pop()
		i = int(ip['pp'])
		if i in out.keys():
			out[i].append(ip)
		else:
			out[i] = [ip]
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

def run(filename1, filename2):

	global fileout, fileref, notes, quotes, notes_cnt

	# fp1 should be the incoming .mmd file
	try:		
		fileref = backupfile(filename1)
		fileout = open_fileoutput(filename1)
		fileout.seek(0)
	except:
		sys.exit("Can't open file " + filename1 + ". Aborting.")

	try:
		fp2 = open_file(filename2)
	except:
		# it may be stdin
		try:
			fp2 = filename2
			fp2.tell()
		except:
			sys.exit("Can't open file " + filename2 + ". Aborting.")

	# fp2 should be the incoming (json) data to inject in fp1

	try:
		sdata = fp2.read()
		data = json.loads(sdata)
	except Exception, ee:
		e = "<inject> Error loading data. Aborting\n"
		if sdata:
			e += "Traceback: " + sdata
		fileout.close()
		fileref.close()
		sys.exit(e)
	finally:
		fp2.close()

	if not data['QUOTES'] and not data['NOTES']:
		print "Document up-to-date."
		fileout.close()
		sys.exit(0)

	quotes = reoder(data['QUOTES'])
	notes = reoder(data['NOTES'])

	notes_cnt = 0

	try:
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
	except:
		trace = "Error injecting.\n\nTrace: \n"
		trace += traceback.format_exc()
	else:
		trace = "Done injection."
	finally:
		fileout.close()
		fileref.close()
		return trace
			
#main allows unix piping
if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit('No input file... Aborting.')

	if len(sys.argv) < 3:
		fp2 = sys.stdin
	else:
		fp2 = sys.argv[2]

	trace = run(sys.argv[1], fp2)
	sys.exit(trace)






