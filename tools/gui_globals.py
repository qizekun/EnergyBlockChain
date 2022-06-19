import numpy as np
import sys
import csv
import os

from pypower.ppoption import ppoption


def init():
    global ppc
    global ppopt

    ppc = {"version": '2', "baseMVA": 100.0, "bus": np.array([
        [1, 3, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [2, 3, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [3, 3, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [4, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [5, 1, 90, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [6, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [7, 1, 100, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [8, 1, 0, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9],
        [9, 1, 125, 0, 0, 0, 1, 1, 0, 345, 1, 1.1, 0.9]
    ]), "branch": np.array([
        [1, 4, 0, 0.0576, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [4, 5, 0.017, 0.092, 0.158, 250, 250, 250, 0, 0, 1, -360, 360],
        [5, 6, 0.039, 0.17, 0.358, 150, 150, 150, 0, 0, 1, -360, 360],
        [3, 6, 0, 0.0586, 0, 300, 300, 300, 0, 0, 1, -360, 360],
        [6, 7, 0.0119, 0.1008, 0.209, 150, 150, 150, 0, 0, 1, -360, 360],
        [7, 8, 0.0085, 0.072, 0.149, 250, 250, 250, 0, 0, 1, -360, 360],
        [8, 2, 0, 0.0625, 0, 250, 250, 250, 0, 0, 1, -360, 360],
        [8, 9, 0.032, 0.161, 0.306, 250, 250, 250, 0, 0, 1, -360, 360],
        [9, 4, 0.01, 0.085, 0.176, 250, 250, 250, 0, 0, 1, -360, 360]
    ]), "gen": np.array([
        [1, 0, 0, 300, -300, 1.0, 100, 1, 250, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 0, 0, 300, -300, 1.0, 100, 1, 300, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 0, 0, 300, -300, 1.0, 100, 1, 270, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])}

    ppopt = ppoption()

    global filename
    filename = ""

    # Power flow settings
    global pf_settings
    pf_settings = {"Qlim": False, "max_iter": 25, "err_tol": 0.00001}


def write_ppc_file(fname):
    """Save PYPOWER file. 
    """

    filename = fname

    base = os.path.basename(fname)
    casename = os.path.splitext(base)[0]

    outfile = open(fname, 'w', newline='')

    outfile.write('from numpy import array\n\n')

    outfile.write('def ' + casename + '():\n')
    outfile.write('\tppc = {"version": ''2''}\n')
    outfile.write('\tppc["baseMVA"] = 100.0\n')

    outfile.write('\tppc["bus"] = ')
    outfile.write(np.array_repr(ppc["bus"]))
    outfile.write('\n\n')

    outfile.write('\tppc["gen"] = ')
    outfile.write(np.array_repr(ppc["gen"]))
    outfile.write('\n\n')

    outfile.write('\tppc["branch"] = ')
    outfile.write(np.array_repr(ppc["branch"]))
    outfile.write('\n\n')

    outfile.write('\treturn ppc')
    outfile.close()

    return True
