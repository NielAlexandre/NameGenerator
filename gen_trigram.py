#!/usr/bin/python3
# -*- coding: utf-8 -*-

from codecs import open
from word_generator import WordGenerator
import sys, os
from itertools import cycle
from time import time
from copy import copy
from calc_virt import calc_virt_nb as calc_virt

from parse_multi import HistParser, lt_fmt
from TimeCop import TimeCop
tcop = TimeCop()

def help():
    print("Usage : {} in_file trigram nb".format(os.path.basename(sys.argv[0])))
def main():

    if len(sys.argv) < 4:
        print("Not enought argument")
        usage()
    elif not sys.argv[-1].isdigit():
        print("{} is not int".format(sys.argv[-1]))
        usage()

    *sys.argv, trigram, nb_turn = sys.argv
    trigram = trigram.split("-")
    nb_turn = int(nb_turn)

    wg = WordGenerator()

    with HistParser(wg) as hist:
        wgs = []
        for a in trigram:
            if len(a) == 0:
                t = (0, 0)
            elif len(a) == 1:
                t = (0, a.upper())
            else:
                t = a.capitalize()
            wgs.append(wg.gen_word(start_point=tuple(t)))

        with open("Trigram_REFINED.txt", "a", 'utf-8') as o:
            while True:
                tcop.start("generation")
                n = " ".join([next(a) for a in wgs])
                tcop.stop()
                print(lt_fmt.format(tcop["generation"].last,
                    "{:>3}% :: {}".format(100*hist.count//50, n)))
                try:
                    if hist.ask_for():
                        print(n, file=o, flush=True)
                except KeyboardInterrupt:
                    break

if __name__ == "__main__":
    main()

