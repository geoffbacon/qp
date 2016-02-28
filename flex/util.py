##  util.py
##
##  Author: Geoff Bacon <bacon@berkeley.edu>. 

"""
Phlex utilities.

This module provides utilities for the PHLEX package. It attempts
to bundle the common aspects of the lexicon and text in one place.
"""

# Use the C version of ElementTree, which is faster, if possible:
try: 
    from xml.etree import cElementTree as et
except ImportError:
    from xml.etree import ElementTree as et

__all__ = ["AbstractFlexObject",
           "_isEmpty"]

class AbstractFlexObject:
    """
    Abstract class for FLEx XML objects such as lexicons and texts.
    """
    
    def __init__(self, filename):
        self._filename = filename
        self.tree = et.parse(filename)
        self.root = self.tree.getroot()
    
    def summaryHeading(self):
        print("Basic facts about", self._filename)
        len_of_asterisks = 18 + len(self._filename)
        print("*"*len_of_asterisks)
        
    def version(self):
        return self.root.get("version")
        
    def write(self, filename=None):
        if filename is None:
            filename = self._filename
        self.tree.write(filename, 'utf-8', True)
               
# TODO make this better       
def _isEmpty(value):
    if value is None or value == "" or (isinstance(value, list) and "" in value):
        return True
    return False
        
            
            
        
        