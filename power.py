from pypower.api import case30, ppoption, runpf, printpf

ppc = case30()
print("#" * 10)
print(ppc)
print("#" * 10)
ppopt = ppoption(PF_ALG=2)
r = runpf(ppc, ppopt)
