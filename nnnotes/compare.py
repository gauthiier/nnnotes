#!/usr/bin/env python

# compares two json formatted indexes
# and return the difference 

import sys, os, string, json
from operator import attrgetter

fp1 = ''
fp2 = ''

def difference(data1, data2):
	output = {'QUOTES' : [], 'NOTES' : []}

	d1 = {i['quote'].rstrip(): i for i in data1['QUOTES']}
	d2 = {i['quote'].rstrip(): i for i in data2['QUOTES']}

	#create sets
	s1 = set(d1.keys())
	s2 = set(d2.keys())

	#symmetric difference - nope
	#diff = list(s1 ^ s2)

	# difference between s2 and s1 (s2 being pdf annotation)
	diff = list(s2 - s1)

	for d in diff:
		output['QUOTES'].append(d2[d])

	d1 = {i['note']: i for i in data1['NOTES']}
	d2 = {i['note']: i for i in data2['NOTES']}

	#create sets
	s1 = set(d1.keys())
	s2 = set(d2.keys())

	#symmetric difference - nope
	#diff = list(s1 ^ s2)

	# difference between s2 and s1 (s2 being pdf annotation)
	diff = list(s2 - s1)

	for d in diff:
		output['NOTES'].append(d2[d])

	return output

def open_file(p):
	if not os.path.exists(p):
		sys.exit('File %s does not exists... Aborting.' % p)
	return open(p, 'rb')

def run(filename1, filename2):

	#open files
	try:
		fp1 = open_file(filename1)
	except:
		sys.exit("Can't open file " + filename1 + ". Aborting.")

	try:
		fp2 = open_file(filename2)
	except:
		# it may be std.in
		try:
			fp2 = filename2
			fp2.tell()
		except:
			sys.exit("Can't open file " + filename2 + ". Aborting.")

	#read data
	try:
		sdata = fp1.read()
		data1 = json.loads(sdata)
	except:
		e = "<compare> Error loading data from" + filename1 + ". Aborting.\n"
		if sdata:
			e += "Traceback: " + sdata
		fp2.close()
		sys.exit(e)		
	finally:
		fp1.close()
		
	try:
		sdata = fp2.read()
		data2 = json.loads(sdata)
	except Exception, ee:
		e = "<compare> Error loading data. Aborting.\n"
		if sdata:
			e += "Traceback: " + sdata
		fp1.close()
		sys.exit(e)
	finally:
		fp2.close()

	#process
	data = difference(data1, data2)

	data['QUOTES'] = sorted(data['QUOTES'], key=lambda entry: int(entry['pp']))
	data['NOTES'] = sorted(data['NOTES'], key=lambda entry: int(entry['pp']))

	#dump
	return data

#main allows unix piping
if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit('No input file... Aborting.')

	json.dump(run(sys.argv[1], sys.stdin), sys.stdout)



