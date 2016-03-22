"""
Module for reading, writing and manipulating FLEx lexicons and texts.

FLEx stores lexicons and texts in XML formats, lexicons as SIL's Lexicon 
Interchange FormaT (LIFT), and texts as flextext. This script provides classes 
for both file formats derived from a common FLEx class. All the data in a file 
of either format is stored as a dictionary in the _data attribute.

Classes
-------

================    =================================
Class               Description
================    =================================
_FLEx               Holds data from XML file as dict.
Lexicon             Models a lexicon document.
Entry               Models an entry in a lexicon.
Text                Models a text document.

Working with lexicons and entries 
---------------------------------

================    ===============================
Method              Description
================    ===============================
headword            Return headword of an entry.
gloss               Return gloss of an entry.
pos                 Return POS of entry.
citation            Return citation form of entry.
================    ===============================

Working with texts 
------------------

================    ===============================
Method              Description
================    ===============================
paras
sents
words
raw
================    ===============================

Example usage
-------------

Read in a LIFT file:

>>> tsw = Lexicon('data', 'tswefap.lift')

Get the 57th entry in the lexicon:

>>> my_entry = tsw._data['entry'][56]

Get the headword of that entry:

>>> my_entry.headword()

Read in a flextext file:

>>> mb = Text('data', 'mobydick.flextext')

TODO: More public methods, but without recreating dictionary syntax.
TODO: Error handling if tag not found (e.g. currently if an entry has no 
`citation` field, the citation() method will break).

"""
import re
from nltk.corpus.reader.xmldocs import XMLCorpusReader

class _FLEx(XMLCorpusReader):
    def __init__(self, root, fileid):
        XMLCorpusReader.__init__(self, root, fileid)
        self._fileid = self._fileids[0]
        self.elt = self.xml()
        self._data = self._load_data(self.elt)
          
    def _has_content(self, str):
        """Return True if String has any non-whitespace characters.
        
        ElementTree sometimes returns new-line, whitespace, etc. as the text 
        contents of an element. If there is no non-whitespace characters, we 
        should treat that element as not having text content. This methods saves
        _load_data from breaking when the text contents would be just whitespace
        or None.
        """
        if str:
            if re.search(r'\S', str):
                return True
        return False  
        
    def _load_data(self, element):
        """Build dictionary of all data in Element.
        
        Data is held in an XML element in three ways: attribute key-value pair,
        text contents, and child elements. 
        """
        data_dict = element.attrib
        text = element.text
        if self._has_content(text):
            data_dict['text'] = text
        for child in element:
            # An element may have multiple subelements with same tag
            if child.tag in data_dict:  
                data_dict[child.tag].append(self._load_data(child))
            else:
                data_dict[child.tag] = [self._load_data(child)]
        return data_dict        

# === Lexicon ===

class Lexicon(_FLEx):
    def __init__(self, root, fileid):
        _FLEx.__init__(self, root, fileid)
        self.entries = [Entry(i) for i in self._data['entry']]
        
    def __str__(self):
        """
        Return a string representation of this lexicon.
        :rtype: string
        """
        return '<Lexicon with {} entries>'.format((len(self._data['entry'])))
       
class Entry:
    def __init__(self, data):
        self._data = data
        
    # === Private methods ===
      
    def _multitext(self, element):
        """Return text from multitext element."""
        out = []
        for elem in element:
            for subelem in elem['form']:
                for subsubelem in subelem['text']:
                    out.append(subsubelem['text'])        
        return out
        
    def _format_output(self, out):
        """Return element of singleton list, else return whole list.
        
        Some fields in LIFT may have one or multiple values. This method provides
        the most useful output.
        """
        if len(out) == 1:
            return out[0]
        return out
        
    def __str__(self):
        """
        Return a string representation of this entry.
        :rtype: string
        """
        return '<{} entry in lexicon>'.format(self.headword())
    
    # === Public methods ===
    
    def headword(self):
        """Return headword of Entry."""
        lexical_unit = self._data['lexical-unit']
        headwords = self._multitext(lexical_unit)
        return self._format_output(headwords)
        
    def citation(self):
        """Return citation form of Entry."""
        citation = self._data['citation']
        citations = self._multitext(citations)
        return self._format_output(citations)
        
    def pos(self):
        """Return POS of Entry."""
        out = []
        senses = self._data['sense']
        for sense in senses:
            pos = sense['grammatical-info'][0]['value']
            out.append(pos)
        return self._format_output(out)
    
    def gloss(self):
        """Return gloss of Entry."""
        out = []
        senses = self._data['sense']
        for sense in senses:
            gloss = sense['gloss'][0]['text'][0]['text']
            out.append(gloss)
        return self._format_output(out)

# === Text ===      
        
class Text(_FLEx):
    """Corpus reader for FLEx's flextext files.

    For access to the complete XML data structure, use the ``xml()``
    method.  For access to simple word lists, use
    ``words()``, ``sents()``.
    """
    def __init__(self, root, fileid):
        _FLEx.__init__(self, root, fileid)
        
    def __str__(self):
        """
        Return a string representation of this text.
        :rtype: string
        """
        num_of_words = sum([1 for elem in self.elt.iter('word')])
        return '<Text with {} words>'.format(num_of_words)
    
    # === Public methods ===
    
    def paras(self):
        pass

    def sents(self):
        out = []
        for sent in self.elt.iter('phrase'):
            one_sent = []
            for word in sent.iter('word'):
                for item in word:
                    item_type = item.attrib['type']
                    if item_type == 'txt' or item_type == 'punct':
                        one_sent.append(item.attrib['text'])
            out.append(one_sent)
        return out
    
    def words(self):
        out = []
        for word in self.elt.iter('word'):
            for item in word:
                item_type = item.attrib['type']
                if item_type == 'txt' or item_type == 'punct':
                    out.append(item.attrib['text'])  
        return out
        
    def raw(self):
        """TODO: Wrong spacing with punctuation."""
        return " ".join(self.words())
