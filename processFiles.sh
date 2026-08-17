#!/bin/bash
set -euo pipefail

INPUT_SUBDIR=${1:-}
TMPDIR=${2:-}
LONGTERMSTORAGE=${3:-/project/6008051/pone_simulation/geometry_subselections/LONGTERMSTORAGE}
SELECTION_FILE=${4:-70string_default.csv}

if [[ -z "$INPUT_SUBDIR" || -z "$TMPDIR" ]]; then
    echo "Usage: $0 <input_subdir> <tmpdir> [longtermstorage] [selection_file]"
    exit 2
fi

if [[ ! -d "$INPUT_SUBDIR" ]]; then
    echo "Input subdirectory not found: $INPUT_SUBDIR"
    exit 1
fi

BASEDIR='/usr/local/icetray'

export PATH=$BASEDIR/build/bin:$PATH
export LD_LIBRARY_PATH=$BASEDIR/build/lib:$BASEDIR/build/lib/tools:/usr/local/OpenBLAS/:$LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH=$BASEDIR/build/lib:$BASEDIR/build/lib/tools:$DYLD_LIBRARY_PATH
export PYTHONPATH=$BASEDIR/build/lib:/cvmfs/software.pacific-neutrino.org/pone_offline/v1.0/:$PYTHONPATH
export I3_SRC=$BASEDIR
export I3_BUILD=$BASEDIR/build
export I3_TESTDATA=$BASEDIR/build/test-data
export I3_PRODDATA=$BASEDIR/build/prod-data
export PONESRCDIR=/project/6008051/pone_simulation/pone_offline

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$LONGTERMSTORAGE"

mapfile -d '' INPUT_FILES < <(
    find "$INPUT_SUBDIR" -maxdepth 1 -type f \( -name '*.i3' -o -name '*.i3.gz' -o -name '*.i3.zst' \) -print0 | sort -z
)

if [[ ${#INPUT_FILES[@]} -eq 0 ]]; then
    echo "No input i3 files found in: $INPUT_SUBDIR"
    exit 1
fi

SUBDIR_NAME=$(basename "$INPUT_SUBDIR")
OUTFILE_TMP="$TMPDIR/filt_${SUBDIR_NAME}.i3.zst"
OUTFILE_FINAL="$LONGTERMSTORAGE/filt_${SUBDIR_NAME}.i3.zst"

python3 "$SCRIPT_DIR/GeoSkimmer.py" -i "${INPUT_FILES[@]}" -o "$OUTFILE_TMP" -s "$SCRIPT_DIR/$SELECTION_FILE"
cp "$OUTFILE_TMP" "$OUTFILE_FINAL"

echo "Wrote merged output: $OUTFILE_FINAL"
