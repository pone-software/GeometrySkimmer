#!/bin/bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
GEOMETRY_DIR=${1:-$(cd "$SCRIPT_DIR/.." && pwd)}
SIMULATION_ROOT=${2:-/project/6008051/pone_simulation}
SOURCE_MAP=${3:-$GEOMETRY_DIR/sourcemap.txt}
SELECTION_FILE=${4:-$GEOMETRY_DIR/70string_default.csv}
GCD_FILE=${5:-/cvmfs/software.pacific-neutrino.org/geometries/PONE_800mGrid_40mSpacing_40OMstring.i3.gz}
LOG_DIR="$SCRIPT_DIR/logs"
FILES_PER_TASK=100

if [[ ! -f "$SOURCE_MAP" ]]; then
    echo "Source map not found: $SOURCE_MAP" >&2
    exit 1
fi

if [[ ! -f "$SELECTION_FILE" ]]; then
    echo "Selection file not found: $SELECTION_FILE" >&2
    exit 1
fi

if [[ ! -f "$GCD_FILE" ]]; then
    echo "GCD file not found: $GCD_FILE" >&2
    exit 1
fi

mkdir -p "$LOG_DIR"
submitted=0

while IFS='|' read -r destination source; do
    [[ -z "$destination" || "$destination" == \#* ]] && continue

    if [[ -z "$source" || "$destination" == */* || "$source" == */* ]]; then
        echo "Invalid source-map entry: $destination|$source" >&2
        exit 1
    fi

    generator_dir="$SIMULATION_ROOT/$source/Generator"
    if [[ ! -d "$generator_dir" ]]; then
        echo "Generator directory not found: $generator_dir" >&2
        exit 1
    fi

    task_count=0
    while IFS= read -r -d '' input_dir; do
        file_count=$(find "$input_dir" -maxdepth 1 -type f \( -name '*.i3' -o -name '*.i3.gz' -o -name '*.i3.zst' \) -printf '.' | wc -c)
        if [[ "$file_count" -gt 0 ]]; then
            task_count=$((task_count + (file_count + FILES_PER_TASK - 1) / FILES_PER_TASK))
        fi
    done < <(find "$generator_dir" -mindepth 1 -type d -print0 | sort -z)

    if [[ "$task_count" -eq 0 ]]; then
        echo "No input directories found in: $generator_dir" >&2
        continue
    fi

    output_dir="$GEOMETRY_DIR/$destination"
    mkdir -p "$output_dir"
    job_name="skim_$destination"
    sbatch \
        --array="0-$((task_count - 1))" \
        --job-name="$job_name" \
        --output="$LOG_DIR/${job_name}_%A_%a.log" \
        "$SCRIPT_DIR/sbatchController.sh" "$generator_dir" "$output_dir" \
        "$SELECTION_FILE" "$GCD_FILE" "$SCRIPT_DIR"
    submitted=$((submitted + 1))
done < "$SOURCE_MAP"

echo "Submitted $submitted job arrays from $SOURCE_MAP"
