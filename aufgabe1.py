#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PCL II, Uebung 4, FS17
# Aufgabe 1

import glob
from lxml import etree
import argparse
import operator
import os


def getfreqwords(indir, outfile, exitCondition):
    """gets 20 most frequent sentences"""
    # checks if exit condition is present
    exit_bool = False
    try:
        exit_bool = type(int(exitCondition)) is int
    except TypeError:
        #print('Either the break condition is missing or exitCondition must be a number')
        pass

    # definition of variables, tmp_file is for memory stabilization
    tmp_file = 'tmp_file.txt'
    counter_exit = 0
    counter_top_20 = 0
    sentenceKeys = {}

    with open(tmp_file, 'wb') as tmp_file_io:

        tmp_file_io.write(b'<?xml version="1.0" encoding="UTF-8"?><root>')
        # xpath is not as pretty as regex :/
        pattern = indir + '/SAC-Jahrbuch_[0-9][0-9][0-9][0-9]_mul.xml'

        try:
            # iterating through sentences to get lemmas
            for file in glob.glob(pattern):
                tree = etree.parse(file)
                # structure of xml
                sentences = tree.xpath('/book/article/div/s')
                for sentence in sentences:
                    if len(sentence.xpath('w/@lemma')) >= 6:
                        sentenceConcat = ' '.join(sentence.xpath('w/@lemma'))
                        key = hash(sentenceConcat)
                        if key not in sentenceKeys:
                            sentenceKeys[key] = 1
                            # creating element tree so it can be parsed again
                            # later
                            el = etree.Element('sentence', hash=str(
                                key), value=sentenceConcat)
                            tmp_file_io.write(etree.tostring(el))
                        else:
                            sentenceKeys[key] += 1
                    if exit_bool:
                        counter_exit += 1
                        if counter_exit > int(exitCondition):
                            raise ExitCondition

        except ExitCondition:
            pass
        tmp_file_io.write(b'</root>')

    # re-using temp file for parsing, now sentence has hash
    sentences_with_hash = etree.parse(tmp_file)
    with open(outfile, 'w', encoding="utf-8") as output:

        # sorting sentences such that most frequent is on top
        for key in sorted(sentenceKeys.items(), key=operator.itemgetter(1), reverse=True):
            counter_top_20 += 1
            if counter_top_20 > 20:
                break
            else:
                output.writelines(sentences_with_hash.xpath(
                    '(/root/sentence[@hash=%d]/@value)[1]' % key[0])[0] + '\n')


    if os.path.exists(tmp_file):
        os.remove(tmp_file)


class ExitCondition(Exception):
    """Helps to show results earlier"""
    pass


def main():
    parser = argparse.ArgumentParser(
        description='Find most frequent sentences.')
    parser.add_argument('--indir', '-i',
                        dest='indir',)

    parser.add_argument('--outfile', '-o',
                        dest="outfile")

    parser.add_argument('--exitcondition', '-e',
                        dest="exitCondition",
                        required=False)

    args = parser.parse_args()
    getfreqwords(args.indir, args.outfile, args.exitCondition)


if __name__ == '__main__':
    main()
