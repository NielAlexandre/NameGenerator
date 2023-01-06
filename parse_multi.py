#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, re
from time import time
import hashlib
from collections import namedtuple

from Anana import getch
from TimeCop import TimeCop
tcop = TimeCop()
lt_fmt = "{:<7.2f}s :: {}"

def log_time(msg, d, **kwargs):
    d = time() - d
    if kwargs.pop("reset_line", False):
        print("\r\033[K", end="")
        kwargs["flush"] = True

    print("{:<7.2f}s :: {}".format(d, msg), **kwargs)
    return time(), d

def parse_args(args, wg):
    #Analyse arguments
    pargs = {}
    time_debut = time()
    for f in args:
        if os.path.isfile(f):
            with open(f) as fh:
                pargs[f] = len([l for l in fh])
        else:
            print(f, "is not a file")
    time_debut, _ = log_time("--  Initialialized file list", time_debut)

    m_size = max(pargs.values())
    for f, s in pargs.items():
        for i in range(m_size//s):
            wg.proba_count(f)
            time_debut, _ = log_time("--  Counted " + str(i+1) + "-" + f, time_debut, end="", reset_line=True)
        print()


def digest_list(lst):
    m = hashlib.sha256()
    for l in sorted(lst):
        with open(l, 'rb') as f:
            m.update(f.read())

    return m.hexdigest()

HTuple = namedtuple("HistTuple", "prct success total hexhash args")
class HistParser:
    hist_fmt = "{:0>3}% ({}/{}) {}"
    hist_re = re.compile(r"(\d{3})% \((\d)+/(\d+)\) (\S+)")
    history_file = "history.out"
    pickle_dir = os.path.join(os.path.dirname(sys.argv[0]), ".pickled")

    def __init__(self, ng):
        self.ng = ng
        self._hist_save = []

        try:
            os.mkdir(HistParser.pickle_dir)
        except FileExistsError:
            pass

        if not os.path.isfile(HistParser.history_file):
            with open(HistParser.history_file, 'w') as f:
                pass

        with open(HistParser.history_file, 'r') as fd:
            for line in fd:
                m = HistParser.hist_re.match(line.strip())
                if m:
                    prct, successes, total, hexhash = m.groups()
                    args = ""
                    with open(os.path.join(HistParser.pickle_dir, hexhash + ".txt")) as f:
                        args=f.read().splitlines()
                    self._hist_save.append(HTuple(int(prct),
                        int(successes),
                        int(total),
                        hexhash,
                        args))
                else:
                    print(line, "did not match")

    def select(self, args):
        if isinstance(args, int):
            me = self._hist_save.pop(args)
            self.args = me.args
            self.hexhash = me.hexhash
            self.success = me.success
            self.count = me.total
            return True
        elif isinstance(args, list):
            hexhash = digest_list(args)
            print(" -- Digested " + hexhash)
            self.success = 0
            self.count = 0
            self.hexhash = hexhash
            self.args = args

            for i, t in enumerate(self._hist_save):
                if t.hexhash == hexhash:
                    me = self._hist_save.pop(i)
                    self.success = me.success
                    self.count = me.total
                    break
            else:
                return False
            return True
        else:
            raise ValueError("args must be list or HTuple")

    @property
    def pickledesc(self):
        return self.picklefile + ".txt"

    @property
    def picklefile(self):
        return os.path.join(HistParser.pickle_dir, self.hexhash)

    @property
    def prct(self):
        if not self.count:
            return 0
        return int(100*self.success/self.count)

    @property
    def htuple(self):
        return HTuple(self.prct, self.success, self.count, self.hexhash, self.args)

    @property
    def hist_save(self):
        a = []
        try:
            a = [self.htuple]
        except AttributeError:
            pass
        return sorted(self._hist_save + a,
                key = lambda x: x.prct, reverse=True)

    @property
    def rank(self):
        return self.hist_save.index(self.htuple)+1


    def print(self, file=sys.stdout):
        #stdout restults
        print("Successes : {}% ({})".format(self.prct, self.success), file=file)
        print("Ranking : {}/{}".format(self.rank, len(self.hist_save)), file=file)

    def save_file(self):
        #saving results for histories
        with open(HistParser.history_file, 'w') as f:
            for t in self.hist_save:
                print(HistParser.hist_fmt.format(*t), file=f)

    def __exit__(self, etype, evalue, traceback):
        self.print()
        self.save_file()

    def __enter__(self):
        if '-q' in sys.argv:
            offset = 1
            nb_shown = 5
            while 1:
                print("\033[2J", end="")
                for i, h in enumerate(self.hist_save[(offset-1)*nb_shown:offset*nb_shown]):
                    print(f"{i:3<} p{offset}- {h.prct}% ({h.success}/{h.total})")
                    print("      ", end="")
                    print(*h.args[:5], ["...", ""][len(h.args)<5], sep="\n      ")
                r = getch()
                if r=="q":
                    return
                elif r.isdigit() and int(r) in range(nb_shown):
                    self.select((offset-1)*nb_shown +int(r))
                    self.ng.load_pcount(self.picklefile)
                    break
                else:
                    offset += 1

                if (offset-1)*nb_shown >= len(self.hist_save):
                    print("No more suggestion")
                    return

            for line in self.args:
                print("--  Counted "  + line.strip())
            print(" -- Loaded " + self.pickledesc)


        # Init WordGen values
        elif self.select(sys.argv[1:]):
            #Loading
            with tcop.open("wg_load"):
                self.ng.load_pcount(self.picklefile)

            for line in self.args:
                print(lt_fmt.format(0, "--  Counted "), line.strip())
            print(lt_fmt.format(tcop["wg_load"].last, "--  Loaded "), self.pickledesc)
        else:
            #parsing new inputs
            with tcop.open("wg_count"):
                parse_args(self.args, self.ng)
                self.ng.save_pcount(self.picklefile)
                with open(self.pickledesc, 'w') as fd:
                    print(*self.args, sep='\n', file=fd)

            print(lt_fmt.format(tcop["wg_count"].last, " -- Saved "), self.picklefile)
        return self

    def ask_for(self):
        self.count += 1
        notok = True
        while notok:
            notok = False
            c = getch()
            if c in "oy":
                self.success += 1
                return True
            elif c in "n\n\r":
                pass
            elif c in "q":
                raise KeyboardInterrupt
            else:
                print(c, "?")
                notok = True
        return False


def main():
    pass

if __name__ == "__main__":
    main()

