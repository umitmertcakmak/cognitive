#!/bin/bash

###############################################################################
# Version:      0.1v
# Description:  This script is used for setting the version for the
#               Pipeline python module.
# Author:       Krishna (krishnamurthy.a@in.ibm.com)
# Change Log:
#
#
###############################################################################


logMsg() {
    curTs=$(date +"%Y-%m-%d:%H.%M.%S.%N")
    lmsg="$1"
    printf "%s [NGP-PYTHONBUILD] %s" $curTs "$lmsg"
}

newline(){
    printf "\n"
}

termMsg(){
    printf "\nTERMINATING -- %s" "$COMMAND"
}

BASECMD=$0
PACKNAME=$1
VERSION=$1
COMMAND="$BASECMD $VERSION"

# Generate the file with the appropriate version
logMsg "Updating __init__.py and setup.py file with the appropriate version"
newline
sed 's/__version__ = .*/__version__ =  '"'"$VERSION"'"'/g' ./pipeline/__init__.py > ./pipeline/.__init__.py
mv ./pipeline/.__init__.py pipeline/__init__.py

sed 's/VERSION=.*/VERSION='"'"$VERSION"'"'/g' setup.py > ./.setup.py
mv ./.setup.py ./setup.py


printf "\nDONE --- %s \n" "$COMMAND"

