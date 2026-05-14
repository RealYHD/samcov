# samcov

[![CI](https://git.reslate.solutions/ydeng/samcov/actions/workflows/ci.yml/badge.svg)](https://git.reslate.solutions/ydeng/samcov/actions)

Extract per-base coverage from SAM/BAM alignment files, compute aggregate statistics, and identify low-coverage regions across multiple samples.

## Features

- **Per-base coverage extraction** from SAM or BAM files via `samtools depth`
- **Multi-sample aggregation** — collect coverage maps from any number of alignments
- **Statistical summaries** — mean, median, and mode coverage per position across samples
- **Low-coverage region detection** — find contiguous gaps below a configurable depth threshold
- **Consensus generation** — produce FASTA consensus sequences with `samtools consensus`
- **Vector line plots** — export coverage trends as SVG (per-sample traces + total coverage line)
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

# Export shared gaps as BED for IGV / genome browsers
samcov *.bam --shared-low-coverage-bed shared_gaps.bed --low-coverage 5

# Export per-sample low-coverage regions as BED
samcov *.bam --low-coverage-bed per_sample_gaps.bed --low-coverage 5

# Generate a vector line plot (one panel per reference)
samcov *.bam --plot-svg coverage_plot.svg

# Generate a simple single-panel plot (single reference)
samcov *.bam --plot-svg-simple coverage_plot.svg
```

## CLI reference

```
usage: samcov [-h] [--csv CSV] [--centers-csv CENTERS_CSV]
              [--low-coverage-csv LOW_COVERAGE_CSV]
              [--low-coverage LOW_COVERAGE] [--start-at START_AT] [--sparse]
              [--verbosity VERBOSITY]
              [--shared-low-coverage-csv SHARED_LOW_COVERAGE_CSV]
              [--shared-low-coverage-bed SHARED_LOW_COVERAGE_BED]
              [--low-coverage-bed LOW_COVERAGE_BED] [--consensus CONSENSUS]
              [--plot-svg PLOT_SVG] [--plot-svg-simple PLOT_SVG_SIMPLE]
              I [I ...]
```

| Flag | Description |
|------|-------------|
| `--csv` | Dense or sparse per-position coverage CSV |
| `--centers-csv` | Per-position mean / median / mode |
| `--low-coverage-csv` | Low-coverage ranges per sample |
| `--shared-low-coverage-csv` | Low-coverage ranges shared across **all** samples |
| `--low-coverage-bed` | Per-sample low-coverage regions in BED6 |
| `--shared-low-coverage-bed` | Shared low-coverage regions in BED6 |
| `--low-coverage N` | Depth threshold (default: 1) |
| `--start-at N` | Coordinate offset (e.g. 1 for 1-based output) |
| `--sparse` | Omit rows where **all** samples have zero coverage |
| `--verbosity LEVEL` | DEBUG, INFO, WARNING, ERROR |
| `--consensus DIR` | Generate FASTA consensus via `samtools consensus` |
| `--plot-svg PATH` | Multi-panel SVG line plot (one panel per reference) |
| `--plot-svg-simple PATH` | Single-panel SVG line plot (single reference) |

### Coverage line plots

Generate publication-quality vector plots directly from the CLI:

```bash
# Multi-panel plot — one subplot per reference sequence
samcov *.bam --plot-svg coverage.svg

# Single-panel plot — all samples on one axis
samcov *.bam --plot-svg-simple coverage.svg
```

- **X-axis**: base position (respects `--start-at`)
- **Y-axis**: coverage depth
- Each sample gets a translucent trace
- A thick black line shows **total coverage** summed across all samples

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

### Low-coverage BED (`--low-coverage-bed`)

Per-sample low-coverage intervals in [BED6](https://genome.ucsc.edu/FAQ/FAQformat.html#format1) format:

```
.\t3\t5\tsample1.bam/ref\t0\t+
.\t150\t156\tsample1.bam/ref\t0\t+
.\t2\t6\tsample2.bam/ref\t0\t+
```

Columns: `chrom`, `start` (0-based), `end` (exclusive), `name`, `score`, `strand`.
The chromosome defaults to `.` because `samcov` processes alignments agnostically.

### Shared low-coverage BED (`--shared-low-coverage-bed`)

Shared low-coverage intervals in BED6 format:

```
.\t3\t5\tshared_low_coverage\t0\t+
.\t150\t156\tshared_low_coverage\t0\t+
```

Use `--start-at` to shift coordinates (e.g. for one-based reference indexing).

## Python API

```python
from samcov import count, metrics, export, visualize

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

# Export to BED
export.export_low_coverage_bed(low_cov, "low_cov.bed")
export.export_shared_low_coverage_bed(shared_gaps, "shared_gaps.bed")

# Generate SVG plots
visualize.plot_coverage(coverage_maps, max_length, "coverage.svg")
visualize.plot_all(coverage_maps, max_length, "multi_ref_coverage.svg")
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
- `tqdm` (progress bars)
- `matplotlib` (for SVG plots)
- `samtools` (optional, required for consensus and coverage extraction)

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
