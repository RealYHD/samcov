# SAMCOV (SAM/BAM Coverage)

This tool aggregates the coverage of multiple BAM/SAM file.

## Installation with PIP

Using pip, installation is simple.

1. Go to the [package page](https://git.reslate.systems/ydeng/-/packages/pypi/samcov).

2. Follow the instructions there.


## Usage

1. After installing, run `samcov -h` to see information about the arguments.

2. Run `samcov alignment.bam --csv output.csv` where replacing `alignment.bam` with your alignment file (SAM and BAM are supported). Replace `output.csv` with the path to the CSV for the output information. 