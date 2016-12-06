#!/bin/sh

###############################################################################
# Version:      0.2v
# Description:  This script is used for generating API documentation for
#               for Pipeline Python APIs
# Author:       Venkateshwara K Goutham (vegoutha@in.ibm.com)
# Change Log:
###############################################################################
export PATH="$PATH:/usr/bin"

# Verify SPHINX Installation
SPHNIX_PATH=`type sphinx-build | wc -l| tr -d ' ' `

if [[ $SPHNIX_PATH -eq 0 ]]; then
    printf "\n*** ERROR !  Failed to find sphinx-build binary file\n"
    exit 1
fi

# Generate API Documentation
VERIFY_USERID=`env | grep -i USER | grep jenkins | wc -l| tr -d ' '`

printf "\nGenerating API documentation\n"

if [[ $VERIFY_USERID -ge 1 ]]; then
    export PYTHONPATH="$PYTHONPATH:/var/local/lib/py4j-0.9-src.zip:/var/local/lib/pyspark.zip"
    make html

# Verify the environment variable SPARK_HOME to use python libraries
else
    SPARK_ENV=`env|grep -i SPARK_HOME| wc -l| tr -d ' '`

    if [[ $SPARK_ENV -eq 0 ]]; then
        printf "\n*** ERROR !  Generation of API documentation failed. Verify environment variable SPARK_HOME is set.\n"
        exit 1
    else
        OS_TYPE=`uname -a|cut -d" " -f1|cut -d"_" -f1|tr '[:lower:]' '[:upper:]'| tr -d ' '`

        Mac_Type=`uname -a|grep -i kernel|wc -l| tr -d ' '`

        if [[ Mac_Type -ge 1 ]]; then
            OS_TYPE="MAC"
        fi

        printf $OS_TYPE
        printf $Mac_Type

        case "$OS_TYPE" in
           "MAC") export PYTHONPATH="$PYTHONPATH:$SPARK_HOME/python/lib/py4j-0.9-src.zip:$SPARK_HOME/python/lib/pyspark.zip"
           ;;
           "LINUX") export PYTHONPATH="$PYTHONPATH:$SPARK_HOME/python/lib/py4j-0.9-src.zip:$SPARK_HOME/python/lib/pyspark.zip"
           ;;
           "CYGWIN") set PYTHONPATH="$PYTHONPATH;$SPARK_HOME\python\lib\py4j-0.9-src.zip;$SPARK_HOME\python\lib\pyspark.zip"
           ;;
           *) printf "\n*** ERROR ! Unable to recognize OS Type.\n"; exit 1
        esac

        make html
    fi
fi

