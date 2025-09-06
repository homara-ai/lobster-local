# 🦞 Lobster AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

**AI-Powered Multi-Omics Bioinformatics Analysis Platform**

Transform your bioinformatics research with intelligent AI agents that understand your data and provide expert analysis insights.

## ✨ What is Lobster AI?

Lobster AI is a revolutionary bioinformatics platform that combines the power of **specialized AI agents** with proven scientific tools to analyze complex multi-omics data. Instead of wrestling with command-line tools and scripts, simply describe your analysis needs in natural language.

### 🎯 **Perfect For**
- **Bioinformatics Researchers** analyzing RNA-seq, proteomics, and multi-omics data
- **Computational Biologists** seeking intelligent analysis workflows  
- **Life Science Teams** requiring reproducible, publication-ready results
- **Students & Educators** learning modern bioinformatics approaches

## 🚀 Key Features

### 🤖 **Intelligent AI Agents**
- **Data Expert**: Handles data loading, format conversion, and quality assessment
- **Research Agent**: Discovers relevant datasets and literature for your analysis
- **Transcriptomics Expert**: Specialized in single-cell and bulk RNA-seq analysis
- **Proteomics Expert**: Mass spectrometry and protein analysis workflows
- **Method Expert**: Extracts optimal parameters from scientific literature

### 🧬 **Advanced Analysis Capabilities**
- **Single-Cell RNA-seq**: Quality control, clustering, cell type annotation, trajectory analysis
- **Bulk RNA-seq**: Differential expression, pathway analysis, batch correction
- **Proteomics**: Missing value handling, statistical analysis, protein networks
- **Multi-Omics Integration**: Cross-platform analysis using MuData framework
- **Literature Mining**: Automated parameter optimization from publications

### 🎨 **User-Friendly Experience**
- **Natural Language Interface**: Describe analyses in plain English
- **Interactive Chat Mode**: Conversational analysis workflow
- **Automatic Visualization**: Publication-ready plots and reports
- **Complete Provenance**: Reproducible analysis trails
- **Format Flexibility**: CSV, Excel, H5AD, 10X MTX, and more

## 🎬 **Quick Example**

```bash
# Install Lobster AI
git clone https://github.com/homara-ai/lobster.git
cd lobster && make install

# Start analyzing in seconds
lobster chat

# Natural language analysis
🦞 You: "Download GSE109564 and perform single-cell clustering analysis"

🦞 Lobster: I'll download and analyze this single-cell dataset for you...

✓ Downloaded 5,000 cells × 20,000 genes
✓ Quality control: filtered to 4,477 high-quality cells  
✓ Identified 12 distinct cell clusters
✓ Generated UMAP visualization and marker gene analysis

Analysis complete! Found 12 cell populations with distinct expression signatures.
```

## 📦 **Quick Installation**

### Local Installation
```bash
git clone https://github.com/homara-ai/lobster.git
cd lobster
make install
lobster chat  # Start analyzing immediately!
```

### Requirements
- Python 3.12+
- 4GB+ RAM recommended
- API keys for LLM providers (OpenAI, AWS Bedrock)

## ☁️ **Lobster Cloud: Seamless Cloud Integration**

Experience the power of cloud computing with **automatic cloud detection**:
- ☁️ **Zero Configuration** - Just set your API key and go
- 🚀 **Scalable Computing** - Handle large datasets without local hardware limits  
- 🔄 **Seamless Switching** - Automatic fallback to local mode if needed
- 🔒 **Secure Processing** - Enterprise-grade security for your data

### **Getting Started with Cloud**

1. **Get your API key** from [cloud.lobster.ai](mailto:cloud@homara.ai?subject=Lobster%20Cloud%20API%20Key%20Request)
2. **Set your environment variable**:
   ```bash
   # Add to your .env file
   LOBSTER_CLOUD_KEY=your-api-key-here
   ```
3. **Run Lobster as usual** - it automatically detects and uses cloud mode:
   ```bash
   lobster chat  # Automatically uses cloud when key is present
   ```

### **Smart Local Fallback**
- **No Cloud Key?** → Runs locally with full functionality
- **Cloud Unavailable?** → Automatically falls back to local mode
- **Same Experience** → Identical interface whether cloud or local

**[Request Cloud Access →](mailto:cloud@homara.ai?subject=Lobster%20Cloud%20API%20Key%20Request)**

## 📚 **Learn More**

- 📖 **[Full Documentation](docs/)** - Complete guides and tutorials
- 🏗️ **[Architecture Overview](docs/architecture_diagram.md)** - Technical deep-dive
- 🧪 **[Example Analyses](examples/)** - Real-world use cases
- 🎓 **[Video Tutorials](https://youtube.com/@homaraai)** - Step-by-step walkthroughs

## 🔍 **Data Quality & Compliance**

Lobster AI maintains **publication-grade data quality standards** for transcriptomics and proteomics analysis -> [source publication](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9926151): 

### ✅ **Quality Assessment Results**
- **✅ 60% COMPLIANT** - Strong foundational QC infrastructure
- **⚠️ 26% PARTIAL** - Areas identified for enhancement  
- **❌ 14% MISSING** - Clear roadmap for remaining features

### 🏗️ **Robust QC Architecture**
- **Comprehensive Provenance Tracking** - W3C-PROV compliant analysis history
- **Automated Quality Control** - Built-in metrics for genes, cells, and proteins
- **Schema Validation** - Structured metadata for reproducible research
- **Batch Effect Management** - Detection and correction workflows
- **Reproducible Workflows** - Containerized analysis with parameter logging

### 📋 **Key QC Components Analyzed**
- `lobster/tools/quality_service.py` - Quality assessment algorithms
- `lobster/tools/preprocessing_service.py` - Normalization and batch correction  
- `lobster/core/provenance.py` - Complete analysis history tracking
- `lobster/core/schemas/` - Transcriptomics and proteomics metadata validation
- `AGENT_DATA_QC_CHECKLIST.md` - Comprehensive quality requirements checklist

### 🎯 **Next Steps for Highest Quality**
**Priority improvements identified:**
1. **Missing Data Handling** - Implement imputation strategies for proteomics
2. **Reference Harmonization** - Add Ensembl/UniProt version management
3. **Statistical Rigor** - Systematic FDR control across all analyses
4. **Proteomics Enhancement** - Multi-level PSM/peptide/protein QC

📊 **[View Full Quality Report →](AGENT_DATA_QC_CHECKLIST_report.md)**

## 🤝 **Community & Support**

- 💬 **[Discord Community](https://discord.gg/homaraai)** - Chat with users and developers
- 🐛 **[Report Issues](https://github.com/homara-ai/lobster/issues)** - Bug reports and feature requests
- 📧 **[Email Support](mailto:support@homara.ai)** - Direct help from our team
- 🐦 **[Follow Updates](https://twitter.com/homaraai)** - Latest news and releases

## 🏢 **Enterprise Solutions**

Need custom integrations, dedicated support, or on-premise deployment?

**[Contact Enterprise Sales →](mailto:enterprise@homara.ai)**

## 📄 **License**

Open source under [MIT License](LICENSE) - Use freely in academic and commercial projects.

---

<div align="center">

**🦞 Transform Your Bioinformatics Research Today**

[Get Started](https://github.com/homara-ai/lobster) • [Documentation](docs/) • [Community](https://discord.gg/homaraai)

*Made with ❤️ by [Homara AI](https://homara.ai)*

</div>
