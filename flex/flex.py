"""
Module for reading, writing and manipulating FLEx lexicons.

FLEx works with SIL's Lexicon Interchange FormaT (LIFT), a file format for 
dictionaries. This script models a LIFT file. Specifically, it models version 
0.13 of the LIFT standard, as described in the relevant document at 
http://lift-standard.googlecode.com/svn/trunk/. Pages 16-7 provide the UML 
diagrams from which the LIFT standard was modelled.

This script is divided into three sections, correpsonding to the three sections 
in the UML diagrams mentioned above: `Base elements`, `Entry elements`, and 
`Header elements`.

TODO: Provide access to data with public methods
TODO: Fix `if element` plague. The classes I define all expect an XML node during 
construction. If that node is not there in the LIFT file, error is raised during 
__init__. If __init__ begins with `if element`, then asking for the attributes of 
an element-less object raises error. 
TODO: Fix Span/Text classes. For some reason, they don't work.

Example usage
-------------

Read in a LIFT file:

>>> tsw = Lift("data", "tswefap.lift")

Get the 57th entry in the lexicon:

>>> tsw.entries[56]
"""

from datetime import datetime

from nltk.corpus.reader.xmldocs import XMLCorpusReader

# === LIFT ===

    # === Base elements ===

# class Span:
#     """Models span class of LIFT."""
#     def __init__(self, element):
#         if element:
#             self.lang = element.get('lang')
#             self.href = element.get('href')
#             self.span_class = element.get('class')
#             self.span = [Span(i) for i in element.findall('span')]
#             
# class Text:
#     """Models text class of LIFT."""
#     def __init__(self, element):
#         if element:
#             self.span = [Span(i) for i in element.findall('span')]

class Form:
    """Models form class of LIFT."""
    def __init__(self, element):
        if element:
            self.lang = element.get('lang')
            self.text = element.find('text').text
            self.annotation = [Annotation(i) for i in element.findall('annotation')]
            
class Multitext:
    """Models multitext class of LIFT."""
    def __init__(self, element):
        if element:
            self.form = [Form(i) for i in element.findall('form')]
            
class Example(Multitext):
    """Models example class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.source = element.get('source')
            self.translation = [Translation(i) for i in element.findall('translation')]
        
class Translation(Multitext):
    """Models translation class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.type = element.get('type')
            
class Field(Multitext):
    """Models field class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.type = element.get('type')
            self.dateModified = element.get('dateModified')
            self.dateCreated = element.get('dateCreated')
            self.trait = [i for i in element.findall('trait')]
            self.annotation = [i for i in element.findall('annotation')]
            
class Trait:
    """Models field class of LIFT."""
    def __init__(self, element):
        if element:
            self.name = element.get('name')
            self.value = element.get('value')
            self.annotation = [Annotation(i) for i in element.findall('annotation')]

class Note(Multitext):
    """Models note class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.type = element.get('type')

class Variant(Multitext):
    """Models variant class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.ref = element.get('ref')
            self.pronunciation = [Phonetic(i) for i in element.findall('pronunciation')]
            self.relation = [Relation(i) for i in element.findall('relation')]
        
class Reversal(Multitext):
    """Models reversal class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.type = element.get('type')
            self.main = Reversal(element.find('main'))
            self.grammatical_info = Grammatical_Info(element.find('grammatical-info'))
    
class Phonetic(Multitext):
    """Models phonetic class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.media = [URLRef(i) for i in element.findall('media')]
            
class URLRef:
    """Models phonetic class of LIFT."""
    def __init__(self, element):
        if element:
            self.href = element.get('href')
            self.label = Multitext(element.find('label'))

class Annotation(Multitext):
    """Models annotation class of LIFT."""
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.name = element.get('name')
            self.value = element.get('value')
            self.who = element.get('who')
            self.when = element.get('when')

    # === Entry elements ===

class Extensible:
    """Models extensible class of LIFT."""
    def __init__(self, element):
        if element:
            self.dateCreated = element.get('dateCreated')
            self.dateModified = element.get('dateModified')
            self.field = [Field(i) for i in element.findall('field')]
            self.trait = [Trait(i) for i in element.findall('trait')]
            self.annotation = [Annotation(i) for i in element.findall('annotation')]

class Etymology(Extensible):
    """Models etymology class of LIFT."""
    def __init__(self, element):
        if element:
            Extensible.__init__(self, element)
            self.type = element.get('type')
            self.source = element.get('source')
            self.gloss = [Form(i) for i in element.findall('gloss')]
            self.form = Form(element.find('form'))
        
class Sense(Extensible):
    """Models sense class of LIFT."""
    def __init__(self, element):
        if element:
            Extensible.__init__(self, element)
            self.id = element.get('id')
            self.order = element.get('order')
            self.grammatical_info = Grammatical_Info(element.find('grammatical-info'))
            self.gloss = [Form(i) for i in element.findall('gloss')]
            self.definition = Multitext(element.find('definition'))
            self.relation = [Relation(i) for i in element.findall('relation')]
            self.note = [Note(i) for i in element.findall('note')]
            self.example = [Example(i) for i in element.findall('example')]
            self.reversal = [Reversal(i) for i in element.findall('reversal')]
            self.illustration = [URLRef(i) for i in element.findall('illustration')]
            self.subsense = [Sense(i) for i in element.findall('subsense')]
        
class Note(Extensible):
    """Models note class of LIFT."""
    def __init__(self, element):
        if element:
            Extensible.__init__(self, element)
            self.type = element.get('type')
    
class Variant(Extensible):
    """Models variant class of LIFT."""
    def __init__(self, element):
        if element:
            Extensible.__init__(self, element)
            self.ref = element.get('ref')
            self.pronunciation = [Phonetic(i) for i in element.findall('pronunciation')]
            self.relation = [Relation(i) for i in element.findall('relation')]
             
class Relation(Extensible):
    """Models relation class of LIFT."""
    def __init__(self, element):
        if element:
            Extensible.__init__(self, element)
            self.type = element.get('type')
            self.ref = element.get('ref')
            self.order = element.get('order')
            self.usage = Multitext(element.find('usage'))

class Example(Extensible):
    """Models example class of LIFT."""
    def __init__(self, element):
        if element:
            Extensible.__init__(self, element)
            self.source = element.get('source')
            self.translation = [Translation(i) for i in element.findall('translation')]
    
class Grammatical_Info:
    """Models grammatical-info class of LIFT."""
    def __init__(self, element):
        if element:
            self.value = element.get('value')
            self.trait = [Trait(i) for i in element.findall('trait')]

class Entry(Extensible):
    """
    Models entry class of LIFT. 
    
    During construction, get() will return None if the attribute isn't found.
    """
    def __init__(self, entry):
        Extensible.__init__(self, entry)
        self._entry = entry
        self.id = entry.get('id')
        self.order = entry.get('order')
        self.guid = entry.get('guid')
        self.dateDeleted = entry.get('dateDeleted')
        self.lexical_unit = Multitext(entry.find('lexical-unit'))
        self.citation = Multitext(entry.find('citation'))
        self.pronunciation = [Phonetic(i) for i in entry.findall('pronunciation')]
        self.variant = [Variant(i) for i in entry.findall('variant')]
        self.sense = [Sense(i) for i in entry.findall('sense')]
        self.note = [Note(i) for i in entry.findall('note')]
        self.relation = [Relation(i) for i in entry.findall('relation')]
        self.etymology = Etymology(entry.find('etymology'))
        
    def _set_date_modified(self):
        date = datetime.utcnow().isoformat().split(".")[0] + "Z"
        self._entry.set('dateModified', date)
        self.dateModified = self._entry.get('dateModified') 
    
    def headword(self):
        """Returns headword of entry."""
        forms = self.lexical_unit.form
        if len(forms) == 0:
            return None
        elif len(forms) == 1:
            return forms[0].text
        else:
            return [form.text for form in forms]
            
    def pos(self):
        """Returns POS of entry."""
        senses = self.sense
        if len(senses) == 0:
            return None
        elif len(senses) == 1:
            return senses[0].grammatical_info.value
        else:
            return [sense.grammatical_info.value for sense in sense]
        
    # === Header elements ===

class Lift(XMLCorpusReader):
    """Models LIFT object."""
    def __init__(self, root, fileid):
        XMLCorpusReader.__init__(self, root, fileid)
        self._fileid = self._fileids[0]
        elt = self.xml()
        self.version = float(elt.get('version'))
        self.producer = elt.get('producer')
        self.header = Header(elt.find('header'))
        self.entries = [Entry(i) for i in elt.findall('entry')] 
        
    def summary(self):
        print("Basic facts about", self._fileid)
        len_of_asterisks = 18 + len(self._fileid)
        print("*"*len_of_asterisks)
        num_of_entries = len(self.entries)
        print("Number of entries:", num_of_entries, "\n")
    
class Header:
    """Models header in LIFT."""
    def __init__(self, element):
        self.description = Multitext(element.find('description'))
        self.ranges = Ranges(element.find('ranges'))
        self.fields = Field_Defns(element.find('fields'))
        
class Ranges:
    """Models ranges in LIFT."""
    def __init__(self, element):
        if element:
            self.range = [Range(i) for i in element.findall('range')]
    
class Range:
    """Models range in LIFT."""
    def __init__(self, element):
        if element:
            self.id = element.get('id')
            self.guid = element.get('guid')
            self.href = element.get('href')
            self.description = [Multitext(i) for i in element.findall('description')]
            self.range = Range_Element(element.find('range-element'))
            self.label = [Multitext(i) for i in element.findall('label')]
            self.abbrev = [Multitext(i) for i in element.findall('abbrev')]
           
class Range_Element:
    """Models range-element in LIFT."""
    def __init__(self, element):
        if element:
            self.id = element.get('id')
            self.parent = element.get('parent')
            self.guid = element.get('guid')
            self.label = [Multitext(i) for i in element.findall('label')]
            self.description = [Multitext(i) for i in element.findall('description')]
            self.abbrev = [Multitext(i) for i in element.findall('abbrev')]
            
class Field_Defns:
    """Models fields-defns in LIFT."""
    def __init__(self, element):
         if element:
             self.field = [Field(i) for i in element.findall('field')]

class Field_Defn(Multitext):
    """Models fields-defns in LIFT.""" 
    def __init__(self, element):
        if element:
            Multitext.__init__(self, element)
            self.tag = element.get('tag')

        






















 
        

      
        
        
        
        
        
# === FLExtext elements ===      
        
class Text(XMLCorpusReader):
    """Corpus reader for FLEx's flextext files.

    For access to the complete XML data structure, use the ``xml()``
    method.  For access to simple word lists, use
    ``words()``, ``sents()``.
    """
    def __init__(self, root, fileid):
        XMLCorpusReader.__init__(self, root, fileid)
        self._fileid = fileid