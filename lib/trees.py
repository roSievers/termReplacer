# -*- coding: utf-8 -*-
from random import randrange, choice


# BTree a b = Node (a, (Tree a b, Tree a b))
#          | Leaf b

# :: Random (BTree () ())
def randomBinaryTree(leafNumber):
    if leafNumber == 1:
        return None
    elif leafNumber == 2:
        return (None, [None, None])
    elif leafNumber > 2:
        leftSize = randrange(1, leafNumber)
        rightSize = leafNumber - leftSize
        return (None, [randomBinaryTree(leftSize), randomBinaryTree(rightSize)])

# :: (a -> a') -> (b -> b') -> BTree a b -> BTree a' b'
def mapTree(nodeMap, leafMap, tree):
    if isinstance(tree, tuple):
        return (nodeMap(tree[0]), [mapTree(nodeMap, leafMap, leaf) for leaf in tree[1]])
    else:
        return leafMap(tree)

def treeTerm(symbols=(choice, ["+++++-*****"], {}), numbers=(randrange, [1, 10], {})):
    def mapping(tree):
        return mapTree( lambda x: symbols[0](*symbols[1], **symbols[2])
                      , lambda x: numbers[0](*numbers[1], **numbers[2])
                      , tree )
    return mapping

# foldTree :: (b -> c) -> (a -> c -> c -> c) -> Btree a b -> c
def foldTree(leafMap, nodeFold, tree):
    if isinstance(tree, tuple):
        ls = [foldTree(leafMap, nodeFold, leaf) for leaf in tree[1]]
        return nodeFold(tree[0], ls)
    else:
        return leafMap(tree)

def operatorType(o):
    if o in "+-":
        return "Addition"
    elif o in "*":
        return "Multiplication"
    else:
        return None


def cleverFold(tree):
    numberMap = lambda i: (None, "%i" % i)
    def nodeFold(o, ls):
        ot = operatorType(o)
        l = ls[0][1]
        r = ls[1][1]
        # ensure correct bracketing
        if ot == "Multiplication":
            if ls[0][0] == "Addition":
                l = "(%s)" % ls[0][1]
            if ls[1][0] == "Addition":
                r = "(%s)" % ls[1][1]
        return (ot, "%s %s %s" % (l, o, r))
    return foldTree(numberMap, nodeFold, tree)
