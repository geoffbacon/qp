"""
Module for historical linguistics tasks.

This module provides functions for automatic sequence alignment,
similarity analysis, cognate identification and regular sound correspondence
identification supporting research in quantitative historical linguistics.

TODO: Check indices in alignment and retreive
TODO: Fill feature_matrix
TODO: Fill consonants
TODO: Docstring
"""
import csv
import numpy as np

# === Data handling ===

def load_data(file):
    """
    Returns data from CSV wordlist.
    
    CSV file must be comma delimited.
    CSV file contains one language per column, as many columns as needed.
    CSV file contains cognates in the rows.

    E.g.:
    
    w11, w12, w13, ..., w1n
    ...
    wm1, wm2, wm3, ..., wmn
    
    where wij is the ith word in the jth language.
    """
    with open(file, mode='rU') as f:
        out = []
        reader = csv.reader(f)
        for row in reader:
            out.append(row)
    return out

# === Align ===

    # === Constants ===
    
# Default values for maximum similarity scores, from p. 54. 
C_skip = 10 # Indels
C_sub = 35  # Substitutions
C_exp = 45  # Expansions/compressions
C_vwl = 10  # Vowel/consonant relative weight

consonants = ['b', 'c', 'd', 'f'] # etc

# Relevant features for comparing consonants and vowels
R_c = ['syllabic', 'manner', 'voice', 'nasal', 'retroflex', 'lateral', 
       'place'] # 'aspirated' removed for time being
R_v = ['syllabic', 'nasal', 'retroflex', 'high', 'back', 'round', 'long']

# Flattened feature matrix from p. 56
similarity_matrix = {'bilabial': 1.0, 'labiodental': 0.95, 'dental': 0.9, 'alveolar': 0.85,
          'retroflex': 0.8, 'palato-alveolar': 0.75, 'palatal': 0.7, 'velar': 0.6,
          'uvular': 0.5, 'pharyngeal': 0.3, 'glottal': 0.1, 'stop': 1.0, 'affricate': 0.9, 'fricative': 0.8, 'approximant': 0.6,
          'high vowel': 0.4, 'mid vowel': 0.2, 'low vowel': 0.0, 'high': 1.0, 'mid': 0.5, 'low': 0.0, 'front': 1.0, 'central': 0.5, 'back': 0.0, 'plus': 1.0, 'minus': 0.0}

# Relative weights of phonetic features, from p. 55.
salience = {'syllabic': 5, 'voice': 10, 'lateral': 10, 'high': 5, 'manner': 50,
            'long': 1, 'place': 40, 'nasal': 10, 'aspirated': 5, 'back': 5,
            'retroflex': 10, 'round': 5}
            
# p. 59-60           
feature_matrix = {
                  'a': {'place': 'velar', 'manner': 'low vowel', 'syllabic': 
                  'plus', 'voice': 'plus', 'nasal': 'minus', 'retroflex': 
                  'minus', 'lateral': 'minus'}, 
                  
                  'b': {'place': 'bilabial', 'manner': 'stop',
                  'syllabic': 'minus', 'voice': 'plus', 'nasal': 'minus', 'retroflex': 'minus',
                  'lateral': 'minus'},
                   
                  'c': {'place': 'alveolar', 'manner': 'stop', 'syllabic': 'minus',
                  'voice': 'minus', 'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus'}, 
                  
                  'd': {'place': 'alveolar', 'manner': 'stop', 'syllabic': 'minus',
                  'voice': 'plus', 'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus'}, 
                  
                  'e': {'place': 'palatal', 'manner': 'mid vowel', 'syllabic': 'plus', 
                  'voice': 'plus', 'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus'},
                  
                  'f': {'place': 'labiodental', 'manner': 'fricative', 'syllabic': 'minus', 
                  'voice': 'minus', 'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus'}
                  }

    # === Algorithm ===
 
def alignment(str1, str2, epsilon=0):
    """
    Compute the alignment of two phonetic strings.
     
    Implemented directly from Greg Kondrak's thesis, p. 51.
    """
     
    m = len(str1)
    n = len(str2)
    S = np.zeros((m+1, n+1), dtype=float)
    
    #redundant because using np.zeros
    for i in range(0, m+1):
        S[i, 0] = 0
    for j in range(0, n+1):
        S[0, j] = 0
         
    for i in range(1, m+1):
        for j in range(1, n+1):
            print((i,j))
            S[i, j] = max(
                          S[i-1, j] + sigma_skip(str1[i-1]),
                          S[i, j-1] + sigma_skip(str2[j-1]),
                          S[i-1, j-1] + sigma_sub(str1[i-1], str2[j-1]),
#                           S[i-1, j-2] + sigma_exp(str1[i-1], str2[j-2:j]),
#                           S[i-2, j-1] + sigma_exp(str1[i-2:i], str2[j-1]),
                          0
                         )
    print("S", S)
    T = (1-epsilon)*np.amax(S) # Threshold score for near-optimal alignments
    print("T", T)
    
    for i in range(1, m+1):
        for j in range(1, n+1):
            if S[i,j] >= T:
                print('got to here ok')
                #retrieve(i, j, 0, S, out=[])
                           
def sigma_skip(p):
    """
    Returns score of an indel of P. 
    
    p.54
    """
    return C_skip

def sigma_sub(p, q):
    """
    Returns score of a substitution of P with Q. 
    
    p.54
    """
    return C_sub - delta(p, q) - V(p) - V(q)
    
def sigma_exp(p, q):
    """
    Returns score of an expansion/compression. 
    
    p.54
    """
    assert len(q) == 2, "q is not two characters long"
    return C_exp - delta(p, q[0]) - delta(p, q[1]) - V(p) - max(V(q[0]), V(q[1]))
    
def delta(p, q):
    """
    Return weighted sum of difference between P and Q.
    
    p. 54
    """
    features = R(p, q)
    total = 0
    for f in features:
        total += diff(p, q, f) * salience[f]
    return total
    
def diff(p, q, f):
    """
    Returns difference between phonetic segments P and Q in feature F.
    
    p. 52, 54
    Does order of P and Q matter?
    """
    p_features, q_features = feature_matrix[p], feature_matrix[q]
    return similarity_matrix[p_features[f]] - similarity_matrix[q_features[f]]
        
def R(p, q):
    """
    Return relevant features for segment comparsion.
    
    p. 54
    """
    if p in consonants or q in consonants:
        return R_c
    return R_v

def V(p):
    """
    Return vowel weight if P is vowel.
    
    p. 54
    """
    if p in consonants:
        return 0
    return C_vwl
    
def retrieve(i, j, s, S, out):
    if S[i, j] == 0:
        print(out)
        print("Alignment score is {}".format(s))
    else:
        if S[i-1, j-1] + sigma_sub(str1[i], str2[j]) + s >= T:
            out.append("align {} with {}".format(str1[i], str2[j]))
            retrieve(i-1, j-1, s+sigma_sub(str1[i], str2[j]))
            out.pop()
        elif S[i, j-1] + sigma_skip(str2[j]) + s >= T:
            out.append("align null with {}".format( str2[j]))
            retrieve(i, j-1, s+sigma_skip(str2[j]))
            out.pop()
        elif S[i-1, j-2] + sigma_exp(str1[i], str2[j-1:j]) + s >= T:
            out.append("align {} with {}".format(str1[i], str2[j-1:j]))
            retrieve(i-1, j-2, s+sigma_exp(str1[i], str2[j-1, j]))
            out.pop()
        elif S[i-1, j] + sigma_skip(str1[i]) + s >= T:
            out.append("align {} with null".format(str1[i]))
            retrieve(i-1, j, s+sigma_skip(str1[i]))
            out.pop()
        elif S[i-2, j-1] + sigma_exp(str2[j], str1[i-1:i]) + s >= T:
            out.append("align {} with {}".format(str1[i-1:i], str2[j]))
            retrieve(i-2, j-1, s+sigma_exp(str2[j], str1[i-1:i]))
            out.pop()

# === Identify cognates ===  
     
    
# === Identify sound correspondences ===      




                
            
            
                
            
                
