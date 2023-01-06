#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os, sys
import tty, termios
from codecs import open
from word_generator import WordGenerator
from time import time
from statistics import mean
from copy import deepcopy

from parse_multi import HistParser, lt_fmt
from Anana import getch
from TimeCop import TimeCop
tcop = TimeCop()


def main():

    #Inits
    ng = WordGenerator()

    #HistInit
    with HistParser(ng) as hist:
        # Initialize word generation
        with tcop.open("set_ready"):
            ngg = ng.gen_word(ignore_dict=False)
        print(lt_fmt.format(tcop["set_ready"].last, " -- Generator Ready"))
        print()

        #Main loop
        with open("0_REFINED.txt", "a", 'utf-8') as o:
            tcop.start("generation")
            for n in ngg:
                tcop.stop()
                print(lt_fmt.format(tcop["generation"].last,
                    "{:>3}% :: {}".format(100*hist.count//50, n)))
                try:
                    if hist.ask_for():
                        print(n, file=o, flush=True)
                except KeyboardInterrupt:
                    break
                tcop.start("generation")

        print("Generation time : {} in {:.3f}s".format(
            tcop["generation"].nb_call, tcop["generation"].mean))

if __name__ == "__main__":
    main()

