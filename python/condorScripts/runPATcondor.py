#local
import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing ()

options.register ('option',
                  "Condor", # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.string,          # string, int, or float
                  "Condor")

options.register ('slice',
                  0, # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.int,          # string, int, or float
                  "Slice of sample")

options.register ('sample',
                  "DY", # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.string,          # string, int, or float
                  "Sample name")


options.parseArguments()
slice = options.slice
sampleName = options.sample
print "slice number", slice
print "sample is ", sampleName

nevents = -1

if sampleName=="DY":
    runOnMC = True
    path1 = "/storage/data/cms/store/mc/Summer12_DR53X/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/AODSIM/PU_S10_START53_V7A-v1/0000/"
    path2 = "/storage/data/cms/store/mc/Summer12_DR53X/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/AODSIM/PU_S10_START53_V7A-v1/0001/"
    path3 = "/storage/data/cms/store/mc/Summer12_DR53X/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/AODSIM/PU_S10_START53_V7A-v1/0002/"
    pathList = [path1,path2,path3]
    njobs=859
    outDir='DYjets_Summer12_S10_2014'
    
if sampleName=="TT":
    runOnMC = True
    path = "/storage/data/cms/store/mc/Summer12_DR53X/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/"
    pathList = [path]
    njobs=722
    outDir='TTjets_Summer12_S10_2014'

if sampleName=="DataMuD":
    runOnMC = False
    path = "/storage/data/cms/store/data/Run2012D/DoubleMuParked/AOD/22Jan2013-v1/30001/"
    pathList = [path]
    njobs=1000
    outDir='DataMuD_2014'

if sampleName=="DataElB":
    runOnMC = False
    path = "/storage/data/cms/store/data/Run2012B/DoubleElectron/AOD/22Jan2013-v1/20001/"
    pathList = [path]
    njobs=500
    outDir='DataElB_2014'
    
    
import os

files=[]
for path in pathList:
    pathname = "file:"+path
    dirList=os.listdir(path)
    for fname in dirList:
        files.append(pathname+fname)
        
if slice: files = files[len(files)*(slice-1)/njobs:len(files)*slice/njobs]
print "input files are", files
print ""

pathdir = '/nfs/user/acaudron/'

if slice : out_fileName = pathdir+outDir+'/pat53_'+str(slice)+'.root'
else     : out_fileName ='test.root'
print "output file is", out_fileName
print ""
#end local

                                                                        
