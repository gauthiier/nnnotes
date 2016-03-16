#!/usr/bin/env python

# parses the information containned in a formatted md file
# and constructs a json formatted index

from statemachine import StateMachine
import sys, string, re, json

def is_quote_identifier(line):
	l = line.strip().upper()
	return l.startswith("<!--") and l.find("PAGE") >= 0

def is_note_identifier(line):
	l = line.strip().upper()
	return l.startswith("<!--") and l.find("NOTE") >= 0	

def is_tag_identifier(line):
	l = line.strip()
	return l.startswith('<') and not l.startswith('<!')

markups = {'QUOTES' : (is_quote_identifier, 'pp', 'tags', 'quote', 'fpc'), 'NOTES' : (is_note_identifier, '#', 'tags', 'note', 'fpc')}
output = {'QUOTES' : [], 'NOTES' : []}
fpindex = None

def error(c):
	fp, l = c
	sys.stderr.write('Unidentifiable line:\n'+ l)

def eof(c):
	json.dump(output, fpindex)

def parse(c):
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		if line.strip().startswith('##'): return section(line), (fp, line)
		else: continue

def QUOTES(c):
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		elif is_quote_identifier(line): return segment, (fp, line, 'QUOTES', markups['QUOTES'])
		elif line.strip().startswith('##'): return section(line), (fp, line)
		else: continue

def NOTES(c):	
	fp, l = c
	while 1:
		line = fp.readline()
		if not line: return eof, (fp, line)
		elif is_note_identifier(line): return segment, (fp, line, 'NOTES', markups['NOTES'])
		elif line.strip().startswith('##'): return section(line), (fp, line)
		else: continue

def segment(c):
	fp, l, sect, mk = c
	m, x, tt, y, cnt = mk
	c = '' 
	t = [] 
	q = ''
	cc = ''
	# identifier
	c = extract_identifier(l)
	while 1:
		cursor = fp.tell()
		line = fp.readline()

		if not line: 
			# transition: EOF - record entry
			record_segment(c, t, q, cc, (sect, x, tt, y, cnt))
			return eof, (fp, line)

		elif m(line):
			# transition: new segment - record entry
			record_segment(c, t, q, cc, (sect, x, tt, y, cnt))
			return segment, (fp, line, sect, mk)
		elif is_tag_identifier(line): 
			# tags
			t += extract_tags(line)
			continue
		elif line[:2] == '##': 
			# transition: new section - record entry
			record_segment(c, t, q, cc, (sect, x, tt, y, cnt))
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
	if line.find('NOTES') >= 0: return NOTES
	elif line.find('QUOTES') >= 0: return QUOTES
	elif line.find('REFERENCE') >= 0: return parse
	else: return parse

# todo - optimise this (i.e: id != only the last word)
def extract_identifier(line):
	t = line.strip().replace('<!--', '').replace('-->', '')
	return t.strip().rsplit()[-1]

def extract_tags(line):
	line = line.rstrip('\n').replace(' ','')
	t = re.split('<|>', line)
	return [v for v in t if v]

def record_segment(idf, tags, text, cnt, mk):
	if not text:
		#sys.stderr.write('hmm... no quote on pp.' + idf)
		return None
	text = escape_quote(text)
	text = escape_note(text)
	section_i, idf_i, tags_i, text_i, cnt_i = mk
	entry = {idf_i : idf, text_i : text, tags_i : tags, cnt_i : cnt}
	output[section_i].append(entry)

def escape_quote(line):
	if(not line.strip().startswith('>')):
		return line
	l = re.sub('\"*\"', '', line.strip()[1:])
	return re.sub('p.[0-9]+', '', l)

def escape_note(line):
	return re.sub('^[0-9]+.', '', line).strip()

def run(fpin, fpout):

	global fpindex

	fpindex = fpout
	m = StateMachine();
	m.add_state(parse)
	m.add_state(NOTES)
	m.add_state(QUOTES)
	m.add_state(segment)
	m.add_state(error, end_state=1)
	m.add_state(eof, end_state=1)
	m.set_start(parse)
	m.run((fpin, ''))	

#main allows unix piping
if __name__ == '__main__':
	fpindx = open('.indx','wb')
	run(sys.stdin, fpindx)
