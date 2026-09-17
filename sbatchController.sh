#!/bin/bash
#SBATCH --time=06:00:00
#SBATCH --account=rpp-nahee
#SBATCH --mem=4000M
#SBATCH --output=%x_%j.log

set -euo pipefail

GENERATOR_DIR=${1:-}
LONGTERMSTORAGE=${2:-}
SELECTION_FILE=${3:-}
GCD_FILE=${4:-}
BATCH_DIR=${5:-}
FILES_PER_TASK=100

if [[ -z "$GENERATOR_DIR" || -z "$LONGTERMSTORAGE" || -z "$SELECTION_FILE" || -z "$GCD_FILE" || -z "$BATCH_DIR" ]]; then
	echo "Usage: $0 <generator_dir> <longtermstorage> <selection_file> <gcd_file> <skimmer_dir>" >&2
	exit 2
fi

task_id=${SLURM_ARRAY_TASK_ID:-}
if [[ ! "$task_id" =~ ^[0-9]+$ ]]; then
	echo "Invalid array task ID '$task_id'" >&2
	exit 1
fi

remaining_task_id=$task_id
input_subdir=""
file_group=""
while IFS= read -r -d '' input_dir; do
	file_count=$(find "$input_dir" -maxdepth 1 -type f \( -name '*.i3' -o -name '*.i3.gz' -o -name '*.i3.zst' \) -printf '.' | wc -c)
	[[ "$file_count" -eq 0 ]] && continue

	group_count=$(( (file_count + FILES_PER_TASK - 1) / FILES_PER_TASK ))
	if [[ "$remaining_task_id" -lt "$group_count" ]]; then
		input_subdir="$input_dir"
		file_group=$remaining_task_id
		break
	fi
	remaining_task_id=$((remaining_task_id - group_count))
done < <(find "$GENERATOR_DIR" -mindepth 1 -type d -print0 | sort -z)

if [[ -z "$input_subdir" ]]; then
	echo "Array task ID '$task_id' exceeds the available file groups for $GENERATOR_DIR" >&2
	exit 1
fi

module --force purge
module load StdEnv/2020 gcc/11.3.0 apptainer scipy-stack/2023b

apptainer exec \
	-B /localscratch/ \
	-B /cvmfs/software.pacific-neutrino.org/ \
	-B "$BATCH_DIR":"$BATCH_DIR" \
	/cvmfs/software.pacific-neutrino.org/containers/itray_v1.17.1 \
	"$BATCH_DIR/processFiles.sh" "$input_subdir" "$SLURM_TMPDIR" \
	"$LONGTERMSTORAGE" "$SELECTION_FILE" "$GCD_FILE" "$BATCH_DIR" "$file_group"
