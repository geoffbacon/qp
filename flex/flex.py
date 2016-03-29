"""
Module for reading, writing and manipulating FLEx lexicons and texts.

Classes and methods defined
---------------------------

=====================================================
Definition          Description
================    =================================
Lexicon             Models a lexicon document.
    version()       Return verison of lexicon.
    entries         List of entries in lexicon.

Entry               Models an entry in a lexicon.
    headword()        
    gloss()
    pos()
    citation()
    guid()
    order()
    date_created()
    date_modified()
    note()
    variant()
    write()

Text                Models a text document.
    sents()
    words()
    raw()
    pos()
    write()
=====================================================

Example usage - Lexicon
-----------------------

# Read in a LIFT file:

>>> tsw = Lexicon('data', 'tswefap.lift')

>>> print(tsw)
<Lexicon with 720 entries>

# Get the 57th entry in the lexicon:

>>> my_entry = tsw.entries[56]

# Get the headword, gloss and POS:

>>> my_entry.headword()
['līb tsə']

>>> my_entry.gloss()
['sweet']

>>> my_entry.pos()
['adjective']

# Get all the verb headwords in the lexicon:

>>> verbs = [entry.headword() for entry in tsw.entries if 'verb' in entry.pos()]

>>> verbs[:5]
[['fī'], ["yɛ́ mà' nzə̄ nīē"], ["fi'"], ['zhə́'], ['popo']]

# Get all the words in the lexicon that start with a "w":

>>> w_words = [entry for entry in tsw.lexicon if entry.headword()[0].startswith('w')]

>>> [entry.headword() for entry in w_words]
[['wɔ̄'], ['wɨ̄g'], ['wōbə́'], ['wɛ̂sì'], ["wā'"], ['wíndò'], ['wátsɔ̂'], ['wə̀kshí'], ['wátsî, ndwātsīndû'], ['wūúb']]

# Get all the words in the lexicon that have been modified since 5th December 2015:

>>> [entry.headword() for entry in tsw.entries if entry.date_modified() > '2015-12-05T20:53:32Z']
[['wūúb']]

# Get all the words that have to do with washing:

>>> wash_words = [entry.headword() for entry in tsw.entries if 'wash' in entry.gloss()]

>>> wash_words
[['sō']]

# Global spelling change of only Tswefap data (final 'k' to 'g'):

>>> import re
>>> pattern = re.compile('k$')
>>> for entry in tsw._data['entry']:
        form = entry['lexical-unit'][0]['form'][0]
        if form['lang'] == 'nnz':
            pattern.sub('g', form['text'][0]['text'])

# Search for a specific tone pattern in headwords:

>>> import unicodedata as uc
>>> headwords = [entry.headword() for entry in tsw.entries]
>>> headwords = [item for sublist in headwords for item in sublist] # Flatten headword list
>>> tone_dict = {}
>>> for headword in headwords:
        tones = []
        for ch in headword:
            if "ACUTE" in uc.name(ch):
               tones.append("H")
            if "GRAVE" in uc.name(ch):
               tones.append("L")
        tone_dict[headword] = tones

>>> HL = [key for key in tone_dict if tone_dict[key] == ["H", "L"]]
>>> HL[:3]
['flówà', "tswə́pà'", 'tə́khwə̀']

Write changes to new file:

>>> tsw.write('new_tswefap.lift')

Example usage - Text
-----------------------

# Read in a flextext file:

>>> mb = Text('data', 'mobydick.flextext')

>>> print(mb)
<Text with 437 words>

# Get the first sentence:

>>> mb.sents()[0]

['Call', 'me', 'Ishmael', '.']

# Tag words with POS:

>>> tagged_words = [(word, tag) for word, tag in zip(mb.words(), mb.pos())]
>>> tagged_words[:3]
[('Call', 'n'), ('me', 'n'), ('Ishmael', None)] # Fake data

Write changes to new file:

>>> mb.write('moby2.flextext')

To do
-----

TODO: Are any more public methods needed?
TODO: Is there a better way to handle errors in public methods?
TODO: Text.raw() has wrong spacing for punctuation.
"""
import re
from nltk.corpus.reader.xmldocs import XMLCorpusReader, ElementTree

# === Utilities ===

def _xml_to_dict(element):
    """
    Build dictionary from XML Element.
        
    Data is held in an XML element in three ways: attribute key-value pair,
    text contents, and child elements. The returned dictionary does not 
    maintain these distinctions. 
    """
    dict = element.attrib
    text = element.text
    if text:
        text = text.strip()
        if text:
        # LIFT has an element called 'text', so 'rtext' is the real text of an element.
            dict['rtext'] = text
    for child in element:
        # An element may have multiple subelements with same tag
        tag = child.tag
        if tag in dict:  
            dict[tag].append(_xml_to_dict(child))
        else:
            dict[tag] = [_xml_to_dict(child)]
    return dict

def _dict_to_xml(dictn, element, attributes):
    """
    Build XML of all data in Dictn.
    
    Attribute is list of keys in Dictn that should be attributes.
    Element is root element of XML.
    """
    for key in dictn:
        if key == 'rtext':
            element.text = dictn[key]
        elif key in attributes:
            element.set(key, dictn[key])
        else:
            for child_dict in dictn[key]:
                subelement = ElementTree.SubElement(element, key)
                _dict_to_xml(child_dict, subelement, attributes)
    return element

class _FLEx(XMLCorpusReader):
    """A base class for FLEx based classes."""
    def __init__(self, root, fileid):
        XMLCorpusReader.__init__(self, root, fileid)
        self._fileid = self._fileids[0]
        self.elt = self.xml()
        self._data = _xml_to_dict(self.elt)   
    
    def _write(self, file, attributes, root_tag):
        """Writes to file."""
        if file == self._fileid:
            print("Warning: you were about to write over original file")
            return
        root = ElementTree.Element(root_tag)
        tree = _dict_to_xml(self._data, root, attributes)
        tree = ElementTree.ElementTree(tree)             
        tree.write(file, encoding='utf-8')     

# === Lexicon ===

class Lexicon(_FLEx):
    """
    Corpus reader for LIFT lexicons.
    
    LIFT is SIL's Lexicon Interchange FormaT, an XML schema for lexicons.
    """
    def __init__(self, root, fileid):
        _FLEx.__init__(self, root, fileid)
        self.entries = [Entry(i) for i in self._data['entry']]
        
    def __str__(self):
        """
        Return a string representation of this lexicon.
        :rtype: string
        """
        return '<Lexicon with {} entries>'.format((len(self._data['entry'])))  
        
    def version(self):
        """
        Return the LIFT version of this lexicon.
        :rtype: string
        """
        return self._data['version']
    
    def write(self, file):
        """Writes to file."""
        attributes = ['lang', 'href', 'class', 'ref', 'type', 'source', 
                      'dateModified', 'dateCreated', 'dateDeleted', 'name', 
                      'value', 'who', 'when', 'order', 'guid', 'version', 
                      'producer', 'id', 'parent', 'tag']
        self._write(file, attributes, 'lift') 
 
class Entry:
    """A model of an entry in a LIFT lexicon."""
    def __init__(self, data):
        self._data = data
          
    def _multitext(self, element):
        """
        Return text from multitext element in LIFT.
        :rtype: list of strings
        """
        out = []
        for elem in element:
            for subelem in elem['form']:
                for subsubelem in subelem['text']:
                    out.append(subsubelem['rtext'])        
        return out
        
    def __str__(self):
        """
        Return a string representation of this entry.
        :rtype: string
        """
        return '<{} entry in lexicon>'.format(self.headword()[0])
        
    def headword(self):
        """
        Return headword of Entry.
        :rtype: list of strings
        """
        try:
            lexical_unit = self._data['lexical-unit']
            return self._multitext(lexical_unit)
        except KeyError:
            print("No data")

    def citation(self):
        """
        Return citation form of Entry.
        :rtype: list of strings
        """
        try:
            citation = self._data['citation']
            return self._multitext(citations)
        except KeyError:
            print("No data")
        
    def pos(self):
        """
        Return syntactic category of Entry.
        :rtype: list of strings
        """
        try:
            senses = self._data['sense']
            out = []
            for sense in senses:
                pos = sense['grammatical-info'][0]['value']
                out.append(pos)
            return out
        except KeyError:
            print("No data") # Should it print or return?
    
    def gloss(self):
        """
        Return gloss of Entry.
        :rtype: list of strings
        """
        try:
            out = []
            senses = self._data['sense']
            for sense in senses:
                gloss = sense['gloss'][0]['text'][0]['rtext']
                out.append(gloss)
            return out
        except KeyError:
            print("No data")
    
    def guid(self):
        """
        Return global unique id of this entry.
        :rtype: string
        """
        return self._data['guid']
        
    def order(self):
        """
        Return order of this entry in the lexicon.
        :rtype: int
        """
        try:
            return int(self._data['order'])
        except KeyError:
            print("No data")
    
    def date_created(self):
        """
        Return date this entry was created.
        :rtype: string
        """
        try:
            return self._data['dateCreated']
        except KeyError:
            print("No data")
    
    def date_modified(self):
        """
        Return date this entry was last modified.
        :rtype: string
        """
        try:
            return self._data['dateModified']
        except KeyError:
            print("No data")
    
    def note(self):
        """
        Return note text of this entry.
        :rtype: string
        """
        try:
            note = self._data['note']
            return self._multitext(note)
        except KeyError:
            print("No data")
    
    def variant(self):
        """
        Return variant text of this entry.
        :rtype: string
        """
        try:
            variant = self._data['variant']
            return self._multitext(variant)
        except KeyError:
            print("No data")
                      
# === Text ===      
        
class Text(_FLEx):
    """
    Corpus reader for FLEx's flextext texts.
    
    Flextext is SIL's XML schema for texts. For access to the complete XML 
    data structure, use the ``xml()`` method.  For access to simple word lists, 
    use ``words()`` and ``sents()``.
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

    def sents(self):
        """
        Returns all of the sentences in the text.

        :return: the text's text nodes as a list of lists of words and punctuation symbols
        :rtype: list(list(str))
        """
        out = []
        for sent in self.elt.iter('phrase'):
            one_sent = []
            for word in sent.iter('word'):
                for item in word:
                    item_type = item.attrib['type']
                    if item_type == 'txt' or item_type == 'punct':
                        one_sent.append(item.attrib['rtext'])
            out.append(one_sent)
        return out
    
    def words(self):
        """
        Returns all of the words and punctuation symbols in the text.

        :return: the text's text nodes as a list of words and punctuation symbols
        :rtype: list(str)
        """
        out = []
        for word in self.elt.iter('word'):
            for item in word:
                item_type = item.get('type')
                if item_type == 'txt' or item_type == 'punct':
                    out.append(item.get('rtext'))  
        return out
        
    def raw(self):
        """
        Returns all of the words and punctuation symbols in the text as one string.

        :return: the text's text nodes as a string of words and punctuation symbols
        :rtype: string
        """
        return " ".join(self.words())

    def pos(self):
        """
        Returns the POS of words and punctuation symbols in the text.

        :return: the text's POS nodes as a list
        :rtype: list(str)
        """
        out = []
        for word in self.elt.iter('word'):
            for item in word:
                if item.get('type') == 'pos':
                    pos = item.text
            if pos:
                out.append(pos)
            else:
                out.append(None)
            pos = ''
        return out
        
    def write(self, file):
        """Writes to file."""
        attributes = ['lang', 'guid', 'type', 'version', 'font', 
                      'vernacular'] # More?
        self._write(file, attributes, 'document')
    
