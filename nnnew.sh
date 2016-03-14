#!/bin/bash

#Black        0;30     Dark Gray     1;30
#Blue         0;34     Light Blue    1;34
#Green        0;32     Light Green   1;32
#Cyan         0;36     Light Cyan    1;36
#Red          0;31     Light Red     1;31
#Purple       0;35     Light Purple  1;35
#Brown/Orange 0;33     Yellow        1;33
#Light Gray   0;37     White         1;37

BLUE='\033[0;34m'
NC='\033[0m'

WHERE=$( cd $(dirname $0) ; pwd -P )

# default configs
if [[ -e "$WHERE/CONFIG" ]]; then
	source $WHERE/CONFIG
fi

print_usage() {
	printf "usage: ${BLUE}nnnew.sh -t [title] -f [pdf file] -b [json biblio] -s [style] -r [reference]${NC}"
}

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
			#echo "invalid option -$OPTARG";
			print_usage
			exit;
			;;
		:)
			echo "option -$OPTARG requires an argument";
			print_usage
			exit;
			;;
	esac
done

shift $((OPTIND-1))

if [[ -z "$TITLE" ]]; then
	echo "No title provided. Aborting."
	print_usage
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

touch notes.mmd

# file exists? copy to output
[ -z "$FILE" ] && echo "No file to copy. Make sure to reference in text in the note!" || curl -O $FILE 

# bibliography exists? fix makefile accordingly
[ -z "$BIB" ] && echo "No bibliography" || sed -i.bak "s#BIB\ :=#BIB\ := $BIB#g" Makefile

# csl style exists? fix makefile accordingly
[ -z "$STYLE" ] && echo "No csl style" || sed -i.bak "s#CSL\ :=#CSL\ := $STYLE#g" Makefile

if [ -z "$BIBLIOGRAPHE_PATH" ]; then
	echo "No bibliographe"	
else
	./parse/refactorbib.py $BIB > tmpbib.json
	REFERENCE=$(node $BIBLIOGRAPHE_PATH/generatebib.js --data tmpbib.json --items [\"$REF\"] --output md)
	AUTHOR=$(whoami)
	DATE=$(date +%Y\-%m\-%d)
	echo $REFERENCE
	rm tmpbib.json
	sed -i.bak "s~*MACHINE-REF*~$REFERENCE~g ; s~%\ title~%\ $REFERENCE~g ; s~%\ author~%\ $AUTHOR~g ; s~%\ date~%\ $DATE~g" notes.mmd
fi

# cleanup
rm *.bak
cd ..
