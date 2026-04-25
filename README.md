# Clinical Data QC Library
A configurable Python package and command-line tool for automated clinical data quality control (QC). This library is designed to detect common data issues in clinical datasets and generate structured QC reports for downstream analysis.

# Overview
Clinical and EHR datasets often contain data quality issues such as missing values, inconsistent coding, invalid date relationships, and out-of-range measurements. These issues can lead to biased statistical analysis and unreliable conclusions.

This project provides a modular and extensible QC framework that:

- Performs systematic validation of clinical datasets
- Supports configurable QC rules via YAML
- Generates interpretable summary reports and visualizations
- Enables reproducible data quality assessment workflows

# Instalization
```
git clone https://github.com/Wei0015/BIOSTAT821_Clinical_Data_QC_Library.git
cd BIOSTAT821_Clinical_Data_QC_Library
pip install -e .
```

# Key Contributions
- Developed a modular QC pipeline for clinical datasets, supporting multiple validation checks across patient-level and variable-level data
- Implemented automated detection of missingness, outliers, range violations, date inconsistencies, and coding issues
- Designed a configurable system using YAML, allowing flexible adaptation to different datasets and study requirements
- Built a command-line interface (CLI) to streamline QC workflows and improve usability
- Generated structured QC reports including summary statistics and visualizations for easy interpretation

# Features
- Missing Data Detection
  - Calculate missingness rates across variables
  - Identify high-missingness fields
- Outlier Detection
  - Detect extreme values using statistical methods
  - Flag abnormal clinical measurements
- Range Validation
  - Validate values against predefined acceptable ranges
  - Date Logic Validation
  - Detect invalid temporal relationships (e.g., discharge before admission)
- Coding Consistency Check
  - Identify inconsistent categorical encodings (e.g., mixed formats)
- Reporting & Visualization
  - Generate QC summaries
  - Export reports and charts
- Configurable Pipeline
  - Define QC rules using YAML configuration files
- Command-Line Interface (CLI)
  - Run QC checks directly from terminal


# Project Structure
```
clinical_qc/
│
├── checks/              # Core QC checks
│   ├── missingness.py
│   ├── outliers.py
│   ├── ranges.py
│   ├── dates.py
│   └── coding.py
│
├── report/              # Reporting and visualization
│   ├── summary.py
│   ├── charts.py
│   └── export.py
│
├── pipeline.py          # QC pipeline orchestration
├── cli.py               # Command-line interface
├── config.py            # Configuration loader
├── models.py            # Data structures
│
examples/
│   ├── sample_clinical_data.csv
│   └── sample_config.yaml
│
tests/                   # Unit tests
```

# Example Usage
## 1. Run via CLI
```
python -m clinical_qc.cli \
  --data examples/sample_clinical_data.csv \
  --config examples/sample_config.yaml
```
## 2. Run in Python
```
python -m clinical_qc.cli \
  --data examples/sample_clinical_data.csv \
  --config examples/sample_config.yaml
```
## Configuration
QC rules are defined in a YAML file:
```
missingness_threshold: 0.8

ranges:
  age: [0, 120]
  bmi: [10, 60]

date_checks:
  admission_date <= discharge_date
```
This allows flexible customization for different datasets and studies.
## Output
The pipeline generates:

- QC summary tables
- Flagged records and variables
- Visualization charts
- Exportable reports

# Applications
- Clinical trial data preprocessing
- EHR data cleaning and validation
- Real-world evidence (RWE) studies
- Biostatistics and epidemiology workflows

# Authors
This project was developed collaboratively by:

- Yichen Lai – M.S. Biostatistics, Duke University  
- Wei Ding – M.S. Biostatistics, Duke University

# Generative AI Usage

This project made use of generative AI tools to support development. All outputs were reviewed, modified, and integrated by the authors.

### Tools Used

- ChatGPT (OpenAI)

### How the Tools Were Used

Generative AI was used in the following ways:

- Assisted in designing the overall project structure (modular layout with checks, pipeline, report, and CLI)
- Provided suggestions for organizing code into reusable components
- Helped debug Python errors during development (e.g., import issues, function errors)
- Suggested improvements for writing unit tests using `pytest`
- Assisted with configuring linting and formatting tools (`ruff`, `pyproject.toml`)
- Helped generate example command-line usage patterns
- Provided the rough structure of the README file
- Assisted in formatting and improving code readability

### What the Tools Produced

The generative AI tools produced:

- Suggested code snippets for functions and project structure
- Example test cases and testing strategies
- Outline drafts and wording improvements
- Debugging suggestions and explanations of errors

All generated outputs were carefully reviewed, tested, and modified before inclusion in the final project.

### Author Responsibility

The authors take full responsibility for the correctness, originality, and integrity of the final submitted code. Generative AI was used as a supporting tool, not as a replacement for understanding or implementation.
