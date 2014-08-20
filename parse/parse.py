#!/usr/bin/env python

from statemachine import StateMachine
import sys, string, re, json

markups = {'QUOTES' : ('PAGE', 'pp', 'tags', 'quote', 'fpc'), 'NOTES' : ('NOTE', '#', 'tags', 'note', 'fpc')}
output = {'QUOTES' : [], 'NOTES' : []}


def error(c):
	fp, l = c
	sys.stderr.write('Unidentifiable line:\n'+ l)

def eof(c):
	fpindx = open('.indx','wb')
	json.dump(output, fpindx)

def parse(c):
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		if line[:2] == '##': return section(line), (fp, line)
		else: continue

def QUOTES(c):
	fp, l = c
	sys.stdout.write('QUOTES\n')		
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		elif string.find(string.upper(line), 'PAGE') >= 0: return segment, (fp, line, 'QUOTES', markups['QUOTES'])
		else: continue

def NOTES(c):
	fp, l = c
	sys.stdout.write('NOTES\n')		
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		elif string.find(string.upper(line), 'NOTE') >= 0: return segment, (fp, line, 'NOTES', markups['NOTES'])
		else: continue

def segment(c):
	fp, l, sect, mk = c
	m, x, tt, y, cnt = mk
	c = '' 
	t = [] 
	q = ''
	cc = ''
	# identifier
	c = ext_identifier(l)
	while 1:
		cursor = fp.tell()
		line = fp.readline()
		if not line: 
			# transition: EOF - record entry
			rec_segment(c, t, q, cc, (sect, x, tt, y, cnt))
			return eof, (fp, line)
		elif string.find(string.upper(line), m) >= 0: 
			# transition: new segment - record entry
			rec_segment(c, t, q, cc, (sect, x, tt, y, cnt))
			return segment, (fp, line, sect, mk)
		elif line[:1] == '<': 
			# tags
			t += ext_tags(line)
			continue
		elif line[:2] == '##': 
			# transition: new section - record entry
			rec_segment(c, t, q, cc, (sect, x, tt, y, cnt))
			return section(line), (fp, line)
		elif line == '\n' :
			continue
		else:
			# text
			if not cc:
				cc = cursor
			q += line
			continue

## helper fncts
def section(line):
	line = string.upper(line)
	if string.find(line, 'NOTES') >= 0: return NOTES
	elif string.find(line, 'QUOTES') >= 0: return QUOTES
	elif string.find(line, 'REFERENCE') >= 0: return parse
	else: return error

def ext_identifier(line):
	b = string.rsplit(line)
	return b[-1]

def ext_tags(line):
	line = line.rstrip('\n').replace(' ','')
	t = re.split('<|>', line)
	return [v for v in t if v]

def rec_segment(idf, tags, text, cnt, mk):
	if not text:
		print 'hmm... no quote on pp.', c
		return None
	section_i, idf_i, tags_i, text_i, cnt_i = mk
	entry = {idf_i : idf, text_i : text, tags_i : tags, cnt_i : cnt}
	output[section_i].append(entry)


if __name__ == '__main__':
	m = StateMachine();
	m.add_state(parse)
	m.add_state(NOTES)
	m.add_state(QUOTES)
	m.add_state(segment)
	m.add_state(error, end_state=1)
	m.add_state(eof, end_state=1)
	m.set_start(parse)
	m.run((sys.stdin, ''))
