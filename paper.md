### Abstract
This paper describes two new modules to the Natural Language Toolkit, a collection of software supporting computational linguistics. The first module, flex, is a corpus reader for FLEx lexicons and texts. This new module allows linguists to manipulate their data in much more powerful ways, including querying by tonal pattern, working with an unstandardized or evolving orthography, and annotating whole sentences. The second module, aline, is a port of Kondrak’s (2002) ALINE, an algorithm for computing optimal alignments in phonetic sequences. Sequence alignment is a necessary step in any form of sequence comparison, which itself is a common task in historical linguistics, sociolinguistics and synchronic phonology. These two new modules provide easy to use open source tools for ready incorporation into linguists’ workflows. Use cases are illustrated with data from Tswefap, an Eastern Grassfields language from Cameroon.


###Introduction (1 page)
* Introduce goals of paper (two tools for linguists)
* Brief background on NLTK

###Flex (14 pages)
* Motivation
* Workflow
* Use cases (Tswefap) and overview of code
  * Get Flex output into Python/NLTK
  * Report missing/duplicate data
  * Global orthography change
  * Support for tone
  * Dialect, orthography, fuzzy search
  * Create csv wordlist from multiple flex files
  * Add CV layer

###Aline (14 pages)
* Introduction
* Motivation
* A tool for linguists, not replacing them
* Background on sequence alignment
* How ALINE works
* Overview of implementation
* Use cases (Tswefap)
* Evaluate/replicate known results

###Summary (1 page)
