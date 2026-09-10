#!/usr/bin/env bash

#
# Download Atom files
#
# Years 2020 to previous year: one file per year
# Current year: one file per month
#
# Portable between:
#   - macOS (BSD tar / libarchive)
#   - Linux with bsdtar installed
#

set -euo pipefail

#
# Read optional configuration variables:
#   PREFIX_URL
#   HAS_MONTHLY_FILES
#
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$SCRIPT_DIR/.env" ]]; then
    source "$SCRIPT_DIR/.env"
fi

: "${PREFIX_URL:=https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3}"
: "${HAS_MONTHLY_FILES:=true}"

DEST="${PREFIX_URL##*/}"

echo "Using PREFIX_URL=${PREFIX_URL}"
echo "Dataset has monthly files: ${HAS_MONTHLY_FILES}"
echo "Downloading atom files to ${DEST}"

#
# Locate a tar implementation capable of reading ZIP files from stdin.
#
if command -v bsdtar >/dev/null 2>&1; then
    TAR_CMD="bsdtar"

elif tar --version >/dev/null 2>&1 && \
     tar --version 2>&1 | grep -qi "bsdtar\|libarchive"; then
    TAR_CMD="tar"

else
    echo "ERROR: No BSD tar / libarchive implementation found." >&2
    echo "       Install bsdtar (libarchive) to extract ZIP files from a pipe." >&2
    exit 1
fi

#
# Locate wget.
#
if ! command -v wget >/dev/null 2>&1; then
    echo "ERROR: wget is not installed." >&2
    exit 1
fi

mkdir -p "$DEST"

#
# Get current year and month.
#
current_year=$(date +%Y)
current_month=$(date +%m)

#
# Remove the leading zero safely.
#
current_month_num=$((10#$current_month))

#
# Download and extract a ZIP directly from the HTTP stream.
#
download_and_extract() {
    local url="$1"

    echo "Downloading:"
    echo "  $url"

    wget -qO- "$url" | "$TAR_CMD" -xvf- -C "$DEST"
    local wget_status=${PIPESTATUS[0]} tar_status=${PIPESTATUS[1]}

    if [[ $wget_status -ne 0 || $tar_status -ne 0 ]]; then
        echo "ERROR processing:" >&2
        echo "  $url" >&2
        echo "wget exit status: $wget_status" >&2
        echo "$TAR_CMD exit status: $tar_status" >&2
        return 1
    fi
}

#
# Download complete years: 2020 to previous year.
#
for ((year=2020; year<current_year; year++)); do

    echo
    echo "========================================"
    echo "Downloading year $year"
    echo "========================================"

    url="${PREFIX_URL}_${year}.zip"

    download_and_extract "$url"

done

#
# Download current year.
#
if [[ "$HAS_MONTHLY_FILES" == "true" ]]; then

    #
    # Download current year months: January to current month.
    #
    for ((month=1; month<=current_month_num; month++)); do

        printf -v month_padded '%02d' "$month"

        echo
        echo "========================================"
        echo "Downloading year ${current_year} month ${month_padded}"
        echo "========================================"

        url="${PREFIX_URL}_${current_year}${month_padded}.zip"

        download_and_extract "$url"

    done

else

    #
    # Download current year's annually updated file.
    #
    url="${PREFIX_URL}_${current_year}.zip"

    download_and_extract "$url"

fi

#
# Generate README.
#
echo "Generated on $(date)" > "$DEST/README.txt"

echo
echo "========================================"
echo "Completed successfully"
echo "Destination: $DEST"
echo "Generated on $(date)"
echo "========================================"

