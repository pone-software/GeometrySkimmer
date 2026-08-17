#!/bin/bash
set -euo pipefail

MCDIR=${1:-}
LONGTERMSTORAGE=${2:-/project/6008051/pone_simulation/geometry_subselections/LONGTERMSTORAGE}
SELECTION_FILE=${3:-70string_default.csv}

if [[ -z "$MCDIR" ]]; then
    echo "Usage: $0 <MCDIR> [longtermstorage] [selection_file]"
    exit 2
fi

GEN_DIR="$MCDIR/Generator"
if [[ ! -d "$GEN_DIR" ]]; then
    echo "Generator directory not found: $GEN_DIR"
    exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

submitted=0

# Submit one job per leaf directory that contains i3 files.
while IFS= read -r -d '' dir; do
    i3_count=$(find "$dir" -maxdepth 1 -type f \( -name '*.i3' -o -name '*.i3.gz' -o -name '*.i3.zst' \) | wc -l)
    if [[ "$i3_count" -eq 0 ]]; then
        continue
    fi

    job_name="skim_$(basename "$dir")"
    sbatch \
        --job-name="$job_name" \
        --output="$LOG_DIR/${job_name}_%j.log" \
        "$SCRIPT_DIR/sbatchController.sh" "$dir" "$LONGTERMSTORAGE" "$SELECTION_FILE"
    submitted=$((submitted + 1))
done < <(find "$GEN_DIR" -mindepth 1 -type d -print0)

echo "Submitted $submitted jobs from $GEN_DIR"
