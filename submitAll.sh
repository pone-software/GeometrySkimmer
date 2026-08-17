#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --account=rpp-nahee
#SBATCH --mem=4000M
#SBATCH --output=/project/6008051/pone_simulation/geometry_subselections/70String_default_geometry/000002/batchscripts/FilterFiles/logs/filt_%a.log
#SBATCH --array=1002-9999
module --force purge
module load StdEnv/2020 gcc/11.3.0 apptainer scipy-stack/2023b

apptainer exec -B /localscratch/ -B /cvmfs/software.pacific-neutrino.org/ /cvmfs/software.pacific-neutrino.org/containers/itray_v1.10 /project/6008051/pone_simulation/geometry_subselections/70String_default_geometry/000002/batchscripts/FilterFiles/runAll.sh ${SLURM_ARRAY_TASK_ID} $SLURM_TMPDIR
