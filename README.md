# Swahili wordnet python library

A library for using the Swahili Wordnet (also known as Swanet) - a lexico-semantic database of the Swahili language.

This library was created because Swahili Wordnet (developed using DebVisc 'XML file format') cannot directly be loaded from the NLTK library and there was a need for faster prototyping and viewing
of synsets in Python as development continues. 

Currently, the library supports viewing synonyms (Visawe), hypernyms, hyponyms, Noun class (Ngeli) and getting root words.

# Usage

Load wordnet from an XML file (there is a local file passed as a default argument), and it prints basic statistics.

```python
import wordnet

sw = wordent.load()

````
Expected results NB(The number of synsets will continue growing)

```python
#Pos           #synsets        #word senses    #words
Nouns           210             311             256
Verbs           48              121             101
Adjectives      3               1               1
Adverbs         0               0               0

```

To query for a synset (finds all the word that relates with the provided word and returns the results as a list of objects)

```python
syn = sw.synset()
print(syn)

```
Expected output

```python
[Synset(kitu.n.4), Synset(kitu.n.2), Synset(kitu.n.3), Synset(kitu.n.1)]

```
Select any of the synsets above to query its synonym

```python
print("=======single object results===========")
print (sw[0].synonym) #get synonym for object in index 0

print("=======loop results====================")
for synobj in sw: #loop through to get synset of all object
    print(synobj.synonym)
```
Expected output 

```python
=======single object results=====
[Synset(kitu chake.n.1)]

=======loop results==============
[Synset(kitu chake.n.1)]
[]
[]
[]
```
To get the hypernym of an object, we do the same as above, rather than accessing the synonym we access the hypernyms. Let's get the hypernym of the last index.

```python
print (sw[-1].synonym) #get hypernym for object in the last index
```
Expected output

```python
Synset(kitu kamili.n.1)
```

