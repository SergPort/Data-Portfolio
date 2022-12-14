# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 17:09:52 2020

@author: sergi
"""

#Dictionary containing single letter amino acids created. later reffered to as 'dict2' in 'transs' function.
Codon_Letters = {'ALA' : 'A' , 'ARG' : 'R' , 'ASN' : 'N' , 'ASP' : 'D' , 
                 'ASX' : 'B' , 'CYS' : 'C' , 'GLU' : 'E' , 'GLN' : 'Q' , 
                 'GLX' : 'Z' , 'GLY' : 'G' , 'HIS' : 'H' , 'ILE' : 'I' , 
                 'LEU' : 'L' , 'LYS' : 'K' , 'MET' : 'M' , 'PHE' : 'F' , 
                 'PRO' : 'P' , 'SER' : 'S' , 'THR' : 'T' , 'TRP' : 'W' , 
                 'TYR' : 'Y' , 'VAL' : 'V' , '***' : '*'} 


#FASTA file reading function. Reads sequence and creates separate string containing lower case bases for codon table to read.
#If sequence is already lower case they wont be converted and we get the same result
def load_fasta(f):
    seq_title = f.readline()

# initialise input sequence string, creates 's' empty list
    s =''


# accumulate sequence line by line and insert in s
    
    print(seq_title)
    while True:
        seq_line = f.readline()

        if seq_line == '':
            break  
        else:
            s += seq_line.strip().lower()
    print('The sequence contains %d bases\n\n' % len(s))
    return (seq_title,s)



#Codon Table function. Creates dictionary 'cod' (later uses variable dict1 to translate codons in function 'transs')
def load_code(f):
    cod = {}
    
    while True:
        cod_line = f.readline()
        if cod_line == '':
            break
        else:
            c = cod_line.strip().split()
            cod[c[0]] = c[1]

    return cod

#comp function to form complementary strand by swapping out bases fr their complement and creating list comp_strand:


def comp(strand):
    comp_strand = ''
    for rna in strand:
        if rna == 'a':
            comp_strand += 't'
        elif rna == 't':
            comp_strand += 'a'
        elif rna == 'c':
            comp_strand += 'g'
        elif rna == 'g':
            comp_strand += 'c'
        else:
            comp_strand += ''
    return comp_strand



#Separates acids and comp.acids lists in 6 frames. Also forms frames 4-6 in reverse to find ORFs later, as the strands are read N to C to find ORFs.
def frames(acids, comp_acids):
    F1 = acids[::3]
    preF2 = acids[1:]
    F2 = preF2[::3]
    preF3 = acids[2:]
    F3 = preF3[::3]
    F5 = comp_acids[::3]
    preF6 = comp_acids[1:]
    F6 = preF6[::3]
    preF4 = comp_acids[2:]
    F4 = preF4[::3]
    rF4 = F4[::-1]
    rF5 = F5[::-1]
    rF6 = F6[::-1]
    return(F1, F2, F3, F4, F5, F6, rF4, rF5, rF6)


#Takes frames formed by function frames and separates frames list every 20th character and prints out codons and amino acids in 6 frames

def frames1(f1, f2, f3, f4, f5, f6, strand1, strand2):
    n = 20
    a1 = [f1[i:i+n] for i in range(0, len(f1), n)]
    a2 = [f2[i:i+n] for i in range(0, len(f2), n)]
    a3 = [f3[i:i+n] for i in range(0, len(f3), n)]
    a4 = [f4[i:i+n] for i in range(0, len(f4), n)]
    a5 = [f5[i:i+n] for i in range(0, len(f5), n)]
    a6 = [f6[i:i+n] for i in range(0, len(f6), n)]
    frames2(a1, a2, a3, a4, a5, a6, strand1, strand2)
    return(a1, a2, a3, a4, a5, a6)
 

#frame2 function takes frames separated by frame1 function and formats + outputs 6 frame or 1 frame translation in 1 or 3 amino acids (depending on input 'choice' from while True loop)

fun = lambda x: x * 3 
def frames2(a1, a2, a3, a4, a5, a6, strand1, strand2):
    if choice == '1':
        sp = '  '
        e = 2
    elif choice == '3':
        sp = ''
        e = 0
    #'sp', 'e' and the 'ss' variables are used for spacing issues between amino acid format and different frames spacing on strand.
    while True:
        nmbr = input('\nPrint Frames: (f1-f6 OR all):')
        if nmbr == 'ALL' or nmbr == 'all' or nmbr == 'All' or nmbr == 'f1' or nmbr == 'f2' or nmbr == 'f3' or nmbr == 'f4' or nmbr == 'f5' or nmbr == 'f6':
            if nmbr == 'f1':
                fr = a1
                strand = strand1
                ss = ''
                break
            if nmbr == 'f2':
                fr = a2
                strand = strand1
                ss = ' '
                break
            if nmbr == 'f3':
                fr = a3
                strand = strand1
                ss = '  '
                break
            if nmbr == 'f4':
                fr = a4
                strand = strand2
                ss = '  '
                break
            if nmbr == 'f5':
                fr = a5
                strand = strand2
                ss = ''
                break
            if nmbr == 'f6':
                fr = a6
                strand = strand2
                ss = ' '
                break
            else:
                break
        else:
            print('Sorry, that input is not available. Try again.')          
    print('\nBASIC FORMAT:')
    print('')
    print('-' * 75)
    print('')
    print('Frame______A  M  I  N  O    A  C  I  D    S  E  Q  U  E  N  C  E_____Amino acid-number')
    print('Base n°_______________________cdna sequence__________________________Base n°')
    for x in range(len(a1)):
        if x == '':
            break
        else:
            amnum = str((x+1)*20)
            seqnum = str(((x+1)*60)-59)
            if nmbr == 'All' or nmbr == 'all' or nmbr == 'ALL':
                print(len(a1[x]))
                print('')
                print('-' * 75)
                print('')
                print('F1', ' '*6, '%s' %sp.join(a1[x]), ' '* (63 - fun(len(a1[x]))), '\t', amnum)
                print('F2', ' '*6, ' %s' %sp.join(a2[x]),  ' '* (63 - fun(len(a2[x]))), '\t',amnum)
                print('F3', ' '*6, '  %s' %sp.join(a3[x]),  ' '* (63 - fun(len(a3[x]))), '\t',amnum)
                print('')
                print(seqnum, ' '*(8 - len(seqnum)), '%s'  %''.join(strand1[x]),  ' '* (63 - len(strand1[x])), '\t', str((x+1)*60))
                print(' '*(9), '----:----|'* 6)
                print(seqnum , ' '*(8 - len(seqnum)), '%s'  %''.join(strand2[x]),  ' '* (63 - len(strand2[x])),'\t', str((x+1)*60))
                print('')
                print('F6', ' '*6, ' %s' %sp.join(a6[x]),  ' '* (63 - fun(len(a6[x]))), '\t', amnum)
                print('F5', ' '*6, '%s' %sp.join(a5[x]), ' '* (63 - fun(len(a5[x]))), '\t', amnum)
                print('F4', ' '*6, '  %s' %sp.join(a4[x]), ' '* (63 - fun(len(a4[x]))), '\t', amnum) 
            #else command works as if nmbr doesnt equal 'All' or 'all' it must equal one of the frames as we already filtered through the nonsense in the while true loop earlier in the function.
            else:
                print('')
                print('-' * 85)
                print('')
                print(str(nmbr), ' '*(7 - len(str(nmbr))), ss, '%s' %sp.join(fr[x]), ' '*((62 + e) - len(strand1[x])), '\t', amnum)
                print(seqnum, ' '*(8 - len(seqnum)), '%s' %''.join(strand[x]), ' '*(62 - len(strand1[x])), '\t', str((x+1)*60))               


#Function that finds all start and stop codons in a sequence and creates a list of them 

def oframe(amino):
    oframes = []
    for i in range(0,len(amino)):
        if amino[i]=='Met' or amino[i]=='MET':
            temp = ''.join(amino[i::])
            oframe = temp[0:temp.find('***') + 3]
            oframes.append(oframe)
    return oframes


#Counts the number of real ORFs: filters out ORFs containing other start codons and other list items from oframe function that start with MET but dont contain a stop codon.
    
def ORFcounter(frame):
    ORFcounter = 0
    frame1 = oframe(frame)
    for x in frame1:
        if x == '':
            break
        else:
            for i in x:
                if i == 'M':
                    if x.count(i) < 2:
                        if '*' in x:
                            ORFcounter += 1
    return ORFcounter, frame1


#Simple function to add up all ORFs if choice1 == all (choice of which frame we w)

def ORFsum(orf1, orf2, orf3, orf4, orf5, orf6):
    Total_ORFs = orf1 + orf2 + orf3 + orf4 + orf5 + orf6
    return Total_ORFs


#Copy of ORFcounter function but instead of finding the frames it prints and formats them. Used separate function to only print out ORFs when needed.

def ORFprinter(frame):
    orf_count = 0
    for x in frame:
        if x == '':
            break
        else:
            for i in x:
                if i == 'M':
                    if x.count(i) < 2:
                        if '*' in x:
                            print('')
                            print('')
                            print('ORF N°', orf_count + 1, ': ')
                            print(x)
                            orf_count += 1


          
#Naming files in directory to start program. Gives user option to use their own fasta files and codon tables.
print('\n*All files being named must be in the same folder as the program*\n')
while True:
    Insert = input('FASTA file: ')
    try:
        file = open(Insert , 'r')
    except FileNotFoundError:
        print('ERROR: File not found. Please check the file directory.')
    else:
        break

while True:
    Insert2 = input('Codon Table ("Y" = standard codon table): ')
    try:
        if Insert2 == 'Y' or Insert2 == 'y':
            table = open('Codon_Table.txt', 'r')
        else:    
            table = open(Insert2 , 'r')
    except FileNotFoundError:
        print('ERROR: File not found. Please check the file directory.')
    else:
        break


# Giving functions variables to be used outside of function
#Created list 'acids' and 'comp_acids? and 1 letter acids.
dict1 = load_code(table)
dict2 = Codon_Letters
#a = seq_line and b = s in load_fasta
(a,b) = load_fasta(file)
#comp_strand creates function variable which defines complementary strand of whichever FASTA file is inputted
comp_strand = comp(b)
reverse = comp_strand[::-1]
       
#for loop creating acc list (collects bases in sequence and creates list with all possible 3 base combinations)
#trans variable uses dict1 (load_code function) to translate all 3 base combinations in acc
#acids list appened to get all possible acids translated from codons in acc

#acc1-16 used to create codons that loop back at start of string

def transs(seq):
#acc1-6 used to create codons that loop back at start of string
    acid = []
    longacid = []
    acc1 = seq[-2]
    acc2 = seq[-1]
    acc3 = seq[0]
    acc4 = seq[1]
    acc5 = acc1 + acc2 + acc3
    acc6 = acc2 + acc3 + acc4
#for loop forming acids list for any strand inserted. Takes sequence and divides it every 3 characters for every frame
#Inserts all codons in acc list and translates list in 1 letter and 3 letter amino acids (trans and trans1)
    for base in range(len(seq)-2):
        acc = ''
        for codon in range(3):
            acc+= seq[base+codon]
        trans = dict1[acc]
        trans1 = dict2[trans.upper()]
        acid.append(trans1)
        longacid.append(trans)
#Below code used to append acid lists with extra codons loopng back to start (acc5 and acc6)
    trans_ = dict1[acc5]
    trans_1 = dict2[trans_.upper()]
    acid.append(trans_1)
    longacid.append(trans_)
    trans__ = dict1[acc6]
    trans__1 = dict2[trans__.upper()]
    acid.append(trans__1)
    longacid.append(trans__)   
    return(acid, longacid)



#Variables given to both acid lists and complementary acid lists
(acids, longacids) = transs(b)
(comp.acids, longcomp_acids) = transs(reverse)

#Reverse complementary acid lists to be in correct order when formatted from C to N temrinus.
comp.acids.reverse()
longcomp_acids.reverse()



#Below code splits strand and comp_strand in a list every 60th character for formatting

split_strand = []
n  = 60
for index in range(0, len(b), n):
    split_strand.append(b[index : index + n])

split_comp_strand = []
n  = 60
for index in range(0, len(comp_strand), n):
    split_comp_strand.append(comp_strand[index : index + n])

#Creates variables for frames function to be inserted into frames1 function, with option of long or short versions
#Also creates variables for orf counter function. The reversed acid lists are used for frames 4-6 as they should be reade N to C to count ORFs

(f1, f2, f3, f4, f5, f6, rf4, rf5, rf6) = frames(acids, comp.acids)
(lf1, lf2, lf3, lf4, lf5, lf6, rlf4, rlf5, rlf6) = frames(longacids, longcomp_acids)
(orf1, frame1) = ORFcounter(lf1)
(orf2, frame2) = ORFcounter(lf2)
(orf3, frame3) = ORFcounter(lf3)
(orf4, frame4) = ORFcounter(rlf4)
(orf5, frame5) = ORFcounter(rlf5)
(orf6, frame6) = ORFcounter(rlf6)
Orf_Sum = ORFsum(orf1, orf2, orf3, orf4, orf5, orf6)
#Loop for robustness, choice of 1 or 3 letter amino acids
#Choice uses function frame1 which splits each frame every 20 acids for formatting, and then sends all these two function frame 2
#frame 2 function formats all frames for output in 1 or 3 letter amino acids and gives choice of outputting all frames or a specific one
while True:
    choice = input('Amino Acid Format (1 letter or 3):')
    if choice == '1':
        frames1(f1, f2, f3, f4, f5, f6, split_strand, split_comp_strand)
        break
    elif choice == '3':
        frames1(lf1, lf2, lf3, lf4, lf5, lf6, split_strand, split_comp_strand)
        break
    else:
        print('Sorry, that input is not available. Try again.')

#Choice of 1 or all frames to count ORFs (Counts all ORFs of any length (no minimum codon number), but negates nested ORFs (start codon within an orf))
#Uses variables orf1-6 and Orf_sum by using all ORF functions to output all specific ORFs in each frame or the total number of ORFs in the whole sequence in all 6 frames
print('')
print('N° ORFs in 6 frames: ', Orf_Sum)
print('F1: ', orf1,
      '\nF2: ', orf2,
      '\nF3: ', orf3,
      '\nF4: ', orf4,
      '\nF5: ', orf5,
      '\nF6: ', orf6)

while True:
    choice1 = input('Show me ORFs in frame (f1-f6): ')
    if choice1 == 'f1':
        print('')
        print('ORFs in ' +choice1, ': ', orf1)
        ORFprinter(frame1)
        break
    elif choice1 == 'f2':
        print('')
        print('ORFs in ' +choice1, ': ', orf2)
        ORFprinter(frame2)
        break
    elif choice1 == 'f3':
        print('')
        print('ORFs in ' +choice1, ': ', orf3)
        ORFprinter(frame3)
        break
    elif choice1 == 'f4':
        print('')
        print('ORFs in ' +choice1, ': ', orf4)
        ORFprinter(frame4)
        break
    elif choice1 == 'f5':
        print('')
        print('ORFs in ' +choice1, ': ', orf5)
        ORFprinter(frame5)
        break
    elif choice1 == 'f6':
        print('')
        print('ORFs in ' +choice1, ': ', orf6)
        ORFprinter(frame6)       
        break
    else:
        print('Sorry, that input is not available. Try again.')
