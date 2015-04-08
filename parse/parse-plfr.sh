#!/bin/bash

for i in *.pdf; do
    f=$i
done

if [[ -d '$f' ]]; then
	echo "$f No pdf file in directory... Aborting.";
	exit;
fi

plfr -json $f

