#!/usr/bin/python3
# -*- coding: utf-8 -*-

from word_generator import default_wg
import sys, os

def print_help():
    print("Usage : {} in_file [nb]".format(os.path.basename(sys.argv[0])))

def main():

    filepath = ""
    nb = 0

    filepaths = [f for f in sys.argv[1:] if os.path.isfile(f)]
    arg_nb = [a for a in sys.argv[1:] if a.isdigit()]

    if arg_nb:
        nb = int(arg_nb[-1])

    if not filepaths:
        print_help()
        print("\tNo input files detected")
        exit(1)

    wg = default_wg(*filepaths)

    while True:
        print(next(wg), end=' ')
        nb -= 1
        if nb < 0:
            if input():
                break
        elif nb == 0:
            break
        else:
            print()
    print()



if __name__ == "__main__":
    main()

