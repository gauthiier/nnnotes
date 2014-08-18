#!/bin/bash

WHERE=$( cd $(dirname $0) ; pwd -P )

# default configs
if [[ -e "$WHERE/CONFIG" ]]; then
	source $WHERE/CONFIG
fi

OPTIND=1 #reset getopts

while getopts t:f:b:s:r: opts; do
	case $opts in
		t)
			TITLE=$OPTARG
			;;
		f)
			FILE=$OPTARG
			;;
		b)
			BIB=$OPTARG
			;;
		s)
			STYLE=$OPTARG
			;;
		r)
			REF=$OPTARG
			;;			
		?)
			echo "invalid option -$OPTARG";
			exit;
			;;
		:)
			echo "option -$OPTARG requires an argument";
			exit;
			;;
	esac
done

shift $((OPTIND-1))

if [[ -z "$TITLE" ]]; then
	echo "No title provided. Aborting."
	exit;
fi

if [[ -d "$TITLE" ]]; then
	read -p "Specified note already exists... Do you wish to continue? " yn
	case $yn in
        [Yy]* ) rm -r $TITLE; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;		
	esac
fi

printf "\n-----\ntitle: $TITLE\nfile: $FILE\nbib: $BIB\ncsl: $STYLE\nref: $REF\nbibliographe: $BIBLIOGRAPHE_PATH\n-----\n"

# output
mkdir -p $TITLE

# copy templates
cp -aR $WHERE/template/* $TITLE

cd $TITLE

# file exists? copy to output
[ -z "$FILE" ] && echo "No file to copy. Make sure to reference in text in the note!" || curl -O $FILE 

# bibliography exists? fix makefile accordingly
[ -z "$BIB" ] && echo "No bibliography" || sed -i.bak "s#BIB\ :=#BIB\ := $BIB#g" Makefile

# csl style exists? fix makefile accordingly
[ -z "$STYLE" ] && echo "No csl style" || sed -i.bak "s#CSL\ :=#CSL\ := $STYLE#g" Makefile

if [ -z "$BIBLIOGRAPHE_PATH" ]; then
	echo "No bibliographe"	
else
	node $BIBLIOGRAPHE_PATH/refactorbib.js --data $BIB > tmpbib.json
	REFERENCE=$(node $BIBLIOGRAPHE_PATH/generatebib.js --data tmpbib.json --items [\"$REF\"] --output md)
	echo $REFERENCE
	rm tmpbib.json
	sed -i.bak "s~*MACHINE-REF*~$REFERENCE~g" notes.mmd
fi

# cleanup
rm *.bak
cd ..
