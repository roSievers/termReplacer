#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange, shuffle, choice
from sys import argv, exit
from lib.templating import Template
import lib.trees as trees
import argparse
from itertools import imap, ifilter
from lib.sources import mapI, filterI, functionSource, tuples, multimap, avoidDuplication, randomlyMix

# Parse command line input:

parser = argparse.ArgumentParser(description="Generates random worksheets.")
parser.add_argument("-n", "--number", dest="num", type=int, default=1, help="The amount of pages in one output.")
parser.add_argument("presets", metavar="preset", nargs="*",
                    help="The preset(s) used for generation.")
parser.add_argument("-a", "--all", help="Use all available presets.",
                    default=False, dest="all", action="store_true")
parser.add_argument("-ls", "--list", help="Show all available presets.",
                    default=False, dest="list", action="store_true")
parser.add_argument("-l", "--logo", type=str, default="default", help="Set a school logo.", dest="logo")


# The templates are loaded lazily (i.e., on first access)
# We can load many templates at once without noticeable speed or space penalty.
shortTemplate    = Template("templates/shortLines-Eichendorfschule.svg")
mediumTemplate   = Template("templates/mediumLines-Eichendorfschule.svg")
longTemplate     = Template("templates/longLines-Eichendorfschule.svg")
veryLongTemplate = Template("templates/veryLongLines-Eichendorfschule.svg")
divisionTemplate = Template("templates/division-Eichendorfschule.svg")


def divisionOhneRest(divisor=[1,10], quotient=[100,300]):
    _divisor = randrange(*divisor)
    _quotient = randrange(*quotient)
    return "%i / %i" % (_divisor * _quotient, _divisor)

# -- Useful maps for working with iterators

renderSymbols = mapI(lambda term: term.replace("*", "•").replace("/", ":"))

orderOfOperation = filterI(lambda term: ("+" in term or "-" in term) and "*" in term)

brackets = filterI(lambda term: "(" in term)
doubleBrackets = filterI(lambda term: term.count("(") >= 2)

def smallResult(n):
    return filterI(lambda term: eval(term) <= n)
def bigResult(n):
    return filterI(lambda term: eval(term) >= n)
def resultBetween(a, b):
    return filterI(lambda term: a <= eval(term) <= b)

nonNegative = filterI(lambda term: 0 <= eval(term))

def myrandrange(a, b):
    return functionSource(randrange, a, b)

multiply  = mapI(lambda t: "%i * %i" % t)
add       = mapI(lambda t: "%i + %i" % t)
substract = mapI(lambda t: "%i - %i" % t)

fst = lambda s: s[0]
snd = lambda s: s[1]

# -- generators

smallMultiplicationTable = multimap(
    myrandrange(1, 11),
    [ tuples
    , multiply
    , avoidDuplication
    , renderSymbols])

bigMultiplicationTable = multimap(
    myrandrange(1, 21),
    [ tuples
    , filterI(lambda t: t[0] > 10 or t[1] > 10)
    , multiply
    , avoidDuplication
    , renderSymbols])

additionUpTo = lambda maximum : multimap(
    myrandrange(1, maximum),
    [ tuples
    , add
    , smallResult(maximum)
    , avoidDuplication ])

substractionUpTo = lambda maximum : multimap(
    myrandrange(2, maximum),
    [ tuples
    , substract
    , nonNegative
    , avoidDuplication ])

def longMixedTerm(length, **aargs):
    return multimap(
        functionSource(trees.randomBinaryTree, length),
        [ mapI(trees.treeTerm(**aargs))
        , mapI(trees.cleverFold)
        , mapI(snd)
        , avoidDuplication ])

simpleOrderOfOperation = multimap(
    longMixedTerm(3),
    [ orderOfOperation
    , nonNegative
    , renderSymbols])

mediumOrderOfOperation = multimap(
    longMixedTerm(5),
    [ orderOfOperation
    , resultBetween(-200, 200)
    , renderSymbols])

hardOrderOfOperation = multimap(
    longMixedTerm(7, numbers=(randrange, [1, 24], {})),
    [ orderOfOperation
    , doubleBrackets
    , resultBetween(-700, 700)
    , renderSymbols])

longDivision = multimap(
    functionSource(divisionOhneRest),
    [ renderSymbols ])

hardLongDivision = multimap(
    functionSource(divisionOhneRest, divisor=[2,25], quotient=[1000, 7000]),
    [ renderSymbols ])

simpleMix = randomlyMix(
    [ additionUpTo(100)
    , substractionUpTo(30)
    , smallMultiplicationTable ])

mediumMix = randomlyMix(
    [ additionUpTo(1000)
    , substractionUpTo(200)
    , bigMultiplicationTable
    , simpleOrderOfOperation ])

# -- define the outputs

outputs = {}
outputList = [] # To track the ordering as well.
def namedOutput(name, template, source):
    if name == "all":
        raise "'all' is a reserved name."
    outputList.append(name)
    outputs[name] = {"name" : name, "template" : template, "source" : source}

namedOutput("Kleines Einmaleins", mediumTemplate, smallMultiplicationTable)
namedOutput("Kleines Einmaleins (viel)", shortTemplate, smallMultiplicationTable)

namedOutput("Großes Einmaleins", mediumTemplate, bigMultiplicationTable)
namedOutput("Großes Einmaleins (viel)", shortTemplate, bigMultiplicationTable)

namedOutput("Addition bis 20", mediumTemplate, additionUpTo(20))
namedOutput("Addition bis 20 (viel)", shortTemplate, additionUpTo(20))
namedOutput("Addition bis 100", mediumTemplate, additionUpTo(100))
namedOutput("Addition bis 100 (viel)", shortTemplate, additionUpTo(100))
namedOutput("Addition bis 500", mediumTemplate, additionUpTo(500))
namedOutput("Addition bis 2000", mediumTemplate, additionUpTo(2000))

namedOutput("Gemischt Einfach", mediumTemplate, simpleMix)
namedOutput("Gemischt Einfach (viel)", shortTemplate, simpleMix)
namedOutput("Gemischt Mittel", mediumTemplate, mediumMix)

namedOutput("Punkt vor Strich Einfach", mediumTemplate, simpleOrderOfOperation)
namedOutput("Punkt vor Strich Mittel", longTemplate, mediumOrderOfOperation)
namedOutput("Punkt vor Strich Schwer", veryLongTemplate, hardOrderOfOperation)

namedOutput("Schriftliche Division Mittel", divisionTemplate, longDivision)
namedOutput("Schriftliche Division Schwer", divisionTemplate, hardLongDivision)


def renderOutput(number, logo, targets):
    for name in targets:
        print "Rendering %i pages of '%s'." % (number, name)
        target = outputs[name]
        target["template"].render(target["source"], logo, number, "out/"+name+".pdf")
        print ""

# We are now ready to actually execute something

def main():
    arguments = parser.parse_args()
    if arguments.list is True:
        print "Available presets are:"
        for name in outputList:
            print "  '%s'" % name
        exit()
    elif arguments.all is True:
        if len(arguments.presets) > 0:
            print "You are trying to use '--all' while selecting specific presets as well."
            print "This is not possible."
            exit()
        arguments.presets = outputList
    elif len(arguments.presets) == 0:
        print "You must either choose a preset or use '--all'."
        print "Use --help for more information."
        exit()
    else:
        badPresets = []
        for preset in arguments.presets:
            if preset not in outputList:
                badPresets.append(preset)
        if len(badPresets) > 0:
            print "The following presets are not available:", badPresets
            print "Use -ls to view a list of available presets."
            exit()

    # Yeah, finally everything is in order!

    renderOutput(arguments.num, arguments.logo, arguments.presets)

if __name__ == "__main__":
    main()
