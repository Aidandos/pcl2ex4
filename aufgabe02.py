#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PCL II, Uebung 4, FS17
# Aufgabe 2

import bz2
from lxml import etree
import itertools
import argparse
from tempfile import mkstemp
from shutil import move
from os import remove, close
import random
import fileinput
import os


def gettitles(infile, testfile, trainfile, k, exitCondition):
    """infile: Korpus der schon durch bz2 geöffnet wurde
        testfile: Ausgabedatei für k zufällig ausgewählte Artikeltitel
        trainfile: Ausgabedatei für alle anderen Titel
        We apply Reservoir Sampling that has been presented in the lecture.
        The counter starts counting after a sufficient amount of test data has
        been collected. Data has already been unzipped. Please provide unzipped data"""

    if os.path.exists(testfile):
        os.remove(testfile)
    if os.path.exists(trainfile):
        os.remove(trainfile)

    exit_bool = False
    try:
        exit_bool = type(int(exitCondition)) is int
    except TypeError:
        # print('Either the break condition is missing or exitCondition must be a number')
        pass

    counter_exit = 0
    i = 0

    """data being read in"""
    tree = etree.iterparse(infile, tag='{http://www.mediawiki.org/xml/export-0.10/}title')

    test = open(testfile, 'a', encoding='utf-8')
    for event, elem in itertools.islice(tree, k):
        test.write(elem.text + "\n")
        i += 1
        # Element clear is for memory cleansing
        elem.clear()
        for element in elem.xpath('ancestor-or-self::*'):
            while element.getprevious() is not None:
                del element.getparent()[0]

    test.close()
    """Algorithm R"""
    train = open(trainfile, 'a', encoding='utf-8')
    try:
        for event, elem in tree:
            r = random.randint(0, i)
            if r < k:
                replaceLine(testfile, elem.text, r)
            else:
                train.write(elem.text + "\n")
            i += 1
            elem.clear()
            for element in elem.xpath('ancestor-or-self::*'):
                while element.getprevious() is not None:
                    del element.getparent()[0]
            if exit_bool:
                counter_exit += 1
                if counter_exit > int(exitCondition):
                    raise ExitCondition
    except ExitCondition:
        pass

    train.close()


def replaceLine(temp_file, replacement, placeOfLine):
    """Adaption from http://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python
    and http://stackoverflow.com/questions/16622754/how-do-you-replace-a-line-of-text-in-a-text-file-python
    Line Replacement for Algorithm R. Writes to new file everytime"""

    fh, abs_path = mkstemp()
    with open(abs_path, 'w', encoding='utf-8') as output_file, open(temp_file, encoding='utf-8') as input_file:
        n = 0
        for line in input_file:
            if n == placeOfLine:
                output_file.write(replacement + "\n")
            else:
                output_file.write(line)
            n += 1
            del line

    close(fh)
    # Remove original file
    remove(temp_file)
    # Move new file
    move(abs_path, temp_file)


class ExitCondition(Exception):
    """Helps to show results earlier"""
    pass


def main():
    parser = argparse.ArgumentParser(
        description='Choose k random titles from dump')
    parser.add_argument('--infile', '-i', dest='infile')

    parser.add_argument('--testfile', '-te', dest="testfile")

    parser.add_argument('--trainfile', '-tr', dest="trainfile")

    parser.add_argument('--samplesize', '-k', dest="k")

    parser.add_argument('--exitcondition', '-e',
                        dest="exitCondition",
                        required=False)

    args = parser.parse_args()

    gettitles(args.infile, args.testfile, args.trainfile,
              int(args.k), args.exitCondition)


if __name__ == '__main__':
    main()
