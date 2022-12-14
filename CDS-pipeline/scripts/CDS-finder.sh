#!/usr/bin/env bash

# Bash script to retrieve specific sequences from a .pep file given header info.
# The bash script collects user input and sets the script path, then calls the
# python script CDS-finder.py

# script help function prints out help message
help()
{
    echo "CDS Finder help page."
    echo
    echo "Find sequences from a .pep file given a FASTA header string to search for."
    echo "CDS Finder can be run with either zero, one (-h) or two (-i, -s) arguments."
    echo
    echo "Syntax: ./CDS-finder.sh -i -s"
    echo "        ./CDS-finder.sh -h"
    echo
    echo "Options:"
    echo "-h      print this help message"
    echo "-i      .pep filename from 'output' folder"
    echo "-s      FASTA header string to search for"
    echo
    echo "Example: ./CDS-finder.sh -i Tcongo_procyclic.pep -s EST=TCpc-01a01.p1k"
    echo
}

# check if the following flags/arguments are used
# h flag doesn't take any arguments, i and s flags do.
while getopts hi:s: flag; do
    case "${flag}" in
        # run help function and exit script
        h) help
           exit 1;;
        # assign argument to variable input_file
        i) input_file=${OPTARG};;
        # assign argument to variable query_string
        s) query_string=${OPTARG};;
        # show error message when given inavalid arguments and exit script
        *) echo "Invalid argument"
           exit 1
    esac
done

# assign script path to variable
scriptpath="$( cd -- "$(dirname "$0")" &> /dev/null; pwd -P )"
# change to script directory
cd $scriptpath

echo "Welcome to the CDS Finder"
echo
# if no arguments given then prompt user for input_file and query_string variable values
if [ $# -eq 0 ]; then
    read -p "Enter name of .pep sequence file from 'output' folder (e.g. Tcongo_procyclic): " input_file
    # if input_file doesn't exist, let user know and exit script
    if [[ ! -f ../output/${input_file}.pep ]]; then
        echo "$(tput setaf 1)File not found. Please enter a filename from the 'output' folder.$(tput sgr0)"
        exit 1
    fi
    # print out user options
    echo
    echo "Options (separated by ','):"
    echo "1: EST"
    echo "    (e.g. EST=TCep-01a09.p1k)"
    echo "2: ORF_type"
    echo "    (e.g. ORF_type=missing_start/missing_stop/missing_start_stop/complete)"
    echo "3: ORF_length"
    echo "    (e.g. ORF_length=190)"
    echo "4: Strand"
    echo "    (e.g Strand=direct/reverse)"
    echo "5: ORF_coordinates_in_EST"
    echo "    (e.g. ORF_coordinates_in_est=150-250)"
    echo "6: TransDecoder_score"
    echo "    (e.g. TransDecoder_score=47.82)"
    echo "7: All options ('all') or any of the options (leave empty). NOTE: specify this variable last."
    echo "    (e.g. orf_type=complete,strand=reverse,all)"
    echo
    read -p "Enter FASTA header option to search for: " query_string
# if four flags/arguments given, continue script
elif [ $# -eq 4 ]; then
    :
# if neither zero or four arguments/flags given, let the user know and exit script
else
    echo "$(tput setaf 1)Wrong number of arguments. Please provide either zero or two arguments, or -h for help.$(tput sgr0)"
    exit 1
fi

# pass file and search variables to CDS finder python script
python3 CDS-finder.py "$input_file" "$query_string"
