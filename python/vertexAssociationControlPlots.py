#! /usr/bin/env python

import ROOT
import sys
import os
from AnalysisEvent import AnalysisEvent
from baseControlPlots import BaseControlPlots
from eventSelection import prepareAnalysisEvent
from vertexAssociation import *
from zbbCommons import zbblabel
#from myFuncTimer import print_timing

class VertexAssociationControlPlots(BaseControlPlots):
    """A class to create control plots for vertex association"""

    def __init__(self, dir=None, dataset=None, mode="plots"):
      # create output file if needed. If no file is given, it means it is delegated
      BaseControlPlots.__init__(self, dir=dir, purpose="vertexAssociation", dataset=dataset, mode=mode)
    
    def beginJob(self, sigcut = 2.):
      self.sigcut = sigcut
      # declare histograms
      self.add("nvertices","nvertices",30,0,30)
      self.add("vx","vx",400,-0.2,0.2)
      self.add("vy","vy",400,-0.2,0.2)
      self.add("vz","vz",100,-25,25)
      self.add("vxerr","vxerr",100,0,0.01)
      self.add("vyerr","vyerr",100,0,0.01)
      self.add("vzerr","vzerr",100,0,0.02)
      self.add("lepton_dz","z distance between the two Z leptons",100,0,0.2)
      self.add("l1v_dz","z distance between lepton and vertex",100,0,1.)
      self.add("l2v_dz","z distance between lepton and vertex",100,0,1.)
      self.add("lvertex","index of the lepton vertex",20,-0.5,19.5)

    #@print_timing
    def process(self,event):
      """vertexAssociationControlPlots"""
      result = { }
      result["nvertices"] = event.vertices.size()
      vertex = event.vertex
      result["vx"] = vertex.x()
      result["vy"] = vertex.y()
      result["vz"] = vertex.z()
      result["vxerr"] = vertex.xError()
      result["vyerr"] = vertex.yError()
      result["vzerr"] = vertex.zError()
      # relevant quantities to monitor: Z vs primary vertex
      bestZ = event.bestZcandidate
      if bestZ is None: return result
      lepton1 = bestZ.daughter(0)
      lepton2 = bestZ.daughter(1)
      result["lepton_dz"] = abs(lepton1.vz()-lepton2.vz())
      result["l1v_dz"] = abs(lepton1.vz()-vertex.z())
      result["l2v_dz"] = abs(lepton2.vz()-vertex.z())
      result["lvertex"] = findPrimaryVertexIndex(bestZ,event.vertices)
      return result

def runTest(path="../testfiles/ttbar/"):
  controlPlots = VertexAssociationControlPlots()

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
  prepareAnalysisEvent(events,checkTrigger=False)

  controlPlots.beginJob()
  i = 0
  for event in events:
    controlPlots.processEvent(event)
    if i%1000==0 : print "Processing... event ", i
    i += 1
  controlPlots.endJob()

