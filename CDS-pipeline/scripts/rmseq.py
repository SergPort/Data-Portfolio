#!/usr/bin/env python

"""
Python script to remove fasta sequences containing non-GATC characters from a
fasta file and write them to another file

Usage: $ ./rmseq.py inputfile
i.e. $ ./rmseq.py sequences.fas
"""

import sys
from Bio import SeqIO

# create writeable file for GATC sequences
out = open(f"temp/{sys.argv[1]}.rmseq", "w")
# create writeable file for non-GATC sequences
excluded_sequences = open(f"temp/{sys.argv[1]}.excluded_sequences", "w")

# bases to include in GATC sequence output file
allowed_bases = ['A', 'T', 'G', 'C']
# open for loop for every set of fasta sequences in file
for record in SeqIO.parse(f"fasta/{sys.argv[1]}", "fasta"):
    # convert sequence to upper case to match allowed_bases
    record_upper = record.seq.upper()
    total_dna_bases = 0
    # add up the number of times each base in allowed_bases occurs
    for base in allowed_bases:
        total_dna_bases += record_upper.count(base)
    # if total ocurrences of allowed_bases matches number of bases in sequence,
    # write to GATC sequence output file, otherwise write sequence to non-GATC
    # file
    if total_dna_bases == len(record):
        out.write(record.format("fasta"))
    else:
        excluded_sequences.write(record.format("fasta"))
