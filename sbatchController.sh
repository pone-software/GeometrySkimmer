#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --account=rpp-nahee
#SBATCH --mem=4000M
#SBATCH --output=%x_%j.log

set -euo pipefail

INPUT_SUBDIR=${1:-}
LONGTERMSTORAGE=${2:-/project/6008051/pone_simulation/geometry_subselections/LONGTERMSTORAGE}
SELECTION_FILE=${3:-70string_default.csv}

if [[ -z "$INPUT_SUBDIR" ]]; then
	echo "Usage: $0 <input_subdir> [longtermstorage] [selection_file]"
	exit 2
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

module --force purge
module load StdEnv/2020 gcc/11.3.0 apptainer scipy-stack/2023b

apptainer exec \
	-B /localscratch/ \
	-B /cvmfs/software.pacific-neutrino.org/ \
	-B "$SCRIPT_DIR":"$SCRIPT_DIR" \
	/cvmfs/software.pacific-neutrino.org/containers/itray_v1.10 \
	"$SCRIPT_DIR/processFiles.sh" "$INPUT_SUBDIR" "$SLURM_TMPDIR" "$LONGTERMSTORAGE" "$SELECTION_FILE"
