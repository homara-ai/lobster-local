# 🦞 Lobster AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**Transform your bioinformatics research with AI agents that understand your data and provide expert analysis insights.**

## 📋 Table of Contents

- [✨ What is Lobster AI?](#-what-is-lobster-ai)
- [🚀 Quick Start](#-quick-start)
- [💡 Example Usage](#-example-usage)
- [🧬 Features](#-features)
- [🔧 Configuration](#-configuration)
- [📚 Documentation](#-documentation)
- [🤝 Community & Support](#-community--support)
- [📄 License](#-license)

## ✨ What is Lobster AI?

Lobster AI is a bioinformatics platform that combines specialized AI agents with open-source tools to analyze complex multi-omics data. Simply describe your analysis needs in natural language - no coding required.

**Perfect for:**
- Bioinformatics researchers analyzing RNA-seq data
- Computational biologists seeking intelligent analysis workflows
- Life science teams requiring reproducible, publication-ready results
- Students learning modern bioinformatics approaches

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- An LLM API key (Claude or AWS Bedrock)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/the-omics-os/lobster-local.git
cd lobster-local

# 2. Install with make (handles all dependencies)
make install

# 3. Set up your API key
cp .env.example .env
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key-here" >> .env

# 4. Start analyzing!
lobster chat
```

## 💡 Example Usage

### Interactive Chat Mode

```bash
🦞 lobster chat

Welcome to Lobster AI - Your bioinformatics analysis assistant

🦞 You: Download GSE109564 and perform single-cell clustering analysis

🦞 Lobster: I'll download and analyze this single-cell dataset for you...

✓ Downloaded 5,000 cells × 20,000 genes
✓ Quality control: filtered to 4,477 high-quality cells
✓ Identified 12 distinct cell clusters
✓ Generated UMAP visualization and marker gene analysis

Analysis complete! Results saved to workspace.
```

### Available Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/files` | List workspace files |
| `/read <file>` | Load a dataset |
| `/data` | Show current dataset info |
| `/plots` | List generated visualizations |
| `/workspace` | Show workspace information |
| `/workspace list` | List available datasets |
| `/workspace load <name>` | Load specific dataset |

### Natural Language Examples

```bash
# Download and analyze GEO datasets
🦞 You: "Download GSE12345 and perform quality control"

# Analyze your own data
🦞 You: "Load my_data.csv and identify differentially expressed genes"

# Generate visualizations
🦞 You: "Create a UMAP plot colored by cell type"

# Perform complex analyses
🦞 You: "Run pseudobulk aggregation and differential expression between conditions"
```

## 🧬 Features

### Current Capabilities

#### **Single-Cell RNA-seq Analysis**
- Quality control and filtering
- Normalization and scaling
- Clustering and UMAP visualization
- Cell type annotation
- Marker gene identification
- Pseudobulk aggregation

#### **Bulk RNA-seq Analysis**
- Differential expression with pyDESeq2
- R-style formula-based statistics
- Complex experimental designs
- Batch effect correction

#### **Data Management**
- Support for CSV, Excel, H5AD, 10X formats
- GEO dataset downloading
- Literature mining via PubMed
- Automatic visualization generation

### Coming Soon

#### **Proteomics Analysis** *(In Development)*
- Mass spectrometry proteomics (DDA/DIA workflows)
- Affinity proteomics (Olink panels, antibody arrays)
- Missing value handling and normalization
- Pathway enrichment analysis

#### **Multi-Omics Integration** *(In Development)*
- Cross-platform data integration
- Multi-modal analysis workflows

#### **Lobster Cloud** *(In Development)*
- Scalable cloud computing
- No local hardware requirements

## 🔧 Configuration

### API Keys

Lobster AI requires an LLM provider (fill these lines in the newly created `.env` file). Choose one:

**Option 1: Claude API (Recommended)**
```bash
# Get your key from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Option 2: AWS Bedrock**
```bash
# Requires AWS account with Bedrock access
AWS_BEDROCK_ACCESS_KEY=AKIA...
AWS_BEDROCK_SECRET_ACCESS_KEY=your-secret-key
```

### Optional Configuration

```bash
# Enhanced literature search
NCBI_API_KEY=your-ncbi-api-key  # Get from NCBI

# Force specific provider (auto-detected by default)
LOBSTER_LLM_PROVIDER=anthropic  # or "bedrock"
```

## 📚 Documentation

- [Full Documentation](docs/) - Guides and tutorials
- [Example Analyses](examples/) - Real-world use cases
- [Architecture Overview](docs/architecture_diagram.md) - Technical details

## 🤝 Community & Support

- 🐛 [Report Issues](https://github.com/the-omics-os/lobster-local/issues) - Bug reports and feature requests
- 📧 [Email Support](mailto:info@omics-os.com) - Direct help from our team

### Enterprise Solutions

Need custom integrations or dedicated support? [Contact us](mailto:info@omics-os.com)

## 📄 License

Open source under [MIT License](LICENSE) - Use freely in academic and commercial projects.

---

<div align="center">

**Transform Your Bioinformatics Research Today**

[Get Started](https://github.com/the-omics-os/lobster-local) • [Documentation](docs/)

*Made with ❤️ by [Omics-OS](https://omics-os.com)*

</div>