# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python script that processes Spanish public procurement tenders from the Plataforma de Contratación del Sector Público. It parses RSS Atom feeds published by the Spanish government's Ministry of Finance and extracts contract information for specific contractors identified by platform ID or DIR3 code.

## Setup & Execution

### Environment Setup
```bash
# Using pyenv (recommended)
source configureEnvironment-pyenv.sh

# Using system venv
source configureEnvironment-venv.sh
```

### Configuration
Copy `.env.sample` to `.env` and configure:
- `FILE_LOCATION`: "WEB" (fetch from API) or "LOCAL" (read from filesystem)
- `ENTRY_CONTRACTOR_IDS`: Comma-separated list of contractor platform IDs
- `ENTRY_DIR3_IDS`: Comma-separated list of DIR3 codes
- `DOC_UPDATED_AFTER`: ISO date filter (e.g., "2025-01-01T00:00:00+01:00")
- `PREFIX_URL`: Base URL for web mode (only for `sindicacion_643` endpoint)

### Running the Script
```bash
# Basic execution - outputs CSV to stdout, logs to stderr
python readatom.py > output.csv 2> logs.log

# With specific config
source configureEnvironment-pyenv.sh
python readatom.py
```

### Downloading Historical Data
- Linux Platform
```bash
# Download and extract historical tenders (for LOCAL mode)
bash download_linux.sh
```
Mac Plaform
```bash
# Download and extract historical tenders (for LOCAL mode)
bash download.sh
```
## Architecture

### Core Components

**CspDoc** (`readatom.py:244`): Manages Atom feed documents. Supports two modes:
- WEB: Fetches Atom XML from `https://contrataciondelestado.es/sindicacion/sindicacion_643/`
- LOCAL: Reads from local filesystem directory

Provides pagination via `next_doc()` method that follows `rel="next"` links.

**CspEntry** (`readatom.py:53`): Represents a single tender entry from an Atom feed. Extracts:
- Contractor ID (platform or DIR3)
- Entry ID
- CPV (Common Procurement Value) codes
- Contract dates, amounts, and titles
- Technical documents, additional docs, and general docs
- Tender results (accepted/excluded/other counts)

### Key Implementation Details

- **Namespace handling**: Uses lxml with custom namespace map for CODICE XML schema extensions
- **XPath queries**: Extracts data from complex nested XML structures using `cac-place-ext:` namespace
- **Output format**: CSV with tender metadata followed by document rows (TechnicalDoc:, GeneralDoc:, AdditionalDoc:)
- **Logging**: Configurable via `LOG_LEVEL` env var (DEBUG/INFO/WARNING/ERROR)

### Dependencies
- `python-dotenv`: Environment variable loading
- `requests`: HTTP client for web mode
- `lxml`: XML parsing with XPath support

## Important Notes

- DIR3 codes are Spanish public entity identifiers; platform IDs are internal IDs
- CPV codes starting with "72" indicate IT services
- Tenders can appear multiple times in feeds when updated (tracked via tender ID (CspEntry.id))
- Only technical and general documents are extracted; legal documents require code modification
