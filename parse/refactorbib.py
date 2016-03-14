#!/usr/bin/env python
import sys, os, json
from optparse import OptionParser

def open_file(p):
	if not os.path.exists(p):
		sys.exit('File %s does not exists... Aborting.' % p)
	return open(p, 'rb')

def refactor(data):

	data_out = {}
	for d in data:
		nid = ''
		if(d['author']):
			nid = d['author'][0]['family'] + d['issued']['date-parts'][0][0]
		elif(d['editor']):
			nid = d['editor'][0]['family'] + d['issued']['date-parts'][0][0]

		if nid in data_out:
			for c in range(97, 122):
				nid = nid + chr(c)
				if not nid in data:
					break
		data_out[nid] = d

	return data_out


if __name__ == '__main__':

	p = OptionParser();
	p.add_option('-i', '--index', action="store_true", help="prints out index")

	options, args = p.parse_args()

	if len(args) < 1:
		sys.exit('No input file... Aborting.')
	try:
		fp = open_file(args[0])
	except:
		sys.exit("Can't open file " + args[0] + ". Aborting.")

	try:
		data = json.loads(fp.read())
	except:
		e = "<refactorbib> Error loading data from" + sys.argv[1] + ". Aborting.\n"
		if sdata:
			e += "Traceback: " + sdata1
		sys.exit(e)		
	finally:
		fp.close()

	out = refactor(data)

	if options.index:
		for e in out.keys():
			print '> ' + e + ' - ' + out[e]['title'] + '  '
	else:
		print json.dumps(out, sort_keys=True, indent=2, separators=(',', ': '))



