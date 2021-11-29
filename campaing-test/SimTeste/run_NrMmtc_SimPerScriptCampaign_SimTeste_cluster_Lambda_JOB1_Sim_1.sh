#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --time=1-12:0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos
module load softwares/gsrc/2020_05
mkdir -p /home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/results_cluster_NrMmtc_SimPerScriptCampaign_SimTeste_Lambda/JOB1/Sim_1
cp -f run_NrMmtc_SimPerScriptCampaign_SimTeste_cluster_Lambda_JOB1_Sim_1.sh /home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/results_cluster_NrMmtc_SimPerScriptCampaign_SimTeste_Lambda
cp -f NrMmtc_SimPerScriptCampaign_SimTeste.yaml /home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/results_cluster_NrMmtc_SimPerScriptCampaign_SimTeste_Lambda
cd '/home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/'
srun -N 1 -n 1 ./waf --cwd='/home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/results_cluster_NrMmtc_SimPerScriptCampaign_SimTeste_Lambda/JOB1/Sim_1' --run 'NrMmtc-M1_v3 --RngRun=362685309059354 --window=0.1 --simTime=90 --Isd=500 --ueNumScenario=84 --centralFrequencyBand=2350000000 --bandwidthBand=100000000 --BwpConfiguration=1 --BwpBand=72000000 --remBwpId=0 --scenario=UmaLos --Shadowing=0 --ChannelUpdate=0 --totalTxPower=26 --totalUePower=23 --DowntiltAngleDegree=0 --BearingAngleTilt=-30 --UlMode=1 --TrafficModel=TriggeredReport --numerology=0 --PacketSize=125 --interval=60 --Lambda=0.1 --outputDir='/home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/results_cluster_NrMmtc_SimPerScriptCampaign_SimTeste_Lambda/JOB1' --BwpConfiguration=1 --BwpBand=72000000 --totalTxPower=26 --Lambda=0.5' > /home/drdluna/5G-LENA/ns-3-dev-nr-1.2-wpatch-epsbearer/results_cluster_NrMmtc_SimPerScriptCampaign_SimTeste_Lambda/JOB1/Sim_1.out 2>&1
