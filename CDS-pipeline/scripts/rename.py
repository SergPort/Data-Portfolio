# -*- coding: utf-8 -*-
"""
Author: Sergio

Modules:

    info_extract (Rosie - Sergio)

    rename (Sergio)

"""
import re
import sys

### function to extract info from FASTA heading
def info_extract(line):
    '''
    This module extracts information out of a certain specified gene

    Header regex format: >Gene.(\d+)::(\w+-\w+.\w+):.+ORF type:(\w+) len:(\d+) \((.)\),score=(.+) .+:(.+)\(.\)


    Args:

        gene_n: Gene number to be searched

        file: File name containing library of protein sequences

    Returns:

        new_header2: Gene information or error in case the sequence is not found

    Example:

        info_extract("90", "Tcongo_procyclic")

            Gene number: 90, EST identifier: TCpc-01a04.p1k, ORF type: missing stop codon, ORF length: 114, Strand: direct, ORF coordinates in EST: 3-344

    '''
    #Dictionary of Transdecoder ORF types
    ORF_type_dict = {
        "complete": "complete",
        "5prime_partial": "missing_start",
        "3prime_partial": "missing_stop",
        "internal": "missing_start_stop"
        }

    strand_dict = {
        "+": "direct",
        "-": "reverse"
        }


    header_regex = re.compile('>Gene.(?P<Gene_ID>\d+)::(?P<EST_ID>\w+-?\w+.\w+):.+ORF type:(?P<ORF_type>\w+) len:(?P<ORF_length>\d+) \((?P<Strand>.)\),score=(?P<Score>.+) .+:(?P<ORF_coords>.+)\(.\)')
    header_info = header_regex.match(line)
    header_dict = header_info.groupdict()

    #reformatting ORF type and strand info
    header_dict['ORF_type'] = ORF_type_dict[header_dict['ORF_type']]
    header_dict['Strand'] = strand_dict[header_dict['Strand']]

    #formatting header from dictionary
    # TransDecoder header output style:
    # >Gene.1::TCep-01a02.p1k::g.1::m.1 Gene.1::TCep-01a02.p1k::g.1  ORF type:5prime_partial len:126 (+),score=6.64 TCep-01a02.p1k:2-379(+)
    new_header2 = ">EST={EST_ID} ORF_type={ORF_type} ORF_length={ORF_length} Strand={Strand} ORF_coordinates_in_EST={ORF_coords} TransDecoder_score={Score}".format(**header_dict)
    # new_header2 output:
    # >EST=TCep-01a02.p1k ORF_type=missing_stop ORF_length=230 Strand=direct ORF_coordinates_in_EST=33-689 TransDecoder_score=6.64

    return new_header2

def rename(file):
    '''
    This module renames the headers of each gene to only include the gene number for easier access throughout the pipeline

    Args:

        file: File name containing library of protein sequences

    Returns:

        new_file: returns the name of the file being written with renamed sequences in FASTA format

    Example:

        rename("Tcongo_procyclic")
            "Tcongo_procyclic_fix_new.fas.transdecoder.pep"

        #output also includes file with renamed sequences

    '''

    #set "file" variable to desired file by user and open read and write files:
    # prot = open(f"{file}_fix.fas.transdecoder.pep", 'r')
    # new_file = f"{file}_fix_new.fas.transdecoder.pep"
    prot = open(f"{file}", 'r')
    new_file = f"{file}.renamed.pep"
    prot2 = open(new_file, 'w')


    #start reading file from line[0]
    line = prot.readline()

    #while loop keeps running till the end of the file (line = '')
    while line != '':
        #if line is header, write in new file the fasta header and gene number
        if line[0] == ">":
            head_info = info_extract(line)
            prot2.write(head_info)
            prot2.write("\n")
        #if line is not a header, write the whole sequence in
        else:
            prot2.write(line)

        #set the line variable to the next line in the file
        line = prot.readline()

    #to make gene_finder script work
    prot2.write('>')

    return new_file

rename(f"temp/{sys.argv[1]}.transdecoder.pep")
