# ALINE

"""
Module for aligning phonetic strings.

This module is a port of Kondrak's (2002) ALINE. It provides functions for 
phonetic sequence alignment and similarity analysis. These are useful in 
historical linguistics, sociolinguistics and synchronic phonology.

Example usage
-------------

# Get optimal alignment of two phonetic sequences

>>> align('θin', 'tenwis')
[[('θ', 't'), ('i', 'e'), ('n', 'n'), ('-', 'w'), ('-', 'i'), ('-', 's')]]

# Get near-optimal alignments of two phonetic sequences

>>> align('təŋ','tsuŋə', 0.1)
[[('t', 't'), ('-', 's'), ('ə', 'u'), ('ŋ', 'ŋ'), ('-', 'ə')],
[('t', 'ts'), ('ə', 'u'), ('ŋ', 'ŋ'), ('-', 'ə')]]

# Read in a CSV file of comparative data:

>>> cognates = load_data('data/aline_test.csv')

TODO: Documentation
TODO: Add more IPA symbols
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

# === Constants ===
 
inf = float('inf')
    
# Default values for maximum similarity scores (Kondrak 2002: 54) 
C_skip = 10 # Indels
C_sub = 35  # Substitutions
C_exp = 45  # Expansions/compressions
C_vwl = 5  # Vowel/consonant relative weight (decreased from 10) 

consonants = ['B', 'N', 'R', 'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 
              'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'z', 'ç', 'ð', 'ħ', 
              'ŋ', 'ɖ', 'ɟ', 'ɢ', 'ɣ', 'ɦ', 'ɬ', 'ɮ', 'ɰ', 'ɱ', 'ɲ', 'ɳ', 'ɴ', 
              'ɸ', 'ɹ', 'ɻ', 'ɽ', 'ɾ', 'ʀ', 'ʁ', 'ʂ', 'ʃ', 'ʈ', 'ʋ', 'ʐ ', 'ʒ',
              'ʔ', 'ʕ', 'ʙ', 'ʝ', 'β', 'θ', 'χ', 'ʐ', 'w']

# Relevant features for comparing consonants and vowels
R_c = ['aspirated', 'lateral', 'manner', 'nasal', 'place', 'retroflex',
       'syllabic', 'voice']
# 'high' taken out of R_v because same as manner
R_v = ['back', 'lateral', 'long', 'manner', 'nasal', 'place',
       'retroflex', 'round', 'syllabic', 'voice'] 

# Flattened feature matrix (Kondrak 2002: 56)
similarity_matrix = {
                     #place
                     'bilabial': 1.0, 'labiodental': 0.95, 'dental': 0.9, 
                     'alveolar': 0.85, 'retroflex': 0.8, 'palato-alveolar': 0.75,
                     'palatal': 0.7, 'velar': 0.6, 'uvular': 0.5, 'pharyngeal': 0.3,
                     'glottal': 0.1, 'labiovelar': 1.0, 'vowel': -1.0,
                     #manner
                     'stop': 1.0, 'affricate': 0.9, 'fricative': 0.8, 'trill': 0.7,
                     'tap': 0.65, 'approximant': 0.6, 'high vowel': 0.4,
                     'mid vowel': 0.2, 'low vowel': 0.0, 'vowel': 0.5,
                     #high
                     'high': 1.0, 'mid': 0.5, 'low': 0.0,
                     #back
                     'front': 1.0, 'central': 0.5, 'back': 0.0,
                     #binary features
                     'plus': 1.0, 'minus': 0.0}

# Relative weights of phonetic features (Kondrak 2002: 55)          
salience = {
            'syllabic': 5, 
			'place': 40, 
			'manner': 50, 
			'voice': 10, 
			'nasal': 10,
			'retroflex': 10, 
			'lateral': 10, 
			'aspirated': 5,
			'long': 1, 
			'high': 3, 
			'back': 3, 
			'round': 3
			}
            
# (Kondrak 2002: 59-60)        
feature_matrix = {
# Consonants
'p': {'place': 'bilabial', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},
                  
'b': {'place': 'bilabial', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

't': {'place': 'alveolar', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'd': {'place': 'alveolar', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʈ': {'place': 'retroflex', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɖ': {'place': 'retroflex', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'c': {'place': 'palatal', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɟ': {'place': 'palatal', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'k': {'place': 'velar', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'g': {'place': 'velar', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'q': {'place': 'uvular', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɢ': {'place': 'uvular', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʔ': {'place': 'glottal', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'm': {'place': 'bilabial', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɱ': {'place': 'labiodental', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'n': {'place': 'alveolar', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɳ': {'place': 'retroflex', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɲ': {'place': 'palatal', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ŋ': {'place': 'velar', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɴ': {'place': 'uvular', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'N': {'place': 'uvular', 'manner': 'stop', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'plus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʙ': {'place': 'bilabial', 'manner': 'trill', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'B': {'place': 'bilabial', 'manner': 'trill', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'r': {'place': 'alveolar', 'manner': 'trill', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʀ': {'place': 'uvular', 'manner': 'trill', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'R': {'place': 'uvular', 'manner': 'trill', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɾ': {'place': 'alveolar', 'manner': 'tap', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɽ': {'place': 'retroflex', 'manner': 'tap', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɸ': {'place': 'bilabial', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'β': {'place': 'bilabial', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'f': {'place': 'labiodental', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'v': {'place': 'labiodental', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'θ': {'place': 'dental', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ð': {'place': 'labiodental', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

's': {'place': 'alveolar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'z': {'place': 'alveolar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʃ': {'place': 'palato-alveolar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʒ': {'place': 'palato-alveolar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʂ': {'place': 'retroflex', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʐ': {'place': 'retroflex', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'ç': {'place': 'palatal', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʝ': {'place': 'palatal', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'x': {'place': 'velar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɣ': {'place': 'velar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'χ': {'place': 'uvular', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʁ': {'place': 'uvular', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ħ': {'place': 'pharyngeal', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ʕ': {'place': 'pharyngeal', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'h': {'place': 'glottal', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɦ': {'place': 'glottal', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɬ': {'place': 'alveolar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'minus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'plus', 'aspirated': 'minus'},

'ɮ': {'place': 'alveolar', 'manner': 'fricative', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'plus', 'aspirated': 'minus'},

'ʋ': {'place': 'labiodental', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɹ': {'place': 'alveolar', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɻ': {'place': 'retroflex', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'plus', 'lateral': 'minus', 'aspirated': 'minus'},

'j': {'place': 'palatal', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'ɰ': {'place': 'velar', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

'l': {'place': 'alveolar', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'plus', 'aspirated': 'minus'},

'w': {'place': 'labiovelar', 'manner': 'approximant', 'syllabic': 'minus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'aspirated': 'minus'},

# Vowels

'i': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'high',
'back': 'front','round': 'minus', 'long': 'minus', 'aspirated': 'minus'},

'y': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'high',
'back': 'front','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'e': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'front','round': 'minus', 'long': 'minus', 'aspirated': 'minus'},

'ø': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'front','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'ɛ': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'front','round': 'minus', 'long': 'minus', 'aspirated': 'minus'},

'œ': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'front','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'a': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'low',
'back': 'front','round': 'minus', 'long': 'minus', 'aspirated': 'minus'},

'ɨ': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'high',
'back': 'central','round': 'minus', 'long': 'minus', 'aspirated': 'minus'},

'ʉ': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'high',
'back': 'central','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'ə': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'central','round': 'minus', 'long': 'minus', 'aspirated': 'minus'},

'u': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'high',
'back': 'back','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'o': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'back','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'ɔ': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'mid',
'back': 'back','round': 'plus', 'long': 'minus', 'aspirated': 'minus'},

'ɒ': {'place': 'vowel', 'manner': 'vowel', 'syllabic': 'plus', 'voice': 'plus',
'nasal': 'minus', 'retroflex': 'minus', 'lateral': 'minus', 'high': 'low',
'back': 'back','round': 'minus', 'long': 'minus', 'aspirated': 'minus'}
}

# === Algorithm ===
 
def align(str1, str2, epsilon=0):
    """
    Compute the alignment of two phonetic strings.
     
    (Kondrak 2002: 51)
    """
    m = len(str1)
    n = len(str2)
    # This includes Kondrak's initialization of row 0 and column 0 to all 0s.
    S = np.zeros((m+1, n+1), dtype=float) 

    # If i <= 1 or j <= 1, don't allow expansions as it doesn't make sense,
    # and breaks array and string indices. Make sure they never get chosen
    # by setting them to -inf. 
    for i in range(1, m+1):
        for j in range(1, n+1):
            edit1 = S[i-1, j] + sigma_skip(str1[i-1])
            edit2 = S[i, j-1] + sigma_skip(str2[j-1])
            edit3 = S[i-1, j-1] + sigma_sub(str1[i-1], str2[j-1])
            if i > 1:
                edit4 = S[i-2, j-1] + sigma_exp(str2[j-1], str1[i-2:i])
            else:
                edit4 = -inf
            if j > 1:
                edit5 = S[i-1, j-2] + sigma_exp(str1[i-1], str2[j-2:j])
            else:
                edit5 = -inf   
            S[i, j] = max(edit1, edit2, edit3, edit4, edit5, 0)

    T = (1-epsilon)*np.amax(S) # Threshold score for near-optimal alignments
    
    alignments = []
    for i in range(1, m+1):
        for j in range(1, n+1):
            if S[i,j] >= T:
                alignments.append(_retrieve(i, j, 0, S, T, str1, str2, []))
    return alignments
                                   
def _retrieve(i, j, s, S, T, str1, str2, out):
    """
    Retrieve the path through the similarity matrix S starting at (i, j).
    
    :return: character by character alignments
    :rtype: list(tuple(str, str))
    """
    if S[i, j] == 0:
        return out
    else:
        if j > 1 and S[i-1, j-2] + sigma_exp(str1[i-1], str2[j-2:j]) + s >= T:
            out.insert(0, (str1[i-1], str2[j-2:j]))
            _retrieve(i-1, j-2, s+sigma_exp(str1[i-1], str2[j-2:j]), S, T, str1, str2, out) 
        elif i > 1 and S[i-2, j-1] + sigma_exp(str2[j-1], str1[i-2:i]) + s >= T:
            out.insert(0, (str1[i-2:i], str2[j-1]))
            _retrieve(i-2, j-1, s+sigma_exp(str2[j-1], str1[i-2:i]), S, T, str1, str2, out)
        elif S[i-1, j-1] + sigma_sub(str1[i-1], str2[j-1]) + s >= T:
            out.insert(0, (str1[i-1], str2[j-1]))
            _retrieve(i-1, j-1, s+sigma_sub(str1[i-1], str2[j-1]), S, T, str1, str2, out)
        elif S[i, j-1] + sigma_skip(str2[j-1]) + s >= T:
            out.insert(0, ('-', str2[j-1]))
            _retrieve(i, j-1, s+sigma_skip(str2[j-1]), S, T, str1, str2, out)
        elif S[i-1, j] + sigma_skip(str1[i-1]) + s >= T:
            out.insert(0, (str1[i-1], '-'))
            _retrieve(i-1, j, s+sigma_skip(str1[i-1]), S, T, str1, str2, out)
    return out
       
def sigma_skip(p):
    """
    Returns score of an indel of P. 
    
    (Kondrak 2002: 54)
    """
    return C_skip

def sigma_sub(p, q):
    """
    Returns score of a substitution of P with Q. 
    
    (Kondrak 2002: 54)
    """
    return C_sub - delta(p, q) - V(p) - V(q)
    
def sigma_exp(p, q):
    """
    Returns score of an expansion/compression. 
    
    (Kondrak 2002: 54)
    """
    q1 = q[0]
    q2 = q[1]
    return C_exp - delta(p, q1) - delta(p, q2) - V(p) - max(V(q1), V(q2))
    
def delta(p, q):
    """
    Return weighted sum of difference between P and Q.
    
    (Kondrak 2002: 54)
    """
    features = R(p, q)
    total = 0
    for f in features:
        total += diff(p, q, f) * salience[f]
    return total
    
def diff(p, q, f):
    """
    Returns difference between phonetic segments P and Q for feature F.
    
    (Kondrak 2002: 52, 54)
    """
    p_features, q_features = feature_matrix[p], feature_matrix[q]
    return abs(similarity_matrix[p_features[f]] - similarity_matrix[q_features[f]])
        
def R(p, q):
    """
    Return relevant features for segment comparsion.
    
    (Kondrak 2002: 54)
    """
    if p in consonants or q in consonants:
        return R_c
    return R_v

def V(p):
    """
    Return vowel weight if P is vowel.
    
    (Kondrak 2002: 54)
    """
    if p in consonants:
        return 0
    return C_vwl
    
# === Useful when testing ===

sounds = feature_matrix.keys()
vowels = [s for s in sounds if s not in consonants]
data = load_data('data/aline_test.csv')
