# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 18:55:05 2021

@author: Sergio
"""
from itertools import chain
import os
import sys

def names(choice, file):

    """
    Manipulate user input for sequence function

    Args:

        file: name of sequence library

    Inputs:

        choice: gene identifiers to be used. 

    Returns:

        filename: string to be used as output filename 

        split_phrase: manipulated "choice" argument for sequence function

        choice: choice argument with "any_all" stripped out

        any_all: user input stripped from choice argument

    """
    #set split_phrase variable and name variable for naming and looping purposes
    split_phrase = []
    name = []

    # In case of incorrect spelling, catch indexing error of name variable
    try:
        # Split user input for output file name
        choice = choice.split(",")

    
        #if user does not input an all or any argument, automatically use "any" as it won't raise errors in any situation as "all" would if two values for the same option are given
        if choice[-1] != "all" and choice[-1] != "any":
            all_any = "any"
            #let user know
            print("Program set to 'any' due to empty variable.")

        else:
            #set all_any variable
            all_any = choice[-1]
            #remove the all_any variable from choice
            choice.pop()

        for i in choice:
            split_phrase.append(i.split("="))
    
    except IndexError:
        #If this doesn't work, we have a formatting error and we can let the user know.
        return "\nSyntax Error: Input not in right formatting. Please type an accepted phrase followed by an ID (e.g. Strand=reverse,orf_type=complete,all)."
    
    for option in split_phrase:
        # splits all the words of user input for output filename
        name.append(option[0].split())
        name.append(option[1].split())
    # set output filename
    filename = f"{file}-{'_'.join(chain.from_iterable(name))}_{all_any}.pep"
    # open output file

    return filename, split_phrase, all_any, choice

def sequence(phrases, choice, file, prot):

    """
    Extract protein sequences based on their gene ID

    Args:

        file: name of sequence library

    Inputs:

        choice: gene identifier to be used. Given a list of possible identifier types to use

        correct input format:

            phrase: identifier

        example:

            ORF type: missing stop codon

    Returns:

        returns protein sequence corresponding to gene ID

    Example:

        sequence("procyclic")

            ['Gene number','EST identifier', 'ORF type','ORF length','Strand','ORF coordinates in EST']: Gene number: 1

            'ARVGFCRRTMAKKVKSKVDTINTKIQLVMKSGKYVLGTQQSLKTLR
            QGRSKLVVISANCPPIRKAEIEYYCTLSKTPIHHYSGNNLDLGTACG
            RHFRACVLSITDVGDSDIAA*'

    """

    filename, split_phrase, all_any, choice = names(choice, file)

    sequences = open(f"../output/{filename}", "w")

    # read lines
    lines = prot.readlines()
    # est counts written lines in output file
    est = 0

    # start loop if input is within headers (phrases options)

    for i in split_phrase:
        if i[0] in phrases:
            continue
        else:
            # raise error in case identifier (such as gene number, orf type, etc) is not in the headers
            # remove file that's been opened if phrase is not accepted
            sequences.close()
            os.remove(f"../output/{filename}")
            return "\nInput Error: Input not in accepted phrases, please read through input options carefully."
        
    #loop through file
    for line in range(len(lines)):
        # start counter for checking lines and another for the all_any function
        count = 1
        check = 0
        # extract gene ID from header
        if lines[line][0] == ">": 
            for i in choice:
                if i in lines[line].lower():
                    check += 1
            #if all_any is set to all, then the check needs to be equal to the amount of options (all the options present in sequence)
            if all_any == "all":
                if check == len(choice):
                    est += 1
                    # added space or comma to stop longer unintended numbers from being picked out
                    sequences.write(lines[line])
                    # loops through lines until finding a new header and writes them down one by one
                    while lines[line + count][0] != ">":
                        sequences.write(lines[line + count])
                        # raise counter to check next line
                        count += 1
            else:
                if check == 1:
                    est += 1
                    # added space or comma to stop longer unintended numbers from being picked out
                    sequences.write(lines[line])
                    # loops through lines until finding a new header and writes them down one by one
                    while lines[line + count][0] != ">":
                        sequences.write(lines[line + count])
                        # raise counter to check next line
                        count += 1

    # close output file and check file size
    sequences.close()
    # if no ests are found (thus output file is empty) remove it from system
    if est == 0:
        os.remove(f"../output/{filename}")
        return f"\n\033[1;32;40mThe search found {est} ESTs. \n"
    # green completion printout with output of number of ESTs:
    return f"\n\033[1;32;40mThe search found {est} ESTs. Output ESTs can be found in 'output' folder as '{filename}'.  \n"

# function to run python file
def run():
    """
    Run gene finder program.

    Returns:

        returns output of sequence function OR an error message if input file is not found.

    """
    # phrases in lower case to prevent traceback errors
    phrases = ["gene", "est", "orf_type", "orf_length", "strand", "orf_coordinates_in_est"]
    # user input
    file = sys.argv[1]
    try:
        # open file
        prot = open(f"../output/{file}.pep", "r")
        # if file isn't found, raise error
    except FileNotFoundError:
        return print(
            "\nFileNotFound Error: That file name is not recognized. Try again."
        )

    choice = sys.argv[2]

    return print(sequence(phrases, choice.lower(), file, prot))


run()
