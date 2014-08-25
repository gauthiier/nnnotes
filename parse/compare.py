#!/usr/bin/env python
import sys, os, string, json

fp1 = ''
fp2 = ''

def difference(data1, data2):
	output = {'QUOTES' : [], 'NOTES' : []}

	d1 = {i['quote']: i for i in data1['QUOTES']}
	d2 = {i['quote']: i for i in data2['QUOTES']}

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

if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.exit('No input file... Aborting.')
	fp1 = open_file(sys.argv[1])
	if len(sys.argv) < 3:
		fp2 = sys.stdin
	else:
		fp2 = open_file(sys.argv[2])

	data1 = json.load(fp1)
	data2 = json.load(fp2)

	# print "----"
	# print data1
	# print "----"
	# print data2
	# print "----"

	fp1.close()
	fp2.close()

	data = difference(data1, data2)

	json.dump(data, sys.stdout)


