#!/bin/bash

for i in *.pdf; do
    f=$i
done

if [[ -z '$f' ]]; then
	echo "No pdf file in directory... Aborting.";
	exit;
fi

filename="${f%.*}"

skimnotes get -format txt $f

parse-skim.py < "$filename.txt"

#rm $filename.txt