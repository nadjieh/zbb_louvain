#!/usr/bin/env python
#Usage: python Launch_allCP ConfigFile
#example: python Launch_allCP zbbConfig

import urllib
import string
import os
import sys
import LaunchOnCondor
import glob
theConfig = "UserCode.zbb_louvain."+sys.argv[1]+"_"+sys.argv[2]
if theConfig is not None:
    configImplementation = __import__(theConfig)
    atts=theConfig.split(".")[1:]
    for att in atts : configImplementation = getattr(configImplementation,att)
    configuration = configImplementation.configuration

mode = configuration.runningMode

dir_plot = {
  "abdollah": "",
  "acaudron": "/nfs/user/acaudron/ControlPlots/cp5314p1/",
  "ajafari": "/home/fynu/ajafari/storage/CP/V5/",
  "bfrancois": "/nfs/user/bfrancois/RDS/ControlPlots/",
  "cbeluffi": "/home/fynu/cbeluffi/storage/ControlPlots/",
  "vizangarciaj": "/home/fynu/vizangarciaj/storage/CP/testOct2014/",
}

dir_rds = {
  "abdollah": "",
  "acaudron": "/nfs/user/acaudron/ControlPlots/cp5314p1/",
  "ajafari": "/home/fynu/ajafari/storage/RDS/SL6/V5"+sys.argv[2]+"/",
  "bfrancois": "/nfs/user/bfrancois/RDS/",
  "cbeluffi": "/home/fynu/cbeluffi/storage/ControlPlots/",
  "vizangarciaj": "/home/fynu/vizangarciaj/storage/RDS/testOct2014/",
}



        
samples = [
    #"DATA",
    #"DY",
    #"TT",
    #"ZZ",
    ##"ZH",
    #"WW",
    #"WZ",
    #"SingleT",
    ##"ZA"
    "Hamb"
    ]
ZZsamples = [
    "ZZ",
    ]
WZsamples = [
    "WZ",
    ]
WWsamples = [
    "WW",
    ]
ZAsamples = [
    "ZA_350_15",
    "ZA_350_30",
    "ZA_350_70",
    #"ZA_142_35",
    #"ZA_200_50",
    #"ZA_200_90",
    #"ZA_329_30",
    #"ZA_329_70",
    #"ZA_329_142",
    #"ZA_575_70",
    #"ZA_575_142",
    #"ZA_575_378",
    #"ZA_875_70",
    #"ZA_875_142",
    #"ZA_875_378",
    #"ZA_875_575",
    #"ZA_875_761",
    #"ZA_286_93",
    #"ZA_662_500",
    #"ZA_262_99",
    #"ZA_660_450",
    ]
DYMissing = [
   ("DYjets" , [0, 1, 10, 100, 103, 104, 105, 106, 108, 109, 11, 111, 112, 113, 114, 115, 116, 117, 118, 119, 12, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 13, 131, 132, 133, 134, 135, 136, 137, 138, 139, 14, 140, 141, 142, 144, 145, 146, 147, 149, 15, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 16, 160, 161, 163, 164, 165, 166, 167, 168, 169, 17, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 18, 180, 181, 186, 187, 188, 189, 19, 190, 192, 194, 195, 196, 198, 199, 2, 20, 200, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 214, 215, 216, 217, 218, 219, 22, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 23, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 24, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 26, 260, 261, 263, 264, 265, 266, 267, 268, 269, 27, 270, 271, 272, 273, 274, 275, 276, 277, 278, 28, 280, 281, 282, 285, 287, 288, 289, 29, 291, 292, 293, 294, 295, 296, 298, 299, 3, 30, 32, 33, 34, 36, 37, 39, 4, 41, 43, 44, 48, 49, 5, 50, 52, 53, 54, 55, 56, 57, 58, 59, 6, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 7, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 8, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 9, 90, 92, 93, 95, 96, 97, 98, 99]),
   ("DYjets_M10to50", [10, 12, 13, 14, 15, 16, 17, 19, 2, 20, 27, 34, 35, 36, 37, 38, 39, 4, 40, 41, 44, 45, 47, 48, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 6, 60, 61, 62, 63, 64, 65, 66, 67, 7, 71, 74, 75, 76, 79, 8, 80, 81, 83, 85, 86, 87, 88, 89, 9, 90, 92, 93, 94, 95, 96, 97, 98, 99]),
]
DYsamples = [
    #"DYjets",
    #"DY1jets",
    #"DY2jets",
    #"DY3jets",
    #"DY4jets",
    #"DYjets_Pt50to70",
    #"DYjets_Pt70to100",
    #"DYjets_Pt100",
    #"DYjets_Pt180",
    #"DYjets_HT200to400",
    #"DYjets_HT400",
    #"Zbb",
    "DYjets_M10to50",
    #"DYjets_aMCatNLO",
    ]

DYbcl = [""]
if mode == "plots":
    DYbcl = [
        "_2b",
        "_1b",
        "_0b",
        ]

TTsamples = [
    "TTFullLept",
    #"TTSemiLept",
    ]
TTMissing = [
    ("TTFullLept", [0, 1, 10, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 11, 110, 111, 112, 113, 114, 115, 116, 117, 12, 121, 123, 124, 125, 126, 127, 128, 129, 13, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 14, 140, 141, 142, 143, 145, 146, 148, 149, 15, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 16, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 17, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 18, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 19, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 2, 20, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 21, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 23, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 24, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 26, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 27, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 28, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 29, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 3, 30, 301, 302, 303, 304, 305, 306, 307, 308, 309, 31, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 32, 320, 321, 322, 326, 327, 328, 329, 33, 330, 331, 332, 333, 334, 336, 339, 34, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 35, 350, 351, 352, 353, 354, 355, 356, 359, 36, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 37, 370, 371, 372, 373, 374, 375, 376, 377, 378, 38, 380, 381, 382, 383, 384, 385, 387, 389, 39, 391, 392, 393, 395, 396, 397, 398, 399, 4, 40, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 41, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 42, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 43, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 44, 440, 441, 442, 443, 444, 445, 446, 447, 448, 45, 46, 47, 48, 49, 5, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 7, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 8, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 9, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]),
]
Hambsamples = [
   "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-30_LowJetPt10",
   "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-40_LowJetPt10",
   "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-50_LowJetPt10",
   "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-60_LowJetPt10",
]
HambMissing = [
	("H2ToH1H1_H1To2Mu2B_mH2-125_mH1-30_LowJetPt10" , []),
	("H2ToH1H1_H1To2Mu2B_mH2-125_mH1-40_LowJetPt10" , [35]),
	("H2ToH1H1_H1To2Mu2B_mH2-125_mH1-50_LowJetPt10" , []),
	("H2ToH1H1_H1To2Mu2B_mH2-125_mH1-60_LowJetPt10" , []),
]
mass = [125] #[110,115,120,125,130,135]

SingleTsamples = [
    "Wt",
    "Wtbar",
    #"SingleT_s-Channel",
    #"SingleTbar_s-Channel",
    #"SingleT_t-Channel",
    #"SingleT_t-Channel"
    ]

MC = "Summer12"
DATA = "2012"
PATversion = "5320"
#PATversion = "ReReco"
#cpVersion = "V44"
cpVersion = ""
README = "What you produced... \nAll configurations are available in ../config"

stages = "--all"
#stages = "-l 18,37"

#dyweight = 'Merging' #apply weight in order to merge DY ptZ, HT and inclusive
#dyweight = 'mc' #apply weight for DY aMC@NLO
#dyweight = 'sfs_dy__Merging' 
#dyweight = 'sfs_dy' #apply data driven normalisation for bkg
#ttweight = 'sfs_tt'
dyweight = 'Merging' # no weight
ttweight = ''
dybjetsplitting = False

listdata=[
    "A",
    "B",
    "C",
    "D",
    ]
listdataMissing =[
    ("A" , []),
    ("B" , [124,117,41]),
    ("C" , [87, 72, 88, 89, 91, 92, 154, 163, 164, 158, 151, 149, 171, 170, 209, 188, 232, 233, 217, 237, 84, 196, 168, 207, 206, 187, 141, 111, 213, 29, 36, 192, 31, 112, 173, 152, 110]),
    ("D" , [26, 30, 18, 19, 33, 52, 55, 56, 101, 98, 106, 95, 236, 230, 244, 245, 246, 269, 277, 283, 24, 234, 247, 218, 10, 32, 1, 107, 50]),
]

DataChannel = [
    #"DoubleEle",
    "DoubleMu",
    #"MuEG"
    ]

jobs = {
    "A" : 50,
    "B" : 150,
    "C" : 250,
    "D" : 300,  
    "TTjets" : 150,
    "TTFullLept" : 450,
    "TTSemiLept" : 250,
    "TTHadronic" : 100,
    "ZZ" : 50,
    "ZH" : 50,
    "ZA" : 50,
    "DYjets" : 300,
    "DY1jets" : 300,
    "DY2jets" : 200,
    "DY3jets" : 150,
    "DY4jets" : 100,
    "DYjets_Pt50to70" : 200,
    "DYjets_Pt70to100" : 100,
    "DYjets_Pt100" : 80,
    "DYjets_Pt180" : 50,
    "DYjets_HT200to400" : 80,
    "DYjets_HT400" : 50,
    "Zbb" : 400,
    "WW" : 50,
    "WZ" : 50,
    "Wt" : 50,
    "Wtbar" : 50,
    "SingleT_s-Channel" : 10,
    "SingleTbar_s-Channel" : 10,
    "SingleT_t-Channel" : 100,
    #"SingleT_t-Channel" : 100,
    "DYjets_M10to50" : 100,
    "DYjets_aMCatNLO" : 300,
    "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-30_LowJetPt10" : 50,
    "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-40_LowJetPt10" : 50,
    "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-50_LowJetPt10" : 50,
    "H2ToH1H1_H1To2Mu2B_mH2-125_mH1-60_LowJetPt10" : 50,
    }

if mode == "plots":
    dir = dir_plot[os.environ["USER"]]
    string_mode='ControlPlots_'
elif mode == "dataset":
    dir = dir_rds[os.environ["USER"]]
    string_mode='RDS_'

os.system('mkdir '+dir+string_mode+cpVersion)
f = open(dir+string_mode+cpVersion+'/README.txt', 'w')
f.write(README)
f.close()
os.system('mkdir '+dir+"/config")
os.system('cp ../Hamb*.py ../hamb*.py ../basicConfig*.py ../ObjectSelection.py ../Objects*.py '+dir+"/config")


for sample in samples :
    if sample=="ZH":
        for m in mass:
            os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+sample+str(m))
            LaunchOnCondor.Jobs_FinalCmds.append('mv ZH'+str(m)+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+sample+str(m)+'/ \n')
    elif sample=="ZA":
        for za in ZAsamples:
            os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+za)
            LaunchOnCondor.Jobs_FinalCmds.append('mv '+za+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+za+'/ \n')
    elif sample=="DY":
        for dy in DYsamples :
            if dybjetsplitting:
                for fl in DYbcl :
                    os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+dy+fl)
                    LaunchOnCondor.Jobs_FinalCmds.append('mv '+dy+fl+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+dy+fl+'/ \n')
            else:
                os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+dy)
	        LaunchOnCondor.Jobs_FinalCmds.append('mv '+dy+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+dy+'/ \n')
    elif sample=="TT":
        for tt in TTsamples :
            os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+tt)
            LaunchOnCondor.Jobs_FinalCmds.append('mv '+tt+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+tt+'/ \n')
    elif sample=="SingleT":
        for St in SingleTsamples :
            os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+St)
            LaunchOnCondor.Jobs_FinalCmds.append('mv '+St+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+St+'/ \n')
    elif sample=="DATA":
        for ch in DataChannel :
            for period in listdata :
                os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+ch+DATA+period)
                LaunchOnCondor.Jobs_FinalCmds.append('mv '+ch+DATA+period+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+ch+DATA+period+'/ \n')
    elif sample=="Hamb":
        for St in Hambsamples :
            os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+St)
            LaunchOnCondor.Jobs_FinalCmds.append('mv '+St+'_'+MC+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+St+'/ \n')
    else :
        os.system('mkdir '+dir+string_mode+cpVersion+'/'+string_mode+sample)
        LaunchOnCondor.Jobs_FinalCmds.append('mv '+sample+'_*.root '+dir+string_mode+cpVersion+'/'+string_mode+sample+'/ \n')
        
FarmDirectory = dir+"FARM_"+string_mode+cpVersion
JobName = "CoPl_list_"+cpVersion

LaunchOnCondor.SendCluster_Create(FarmDirectory, JobName)

if "TT" in samples :
    for tt in TTsamples :
	missingTT = []
        for itt in range(0,len(TTMissing)):
          if TTMissing[itt][0] == tt:
            missingTT = TTMissing[itt][1]
        njobs = jobs[tt]
        for i in range(0,njobs):
	    #if not i in missingTT: continue
	    if i in missingTT: continue
            LaunchOnCondor.SendCluster_Push(["BASH", "export weightmode='"+ttweight+"'; "+os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_"+tt+"/ -o "+tt+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "SingleT" in samples :
    for St in SingleTsamples :
        njobs = jobs[St]
        for i in range(0,njobs):
            LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_"+St+"/ -o "+St+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "ZZ" in samples :
    njobs = jobs["ZZ"]
    for i in range(0,njobs):
        LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_ZZ/ -o ZZ_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "WZ" in samples :
    njobs = jobs["WZ"]
    for i in range(0,njobs):
        LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_WZ/ -o WZ_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "WW" in samples :
    njobs = jobs["WW"]
    for i in range(0,njobs):
        LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_WW/ -o WW_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "DATA" in samples :
    for ch in DataChannel :
        for period in listdata :
          missingData = []
          for idata in range(0,len(listdataMissing)):
             if listdataMissing[idata][0] == period:
                missingData = listdataMissing[idata][1]
          njobs = jobs[period]
          for i in range(0,njobs):
	     if not i in missingData: continue
             LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+"_data -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/"+ch+DATA+period+"/ -o "+ch+DATA+period+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "DY" in samples :
    for dy in DYsamples :
	missingList = []
        for iDy in range(0,len(DYMissing)):
          if DYMissing[iDy][0] == dy:
            missingList = DYMissing[iDy][1]
        njobs = jobs[dy]       
        if dybjetsplitting: 
            for fl in DYbcl :
                for i in range(0,njobs):
                    LaunchOnCondor.SendCluster_Push(["BASH", "export ZjetFilter='"+fl.replace("_","")+"'; export weightmode='"+dyweight+"'; "+os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_"+dy+"/ -o "+dy+fl+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])
        else:
            for i in range(0,njobs):
		#if not i in missingList: continue
		if i in missingList: continue
		LaunchOnCondor.SendCluster_Push(["BASH", "export weightmode='"+dyweight+"';"+os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_"+dy+"/ -o "+dy+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "ZH" in samples :
    mass = [125]#[115,120,125,130,135]
    for m in mass:
        njobs = jobs["ZH"]
        for i in range(0,njobs):
            LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_ZH"+str(m)+"/ -o ZH"+str(m)+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])

if "ZA" in samples :
    for za in ZAsamples:
        njobs = jobs["ZA"]
        for i in range(0,njobs):
            LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/acaudron/"+za+"_PAT2014/ -o "+za+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])
if "Hamb" in samples :
    for St in Hambsamples :
	missingList = []
        for iSt in range(0,len(HambMissing)):
	  if HambMissing[iSt][0] == St:
	    missingList = HambMissing[iSt][1]
        njobs = jobs[St]
        for i in range(0,njobs):
	    if not i in missingList: continue
            LaunchOnCondor.SendCluster_Push(["BASH", os.getcwd()+"/../PatAnalysis/ControlPlots.py -c "+theConfig+" -i /nfs/user/llbb/Pat_8TeV_"+PATversion+"/Summer12_"+St+"/ -o "+St+"_"+MC+"_"+str(i)+".root "+stages+" --Njobs "+str(njobs)+" --jobNumber "+str(i)])



LaunchOnCondor.SendCluster_Submit()
