# Project Summary

## Overview

AtomReader is a small Python project that processes public procurement tenders from the Spanish Plataforma de Contratacion del Sector Publico. It parses RSS/Atom feeds published as open data and exports filtered tender information plus linked document URLs as CSV.

The repository is code-light and data-heavy:
- Core application logic lives in a single script: `readatom.py`
- Setup and download behavior is handled by a few shell scripts
- The repository includes a very large local cache of downloaded `.atom` files

## Primary Purpose

The script filters tenders for specific contracting entities and outputs:
- Tender metadata
- Contract folder identifier
- CPV code
- Updated timestamp
- Total amount
- Awarded company name when present
- Tender result counts
- Linked technical, additional, and general documents

The main use case is extracting tenders for one or more entities identified by:
- `ID_PLATAFORMA`
- `DIR3`

## Repository Shape

Main files:
- `readatom.py`: main executable and domain logic
- `readme.md`: detailed Spanish documentation and usage notes
- `requirements.txt`: minimal Python dependencies
- `configureEnvironment-pyenv.sh`: pyenv-based environment setup
- `configureEnvironment-venv.sh`: alternate environment setup script
- `download.sh`: dynamic bulk downloader for local historical processing
- `download_linux.sh`: older Linux-oriented download script
- `CLAUDE.md`: machine-oriented repo guidance

Data and generated artifacts:
- `licitacionesPerfilesContratanteCompleto3/`: local Atom archive, around 35 GB
- Example outputs such as `licitaciones.csv`, logs, and spreadsheets

## Runtime Model

The script is driven entirely by environment variables loaded from `.env`.

Two operating modes are supported:

### 1. WEB mode

The script downloads the current Atom feed from the official endpoint and follows `rel="next"` links to older feed files.

Relevant variables:
- `FILE_LOCATION=WEB`
- `PREFIX_URL`
- `FILE`

### 2. LOCAL mode

The script reads Atom files from a previously downloaded local directory and follows local `next` links backward through the archive.

Relevant variables:
- `FILE_LOCATION=LOCAL`
- `PREFIX_PATH`
- `FILE`

## Core Architecture

### `CspEntry`

Represents a single Atom `<entry>` and exposes parsed fields through properties. It extracts values using `lxml` plus XPath and namespace-aware element lookups.

Important fields exposed by the class:
- entry ID
- detail page link
- title
- `ID_PLATAFORMA`
- `DIR3`
- CPV
- updated date
- total amount
- contract folder ID
- awarded tender name
- accepted/excluded/other tender counts
- technical documents
- additional documents
- general documents

### `CspDoc`

Represents one Atom feed document and handles:
- loading from web or local filesystem
- validating feed age against `DOC_UPDATED_AFTER`
- searching entries by platform ID and DIR3
- following the feed chain using `rel="next"`
- iteration over current and previous feed documents

## Execution Flow

High-level script flow:
1. Load `.env` via `python-dotenv`
2. Read configuration values
3. Build the first `CspDoc`
4. Iterate across the feed chain
5. Search matching entries by configured contractor IDs and DIR3 codes
6. De-duplicate by entry ID because tenders may appear multiple times across updates
7. Write CSV rows to `stdout`
8. Write logs to `stderr`

## Output Format

The CSV starts with one main row per unique tender, followed by optional rows for each related document.

Main tender row includes:
- `ID_PLATAFORMA`
- `DIR3`
- `Contract Folder Id`
- `CPV`
- `Title`
- `Date`
- `Total Amount`
- `Id`
- `URI`
- `Tender Name/Document Hash/Filename`
- `# Tender Accepted`
- `# Tender Excluded`
- `# Tender Other`

Document rows reuse the same leading tender fields but place markers such as:
- `TechnicalDoc:`
- `AdditionalDoc:`
- `GeneralDoc:`

## Dependencies

Python dependencies are intentionally small:
- `python-dotenv`
- `requests`
- `lxml`

The project is script-oriented rather than package-oriented. There is no `src/` layout, CLI framework, or test framework in place.

## Configuration Notes

Key environment variables:
- `FILE`
- `FILE_LOCATION`
- `PREFIX_URL`
- `PREFIX_PATH`
- `ENTRY_CONTRACTOR_IDS`
- `ENTRY_DIR3_IDS`
- `DOC_UPDATED_AFTER`
- `LOGLEVEL`

The sample configuration currently targets Banco de Espana using:
- `ENTRY_DIR3_IDS="I00000381"`

## Download and Historical Processing

For large date ranges, the intended workflow is:
1. Download and extract the historical Atom archives
2. Point `PREFIX_PATH` to the extracted directory
3. Run in `LOCAL` mode

This is the practical mode for multi-month or multi-year processing. `download.sh` is the more flexible bulk download script currently present in the repo.

## Current Strengths

- Very small code surface area
- Clear domain purpose
- Minimal dependency footprint
- Supports both live and offline processing
- Handles feed pagination/history traversal automatically
- Produces immediately usable CSV output

## Current Risks and Caveats

Known or likely issues based on the current code:

- In `readatom.py`, `additional_docs` appends to `self._technical_docs` instead of `self._additional_docs`, so additional document extraction is broken.
- Many XML fields are accessed without null checks, so missing nodes could raise runtime errors.
- `DOC_UPDATED_AFTER` is parsed unconditionally; an empty or malformed value can fail startup.
- `configureEnvironment-venv.sh` appears inconsistent with its name because it still uses `pyenv` commands and targets Python `3.14`, while documentation mentions Python `3.12`.
- There are no automated tests.

## Practical Mental Model

For future work, treat this project as:
- a single-file XML/XPath extraction utility
- configured entirely through environment variables
- optimized for filtering procurement feeds by entity identifiers
- easy to extend with more extracted fields or output formats
- in need of robustness improvements before larger-scale automation

## Good Next Task Candidates

Natural follow-up improvements include:
- fix `additional_docs`
- add defensive null handling for optional XML fields
- validate environment variables more safely
- add a small test fixture and regression tests
- separate CSV formatting from XML parsing
- add filters for CPV, dates, or document types
- support extra identifier schemes such as NIF if needed

## Reusable Short Summary

AtomReader is a single-script Python tool that parses Spanish public procurement Atom feeds, filters tenders by contractor identifiers (`ID_PLATAFORMA` and `DIR3`), follows paginated historical feed links, and exports tender metadata plus document URLs to CSV. The core logic lives in `readatom.py`; the rest of the repository is setup scripts, examples, and a large local archive of downloaded feed files.
