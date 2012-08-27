# to run this:
# go to the main() function, and define an object by copying the aother "testu" lines
# arguments go as follows:
# testu = unfolder(**dataset_path**, steps, startup, finish, **muchannel**)
# it will write results in a file which name is based on the current minute -> start different runs on different minutes 
# number of events to process is the argument of the main() function 

import ROOT
import sys
import os
import itertools
import time
import glob
import math
import datetime
from copy import deepcopy
import numpy as np

from DataFormats.FWLite import Events, Handle
import eventSelection as llbb
from zbbCommons import zbbfile, zbblabel

from LumiReWeighting import LumiReWeighting 
from LeptonsReweighting import LeptonsReWeighting
from btaggingWeight import btaggingWeight

class unfolder:
    """ Class to compute unfolding "matrices" """
    def __init__(self, infiles0 = "", whattodo = [], startup = [], finish = [], muchannel = None):
        """ Initialization: definition of all handles, etc ... """
        # allowing to use directories or filenames
        infiles = os.path.isdir(infiles0) and glob.glob(os.path.join(infiles0,"*")) or [infiles0]
        # variables that will become members
        self.collections = { "jets":          {"handle":"vector<pat::Jet>", "collection":zbblabel.jetlabel},
                             "muons":         {"handle":"vector<pat::Muon>", "collection":zbblabel.allmuonslabel},
                             "goodmuons":     {"handle":"vector<pat::Muon>", "collection":zbblabel.muonlabel},
                             "electrons":     {"handle":"vector<pat::Electron>", "collection":zbblabel.allelectronslabel},
                             "goodelectrons": {"handle":"vector<pat::Electron>", "collection":zbblabel.electronlabel},
                             "genjets":       {"handle":"vector<reco::GenJet>", "collection":"ak5GenJets"},
                             "genparticles":  {"handle":"vector<reco::GenParticle>", "collection":zbblabel.genlabel},
                             "zee":           {"handle":"vector<reco::CompositeCandidate>", "collection":"zelAllelAll"},
                             "zmumu":         {"handle":"vector<reco::CompositeCandidate>", "collection":"zmuAllmuAll"},
                             "zeegood":       {"handle":"vector<reco::CompositeCandidate>", "collection":zbblabel.zelelabel},
                             "zmumugood":     {"handle":"vector<reco::CompositeCandidate>", "collection":zbblabel.zmumulabel}
                           }
        # defining all handles
        for key, value in self.collections.items():
            setattr(self, key+"Handle", Handle (value["handle"]))
            setattr(self, key+"Collection", value["collection"])
        # load events
        self.events = Events (infiles)
        # tasks
        self.whattodo = whattodo
        self.startup = startup
        self.finish = finish
        # creating tasks vector to avoid function lookup for each event
        self.funcs_todo = [getattr(self, "step_"+task) for task in self.whattodo]
        # format outfile and logfile:
        self.outfile = "unfolding_"+datetime.datetime.strftime(datetime.datetime.now(),"%Y%d%m_%H%M")+".txt"
        self.logfile = "unfolding_log_"+datetime.datetime.strftime(datetime.datetime.now(),"%Y%d%m_%H%M")+".txt"
        logf = open(self.logfile, "w")
        logf.write("Running on %s \n" % (infiles0))
        logf.write("Muchannel = %s \n" % (str(muchannel)))
        logf.write("Output file = %s \n" % self.outfile)
        # mu channel (True means muons)
        self.muchannel = muchannel

    class usercontent:
        def __init__(self):
            self.stop = False

    def step(self, event):
        """ Run analysis step on one event. Everything should be done here """
        # get collections
        for key, value in self.collections.items():
            event.getByLabel(value["collection"], getattr(self,key+"Handle"))
            setattr(self, key, getattr(self,key+"Handle").product())
        # do magic
        ucont = self.usercontent()
        # initialize output
        ucont.event = event
        for task in self.funcs_todo:
            res = task(ucont)
            if ucont.stop: break
            if res:
                print "Error during", task
                return 1
        del ucont
               

    def run(self, tot = -1):
        """ run on the first 'tot' events """
        num = 1
        dumpevery = 10000
        if dumpevery > tot and tot > 0 : dumpevery = tot
        dumpfile = "unfolding_"+datetime.datetime.strftime(datetime.datetime.now(),"%Y%d%m_%H%M")+".txt"
        print "============================"
        print "=== Initialization steps ==="
        print "============================"
        for start in self.startup:
            start_todo = getattr(self,"start_"+start)
            start_todo()
        print "============================"
        print "===  running on events   ==="
        print "============================"
        for event in self.events:
            # print the first ten events to see when it really starts
            if num < 10: print "event:", num 
            # regularly print where we are
            if not num%(tot/10) and tot > 0: print "event:", num
            # dump output every few events in case of long runs
            if not num%dumpevery:
                self.out = ""
                for fin in self.finish:
                    finish_todo = getattr(self,"finish_"+fin)
                    finish_todo()
                outf = open(self.outfile, "w")
                outf.write(self.out)
                outf.write("last update: %s \n" % (str(datetime.datetime.now())))
                outf.close()
            self.step(event)
            num += 1
            if num > tot and tot > 0: break
        print "============================"
        print "===     Finalization     ==="
        print "============================"
        for fin in self.finish:
            finish_todo = getattr(self,"finish_"+fin)
            finish_todo()
        print "Results are in:", self.outfile

    def run_all(self):
        """ run list of tasks on all events in file(s) """
        print "============================"
        print "=== Initialization steps ==="
        print "============================"
        for start in self.startup:
            start_todo = getattr(self,"start_"+start)
            start_todo()
        print "============================"
        print "===   running on events  ==="
        print "============================"
        for event in self.events:
            self.step(event)
        print "============================"
        print "===     Finalization     ==="
        print "============================"
        for fin in self.finish:
            finish_todo = getattr(self,"finish_"+fin)
            finish_todo()

    # starting here, methods are supposed to be run inside the "step" method 
    # and can be called by their names as arguments of said method.
    # all collections are also supposed to be well defined
    def step_stupid_test(self,ucont):
        """ As a basic test, print all jet PT's as a list"""
        print "Jets PT:"
        print ", ".join([f_2(jet.pt()) for jet in self.jets])

    def step_event_weight(self, ucont):
        """ computing weight """
        ucont.rw = self.pu_engine.weight( fwevent=ucont.event )
        return 0

    # starting here, we'll be doing one step per matrix in order to get a clearer view of the process
    def step_a_l(self, ucont):
        """ computing:
                # number of gen b-jets per event
                # global flavour of the event
                # events passing leptons baseline cuts in each gen b-jet bin
                # events passing leptons acceptance cuts in each b-jet bin
        """
        # print number of reco b-jets for cross-check
        # print "reco b-jets:", len([jet for jet in self.jets if llbb.isBJet(jet,"HE","SSV")])
        # count total number of events
        # ----------------------------
        try:
            self.total_events += ucont.rw
        except AttributeError:
            self.total_events = ucont.rw
        # baseline leptons from Z
        #------------------------
        gen_elec_pt_base = 20.0
        gen_elec_eta_base = 2.5
        gen_muon_pt_base = 20.0
        gen_muon_eta_base = 2.5
        ucont.gen_z_yes = False
        ucont.flav = -1
        for particle in self.genparticles:
            if particle.pdgId() == 23:
                ucont.gen_leptons = [particle.daughter(i) for i in range(particle.numberOfDaughters()) if particle.daughter(i).pdgId() != 23]
                if ucont.gen_leptons:
                    if math.fabs(ucont.gen_leptons[0].pdgId()) == 13 and len([lep for lep in ucont.gen_leptons if acc_pt_eta(lep,gen_muon_pt_base,gen_muon_eta_base)])== 2:
                        ucont.flav = 13
                        if self.muchannel == True or self.muchannel == None:
                            ucont.gen_z_yes = True
                    elif math.fabs(ucont.gen_leptons[0].pdgId()) == 11 and len([lep for lep in ucont.gen_leptons if acc_pt_eta(lep,gen_elec_pt_base,gen_elec_eta_base)])== 2:
                        ucont.flav = 11
                        if self.muchannel == False or self.muchannel == None:
                            ucont.gen_z_yes = True
                    else:
                        ucont.flav = -1
                else: ucont.flav = -1
                break
        # number of gen b-jets + b-jets array
        # -----------------------------------
        gen_jet_pt  = 25.0
        gen_jet_eta = 2.1
        gen_jet_dr = 0.5
        gen_jet_lepton_dr = 0.5
        # match with b-hadrons
        # get final b-hadrons
        bparts = [part for part in self.genparticles if (499 < part.pdgId() < 600) or (4999 < part.pdgId() < 6000)]
        bhads = [part for part in bparts if is_final_bhad(part)]
        # bhads = [part for part in self.genparticles if is_final_bhad(part)]
        # list jets that match these by dr
        ucont.gen_b_jets = match_obo(self.genjets, bhads, gen_jet_dr)
        ucont.gen_b_jets_all = ucont.gen_b_jets[:]
        ucont.gen_b_jets = [jet for jet in ucont.gen_b_jets if acc_pt_eta(jet, gen_jet_pt, gen_jet_eta)]
        ucont.gen_b_jets = [jet for jet in ucont.gen_b_jets if not overlap(jet, ucont.gen_leptons, gen_jet_lepton_dr)]
        ucont.gen_b = len(ucont.gen_b_jets)>1 and 2 or len(ucont.gen_b_jets)
        if ucont.gen_z_yes:
            try:
                self.gen_baseline[ucont.gen_b] += ucont.rw
            except AttributeError:
                self.gen_baseline = [0,0,0]
                self.gen_baseline[ucont.gen_b] += ucont.rw
        # leptons in acceptance w/ correct reconstructed mass 
        # ---------------------------------------------------
        gen_elec_pt = 25.0
        gen_elec_eta = 2.5
        gen_muon_pt = 20.0
        gen_muon_eta = 2.1
        ucont.gen_z_kin_yes = False
        ucont.gen_zb = 0
        if ucont.flav == 13 and len([lep for lep in ucont.gen_leptons if acc_pt_eta(lep,gen_muon_pt,gen_muon_eta)]) == 2 and (self.muchannel == True or self.muchannel == None):
            ucont.gen_z_kin_yes = True
        elif ucont.flav == 11 and len([lep for lep in ucont.gen_leptons if acc_pt_eta(lep,gen_elec_pt,gen_elec_eta)]) == 2 and (self.muchannel == False or self.muchannel == None):
            ucont.gen_z_kin_yes = True
        # number of gen b-jets after acceptance cuts
        if ucont.gen_z_kin_yes: 
            ucont.gen_zb = ucont.gen_b
            try:
                self.gen_acc[ucont.gen_b] += ucont.rw
            except AttributeError:
                self.gen_acc = [0,0,0]
                self.gen_acc[ucont.gen_b] += ucont.rw
        if not ucont.gen_z_kin_yes: ucont.stop = True

    def finish_print_a_l(self):
        """ print resume from A_l computation """
        if not hasattr(self,"out"): self.out = ""
        self.a_l = [0,0,0]
        for i in range(3):
             if self.gen_baseline[i]:
                 self.a_l[i] = self.gen_acc[i]/float(self.gen_baseline[i])
        self.out += "===             A_l                ===\n"
        self.out += "Total events: %i\n" % (self.total_events)
        self.out += "Gen b-jets    :\t0\t1\t2\n"
        self.out += "Baseline cuts :\t"+"\t".join([f_2(el) for el in self.gen_baseline])+"\n" 
        self.out += "Acceptance    :\t"+"\t".join([f_2(el) for el in self.gen_acc])+"\n" 
        self.out += "A_l           :\t"+"\t".join([f_2(el) for el in self.a_l])+"\n"
        

    def step_e_r(self, ucont):
        """ computing:
                # events with a reconstructed Z (should i use findBestCandidate as it does not match gen leptons ?)
                # events with reconstructed jets matching the gen b-jets and inside acceptance cuts
                # e_r matrix
                # needs the gen_zb variable from a_l routine
        """
        # print "z cands (mu): all:", len(self.zmumu), "good:", len(self.zmumugood)
        # print "z cands (el): all:", len(self.zee), "good:", len(self.zeegood)
        ucont.rec_z_yes = False
        ucont.reco_leptons = []
        # getting best reco Z candidate
        # -----------------------------
        ucont.reco_z = False
        # removing candidates whose leptons are not matching the gen ones
        gen_lep_dr = 0.3
        zmumu_match = []
        if (self.muchannel == True or self.muchannel == None):
            for z in self.zmumu:
                if len(match_obo([z.daughter(0), z.daughter(1)], ucont.gen_leptons, gen_lep_dr)) == 2:
                    zmumu_match.append(z) 
        zelel_match = []
        if (self.muchannel == False or self.muchannel == None):
            for z in self.zee:
                if len(match_obo([z.daughter(0), z.daughter(1)], ucont.gen_leptons, gen_lep_dr)) == 2:
                    zelel_match.append(z) 
        ucont.reco_z = llbb.findBestCandidate(self.muchannel, None, zelel_match, zmumu_match)
        if ucont.reco_z:
            ucont.rec_z_yes = True
            ucont.reco_leptons = [ucont.reco_z.daughter(0), ucont.reco_z.daughter(1)]
        # getting good jets matching the gen b-jets 
        # -----------------------------------------------------------------
        ucont.rec_b = 0
        ucont.rec_zb = 0
        reco_jet_gen_jet_dr = 0.5
        # select good jets
        ucont.reco_jets = [jet for jet in self.jets if llbb.isGoodJet(jet,ucont.reco_z)]
        # keep jets that match gen b-jets by 0.5
        # ucont.reco_jets = [jet for jet in ucont.reco_jets if overlap(jet, ucont.gen_b_jets, reco_jet_gen_jet_dr)]
        ucont.reco_jets = match_obo(ucont.reco_jets, ucont.gen_b_jets_all, reco_jet_gen_jet_dr)
        ucont.rec_b = len(ucont.reco_jets)>1 and 2 or len(ucont.reco_jets)
        if ucont.rec_z_yes : ucont.rec_zb = ucont.rec_b
        try:
            self.rec_zb[ucont.rec_zb] += ucont.rw
        except AttributeError:
            self.rec_zb = [0,0,0]
            self.rec_zb[ucont.rec_zb] += ucont.rw
        # computing e_r matrix
        # --------------------
        try:
            self.mat_e_r[ucont.rec_zb][ucont.gen_zb] += ucont.rw
        except AttributeError:
            self.mat_e_r = [[0,0,0],[0,0,0],[0,0,0]]
            self.mat_e_r[ucont.rec_zb][ucont.gen_zb] += ucont.rw 
        # interrupt if there's no reco z cand
        # -----------------------------------
        if not ucont.rec_zb: ucont.stop = True       

    def finish_print_e_r(self):  
        if not hasattr(self,"out"): self.out = ""      
        self.out += "===             E_r                ===\n"
        self.out += "--------------------------------------\n"
        self.out += "gen b:\t\t0\t1\t2\n"
        # print "-------- un-normalized ---------------"
        # for i, row in enumerate(self.mat_e_r):
        #     print "rec j: ", f_2(i), " :\t", "\t".join(["%.2f" % (el) for el in row])
        # print "--------- normalized -----------------"
        self.e_r_norm = deepcopy(self.mat_e_r)
        norms = norm_by_column(self.e_r_norm)
        for i, row in enumerate(self.e_r_norm):
            self.out += "rec j: "+str(i)+" :\t"+"\t".join(["%.2f" % (el) for el in row])+"\n"
        self.out += "--------------------------------------\n"
        self.out += "norms:\t\t"+"\t".join([f_2(norm) for norm in norms])+"\n"
        self.out += "--------------------------------------\n"
        self.rfact = (norms[1]+norms[2]) and norms[0]/float(norms[1]+norms[2]) or 0
        self.out += "R-factor:"+str(self.rfact)+"\n"
        self.out += "--------------------------------------\n"

    def step_e_l(self, ucont):
        """ compute lepton efficiency for each rec_zb bin """
        # ucont.goodleps = [lep for lep in ucont.reco_leptons if (llbb.isGoodElectron(lep,'matched') or llbb.isGoodMuon(lep,'matched'))]
        gen_lep_dr = 0.3

        zmumu_match = []
        if (self.muchannel == True or self.muchannel == None):
            for z in self.zmumugood:
                if len(match_obo([z.daughter(0), z.daughter(1)], ucont.gen_leptons, gen_lep_dr)) == 2:
                    zmumu_match.append(z) 

        zelel_match = []
        if (self.muchannel == False or self.muchannel == None):
            for z in self.zeegood:
                if len(match_obo([z.daughter(0), z.daughter(1)], ucont.gen_leptons, gen_lep_dr)) == 2:
                    zelel_match.append(z) 

        reco_z_good = llbb.findBestCandidate(self.muchannel, None, zelel_match, zmumu_match)
        if reco_z_good and ucont.rec_z_yes:
            ucont.el_weight = self.el_engine.weight(fwevent=ucont.event, muChannel=self.muchannel)
            try: 
                self.lep_eff[ucont.rec_zb] += ucont.rw*ucont.el_weight
            except AttributeError:
                self.lep_eff = [0,0,0]
                self.lep_eff[ucont.rec_zb] += ucont.rw*ucont.el_weight
        else:
            ucont.stop = True

    def finish_print_e_l(self):
        if not hasattr(self,"lep_eff"):
            self.out += "== No events passed the lepton selection =="
        else:
            self.e_l = [self.lep_eff[i]/float(self.rec_zb[i]) if self.rec_zb[i] else 0 for i in range(3)]
            self.out += "===             E_l                ===\n"
            self.out += "Reco b-jets    :   0\t1\t2\n"
            self.out += "basic Z + jet  : "+"\t".join([f_2(el) for el in self.rec_zb])+"\n"
            self.out += "Lepton iso/ID  : "+"\t".join([f_2(el) for el in self.lep_eff])+"\n"
            self.out += "E_l            : "+"\t".join([f_2(el) for el in self.e_l])+"\n"

    def step_e_b(self, ucont):
        """ computes:
                the e_b matrix based on b-tagging
        """
        algo = "SSV"
        n_he = len([jet for jet in ucont.reco_jets if llbb.isBJet(jet, "HE", algo)])
        n_hp = len([jet for jet in ucont.reco_jets if llbb.isBJet(jet, "HP", algo)])
        if n_he > 2: n_he = 2
        if n_hp > 2: n_hp = 2
        ucont.n_he = n_he
        ucont.n_hp = n_hp
        he_modes = [None, "HE", "HEHE"]
        hp_modes = [None, "HP", "HPHP"]
        heweight = 1
        if he_modes[ucont.n_he]: 
            self.btag_engine.setMode(he_modes[ucont.n_he])
            heweight = self.btag_engine.weight(ucont.event,self.muchannel)
        hpweight = 1
        if hp_modes[ucont.n_hp]:
            self.btag_engine.setMode(hp_modes[ucont.n_hp])
            hpweight = self.btag_engine.weight(ucont.event,self.muchannel)
        try:
            self.mat_e_b_he[ucont.n_he][ucont.rec_zb] += ucont.rw*heweight*ucont.el_weight
            self.mat_e_b_hp[ucont.n_hp][ucont.rec_zb] += ucont.rw*hpweight*ucont.el_weight
        except AttributeError:
            self.mat_e_b_he = [[0,0,0],[0,0,0],[0,0,0]]
            self.mat_e_b_hp = [[0,0,0],[0,0,0],[0,0,0]]
            self.mat_e_b_he[ucont.n_he][ucont.rec_zb] += ucont.rw*heweight*ucont.el_weight
            self.mat_e_b_hp[ucont.n_hp][ucont.rec_zb] += ucont.rw*hpweight*ucont.el_weight

    def finish_print_e_b(self):
        self.out += "--------------------------------------\n"
        self.out += "                E_b                   \n"
        self.out += "--------------------------------------\n"
        self.out += "--------------------------------------\n"
        self.out += "rec b:\t\t0\t1\t2\n"
        self.out += "--------------------------------------\n"
        # for i, row in enumerate(self.mat_e_b_he):
        #     print "HE b: ", f_2(i), " :\t", "\t".join(["%.2f" % (el) for el in row])
        # print "--------------------------------------"
        self.e_b_he_norm = deepcopy(self.mat_e_b_he)
        norms_he = norm_by_column(self.e_b_he_norm)
        for i, row in enumerate(self.e_b_he_norm):
            self.out += "HE b: "+str(i)+" :\t"+"\t".join(["%.2f" % (el) for el in row])+"\n"
        self.out += "--------------------------------------\n"
        self.out += "norms:\t\t"+"\t".join([f_2(norm) for norm in norms_he])+"\n"
        self.out += "--------------------------------------\n"
        # for i, row in enumerate(self.mat_e_b_hp):
        #     print "HP b: ", f_2(i), " :\t", "\t".join(["%.2f" % (el) for el in row])
        # print "--------------------------------------"
        self.e_b_hp_norm = deepcopy(self.mat_e_b_hp)
        norms_hp = norm_by_column(self.e_b_hp_norm)
        for i, row in enumerate(self.e_b_hp_norm):
            self.out += "HP b: "+str(i)+" :\t"+"\t".join(["%.2f" % (el) for el in row])+"\n"
        self.out += "--------------------------------------\n"
        self.out += "norms:\t\t"+"\t".join([f_2(norm) for norm in norms_hp])+"\n"
        self.out += "--------------------------------------\n"

    def finish_comparison(self):
        """ compares with values from imperial """
        # for muons 
        eb_11_m = 49.7
        eb_21_m = 50.4
        eb_22_m = 26.2
        el_1_m  = 84.7
        el_2_m  = 84.0
        er_11_m = 81.8
        er_21_m = 13.1
        er_12_m = 1.10
        er_22_m = 77.2
        er_01_m = 0.78
        er_02_m = 0.01
        rfact_m = 12.9
        al_1_m  = 88.2
        al_2_m  = 88.9 
        # for electrons
        eb_11_e = 49.7
        eb_21_e = 49.5
        eb_22_e = 26.8
        el_1_e  = 62.9
        el_2_e  = 63.7
        er_11_e = 71.6
        er_21_e = 13.1
        er_12_e = 1.10
        er_22_e = 69.9
        er_01_e = 0.78
        er_02_e = 0.02
        rfact_e = 12.9
        al_1_e  = 84.4
        al_2_e  = 83.8
        # printing comparisons A_l:
        self.out += "--------------------------------------\n"
        self.out += "A_l comparison:\ta_l_1\ta_l_2\n"
        self.out += "this study    :\t%.2f\t%.2f\n" % (self.a_l[1], self.a_l[2])
        self.out += "imp, electrons:\t%.2f\t%.2f\n" % (al_1_e, al_2_e)
        self.out += "imp, muons    :\t%.2f\t%.2f\n" % (al_1_m, al_2_m)
        # E_r
        self.out += "--------------------------------------\n"
        self.out += "e_r comparison:\te_r_11\te_r_12\te_r_21\te_r_22\tR\n"
        self.out += "this study    :\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (self.e_r_norm[1][1], self.e_r_norm[2][1], self.e_r_norm[1][2], self.e_r_norm[2][2], self.rfact)
        self.out += "imp, electrons:\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (er_11_e, er_12_e, er_21_e, er_22_e, rfact_e)
        self.out += "imp, muons    :\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\n" % (er_11_m, er_12_m, er_21_m, er_22_m, rfact_m)
        # E_l
        self.out += "--------------------------------------\n"
        self.out += "e_l comparison:\te_l_1\te_l_2\n"
        self.out += "this study    :\t%.2f\t%.2f\n" % (self.e_l[1], self.e_l[2])
        self.out += "imp, electrons:\t%.2f\t%.2f\n" % (el_1_e, el_2_e)
        self.out += "imp, muons    :\t%.2f\t%.2f\n" % (el_1_m, el_2_m)
        # E_b
        self.out += "--------------------------------------\n"
        self.out += "e_b comparison:\te_b_11\te_b_21\te_b_22\n"
        self.out += "this study    :\t%.2f\t%.2f\t%.2f\n" % (self.e_b_he_norm[1][1], self.e_b_he_norm[1][2], self.e_b_he_norm[2][2])
        self.out += "imp, electrons:\t%.2f\t%.2f\t%.2f\n" % (eb_11_e, eb_21_e, eb_22_e)
        self.out += "imp, muons    :\t%.2f\t%.2f\t%.2f\n" % (eb_11_m, eb_21_m, eb_22_m)
        # full matrix comparison
        self.out += "--------------------------------------\n"
        print self.out
        vals = {"al_1":self.a_l[1], "al_2":self.a_l[2],
                "el_1":self.e_l[1], "el_2":self.e_l[2],
                "er_01":self.e_r_norm[1][0]/100., "er_02":self.e_r_norm[2][0]/100., 
                "er_11":self.e_r_norm[1][1]/100., "er_12":self.e_r_norm[2][1]/100.,
                "er_21":self.e_r_norm[1][2]/100., "er_22":self.e_r_norm[2][2]/100.,
                "rfact":self.rfact,
                "eb_11":self.e_b_he_norm[1][1]/100., "eb_21":self.e_b_he_norm[1][2]/100., "eb_22":self.e_b_he_norm[2][2]/100.
            }
        this_mat = compute_fullmatrix(**vals)
        # this_mat = compute_fullmatrix(self.a_l[1], self.a_l[2], self.e_l[1], self.e_l[2], self.e_r_norm[1][0]/100., self.e_r_norm[2][0]/100., self.e_r_norm[1][1]/100.,
        #     self.e_r_norm[2][1]/100., self.e_r_norm[1][2]/100., self.e_r_norm[2][2]/100., self.rfact, 
        #     self.e_b_he_norm[1][1]/100., self.e_b_he_norm[1][2]/100., self.e_b_he_norm[2][2]/100.)
        print this_mat
      
        # the end
        self.out += "--------------------------------------\n"


    def start_weights(self):
        self.pu_engine = LumiReWeighting()
        self.el_engine = LeptonsReWeighting()
        self.btag_engine = btaggingWeight(0,999,0,999)

# helper functions

def compute_fullmatrix(al_1, al_2, el_1, el_2, er_01, er_02, er_11, er_12, er_21, er_22, rfact, eb_11, eb_21, eb_22):
    # arguments should be normalized to 1 (not 100)
    # making matrices:
    try:
        al_mat = np.matrix([[1/al_1, 0],[0, 1/al_2]])
    except ZeroDivisionError:
        print "A_l_1 or A_l_2 is empty"
        return None
    print al_mat
    er_mat = np.matrix([[er_11 + er_01*rfact, er_21 + er_01*rfact],[er_12 + er_02*rfact, er_22 + er_02*rfact]]).getI()
    print er_mat
    try:
        el_mat = np.matrix([[1/el_1, 0],[0, 1/el_2]])
    except ZeroDivisionError:
        print "e_l_1 or e_l_2 is empty"
        return None
    print el_mat
    try:
        eb_mat = np.matrix([[1/eb_11, -eb_21/(eb_22*eb_11)],[0, 1/eb_22]]) 
    except ZeroDivisionError:
        print "e_b_11 or e_b_22 is empty"
        return None
    print eb_mat
    final_mat = al_mat*er_mat*el_mat*eb_mat
    return final_mat

def acc_pt_eta(vec, ptcut, etacut):
    if (math.fabs(vec.eta()) > etacut) or (vec.pt() < ptcut): return False
    return True

def jet_b_parton(genjet):
    """ returns the first b quark in jet based on first particle path (this is not sufficient), or the initial parton """
    cons0 = genjet.getGenConstituent(0)
    while True:
        if cons0.numberOfMothers() and cons0.mother(0).pdgId() != 2212 and math.fabs(cons0.pdgId()) != 5:
            cons0 = cons0.mother(0)
        else:
            return cons0

def user_members(obj):
    from inspect import getmembers
    return dict([mem for mem in getmembers(obj) if mem[0][0] != "_"])

def is_equal(vec1,vec2):
    if vec1 and vec2:
        return vec1.pt() == vec2.pt() and vec1.eta() == vec2.eta() and vec1.phi() == vec2.phi() and vec1.pdgId() == vec2.pdgId()
    return False

def get_vec(part):
    return TLorentzVector(part.px(), part.py(), part.pz(), part.energy())

def overlap(vec, collection, dr):
    for obj in collection:
        if math.hypot((vec.eta() - obj.eta()), (vec.phi() - obj.phi())) < dr: return True
    return False

def match_obo(rec, gen, dr):
    gen2 = deepcopy(gen)
    matching = []
    for vec in rec:
        for part in gen2:
            if math.hypot((vec.eta() - part.eta()), (vec.phi() - part.phi())) < dr:
                matching.append(vec)
                gen2.remove(part)
    return matching
      

def norm_by_column(mat):
    """ only for matrices with positive values """
    cols = len(mat[0])
    norms = [0]*cols
    for i in range(cols):
        for row in mat:
            norms[i] += row[i]
    for j, row in enumerate(mat):
        for i, el in enumerate(row):
            if norms[i]:
                mat[j][i] = el/float(norms[i]) * 100
    return norms

def norm_by_line(mat):
    for i, row in enumerate(mat):
        norm = sum(row)
        if norm:
            mat[i] = [el/float(norm) for el in row]
    return [0]*len(mat[0])

def f_2(num):
    return "%.2f" % (num)

def is_bhad(genpart):
    pdgid = genpart.pdgId()
    return (499 < pdgid < 600) or (4999 < pdgid < 6000)

def is_final_bhad(genpart):
    if not is_bhad(genpart): return False
    if len([genpart.daughter(i) for i in range(genpart.numberOfDaughters()) if is_bhad(genpart.daughter(i))]): return False
    return True

def compare_matrices():
    vals_imp_mu = {"al_1":0.882, "al_2":0.889, "el_1":0.847, "el_2":0.840, "er_01":0.008, "er_02":0.000, 
        "er_11":0.818, "er_12":0.011, "er_21":0.131, "er_22":0.772, "rfact":12.17, "eb_11":0.497, "eb_21":0.504, "eb_22":0.262}
    vals_imp_el = {"al_1":0.844, "al_2":0.838, "el_1":0.629, "el_2":0.637, "er_01":0.008, "er_02":0.000, 
        "er_11":0.716, "er_12":0.011, "er_21":0.102, "er_22":0.699, "rfact":12.93, "eb_11":0.497, "eb_21":0.495, "eb_22":0.268} 
    vals_cp3_mu = {"al_1":0.910, "al_2":0.910, "el_1":0.730, "el_2":0.700, "er_01":0.000, "er_02":0.000, 
        "er_11":0.836, "er_12":0.002, "er_21":0.228, "er_22":0.740, "rfact":212.4, "eb_11":0.507, "eb_21":0.470, "eb_22":0.276} 
    vals_cp3_el = {"al_1":0.860, "al_2":0.860, "el_1":0.640, "el_2":0.620, "er_01":0.000, "er_02":0.000, 
        "er_11":0.839, "er_12":0.002, "er_21":0.244, "er_22":0.724, "rfact":180.8, "eb_11":0.502, "eb_21":0.500, "eb_22":0.157}
    print "cp3, electrons:"
    print compute_fullmatrix(**vals_cp3_el)
    print "imperial, electrons:" 
    print compute_fullmatrix(**vals_imp_el)
    print "cp3, muons:"
    print compute_fullmatrix(**vals_cp3_mu)
    print "imperial, muons:"
    print compute_fullmatrix(**vals_imp_mu)


def main(num = -1):
    startup = ["weights"]
    steps = ["event_weight","a_l", "e_r", "e_l", "e_b"]
    finish = ["print_a_l", "print_e_r", "print_e_l", "print_e_b", "comparison"]
    # testu = unfolder("/storage/data/cms/users/llbb/production2012_44X/Fall11_DYJets/PATskim-Zjets_2619_1_jGj.root", steps, startup, finish, False)
    # testu = unfolder("/storage/data/cms/users/llbb/productionJune2012_444/MCwithMatching/Fall11_DYjets_v4", steps, startup, finish, True)
    # testu = unfolder("/storage/data/cms/users/llbb/productionJune2012_444/MCwithMatching/Fall11_DYjets_v4/PATprod-MC_1432_1_f5u.root", steps, startup, finish, True)
    # testu = unfolder("/storage/data/cms/users/llbb/production2012_44X/Fall11_DYJets", steps, startup, finish, False)
    testu = unfolder("/storage/data/cms/users/llbb/productionJune2012_444/ZbSkims/Zbb_MC/", steps, startup, finish, True)
    testu.run(num)

if __name__ == '__main__':
     main()