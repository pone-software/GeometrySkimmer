#!/bin/bash
set -euo pipefail

INPUT_SUBDIR=${1:-}
TMPDIR=${2:-}
LONGTERMSTORAGE=${3:-}
SELECTION_FILE=${4:-}
GCD_FILE=${5:-}
BATCH_DIR=${6:-}
FILE_GROUP=${7:-}
FILES_PER_TASK=100

if [[ -z "$INPUT_SUBDIR" || -z "$TMPDIR" || -z "$LONGTERMSTORAGE" || -z "$SELECTION_FILE" || -z "$GCD_FILE" || -z "$BATCH_DIR" || ! "$FILE_GROUP" =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 <input_subdir> <tmpdir> <longtermstorage> <selection_file> <gcd_file> <skimmer_dir> <zero-based-file-group>" >&2
    exit 2
fi

if [[ ! -d "$INPUT_SUBDIR" ]]; then
    echo "Input subdirectory not found: $INPUT_SUBDIR"
    exit 1
fi

if [[ ! -f "$SELECTION_FILE" || ! -f "$GCD_FILE" ]]; then
    echo "Selection file or GCD file not found" >&2
    exit 1
fi

BASEDIR='/usr/local/icetray'

export PATH=$BASEDIR/build/bin:$PATH
export LD_LIBRARY_PATH=$BASEDIR/build/lib::$LD_LIBRARY_PATH
export PYTHONPATH=/usr/local/lib:$BASEDIR/build/lib:/cvmfs/software.pacific-neutrino.org/pone_offline/v4.0:$PYTHONPATH
export I3_SRC=$BASEDIR
export I3_BUILD=$BASEDIR/build
export PONESRCDIR=/project/6008051/pone_simulation/pone_offline

mapfile -d '' INPUT_FILES < <(
    find "$INPUT_SUBDIR" -maxdepth 1 -type f \( -name '*.i3' -o -name '*.i3.gz' -o -name '*.i3.zst' \) -print0 | sort -z
)

if [[ ${#INPUT_FILES[@]} -eq 0 ]]; then
    echo "No input i3 files found in: $INPUT_SUBDIR"
    exit 1
fi

file_offset=$((FILE_GROUP * FILES_PER_TASK))
INPUT_FILES=("${INPUT_FILES[@]:file_offset:FILES_PER_TASK}")
if [[ ${#INPUT_FILES[@]} -eq 0 ]]; then
    echo "File group $FILE_GROUP is outside the input range for: $INPUT_SUBDIR" >&2
    exit 1
fi

SUBDIR_NAME=$(basename "$INPUT_SUBDIR")
OUTPUT_GROUP=$((FILE_GROUP + 1))
OUTFILE_TMP="$TMPDIR/filt_${SUBDIR_NAME}_${OUTPUT_GROUP}.i3.zst"
OUTFILE_FINAL="$LONGTERMSTORAGE/filt_${SUBDIR_NAME}_${OUTPUT_GROUP}.i3.zst"

mkdir -p "$LONGTERMSTORAGE"
python3 "$BATCH_DIR/GeoSkimmer.py" -i "${INPUT_FILES[@]}" -o "$OUTFILE_TMP" -s "$SELECTION_FILE" -g "$GCD_FILE"
cp "$OUTFILE_TMP" "$OUTFILE_FINAL"

echo "Wrote merged output: $OUTFILE_FINAL"
