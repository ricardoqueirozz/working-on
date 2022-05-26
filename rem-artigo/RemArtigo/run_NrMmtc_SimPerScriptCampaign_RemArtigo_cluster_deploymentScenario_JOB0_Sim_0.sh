#!/bin/bash
#SBATCH --time=1-24:0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
mkdir -p /home/rqdfhsilva/ns-3-dev-master/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo_deploymentScenario/JOB0/Sim_0
cp -f run_NrMmtc_SimPerScriptCampaign_RemArtigo_cluster_deploymentScenario_JOB0_Sim_0.sh /home/rqdfhsilva/ns-3-dev-master/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo_deploymentScenario
cp -f NrMmtc_SimPerScriptCampaign_RemArtigo.yaml /home/rqdfhsilva/ns-3-dev-master/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo_deploymentScenario
cd '/home/rqdfhsilva/ns-3-dev-master/'
srun -N 1 -n 1 ./waf --cwd='/home/rqdfhsilva/ns-3-dev-master/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo_deploymentScenario/JOB0/Sim_0' --run 'rem-artigo --RngRun=492654656509539 --scenario=InH-OfficeOpen_LoS --deploymentScenario=Case1_Omni --frequency=24.3e9 --txPower=23 --outputDir='/home/rqdfhsilva/ns-3-dev-master/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo_deploymentScenario/JOB0/Sim_0' --scenario=InH-OfficeOpen_LoS --frequency=24.3e9 --txPower=23 --deploymentScenario=Case1_Omni' > /home/rqdfhsilva/ns-3-dev-master/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo_deploymentScenario/JOB0/Sim_0.out 2>&1
