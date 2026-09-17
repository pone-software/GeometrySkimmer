#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --account=rpp-nahee
#SBATCH --mem=4000M
#SBATCH --output=%x_%j.log

set -euo pipefail

GENERATOR_DIR=${1:-}
LONGTERMSTORAGE=${2:-}
SELECTION_FILE=${3:-}
GCD_FILE=${4:-}
BATCH_DIR=${5:-}

if [[ -z "$GENERATOR_DIR" || -z "$LONGTERMSTORAGE" || -z "$SELECTION_FILE" || -z "$GCD_FILE" || -z "$BATCH_DIR" ]]; then
	echo "Usage: $0 <generator_dir> <longtermstorage> <selection_file> <gcd_file> <skimmer_dir>" >&2
	exit 2
fi

mapfile -d '' input_subdirs < <(
	while IFS= read -r -d '' input_dir; do
		if find "$input_dir" -maxdepth 1 -type f \( -name '*.i3' -o -name '*.i3.gz' -o -name '*.i3.zst' \) -print -quit | grep -q .; then
			printf '%s\0' "$input_dir"
		fi
	done < <(find "$GENERATOR_DIR" -mindepth 1 -type d -print0 | sort -z)
)

task_id=${SLURM_ARRAY_TASK_ID:-}
if [[ ! "$task_id" =~ ^[0-9]+$ || "$task_id" -ge "${#input_subdirs[@]}" ]]; then
	echo "Invalid array task ID '$task_id' for $GENERATOR_DIR" >&2
	exit 1
fi

module --force purge
module load StdEnv/2020 gcc/11.3.0 apptainer scipy-stack/2023b

apptainer exec \
	-B /localscratch/ \
	-B /cvmfs/software.pacific-neutrino.org/ \
	-B "$BATCH_DIR":"$BATCH_DIR" \
	/cvmfs/software.pacific-neutrino.org/containers/itray_v1.17.1 \
	"$BATCH_DIR/processFiles.sh" "${input_subdirs[$task_id]}" "$SLURM_TMPDIR" \
	"$LONGTERMSTORAGE" "$SELECTION_FILE" "$GCD_FILE" "$BATCH_DIR"
