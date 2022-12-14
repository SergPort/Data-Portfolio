#!/usr/bin/env bash

#----------------------------
# User guide - macOS version
#----------------------------
# - Put fasta (or gzip compressed fasta) sequence files in ./fasta folder, with
#   .fas (or .fas.gz for gzip compressed fasta) file extension
# - Execute script with no arguments, i.e.:
#   $ ./test-macOS.sh
# - Output files can be found in the ./output folder
#----------------------------

help()
{
    echo "generate-CDS-macOS.sh help page."
    echo
    echo "Generate CDS (coding protein sequences) from fasta (.fas) or gzipped fasta (.fas.gz) files."
    echo "generate-CDS-macOS.sh should be run with no arguments (or -h for help)."
    echo
    echo "Syntax: ./generate-CDS-macOS.sh"
    echo "        ./generate-CDS-macOS.sh -h"
    echo
}

# check if the following flags/arguments are used
# h flag doesn't take any arguments, i and s flags do.
while getopts h flag; do
    case "${flag}" in
        # run help function and exit script
        h) help
           exit 1;;
        # show error message when given inavalid arguments and exit script
        *) echo "Invalid argument. generate-CDS-macOS runs with no arguments (or -h for help)"
           exit 1
    esac
done

# assign script path to variable
scriptpath="$( cd -- "$(dirname "$0")" &> /dev/null; pwd -P )"
# assign CDS-pipeline path to variable (parent directory of scriptpath) and
# change to directory
cdspath="${scriptpath%/*}"
cd $cdspath

# Print ASCII art :)
echo "____ ____ _  _ ____ ____ ____ ___ ____    ____ ___  ____ "
echo "| __ |___ |\ | |___ |__/ |__|  |  |___ __ |    |  \ [__  "
echo "|__] |___ | \| |___ |  \ |  |  |  |___    |___ |__/ ___] "
echo

# check if dependencies are installed and install if they are not
# set dependency check variable
dependency_check='0'
# set apt update variable
apt_update_run='0'
# check for transdecoder apt package
if [ ! -d ../TransDecoder ]; then
    echo "Dependency 'TransDecoder' not installed"
    echo "- Updating WSL Ubuntu packages - this may take a while!"
    # update and upgrade apt packages
    #sudo apt update &> /dev/null && sudo apt upgrade -y &> /dev/null
    # modify apt update variable
    apt_update_run='1'
    echo "- Installing TransDecoder  - please wait!"
    # install transdecoder apt package
    #sudo apt install -y transdecoder &> /dev/null
    # update dependency check variable
    dependency_check='1'
fi
# check for pip package
if ! which pip | grep "pip" &> /dev/null; then
    echo "Dependency 'pip' not installed"
    # if apt update and upgrade not already run, update and upgrade apt packages
    if [ "$apt_update_run" == "0" ]; then
        echo "- Updating WSL Ubuntu packages (APT update and upgrade)"
        #sudo apt update &> /dev/null && sudo apt upgrade -y &> /dev/null
    fi
    echo "- Installing pip"
    # install pip package
    #sudo apt install -y python3-pip &> /dev/null
    # update dependency check variable
    dependency_check='1'
fi
# check for biopython pip package
if ! pip list | grep "biopython" &> /dev/null; then
    echo "Dependency 'Biopython' not installed"
    echo "- Installing Biopython"
    # install biopython pip package
    #pip install biopython &> /dev/null
    # update dependency check variable
    dependency_check='1'
fi
# let user know if dependency checks have caused any updates
if [ "$dependency_check" == "1" ]; then
    echo "$(tput setaf 2)Dependency installation complete$(tput sgr0)"
    echo
fi

# make fasta folder if it doesnt exist and exit script
if [ ! -d fasta ]; then
    echo "'fasta' folder not detected. Making folder in current directory."
    mkdir -p fasta
    echo "$(tput setaf 3)Please put FASTA files in the 'fasta' folder, then run this script again.$(tput sgr0)"
    exit 1
fi

# detect if fas or fas.gz files exist in fasta folder and if not, exit script
count_fasta=`ls -1 fasta/*.fas 2> /dev/null | wc -l`
count_fas_gz=`ls -1 fasta/*.fas.gz 2> /dev/null | wc -l`
if [ $count_fasta == 0 ] && [ $count_fas_gz == 0 ]; then
    echo "FASTA files not found. This script works with .fas or .fas.gz (gzip compressed) FASTA files."
    echo "$(tput setaf 3)Please put FASTA files in the 'fasta' folder, then run this script again.$(tput sgr0)"
    exit 1
fi

# make other folders used by script if they don't exist
if [ ! -d temp ]; then
    echo "'temp' folder not detected. Making folder."
    mkdir -p temp
fi
if [ ! -d output ]; then
    echo "'output' folder not detected. Making folder."
    mkdir -p output
fi
if [ ! -d output/excluded_sequences ]; then
    echo "'output/excluded_sequences' folder not detected. Making folder."
    mkdir -p output/excluded_sequences
fi

cd "${cdspath}/fasta"
# count number of compressed fas (.fas.gz) files
count_fas_gz_files=`ls -p *.fas.gz 2> /dev/null | grep -v / | wc -l`
# if there is one or more fas.gz file, inform user
if [ $count_fas_gz_files -gt 0 ]; then
    echo "Extracting compressed FASTA files:"
fi
# if present, decompress gzip'ed FASTA file/s
for f in *.fas.gz; do
    # if no .fas.gz files detected, skip loop to avoid globbing
    [ -f "$f" ] || continue
    gunzip -c "${f}" > "`echo $f | sed 's/.gz//'`"
    echo "- '${f}' extracted as ${f%.gz}'"
done

# if present, replace spaces with underscores in fasta file names - workaround
# for TransDecoder not working with filename spaces
# count number of .fas files containing filename spaces
count_fas_files_with_spaces=`ls -p *.fas 2> /dev/null | grep -v / | grep " " | wc -l`
# if there is one or more fas file with filename spaces, warn user
if [ $count_fas_files_with_spaces -gt 0 ]; then
    echo "$(tput setaf 3)Warning: TransDecoder doesn't work properly with spaces in filenames$(tput sgr0)"
fi
# for every fas file with a space in its filename, replace spaces with
# underscores
for f in *.fas; do
    if [[ $f == *" "* ]] ; then
        mv "$f" "${f// /_}"
        # let user know which file has been renamed and to what
        echo "- '${f}' renamed to '${f// /_}' to continue analysis"
    fi
done

echo
# count number of fasta files to analyse
count_fasta_again=`ls -1 *.fas 2> /dev/null | grep -v / | wc -l | xargs`
echo "Processing $count_fasta_again files:"
echo

# loop through every fasta file in the "fasta" folder, and check for non-GATC
# sequence bases using rmseq.py
cd $cdspath
echo "Checking for sequences containing non-GATC bases incompatible with TransDecoder:"
for f in fasta/*.fas; do
    # spawn separate shell for code within parentheses and run in parallel
    (
        # pass fasta files to rmseq.py script to detect non-GATC characters in
        # sequences
        python3 scripts/rmseq.py "${f#fasta/}"
        # calculate sequence loss percentage
        # number of sequences in original file
        a=`grep -c "^>" "${f}"`
        # number of sequences in excluded_sequences file
        b=`grep -c "^>" "temp/${f#fasta/}.excluded_sequences"`
        # non-GATC sequence percentage calculation up to two decimal places
        c=`bc <<<"scale=2 ; 100 * $b / $a"`
        # if all sequences contain non-GATC characters, let user know, delete
        # non-GATC sequence file and empty rmseq file, and exit script
        if [ ${c} == 100.00 ]; then
            rm -rf temp/${f#fasta/}.excluded_sequences temp/${f#fasta/}.rmseq
            echo "- '${f#fasta/}': $(tput setaf 3)All sequences contain non-GATC bases - analysis halted for file$(tput sgr0)"
            exit 1
        # if no sequences contain non-GATC characters, let user know and delete
        # empty non-GATC sequence file
        elif [ ${c} == 0 ]; then
            rm -rf temp/${f#fasta/}.excluded_sequences
            echo "- '${f#fasta/}': No sequences contain non-GATC bases"
        # if some sequences contain non-GATC characters, let user know
        # percentage and move non-GATC sequence file to output folder
        else
            mv temp/${f#fasta/}.excluded_sequences output/excluded_sequences/${f#fasta/}.excluded_sequences
            echo "- '${f#fasta/}': ${c}% of sequences containing non-GATC bases copied to 'output/excluded_sequences/${f#fasta/}.excluded_sequences'"
        fi
    ) &
done
# wait for all parallel tasks to finish before continuing
wait
echo

echo "TransDecoder predicting CDS - please wait:"
# run subsequent commands in "temp" folder
cd "${cdspath}/temp"
# loop through every rmseq files in the "temp" folder, and use TransDecoder to
# predict CDS
for f in *.rmseq; do
    # spawn separate shell for code within parentheses and run in parallel
    (
        # TransDecoder commands - hide TransDecoder output (stdout and stderr)
        # by redirection
        ../../TransDecoder/TransDecoder.LongOrfs -t "${f}" &> /dev/null
        ../../TransDecoder/TransDecoder.Predict -t "${f}" &> /dev/null
        echo "- '${f%.rmseq}' complete"
    ) &
done
# wait for all parallel tasks to finish before continuing
wait
echo

echo "Renaming sequences headers in human-readable format:"
# run subsequent commands in CDS-pipeline folder
cd "${cdspath}"
# loop through every rmseq files in the "temp" folder, and rename sequence
# headers with rename.py
for f in temp/*.rmseq; do
    # spawn separate shell for code within parentheses and run in parallel
    (
        # pass rmseq files to rename.py to modify sequence headers
        python3 scripts/rename.py "${f#temp/}"
        # strip 'temp/' from start of filename
        f2="${f#temp/}"
        echo "- '${f2%.rmseq}' complete"
    ) &
done
# wait for all parallel tasks to finish before continuing
wait
echo

# 0.5 second pause in command output to prevent too much code appearing on the
# screen
sleep 0.5
echo "Cleaning 'temp' directory"
# remove working files created by this script. Specifying files to remove
# rather than deleting all files in the directory with a wildcard command for
# development convenience
cd "${cdspath}/temp" && rm -rf *.rmseq \
*.rmseq.transdecoder_dir \
*.rmseq.transdecoder_dir.__checkpoints \
*.rmseq.transdecoder.bed \
*.rmseq.transdecoder.cds \
*.rmseq.transdecoder.gff3 \
pipeliner.*.cmds \
*.rmseq.transdecoder.pep

sleep 0.5
echo "Moving file/s to 'output' folder"
# move every fasta header renamed file to the output folder and rename
# appropriately
for f in *.fas.rmseq.transdecoder.pep.renamed.pep; do
    mv "$f" "`echo ../output/$f | sed 's/.fas.rmseq.transdecoder.pep.renamed//'`"
done
# return from temp folder to CDS-pipeline folder
cd "${cdspath}"
sleep 0.5
echo "$(tput setaf 2)Process complete. Please find CDS files in 'output' folder as .pep files.$(tput sgr0)"
echo
