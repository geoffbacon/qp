##  Module historical.py
##
##  Author: Geoff Bacon <bacon@berkeley.edu>.

"""
Module for historical linguistics tasks.

This module provides functions for automatic sequence alignment,
similarity analysis, cognate identification and regular sound correspondence
identification supporting research in quantitative historical linguistics.

Classes
-------

A single class is defined: Wordlist.

Working with wordlists
----------------------

================    ===============================
Method              Description
================    ===============================
editDistance        Return edit distance of two str
optimalAlignment    Wagner-Fischer algorithm
================    =============================

Example usage
-------------

python3 historical.py

Read in a CSV file:

>>> greek = Wordlist("data/greek-data.csv", header=True, glosses=True)

Inspect the languages in the wordlist

>>> greek.languages
['Earlier', 'Silli', ' Gloss']

Retreive cognates by gloss

>>> greek.data['paper']
['Oti', 'OCi']

Align two words NB: Currently scoring function prefers gaps over aligning
non-identical segments.

>>> word1, word2 = greek.data['paper']
>>> optimalAlignment(word1, word2)
('i', 'i')
('t', '-')
('-', 'C')
('O', 'O')

"""

import csv
import numpy as np

# === Get data in ===

class Wordlist:
    """ 
    Class to retrieve and store a wordlist from a CSV file.
    
    CSV file must be comma delimited.
    CSV file contains one language per column, as many columns as needed.
    CSV file contains cognates in the rows.
    CSV file may contain one header row indicating language names.
    CSV file may contain glosses, which must appear in the rightmost column.
    
    E.g.:
    
    LG1, LG2, LG3, ..., LGn, GLOSS
    w11, w12, w13, ..., w1n, g1
    ...
    wm1, wm2, wm3, ..., wmn, gm 
    
    where wij is the ith word in the jth language.
    """
    
    def __init__(self, file, header=False, glosses=False):
        self.data = {}
        with open(file, mode='rU') as f:
            reader = csv.reader(f)
            if header:
                self.languages = next(reader)   
            if glosses:
                for row in reader:
                    gloss = row[-1]
                    words = row[:-1]
                    self.data[gloss] = words
            else:
                i = 0
                for row in reader:
                    self.data[i] = row
                    i += 1
                    
# === Preprocessing ===

# Standardise orthography, combining characters, suprasegmentals, etc.
# Already offered in NLTK? 

# === Align ===
    
def _editDistance(str1, str2):
    """
    Returns the distance matrix between two strings and the two strings' lengths.
    
    This was implemented directly from Greg Kondrak's thesis. 
    """
    
    m = len(str1)
    n = len(str2)
    d = np.zeros((m + 1, n + 1), dtype=int)
    
    for i in range(1, m + 1):
        d[i, 0] = d[i-1, 0] + 1
    for j in range(1, n + 1):
        d[0, j] = d[0, j-1] + 1
        
    for i in range(1, m+1):
        for j in range(1, n+1):
            if str1[i-1] == str2[j-1]:
                d[i, j] = d[i-1, j-1]
            else:
                d[i, j] = min(
                          d[i-1, j-1] + _cost(str1[i-1], str2[j-1]),
                          d[i-1, j] + _cost(str1[i-1], "-"),
                          d[i, j-1] + _cost("-", str2[j-1])
                          )
    return m, n, d
    
def editDistance(str1, str2):
    """
    Returns minimal edit distance between two strings.
    
    Wrapper function for _editDistance.
    """
    
    m, n, d = _editDistance(str1, str2)
    return d[m, n]
    
    
def optimalAlignment(str1, str2):
    """
    Return the optimal alignment between two strings.
    
    This is the `plain-vanilla` Wagner-Fischer algorithm. This was implemented
    directly from Greg Kondrak's thesis, although it is not yet ALINE. Kondrak
    made a number of changes to WF, which are in TODOs below. 
    
    TODO: Retrieve best alignments, withing epsilon of optimal alignment. 
    TODO: Use string similarity rather than string difference.
    TODO: Local and semiglobal alignment.
    TODO: Affine gap functions.
    TODO: Add edit operations (compression, expansion).
    TODO: Comparing phonetic segments (more sophisticated cost/similarity).
    """
    
    m, n, d = _editDistance(str1, str2)
    
    i, j = m, n
    while i != 0 or j != 0:
        if d[i,j] == d[i-1, j] + _cost(str1[i-1], "-"):
            print((str1[i-1], "-"))
            i -= 1
        elif d[i, j] == d[i, j-1] + _cost("-", str2[j-1]):
            print(("-", str2[j-1]))
            j -= 1
        else:
            print((str1[i-1], str2[j-1]))
            i -= 1
            j -= 1
            
def _cost(a, b):
    """Return the cost of replacing character A with character B."""
    if a == "-":
        return 1
    if b == "-":
        return 1
    else:
        return 2
        
def _similarity(a, b):
    """Return the similarity of character A with character B."""
    if a == "-":
        return 1
    if b == "-":
        return 1
    else:
        return 2

# This is work-in-progress.        
def _local(str1, str2):
    """
    Compute local similarty between two strings.
    """
    
    m = len(str1)
    n = len(str2)
    s = np.zeros((m + 1, n + 1), dtype=int)
    
    for i in range(1, m+1):
        s[i, 0] = 0
    for j in range(1, n+1):
        s[0, j] = 0
        
    for i in range(1, m+1):
        for j in range(1, n+1):
            s[i, j] = max(
                          s[i-1, j-1] + _similarity(str1[i-1], str2[j-1]),
                          s[i-1, j] + _similarity(str1[i-1], "-"),
                          s[i, j-1] + _similarity("-", str2[j-1]),
                          0
                          )
    return m, n, s
        

        

# === Identify cognates ===  
     
    
# === Identify sound correspondences ===      




                
            
            
                
            
                