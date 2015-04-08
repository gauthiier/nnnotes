#!/bin/bash

INDXFILE='.indx'

for i in *.mmd; do
    f=$i
done

if [[ ! -f $INDXFILE ]]; then
	make --quiet index
elif [[ $f -nt $INDXFILE ]]; then
	rm $INDXFILE
	make --quiet index
fi	

#parse-skim.sh | compare.py .indx

parse-plfr.sh | compare.py .indx
