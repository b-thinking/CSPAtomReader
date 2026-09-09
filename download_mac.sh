#!/usr/bin/env bash
# Download Atom files
# Years 2020-current_year-1: one file per year
# Current year: one file per month

set -euo pipefail

mkdir -p licitacionesPerfilesContratanteCompleto3

# Get current year and month from system date
current_year=$(date +%Y)
current_month=$(date +%m)

# Download full years (2020 to previous year)
for year in $(seq 2020 $(($current_year - 1))); do
    echo "Downloading year $year"
    wget -qO- "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_${year}.zip" | tar -xvf- -C licitacionesPerfilesContratanteCompleto3
done

# Download current year months (one file per month up to current month)
for month in $(seq -w 1 $current_month); do
    echo "Downloading year '${current_year}' month '${month}'"
    wget -qO- "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_${current_year}${month}.zip" | tar -xvf- -C licitacionesPerfilesContratanteCompleto3
done

echo "Generated on $(date)" > licitacionesPerfilesContratanteCompleto3/README.txt
