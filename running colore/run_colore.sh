#!/bin/bash
#SBATCH --job-name=run_colore
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=normal-arm
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH --time=00:10:00
#SBATCH --output=run_colore_%j.out

# Load modules
set -e
module purge
module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
module load libconfig

# Start project
cd /projects/F202315069PEXF1/vitoria/running_colore
echo "Job started: $(date)"
start_time=$(date +%s)

srun --cpu-bind=none /home/vitoria.ab/packages/CoLoRe/CoLoRe \
    "$1/params.cfg" > "$1/log.txt" 2>&1
exit_code=$?
cat "$1/log.txt"

end_time=$(date +%s)
elapsed=$((end_time - start_time))
printf "Elapsed time: %02d:%02d:%02d\n" \
    $((elapsed/3600)) $(((elapsed%3600)/60)) $((elapsed%60))
echo "Exit code: $exit_code"

echo "Job step memory statistics:"
sacct -j "$SLURM_JOB_ID" --format=JobID,State,Elapsed,MaxRSS,ReqMem --units=G
echo "Job ended: $(date)"
