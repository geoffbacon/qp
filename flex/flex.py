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
TODO: change docstring to reflect this week's changes.
TODO: _multitext
TODO: rewrite Text methods to use _data, not elt. 
TODO: Text.raw() has wrong spacing for punctuation.
"""
import re
from collections import defaultdict
from nltk.corpus.reader.xmldocs import XMLCorpusReader, ElementTree

# === Utilities ===

def _xml_to_dict(element):
    """
    Build dictionary from XML Element.
        
    Data is held in an XML element in three ways: attribute key-value pair,
    text contents, and child elements. The returned dictionary does not 
    maintain these distinctions. 
    """
    d = defaultdict(list)
    d.update(element.attrib)
    text = element.text
    if text:
        text = text.strip()
        if text:
        # LIFT has an element called 'text', so 'rtext' is the real text of an element.
            d['rtext'] = text
    for child in element:
        # An element may have multiple subelements with same tag
        d[child.tag].append(_xml_to_dict(child))
    return d

def _dict_to_xml(d, element, attributes):
    """
    Build XML of all data in D.
    
    Attribute is list of keys in D that should be attributes.
    Element is root element of XML.
    """
    for key in d:
        if key == 'rtext':
            element.text = d[key]
        elif key in attributes:
            element.set(key, d[key])
        else:
            for child_dict in d[key]:
                subelement = ElementTree.SubElement(element, key)
                _dict_to_xml(child_dict, subelement, attributes)
    return element

class FLEx(XMLCorpusReader):
    """A base class for FLEx based classes."""
    def __init__(self, root, fileid):
        XMLCorpusReader.__init__(self, root, fileid)
        self._fileid = self._fileids[0]
        self.elt = self.xml()
        self._data = _xml_to_dict(self.elt)   
    
    def write(self, file, attributes, root_tag):
        """Writes to file."""
        if file == self._fileid:
            print("Warning: you were about to write over original file")
            return
        root = ElementTree.Element(root_tag)
        tree = _dict_to_xml(self._data, root, attributes)
        tree = ElementTree.ElementTree(tree)             
        tree.write(file, encoding='utf-8')

# === Lexicon ===

class Lexicon(FLEx):
    """
    Corpus reader for LIFT lexicons.
    
    LIFT is SIL's Lexicon Interchange FormaT, an XML schema for lexicons.
    """
    def __init__(self, root, fileid):
        FLEx.__init__(self, root, fileid)
        self.entries = [self._build_entry(entry) for entry in self._data['entry']]
        
    def _build_entry(self, e):
        """Builds user-friendly dictionary from E."""
        d = defaultdict(list)
        d['guid'] = e.get('guid', [])
        d['order'] = e.get('order', [])
        d['dateCreated'] = e.get('dateCreated', [])
        d['dateModified'] = e.get('dateModified', [])
        senses = e.get('sense', [])
        d['pos'] = [sense['grammatical-info'][0]['value'] for sense in senses]
        d['gloss'] = [sense['gloss'][0]['text'][0]['rtext'] for sense in senses]
        lexical_unit = e.get('lexical-unit', [])
        d['headword'] = lexical_unit #self._multitext(lexical-unit)
        citation = e.get('citation', [])
        d['citation'] = citation
        note = e.get('note', [])
        d['note'] = note
        variant = e.get('variant', [])
        d['variant'] = variant
        return d  
        
    def _multitext(self, unit):
        """
        Return text from multitext element in LIFT.
        :rtype: list of strings
        """  
        return [form['text'][0]['rtext'] for form in unit[0]['form']]      
   
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
        super().write(file, attributes, 'lift')
                      
# === Text ===      
        
class Text(FLEx):
    """
    Corpus reader for FLEx's flextext texts.
    
    Flextext is SIL's XML schema for texts. For access to the complete XML 
    data structure, use the ``xml()`` method.  For access to simple word lists, 
    use ``words()`` and ``sents()``.
    """
    def __init__(self, root, fileid):
        FLEx.__init__(self, root, fileid)
        
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
                        one_sent.append(item.text)
            out.append(one_sent)
        return out
        
    def tagged_sents(self):
        """
        Returns all of the words and punctuation symbols in the text tagged with pos.

        :return: the text's text nodes as a list of words and punctuation symbols
        :rtype: list((str, str))
        """
        pass
    
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
                    out.append(item.text)  
        return out
        
    def tagged_words(self):
        """
        Returns all of the words and punctuation symbols in the text tagged with pos.

        :return: the text's text nodes as a list of words and punctuation symbols
        :rtype: list((str, str))
        """
        return [(word, tag) for word, tag in zip(mb.words(), mb._pos())]
            
    def raw(self):
        """
        Returns all of the words and punctuation symbols in the text as one string.

        :return: the text's text nodes as a string of words and punctuation symbols
        :rtype: string
        """
        return " ".join(self.words())

    def _pos(self):
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
        super().write(file, attributes, 'document')
    
