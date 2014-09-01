#!/bin/bash

for i in *.pdf; do
    f=$i
done

if [[ -d '$f' ]]; then
	echo "$f No pdf file in directory... Aborting.";
	exit;
fi

filename="${f%.*}".txt

skimnotes get -format txt $f

if [[ ! -f $filename ]]; then
	echo "No skim notes in pdf $f. Aborting.";
	exit;
fi

parse-skim.py < $filename

#rm $filename