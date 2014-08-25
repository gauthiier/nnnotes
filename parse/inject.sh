#!/bin/bash

for i in *.mmd; do
    f=$i
done

if [[ -z '$f' ]]; then
	echo "No mmd file (markdown source file) in directory... Aborting.";
	exit;
fi

# inject new nnnotes in source file
compare.sh | inject.py $f

# update index
make --quiet index
