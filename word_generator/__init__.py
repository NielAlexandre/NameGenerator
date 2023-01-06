# -*- coding: utf-8 -*-
"""
Original code credits :
2015-10-27. David Louapre. sciencetonnante@gmail.com
http://sciencetonnante.wordpress.com
"""

import codecs
import re
import sys

import pickle

from copy import deepcopy
from collections import Counter
from string import ascii_lowercase as alphabet
from itertools import product

import numpy as np
from numpy.random import choice, seed, shuffle

class Triplet(object):
    """
    Count tripelt caracter probability
    """
    def __init__(self):
        self._dict = {}

    def append(self, i, j, k):
        """
        Append a triplet to the counter
        """
        if not i in self._dict:
            self._dict[i] = {}
        if not j in self._dict[i]:
            self._dict[i][j] = Counter()

        self._dict[i][j][k] += 1

    def count(self):
        """ return the number of caracter append in total """
        res = 0
        for first in self._dict.iteritems():
            for second in first[1].iteritems():
                for third in second[1].itervalues():
                    res += third
        return res

    def proba(self, i, j):
        """ return list of probability of the third caracter for a triplet """
        total = sum(self._dict[i][j].values())
        return [count/total for count in self._dict[i][j].values()]

    def choice(self, i, j):
        """ return a randomly choosen caracter considering the probablity """
        proba = self.proba(i, j)
        return choice(self._dict[i][j].keys(), 1, p=proba)[0]

    def weight_1(self):
        return Counter(dict([(k, sum(self.weight_2(k).values()))
            for k in self._dict.keys()]))

    def weight_2(self, i):
        return Counter(dict([(k, sum(self.weight_3(i, k).values()))
            for k in self._dict[i].keys()]))

    def weight_3(self, i, j):
        return self._dict[i][j]

    def most_common(self, i=0, j=0):
        """ return the most common last caracter for a triplet """
        return self[i][j].most_common(1)[0][0]

    def choose_next(self, i=0, j=0):
        """ choose the next caractere considering the probability """
        return choice(list(self[i][j].keys()), 1, p=self.proba(i, j))[0]

    def __getitem__(self, i):
        """ return the dict probability for a caractere """
        return self._dict[i]

    def __str__(self):
        """ pretty printing for the object """
        res = ""
        for first in self._dict.items():
            res += str(first[0]) + ":"
            for second in first[1].items():
                res += ' ' + str(second[0]) + ":"
                for third in second[1].items():
                    res += str(third[0]) + ','
                res += "\n"

        return res

class WordGenerator(object):
    """
    Generate words from trigram probabilities of dictionnary file
    """

    def __init__(self, encoding="utf-8"):
        self.seed = seed
        self.dico = []
        self.length = Counter()
        self.encoding = encoding
        self.count = Triplet()

    def most_common(self):
        res = self.count.weight_3(0, 0).most_common()[0][0]
        res += self.count.weight_3(0, res[-1]).most_common()[0][0]

        def sort_key(k):
            return k[1] * dict(self.count.weight_3(*list(res[-2:]))).get(k[0], 0)

        def repeats(string):
            for x in range(3, len(string)):
                substr = string[-x:]

                if substr in string[:-x]:
                    return x
            return 0

        while res[-1] != '\n':
            c = max(self.count.weight_1().items(), key=sort_key)
            res += str(c[0])
            x = repeats(res)
            if x:
                res = res[:-x]
                break

        return res

    def proba_count(self, infile):
        """ Read the dictionnary and compute the occurence of each trigram """
        with codecs.open(infile, "r", self.encoding) as lines:
            for line in  lines:
                # Trimming of the line :
                # Split on white space, tab, slash backslah or open parenthesis
                line = line.strip()
                if not line:
                    continue
                self.dico.append(line)
                self.length[len(line)] += 1
                i, j = 0, 0
                for k in line + "\n":
                    self.count.append(i, j, k)
                    i = j
                    j = k
        # Save the results for later use
        return self.count

    def save_pcount(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump((self.length, self.count), f)

    def load_pcount(self, filepath):
        with open(filepath, 'rb') as f:
            self.length, self.count = pickle.load(f)

    def gen_word(self, count=None, ignore_dict=False, start_point=(0, 0)):
        """ Generate nb of random words
        writes it in outfile if given, one per line
        ignore_dict = True will allow you to generate words already existing
            in proba_count inputfile
        an external count can be provided throught count parameter
        """
        if not count:
            count = self.count
        out = []
        gen_l = self.choose_len()
        choosen_l = next(gen_l)
        while 1:
            i, j = start_point[-2:]
            res = u''
            res = ''.join([start for start in start_point if start != 0])

            #Generate the word one caracter at a time until EOL is found
            while j != '\n' and len(res) <= choosen_l:
                k = count.choose_next(i, j)
                res += k
                i, j = j, k
            res = res[:-1]
            if len(res) != choosen_l or j!='\n':
                continue
            #ignore words in dicts and words already generated
            if (not ignore_dict and res in self.dico) or res in out:
                continue
            choosen_l = next(gen_l)
            out.append(res)
            yield res

    def choose_len(self):
        """ return a choosen length consigering the probability """
        lengths = list(self.length.keys())
        plenghts = [a/sum(self.length.values()) for a in self.length.values()]
        while 1:
            yield choice(lengths, 1, p=plenghts)[0]

    def gen_matrix(self, outfile, count=None):
        """ generat 2D plot showing bigram probabilities """
        import matplotlib.pyplot as plt
        if not count:
            count = self.count

        tmpcount = Triplet()
        # We have to do a partial sum on the 3D matrix to go fro trigram to bigram
        for i in alphabet:
            tmpcount.append(0, 0, i)
        for i, j in product(alphabet, alphabet):
            try:
                tmpcount[0][j] = deepcopy(self.count[i][j])
            except KeyError:
                pass
            try:
                tmpcount[0][j] += deepcopy(self.count[0][j])
            except KeyError:
                pass
            try:
                tmpcount[0][j] += deepcopy(self.count[0][j.upper()])
            except KeyError:
                pass


        # For better contrast, we plot proba^alpha instead of proba
        alpha = 0.33
        for k, v in tmpcount[0].items():
            for l, w in v.items():
                v[l] = w*alpha

        return tmpcount[0]
        # We display only letters a to z, ie ASCII from 97 to 123.
        plt.figure(figsize=(8, 8))
        plt.imshow(p2da[97:123, 97:123], interpolation='nearest')
        plt.axis('off')

        for i in range(97, 123):
            plt.text(-1, i-97, chr(i), horizontalalignment='center',
                     verticalalignment='center')
            plt.text(i-97, -1, chr(i), horizontalalignment='center',
                     verticalalignment='center')
        plt.savefig(outfile)


def default_wg(*filenames):
    """ return a default word generator """
    import os
    word_gen = WordGenerator()
    for filename in filenames:
        word_gen.proba_count(filename)
    return word_gen.gen_word()
