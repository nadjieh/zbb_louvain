import ROOT
import sys
import os 
from AnalysisEvent import AnalysisEvent
from eventSelection import *
from LumiReWeighting import *
from zbbCommons import zbblabel,zbbfile

def btagEfficiencyTreeProducer(stage=4, muChannel=True, path='../testfiles/'):
  # prepare output
  ROOT.gROOT.ProcessLine(
  "struct MyStruct {\
     Float_t     pt;\
     Float_t     eta;\
     Int_t       flavor;\
     Float_t     ssvhe;\
     Float_t     ssvhp;\
     Float_t     csv;\
     Float_t     eventWeight;\
  };" )
  from ROOT import MyStruct
  mystruct = MyStruct()
  f = ROOT.TFile( 'mybtagEfftree.root', 'RECREATE' )
  tree = ROOT.TTree( 'btagEff', 'btag efficiency' )
  tree.Branch( 'data', mystruct, 'pt/F:eta/F:flavor/I:ssvhe/F:ssvhp/F:csv/F:eventWeight/F' )
  # input
  if os.path.isdir(path):
    dirList=os.listdir(path)
    files=[]
    for fname in dirList:
      files.append(path+fname)
  elif os.path.isfile(path):
    files=[path]
  else:
    files=[]
  events = AnalysisEvent(files)
  prepareAnalysisEvent(events,btagging="SSV",ZjetFilter="bcl",checkTrigger=False)
  weight_engine = LumiReWeighting(zbbfile.pileupMC, zbbfile.pileupData, zbblabel.pulabel)
  # event loop
  eventCnt = 0
  for event in events:
    categoryData = event.catMu if muChannel else event.catEle
    goodJets = event.goodJets_mu if muChannel else event.goodJets_ele
    if isInCategory(stage, categoryData):
      eventCnt = eventCnt +1
      if eventCnt%100==0 : print ".",
      if eventCnt%1000==0 : print ""
      # event weight
      mystruct.eventWeight = weight_engine.weight( fwevent=event )
      # that's where we access the jets
      for index,jet in enumerate(event.jets):
        if not goodJets[index]: continue
        mystruct.pt = jet.pt()
        mystruct.eta = jet.eta()
        mystruct.flavor = jet.partonFlavour()
        mystruct.ssvhe = jet.bDiscriminator("simpleSecondaryVertexHighEffBJetTags")
        mystruct.ssvhp = jet.bDiscriminator("simpleSecondaryVertexHighPurBJetTags")
        mystruct.csv = jet.bDiscriminator("combinedSecondaryVertexBJetTags")
        tree.Fill()
  f.Write()
  f.Close()
  print ""

