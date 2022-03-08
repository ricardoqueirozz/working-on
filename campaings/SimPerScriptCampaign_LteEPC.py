import os
import argparse
import pickle
import numpy as np

# To install YAML: sudo apt-get install python3-yaml
import yaml

class Simulation:
    def __init__(self, configurations_file):
        #self.email_to = 'sicrano@gmail.com'            
        with open(configurations_file, 'r') as f:
            self.doc = yaml.load(f, Loader=yaml.loader.BaseLoader)
        self.campaign_name = os.path.splitext(configurations_file)[0]
       
        # Simu parameters
        self.commandScript = ''
        for iscenarioParameters in self.doc['scenarioParameters'].items():
            commandraw= " --"+str(iscenarioParameters[0])+"="+str(iscenarioParameters[1][0])
            self.commandScript = self.commandScript + commandraw
        #print (self.commandScript)
    
        # ns-3 script configuration
        self.ns3_path = str(self.doc['ns3Parameters']['ns3_path'])
        self.ns3_path = os.getcwd() + '/' + self.ns3_path
        self.ns3_script = str(self.doc['ns3Parameters']['ns3_script'])
        self.CampaignTag = str(self.doc['ns3Parameters']['CampaignTag'])
        self.configurations_file = configurations_file       
        self.cluster_path = str(self.doc['ns3Parameters']['cluster_path'])
        self.simLocation = str(self.doc['ns3Parameters']['simLocation'])
        
        # Shell Script Parameters configuration
        self.nOfCurlines=self.doc['ShellScriptParameters']['nOfCurlines']
        self.SimTied = self.doc['ShellScriptParameters']['SimTied']
        self.nOfCurlinesTied = self.doc['ShellScriptParameters']['nOfCurlinesTied']
        self.daytime  = self.doc['ShellScriptParameters']['daytime']
        self.htime  = self.doc['ShellScriptParameters']['htime']
        self.ntasks = self.doc['ShellScriptParameters']['ntasks']
        self.cpusPerTask = self.doc['ShellScriptParameters']['cpusPerTask']
        self.numberOfJobsShellScript = int(self.doc['ShellScriptParameters']['numberOfJobsShellScript'])
        
         #Lines/curves
        self.campaignX = self.doc['campaignLines']['campaignX']
        self.campaignLines = self.doc['campaignLines']['campaignLines']
        self.nJobs = int(self.doc['campaignLines']['jobs'])
        
    def recursiveCommand(self,CurLine,scenarioParameters,vposition):
        command = (" --"+CurLine+"="+scenarioParameters[CurLine][vposition])
        return command
        
    
    def runCampaign(self,curCampaign):
        # Configure simulation file in accordance with campaign parameter
        numberOfJobsShellScript = self.numberOfJobsShellScript
        for iCallScripts in range (0,int(self.nJobs/numberOfJobsShellScript)):
            sh_name_main = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_AllJOBS'+str(iCallScripts) +".sh"
            print("Main Shell Script: " + sh_name_main)  
            with open(sh_name_main, "w") as f:
                f.write("#!/bin/bash\n")
                #f.write("cd "+ self.cluster_path +"\n")
                for iJob in range(iCallScripts*numberOfJobsShellScript,iCallScripts*numberOfJobsShellScript + numberOfJobsShellScript):
                    for iSim in range(0, int(self.ntasks)):
                        sh_name = "run_"+self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(iSim)
                        f.write("sbatch " + sh_name + ".sh" + " & sleep 1\n")            
        for iJob in range(0,self.nJobs):         
            nOfCurlines=int(self.nOfCurlines[0]) # number of Campaign Lines in 1 simulation (max value = 3)
            SimTied = int(self.SimTied[0]) # whether or not the simulation parameters are tied (0 or 1)
            nOfCurlinesTied = int(self.nOfCurlinesTied[0]) # number of Campaign Lines tied (max value = nOfCurlines)
            with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
            count = 0
            """
            if SimTied == 0:
                minIterations=1
                for CampaignLines in self.doc['campaignLines']['campaignLines']:
                    CurlineIteration = len(self.doc['scenarioParameters'][CampaignLines])
                    totalCurlineIterations = minIterations*CurlineIteration
                    minIterations= totalCurlineIterations
                
                for varParam in self.doc['scenarioParameters'][curCampaign]:
                    tracker = [0]*nOfCurlines
                    for itotalCurlineIterations in range(totalCurlineIterations):
                        sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                        print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                        with open('run_%s.sh' % sh_name, 'w') as f:                    
                            f.write('#!/bin/bash\n')
                            f.write('#SBATCH --ntasks=1\n')
                            f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                            f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                            f.write('module load softwares/gsrc/2020_05\n')
                            outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                            #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                            #for iJob in range(0, self.nJobs):
                            f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                            f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                            f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                            f.write("cd '"+self.cluster_path+"'"+"\n")
                            command1 = (
                            'srun -N 1 -n 1' +
                            " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                            " --run '"+self.ns3_script+
                            " --RngRun="+str(jobRunSeed[iJob]))
                            command = ''
                            for iCampaignLines in range(len(self.doc['campaignLines']['campaignLines'])):
                                commandraw=self.recursiveCommand(self.doc['campaignLines']['campaignLines'][iCampaignLines], self.doc['scenarioParameters'],tracker[iCampaignLines])
                                command = command + commandraw
                                maxParamCurline = len(self.doc['scenarioParameters'][self.doc['campaignLines']['campaignLines'][iCampaignLines]])
                                print (command)
                                if iCampaignLines == 0 and tracker[iCampaignLines] < maxParamCurline:
                                    tracker[iCampaignLines] +=1
                                elif iCampaignLines == 0 and tracker[iCampaignLines] == maxParamCurline:
                                    tracker[iCampaignLines] = 0
                                
                                if iCampaignLines > 0:
                                    maxParamCurlinePrevious = len(self.doc['scenarioParameters'][self.doc['campaignLines']['campaignLines'][iCampaignLines-1]])
                                    if tracker[iCampaignLines-1] == maxParamCurlinePrevious:
                                        tracker[iCampaignLines] +=1
                                        tracker[iCampaignLines-1] =0
                            
                            command3 =(
                            " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                            command+
                            " --"+curCampaign+"="+varParam+
                            "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                            f.write(command1+self.commandScript+command3+'\n')
                            count = count + 1
                          
            """
            if nOfCurlines == 1 and SimTied == 0:
                curline = self.campaignLines[0]
                count=0
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                for i in range(len(self.doc['scenarioParameters'][curline])):    
                    for varParam in self.doc['scenarioParameters'][curCampaign]:
                        sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                        print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                        with open('run_%s.sh' % sh_name, 'w') as f:                    
                            f.write('#!/bin/bash\n')
                            f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                            f.write('#SBATCH --ntasks=1\n')
                            f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                            f.write('module load softwares/gsrc/2020_05\n')
                            outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                            #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                            #for iJob in range(0, self.nJobs):
                            f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                            f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                            f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                            f.write("cd '"+self.cluster_path+"'"+"\n")
                            command1 = (
                                'srun -N 1 -n 1' +
                                " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                                " --run '"+self.ns3_script+
                                " --RngRun="+str(jobRunSeed[iJob]))
                            command3 =(
                            " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                            " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                            " --"+curCampaign+"="+varParam+
                            "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                            f.write(command1+self.commandScript+command3+'\n')
                            count = count + 1
                                
            elif nOfCurlines==2 and SimTied == 0:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                count=0
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for j in range(len(self.doc['scenarioParameters'][curline1])):
                        for varParam in self.doc['scenarioParameters'][curCampaign]:
                            sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                            print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                            with open('run_%s.sh' % sh_name, 'w') as f:                    
                                f.write('#!/bin/bash\n')
                                f.write('#SBATCH --ntasks=1\n')
                                f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                                f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                                f.write('module load softwares/gsrc/2020_05\n')
                                outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                                #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                                #for iJob in range(0, self.nJobs):
                                f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                                f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                                f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                                f.write("cd '"+self.cluster_path+"'"+"\n")
                                command1 = (
                                'srun -N 1 -n 1' +
                                " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                                " --run '"+self.ns3_script+
                                " --RngRun="+str(jobRunSeed[iJob]))
                                command3 =(
                                " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                                " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                                " --"+curline1+"="+self.doc['scenarioParameters'][curline1][j]+
                                " --"+curCampaign+"="+varParam+
                                "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                                f.write(command1+self.commandScript+command3+'\n')
                                count = count + 1
                            

            elif nOfCurlines == 3 and SimTied == 0:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                curline2 = self.campaignLines[2]
                count=0;
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for j in range(len(self.doc['scenarioParameters'][curline1])):
                        for k in range(len(self.doc['scenarioParameters'][curline2])):
                            for varParam in self.doc['scenarioParameters'][curCampaign]:
                                sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                                print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                                with open('run_%s.sh' % sh_name, 'w') as f:                    
                                    f.write('#!/bin/bash\n')
                                    f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                                    f.write('#SBATCH --ntasks=1\n')
                                    f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                                    f.write('module load softwares/gsrc/2020_05\n')
                                    outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                                    #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                                    #for iJob in range(0, self.nJobs):
                                    f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                                    f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                                    f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                                    f.write("cd '"+self.cluster_path+"'"+"\n")
                                    command1 = (
                                    'srun -N 1 -n 1' +
                                    " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                                    " --run '"+self.ns3_script+
                                    " --RngRun="+str(jobRunSeed[iJob]))
                                    command3 =(
                                    " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                                    " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                                    " --"+curline1+"="+self.doc['scenarioParameters'][curline1][j]+
                                    " --"+curline2+"="+self.doc['scenarioParameters'][curline2][k]+
                                    " --"+curCampaign+"="+varParam+
                                    "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                                    f.write(command1+self.commandScript+command3+'\n')
                                    count = count + 1
            
            elif nOfCurlines == 2 and SimTied == 1 and nOfCurlinesTied == 2:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                #curline=self.doc['scenarioParameters'][campaignLines][0]
                #curline1=self.doc['scenarioParameters'][campaignLines][1]
                count=0
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for varParam in self.doc['scenarioParameters'][curCampaign]:
                        sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                        print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                        with open('run_%s.sh' % sh_name, 'w') as f:
                            f.write('#!/bin/bash\n')
                            f.write('#SBATCH --ntasks=1\n')
                            f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                            f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                            f.write('module load softwares/gsrc/2020_05\n')
                            outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                            #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                            #for iJob in range(0, self.nJobs):
                            f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                            f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                            f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                            f.write("cd '"+self.cluster_path+"'"+"\n")
                            command1 = (
                            'srun -N 1 -n 1' +
                            " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                            " --run '"+self.ns3_script+
                            " --RngRun="+str(jobRunSeed[iJob]))
                            command3 =(
                            " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                            " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                            " --"+curline1+"="+self.doc['scenarioParameters'][curline1][i]+
                            " --"+curCampaign+"="+varParam+
                            "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                            f.write(command1+self.commandScript+command3+'\n')
                            count = count + 1

                        
            elif nOfCurlines == 3 and SimTied == 1 and nOfCurlinesTied == 2:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                curline2 = self.campaignLines[2]
                count=0;
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for k in range(len(self.doc['scenarioParameters'][curline2])):
                        for varParam in self.doc['scenarioParameters'][curCampaign]:
                            sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                            print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                            with open('run_%s.sh' % sh_name, 'w') as f:
                                f.write('#!/bin/bash\n')
                                f.write('#SBATCH --ntasks=1\n')
                                f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                                f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                                f.write('module load softwares/gsrc/2020_05\n')
                                outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                                #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                                #for iJob in range(0, self.nJobs):
                                f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                                f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                                f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                                f.write("cd '"+self.cluster_path+"'"+"\n")
                                command1 = (
                                'srun -N 1 -n 1' +
                                " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                                " --run '"+self.ns3_script+
                                " --RngRun="+str(jobRunSeed[iJob]))
                                command3 =(
                                " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                                " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                                " --"+curline1+"="+self.doc['scenarioParameters'][curline1][i]+
                                " --"+curline2+"="+self.doc['scenarioParameters'][curline2][k]+
                                " --"+curCampaign+"="+varParam+
                                "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                                f.write(command1+self.commandScript+command3+'\n')
                                count = count + 1
            
            elif nOfCurlines == 3 and SimTied == 1 and nOfCurlinesTied == 3:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline0 = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                curline2 = self.campaignLines[2]
                count=0
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for varParam in self.doc['scenarioParameters'][curCampaign]:
                        sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                        print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                        with open('run_%s.sh' % sh_name, 'w') as f:
                            f.write('#!/bin/bash\n')
                            f.write('#SBATCH --ntasks=1\n')
                            f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                            f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                            f.write('module load softwares/gsrc/2020_05\n')
                            outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                            #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                            #for iJob in range(0, self.nJobs):
                            f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                            f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                            f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                            f.write("cd '"+self.cluster_path+"'"+"\n")
                            command1 = (
                            'srun -N 1 -n 1' +
                            " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                            " --run '"+self.ns3_script+
                            " --RngRun="+str(jobRunSeed[iJob]))
                            command3 =(
                            " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                            " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                            " --"+curline1+"="+self.doc['scenarioParameters'][curline1][i]+
                            " --"+curline2+"="+self.doc['scenarioParameters'][curline2][i]+
                            " --"+curCampaign+"="+varParam+
                            "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                            f.write(command1+self.commandScript+command3+'\n')
                            count = count + 1
            
            elif nOfCurlines == 4 and SimTied == 1 and nOfCurlinesTied == 2:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                curline2 = self.campaignLines[2]
                curline3 = self.campaignLines[3]
                count=0
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for k in range(len(self.doc['scenarioParameters'][curline2])):
                        for n in range(len(self.doc['scenarioParameters'][curline3])):
                            for varParam in self.doc['scenarioParameters'][curCampaign]:
                                sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                                print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                                with open('run_%s.sh' % sh_name, 'w') as f:
                                    f.write('#!/bin/bash\n')
                                    f.write('#SBATCH --ntasks=1\n')
                                    f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                                    f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                                    f.write('module load softwares/gsrc/2020_05\n')
                                    outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                                    #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                                    #for iJob in range(0, self.nJobs):
                                    f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                                    f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                                    f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                                    f.write("cd '"+self.cluster_path+"'"+"\n")
                                    command1 = (
                                    'srun -N 1 -n 1' +
                                    " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                                    " --run '"+self.ns3_script+
                                    " --RngRun="+str(jobRunSeed[iJob]))
                                    command3 =(
                                    " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                                    " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                                    " --"+curline1+"="+self.doc['scenarioParameters'][curline1][i]+
                                    " --"+curline2+"="+self.doc['scenarioParameters'][curline2][k]+
                                    " --"+curline3+"="+self.doc['scenarioParameters'][curline3][n]+
                                    " --"+curCampaign+"="+varParam+
                                    "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                                    f.write(command1+self.commandScript+command3+'\n')
                                    count = count + 1
            
            elif nOfCurlines == 5 and SimTied == 1 and nOfCurlinesTied == 2:
                with open('ListOfRandomNumbers.pkl', 'rb') as f:
                    jobRunSeed = pickle.load(f)
                curline = self.campaignLines[0]
                curline1 = self.campaignLines[1]
                curline2 = self.campaignLines[2]
                curline3 = self.campaignLines[3]
                curline4 = self.campaignLines[4]
                count=0
                for i in range(len(self.doc['scenarioParameters'][curline])):
                    for k in range(len(self.doc['scenarioParameters'][curline2])):
                        for n in range(len(self.doc['scenarioParameters'][curline3])):
                            for h in range(len(self.doc['scenarioParameters'][curline4])):
                                for varParam in self.doc['scenarioParameters'][curCampaign]:
                                    sh_name = self.campaign_name + '_' + self.simLocation + '_' + curCampaign + '_JOB' + str(iJob) + '_Sim_' + str(count)
                                    print(curCampaign+" campaign written in file: " 'run_%s.sh' % sh_name)
                                    with open('run_%s.sh' % sh_name, 'w') as f:
                                        f.write('#!/bin/bash\n')
                                        f.write('#SBATCH --ntasks=1\n')
                                        f.write('#SBATCH --cpus-per-task='+self.cpusPerTask+'\n')
                                        f.write('#SBATCH --time='+self.daytime+'-'+self.htime+':0 #especifica o tempo máximo de execução do job, dado no padrão dias-horas:minutos\n')
                                        f.write('module load softwares/gsrc/2020_05\n')
                                        outputDir = self.cluster_path+'results_'+self.simLocation + '_' + self.campaign_name + '_' + curCampaign
                                        #f.write('rm -rf '+outputDir+"/JOB"+str(iJob)+' 2>/dev/null\n')
                                        #for iJob in range(0, self.nJobs):
                                        f.write('mkdir -p '+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +'\n')
                                        f.write('cp -f run_'+sh_name+'.sh'+' '+outputDir+'\n')
                                        f.write('cp -f '+self.configurations_file+ ' ' +outputDir+'\n')
                                        f.write("cd '"+self.cluster_path+"'"+"\n")
                                        command1 = (
                                        'srun -N 1 -n 1' +
                                        " ./waf --cwd='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"
                                        " --run '"+self.ns3_script+
                                        " --RngRun="+str(jobRunSeed[iJob]))
                                        command3 =(
                                        " --outputDir='"+outputDir+"/JOB"+str(iJob)+"/Sim_"+str(count) +"'"+
                                        " --"+curline+"="+self.doc['scenarioParameters'][curline][i]+
                                        " --"+curline1+"="+self.doc['scenarioParameters'][curline1][i]+
                                        " --"+curline2+"="+self.doc['scenarioParameters'][curline2][k]+
                                        " --"+curline3+"="+self.doc['scenarioParameters'][curline3][n]+
                                        " --"+curline4+"="+self.doc['scenarioParameters'][curline4][h]+
                                        " --"+curCampaign+"="+varParam+
                                        "' > "+outputDir+"/JOB"+str(iJob)+'/Sim_' + str(count)+'.out 2>&1')
                                        f.write(command1+self.commandScript+command3+'\n')
                                        count = count + 1

            #f.write('wait')
                                                
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type=str, help='Configuration File')
args = parser.parse_args()

configurations_file = args.file; 
with open(configurations_file, 'r') as f:
    doc = yaml.load(f, Loader=yaml.loader.BaseLoader)
    campaign_name = os.path.splitext(configurations_file)[0]
"""
doc = {'ns3Parameters': {'ns3_path': '',
  'ns3_script': 'NrMmtc-M0_v10_REM',
  'cluster_path': '/home/drdluna/5G-LENA/ns-3-dev-nr-1.2-rem/',
  'filename': 'CampaignNrCa',
  'simLocation': 'cluster'},
 'ShellScriptParameters': {'nOfCurlines': '3',
  'SimTied': '0',
  'nOfCurlinesTied': '0',
  'daytime': '1',
  'htime': '6',
  'ntasks': '8',
  'cpusPerTask': '1',
  'numberOfJobsShellScript': '1'},
 'campaignLines': {'campaignX': ['totalUePower'],
  'campaignLines': ['totalTxPower', 'DowntiltAngleDegree','BearingAngleTilt'],
  'jobs': '1'},
 'scenarioParameters': {'window': ['0.1'],
  'simTime': ['15'],
  'Isd': ['500'],
  'ueNumScenario': ['84'],
  'centralFrequencyBand': ['2350000000'],
  'bandwidthBand': ['100000000'],
  'BwpConfiguration': ['1'],
  'BwpBand': ['72000000'],
  'remBwpId': ['0'],
  'scenario': ['UmaLos'],
  'Shadowing': ['0'],
  'ChannelUpdate': ['0'],
  'totalTxPower': ['32', '26'],
  'totalUePower': ['23', '17'],
  'DowntiltAngleDegree': ['0', '15'],
  'BearingAngleTilt': ['0','-30'],
  'UlMode': ['1'],
  'TrafficModel': ['TriggeredReport'],
  'numerology': ['0'],
  'PacketSize': ['125'],
  'interval': ['60'],
  'Lambda': ['0.1']}}

configurations_file = "SimPerScriptCampaign_Teste.yaml"
"""
print('Simulação escolhida: ')
campaign = doc['campaignLines']['campaignX']
print(campaign)
                 
simu = Simulation(configurations_file)

for simC in campaign:
    simu.runCampaign(simC)
