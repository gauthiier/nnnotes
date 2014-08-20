#!/bin/bash

WHERE=$( cd $(dirname $0) ; pwd -P )

# default configs
if [[ -e "$WHERE/CONFIG" ]]; then
	source $WHERE/CONFIG
fi

OPTIND=1 #reset getopts

OUT=txt # default output

while getopts :b:r:o: opts; do
	case $opts in
		b)
			BIB=$OPTARG
			;;
		r)
			REF=$OPTARG
			;;			
		o)
			OUT=$OPTARG
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

# bibliographe's path set?
if [[ -z "$BIBLIOGRAPHE_PATH" ]]; then 
	echo "No bibliographe"; 
	exit;
fi

# bibliography exists?
if [[ -z "$BIB" ]]; then
	echo "No bibliography"
	exit;
fi 

# referebce exists?
if [[ -z "$REF" ]]; then
	echo "No reference"
	exit;
fi 

node $BIBLIOGRAPHE_PATH/refactorbib.js --data $BIB > tmpbib.json
REFERENCE=$(node $BIBLIOGRAPHE_PATH/generatebib.js --data tmpbib.json --items [\"$REF\"] --output $OUT)
echo $REFERENCE
rm tmpbib.json

