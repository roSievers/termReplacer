# -*- coding: utf-8 -*-
import string
from random import randrange, choice
from subprocess import call
from functools import wraps

def join(listOfLists):
    # The monadic join for lists.
    return [j for i in listOfLists for j in i]

class Template(object):
    def __init__(self, filename, tempfile="temp/_page.svg"):
        self._filename = filename
        self.tempfile = tempfile
        self._template = None # The template is loaded lazily.
    def load(self):
        # ensures the template is actually loaded.
        if self._template is None:
            self._load()
    def _load(self):
        with open(self._filename) as inputFile:
            inputSvg = inputFile.read()

        # Prepare template
        skeleton = inputSvg.split("#term")

        self.termNumber = len(skeleton) - 1

        result = ""

        for i in xrange(self.termNumber):
            result += skeleton[i] + ("${term%i}" % i)
        result += skeleton[-1]

        result = result.replace("../logos/default.png", "../logos/${logo}.png")

        self._template = string.Template(result)
    def _variables(self):
        for i in xrange(self.termNumber):
            yield "term%i" % i

    def _renderOne(self, generator, logo, output):
        with open(self.tempfile, "w") as file:
            replacements = {var : generator.next() for var in self._variables()}
            replacements["logo"] = logo
            file.write(self._template.substitute(replacements))
        call(["inkscape", "-z", "--export-pdf=%s" % output, self.tempfile])

    def render(self, generator, logo, amount, output):
        self.load()
        pdftkSource = []
        for i in xrange(amount):
            temporaryOutput = "./temp/output%i.pdf" % i
            self._renderOne(generator(), logo, temporaryOutput)
            pdftkSource.append(temporaryOutput)
            print "Page %i out of %i is done." % (i+1, amount)

        print "Collecting all pages into one document."

        call(join([["pdftk"], pdftkSource, ["output", output]]))

        print "Document created."
"""
def mixGenerators(generators):
    def mixedGenerator(*args, **aargs):
        gs = map(lambda f: f(), generators)
        while True:
            yield choice(gs).next()
    return mixedGenerator"""
