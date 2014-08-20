#!/bin/bash

WHERE=$( cd $(dirname $0) ; pwd -P )

# default configs
if [[ -e "$WHERE/CONFIG" ]]; then
	source $WHERE/CONFIG
fi

OPTIND=1 #reset getopts

while getopts :b: opts; do
	case $opts in
		b)
			BIB=$OPTARG
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

node $BIBLIOGRAPHE_PATH/refactorbib.js --data $BIB --index --print
