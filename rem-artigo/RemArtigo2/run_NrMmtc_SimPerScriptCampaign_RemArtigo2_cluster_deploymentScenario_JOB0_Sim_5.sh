#!/bin/bash
#SBATCH --time=1-12:0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
module load softwares/gsrc/2020_05
mkdir -p /home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario/JOB0
cp -f run_NrMmtc_SimPerScriptCampaign_RemArtigo2_cluster_deploymentScenario_JOB0_Sim_5.sh /home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario
cp -f NrMmtc_SimPerScriptCampaign_RemArtigo2.yaml /home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario
cd '/home/rqdfhsilva/ns-allinone-3.36/ns-3.36/'
sleep $((11 + RANDOM % 50))
srun -N 1 -n 1 ./ns3 --cwd='/home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario/JOB0/Sim_5' --run 'rem-artigo2 --RngRun=492654656509539 --remMode=CoverageArea --scenario=UMa --deploymentScenario=Line_3s --frequency=24.3e9 --outputDir='/home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario/JOB0/Sim_5' --outputDir2='/home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario/JOB0' --remMode=BeamShape --scenario=UMa --frequency=3.5e9 --deploymentScenario=Line_3s' > /home/rqdfhsilva/ns-allinone-3.36/ns-3.36/results_cluster_NrMmtc_SimPerScriptCampaign_RemArtigo2_deploymentScenario/JOB0/Sim_5.out 2>&1
