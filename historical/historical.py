"""
Module for historical linguistics tasks.

This module provides functions for automatic sequence alignment,
similarity analysis, cognate identification and regular sound correspondence
identification supporting research in quantitative historical linguistics.
"""
import csv
import numpy as np

# === Data handling ===

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

# === Align ===

    # === Constants ===
    
C_skip = 10
C_sub = 35
C_exp = 45
C_vwl = 10
consonants = ['b', 'c'] # etc
R_c = ['syllabic', 'manner', 'voice', 'nasal', 'retroflex', 'lateral',
       'aspirated', 'place']
R_v = ['syllabic', 'nasal', 'retroflex', 'high', 'back', 'round', 'long']

place =  {'bilabial': 1.0, 'labiodental': 0.95, 'dental': 0.9, 'alveolar': 0.85,
          'retroflex': 0.8, 'palato-alveolar': 0.75, 'palatal': 0.7, 'velar': 0.6,
          'uvular': 0.5, 'pharyngeal': 0.3, 'glottal': 0.1}

manner = {'stop': 1.0, 'affricate': 0.9, 'fricative': 0.8, 'approximant': 0.6,
          'high vowel': 0.4, 'mid vowel': 0.2, 'low vowel': 0.0}

high =   {'high': 1.0, 'mid': 0.5, 'low': 0.0}

back =   {'front': 1.0, 'central': 0.5, 'back': 0.0}

other_features = {'plus': 1.0, 'minus': 0.0}

salience = {'syllabic': 5, 'voice': 10, 'lateral': 10, 'high': 5, 'manner': 50,
            'long': 1, 'place': 40, 'nasal': 10, 'aspirated': 5, 'back': 5,
            'retroflex': 10, 'round': 5}
            
            
# TODO: feature_matrix = {}

    # === Algorithm ===
 
def alignment(str1, str2, epsilon=0):
    '''Compute the alignment of two phonetic strings.
     
    Implemented directly from Greg Kondrak's thesis, p. 51.'''
     
    m = len(str1)
    n = len(str2)
    S = np.zeros((m+1, n+1), dtype=int)
     
    for i in range(1, m+1):
        S[i, 0] = 0
    for j in range(1, n+1):
        S[0, j] = 0
         
    for i in range(1, m+1):
        for j in range(1, n+1):
            S[i, j] = max(
                          S[i-1, j] + sigma_skip(str1[i]),
                          S[i, j-1] + sigma_skip(str2[j]),
                          S[i-1, j-1] + sigma_sub(str1[i], str2[j]),
                          S[i-1, j-2] + sigma_exp(str1[i], str2[j-1:j]),
                          S[i-2, j-1] + sigma_exp(str1[i-1:i], str2[j]),
                          0
                         )
    T = (1-epsilon)*S.amax()
    
    for i in range(1, m+1):
        for j in range(1, n+1):
            if S[i,j] >= T:
                retrieve(i, j, 0)
                           
def sigma_skip(p):
    return C_skip

def sigma_sub(p, q):
    return C_sub - delta(p, q) - V(p) - V(q)
    
def sigma_exp(p, q):
    return C_exp - delta(p, q[0]) - delta(p, q[1]) - V(p) - max(V(q[0]), V(q[1]))
    
def delta(p, q):
    features = R(p, q)
    total = 0
    for f in features:
        total += diff(p, q, f) * salience[f]
    return total
    
def diff(p, q, f):
    p_features, q_features = feature_matrix[p], feature_matrix[q]
    return p_features[f] - q_features[f]
        
def R(p, q):
    if p in consonants or q in consonants:
        return R_c
    return R_v

def V(p):
    if p in consonants:
        return 0
    return C_vwl
    
def retrieve(i, j, s):
    pass
  
# === Identify cognates ===  
     
# === Identify sound correspondences ===      
