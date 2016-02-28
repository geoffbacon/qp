##  phlextext.py
##
##  Author: Geoff Bacon <bacon@berkeley.edu>. 

"""
FLEx text reader.

This module provides functions for reading, writing and manipulating 
FLEx texts.

Classes
-------

A single class is defined: Text.

Working with LIFT files
-----------------------

================    ===============================
Method              Description
================    ===============================
summary             Print summary of text.
data                Return all words and their pos.
words               Return all words.
raw                 Return raw text.
sentences           Return all sentences.
================    =============================

Example usage
-------------

python3 phlexicon.py

Load a flextext text:

>>> mb = Text("data/mobydick.flextext")

Print fifth word:

>>> mb.words[4]
'Some'

Print the sixth sentence:

>>> mb.sentences[5]
' With a philosophical flourish Cato throws himself upon his sword ; 
I quietly take to the ship .'

Find missing POS:

>>> for (word, pos) in mb.data:
...     if pos == "Unknown":
...         print(word)

"""

__all__ = ['Text']

from util import *

# === Public class ===

class Text(AbstractFlexObject):
    """
    Class for reading and processing FLEx's flextext files.
    """
    def __init__(self, filename):
        AbstractFlexObject.__init__(self, filename)
        self.data = []
        self.words = []
        entries = self.root.findall(".//word")
        for entry in entries:
            items = entry.findall("item")
            for item in items:
                item_type = item.get("type")
                pos = "Unknown"
                if item_type == "txt":
                    word = item.text
                elif item_type == "pos":
                    pos = item.text
                elif item_type == "punct":
                    word = item.text
                    pos = "punct"    
            self.data.append((word, pos))
            self.words.append(word)
        self.raw = " ".join(self.words) # spaces are wrong
        self.sentences = []
        sents = self.root.findall('.//words')
        for sent in sents:
            text = ""
            for word in sent:
                for item in word:
                    item_type = item.get("type")
                    if item_type == "txt" or item_type == "punct":
                        text = text + " " + item.text
            self.sentences.append(text)
        self.summary()
        
    def summary(self):
        self.summaryHeading()
        num_of_chars = len(self.raw)
        num_of_tokens = len(self.words)
        num_of_types = len(set(self.words))
        num_of_sents = len(self.sentences)
        print("Number of characters:", num_of_chars, "\n")
        print("Numer of word tokens:", num_of_tokens, "\n")
        print("Number of word types:", num_of_types, "\n")
        print("Number of sentences:", num_of_sents, "\n")
        
  
def demo():
    pass

if __name__ == '__main__':
    demo()