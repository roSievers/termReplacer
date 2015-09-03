# -*- coding: utf-8 -*-
from itertools import imap, ifilter
from random import choice

# type Source a = () ~> Iterator a
# where (() ~> a) is a python approximation of the monadic (Random a)
# In general (a ~> b) is just (a -> Random b) and then
# () ~> a = () -> Random a = Random a

# :: (a ~> b) -> a -> Source b
def functionSource(function, *args, **aargs):
    def generator():
        while True:
            yield function(*args, **aargs)
    return generator

# :: (() ~> a_0) -> [a_i -> a_{i+1}]_{i=0..k-1} -> (() ~> a_k)
def multimap(value, functions):
    def closure():
        # pop the bubble
        v = value()
        # apply all functions to the inner value
        for f in functions:
            v = f(v)
        return v
    # return the result inside a new bubble
    return closure

# :: [Source b] -> Source b
def randomlyMix(sources):
    def mixedGenerator():
        iterators = map(lambda f: f(), sources)
        while True:
            yield choice(iterators).next()
    return mixedGenerator

def mapI(f):
    def lifted(gen):
        return imap(f, gen)
    return lifted

def filterI(f):
    def lifted(gen):
        return ifilter(f, gen)
    return lifted

def avoidDuplication(gen):
    hashMap = {}
    while True:
        new = gen.next()
        if new not in hashMap:
            yield new
            hashMap[new] = True

def tuples(gen):
    while True:
        yield (gen.next(), gen.next())
