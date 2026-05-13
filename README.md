# samcov

[![CI](https://git.reslate.solutions/ydeng/samcov/actions/workflows/ci.yml/badge.svg)](https://git.reslate.solutions/ydeng/samcov/actions)

Extract per-base coverage from SAM/BAM alignment files, compute aggregate statistics, and identify low-coverage regions across multiple samples.

## Features

- **Per-base coverage extraction** from SAM or BAM files via `samtools depth`
- **Multi-sample aggregation** — collect coverage maps from any number of alignments
- **Statistical summaries** — mean, median, and mode coverage per position across samples
- **Low-coverage region detection** — find contiguous gaps below a configurable depth threshold
- **Consensus generation** — produce FASTA consensus sequences with `samtools consensus`
- **CSV export** — sparse or dense output for downstream analysis in R, pandas, Excel, etc.

## System Requirements

- Python >= 3.10
- [samtools](http://www.htslib.org/) (>= 1.20) must be installed on your `PATH`. The tool uses `samtools depth` for coverage extraction and `samtools consensus` for FASTA generation.

### From the Reslate Solutions package registry

```bash
pip install samcov --index-url https://git.reslate.solutions/api/packages/ydeng/pypi/
```

### From source (with uv)

```bash
git clone https://git.reslate.solutions/ydeng/samcov.git
cd samcov
uv pip install -e ".[dev]"
```

### From source (with pip)

```bash
git clone https://git.reslate.solutions/ydeng/samcov.git
cd samcov
pip install -e ".[dev]"
```

## Quick start

```bash
# Extract coverage for a single BAM
samcov alignment.bam --csv coverage.csv

# Process multiple alignments
samcov sample1.bam sample2.bam sample3.bam --csv coverage.csv

# Also compute per-position statistics (mean / median / mode)
samcov *.bam --csv coverage.csv --centers-csv centers.csv

# Find regions with depth < 5 in ANY sample
samcov *.bam --low-coverage-csv low_cov.csv --low-coverage 5

# Find regions with depth < 5 in ALL samples (shared gaps)
samcov *.bam --shared-low-coverage-csv shared_gaps.csv --low-coverage 5
```

## CLI reference

```
usage: samcov [-h] [--csv CSV] [--centers-csv CENTERS_CSV]
              [--low-coverage-csv LOW_COVERAGE_CSV]
              [--shared-low-coverage-csv SHARED_LOW_COVERAGE_CSV]
              [--low-coverage LOW_COVERAGE]
              [--start-at START_AT] [--sparse] [--verbosity VERBOSITY]
              [--consensus CONSENSUS]
              I [I ...]

positional arguments:
  I                     The SAM/BAM files to extract coverages upon.

options:
  -h, --help            show this help message and exit
  --csv CSV             Path to output as a CSV
  --centers-csv CENTERS_CSV
                        Path to output as a CSV of center measures of each position.
  --low-coverage-csv LOW_COVERAGE_CSV
                        Path to output low coverage ranges as a CSV.
  --shared-low-coverage-csv SHARED_LOW_COVERAGE_CSV
                        Path to output shared low-coverage ranges (across all samples) as a CSV.
  --low-coverage LOW_COVERAGE
                        A number that is to be considered low coverage. (default: 1)
  --start-at START_AT   Sets the first position.
  --sparse              Whether or not output should be as sparse as possible.
  --verbosity VERBOSITY
                        Sets the verbosity of the output (default: INFO)
  --consensus CONSENSUS
                        Generates consensus sequences at the specified output directory.
```

## Output formats

### Coverage CSV (`--csv`)

| position | sample1.bam/ref | sample2.bam/ref | … |
|----------|----------------:|----------------:|:--|
| 0 | 42 | 38 | … |
| 1 | 45 | 40 | … |
| 2 | 0 | 1 | … |

Use `--sparse` to omit rows where **all** samples have zero coverage.

### Centers CSV (`--centers-csv`)

| position | mean | median | mode |
|----------|-----:|-------:|-----:|
| 0 | 40.0 | 42.0 | 42 |
| 1 | 42.5 | 45.0 | 45 |

### Low-coverage CSV (`--low-coverage-csv`)

| sample | low coverage ranges |
|--------|---------------------|
| sample1.bam/ref | [3, 4], [150, 155] |
| sample2.bam/ref | [2, 5] |

### Shared low-coverage CSV (`--shared-low-coverage-csv`)

| start | end | length | threshold |
|------:|----:|-------:|----------:|
| 3 | 4 | 2 | 5 |
| 150 | 155 | 6 | 5 |

Intervals where **all** samples have depth below the threshold. Use this to find consensus assembly gaps or universally problematic regions.

Ranges are **zero-based, inclusive** by default. Use `--start-at` for one-based output.

## Python API

```python
from samcov import count, metrics, export

# Load coverage from one or more BAMs
coverage_maps, max_length = count.count_all_sam_positions(["sample1.bam", "sample2.bam"])

# coverage_maps = {
#     "sample1.bam/NC_000962.3": {0: 42, 1: 45, ...},
#     "sample2.bam/NC_000962.3": {0: 38, 1: 40, ...},
# }

# Compute mean / median / mode per position
centers = metrics.measure_centers(coverage_maps, max_length)

# Find contiguous low-coverage regions in ANY sample (depth < 5)
low_cov = metrics.calculate_consecutive_low_coverage(coverage_maps, max_length, threshold=5)

# Find contiguous low-coverage regions in ALL samples (shared gaps)
shared_gaps = metrics.calculate_shared_low_coverage(coverage_maps, max_length, threshold=5)

# Export to CSV
export.export_coverages_as_csv(coverage_maps, max_length, "coverage.csv", sparse=False)
export.export_centers_as_csv(centers, max_length, "centers.csv", sparse=False)
export.export_low_coverage_csv(low_cov, max_length, "low_cov.csv")
export.export_shared_low_coverage_csv(shared_gaps, max_length, "shared_gaps.csv", threshold=5)
```

## Consensus generation

```python
from samcov.consensus import generate_all_consensus

# Requires samtools on PATH
generate_all_consensus("sample1.bam", "sample2.bam", output_folder="consensus/")
# → consensus/sample1.fasta
# → consensus/sample2.fasta
```

## Requirements

- Python ≥ 3.10
- `pysam` (handles SAM/BAM parsing)
- `tqdm` (progress bars)
- `samtools` (optional, only for consensus generation)

## Development

```bash
# Run the test suite
uv run pytest tests/ -v

# Build a wheel
uv build

# Release (semantic-release, CI only)
npx semantic-release
```

## License

MIT
