# CDS-pipeline

Pipeline: For obtaining coding protein sequences (CDS) from EST data, and for retrieving specific protein sequences based on FASTA header information.

## Workflow

The pipelines works on the latest Windows 10 operating system, but a macOS script is also provided.

1. Right-click 'install-WSL.bat', then select 'Run as administrator' to install WSL
2. Put FASTA files to analyse in 'fasta' folder
3. Double-click 'generate-CDS.bat' to predict coding protein sequences, which are output to the 'output' folder
4. Double-click 'CDS-finder.bat' and follow the prompts to find protein sequences of interest

## Files in project

This folder contains the following files & folders: *NEEDS UPDATING*

CDS-pipeline/                  - Project folder
├── fasta/                     - FASTA files for analysis should be pasted here
├── scripts/                   - Contains the Python files accessed by generate-CDS-WSL.sh
│   ├── CDS-finder.py          - Python script to find sequences from a file given FASTA header information to search for
│   ├── CDS-finder.sh          - Shell script to run 'CDS-finder.py'
│   ├── generate-CDS-WSL.sh    - The shell script which will produce protein sequences from the provided FASTA files
│   ├── generate-CDS-macOS.sh  - Same function as 'generate-CDS-WSL.sh', but for macOS users
│   ├── rename.py              - Python script to make the FASTA headers of output files human readable
│   └── rmseq.py               - Python script to remove non-GATC characters from FASTA files
├── output/                    - Folder containing predicted coding protein sequences
│   └── excluded_sequences/    - Non-GATC sequences from FASTA files are output in this folder
├── temp/                      - Folder where temporary files from scripts are stored
├── CDS-finder.bat             - Batch file to run 'CDS-finder.sh'
├── generate-CDS.bat           - Batch file to run 'generate-CDS-WSL.sh'
├── install-WSL.bat            - Batch file to install Ubuntu via Windows Subsystem for Linux (WSL)
├── tutorial.ipynb             - An in-depth guide for predicting proteins sequences from FASTA files
└── README.md                  - File being read by the user right now, containing information about project files

When generate-CDS-WSL.sh is run, it will check for required dependencies to install and also create any missing folders.

The file 'tutorial.pynb' talks through the installation of Ubuntu and the subsequent steps to run this
analysis on a Windows OS. The pipeline can also be run on Mac OS with some additional installations, as
described in the tutorial.

## Authors

- Sergio Antonelli
- Rosie Charles
- Daniel Li
- Lingyun Yang
