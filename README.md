# Swahili wordnet python library

A library for using the Swahili Wordnet (also known as Swanet) - a lexico-semantic database of the Swahili language.

This library was created because Swahili Wordnet (developed using DebVisc 'XML file format') cannot directly be loaded from the NLTK library and there was a need for faster prototyping and viewing
of synsets in Python as development continues. 

Currently, the library supports viewing synonyms (Visawe), hypernyms, hyponyms, Noun class (Ngeli) and getting root words.

# Usage

```python
import wordnet

Load wordnet from an XML file (there is a local file passed as a default argument), and it prints basic statistcs.

sw = wordent.load()

````
