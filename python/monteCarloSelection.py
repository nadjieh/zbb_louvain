
def isZlEvent(genParticles,ptcut=15, onlyStatus3=False):
  hasUDSG = False
  for part in genParticles:
    if onlyStatus3 and part.status()!=3: break;
    if part.pdgId() in [-1,-2,-3,3,2,1,9,21] and part.pt()>ptcut : 
      hasUDSG = True
      break
  return hasUDSG

def isZbEvent(genParticles,ptcut=15, onlyStatus3=False):
  hasB = False
  for i,part in enumerate(genParticles):
    if onlyStatus3 and part.status()!=3: break;
    if part.pdgId() in [-5,5] and part.pt()>ptcut : 
      hasB = True
      break
  return hasB

def isZcEvent(genParticles,ptcut=15, onlyStatus3=False):
  hasC = False
  for part in genParticles:
    if onlyStatus3 and part.status()!=3: break;
    if part.pdgId() in [-4,4] and part.pt()>ptcut : 
      hasC = True
      break
  return hasC
