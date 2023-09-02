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
Nouns           236             347             277
Verbs           266             367             330
Adjectives      5               2               2
Adverbs         0               0               0

```

To query for a synset (it finds all the word that relates with the provided word and returns the results as a list of objects)

```python
syn = sw.synset()
print(syn)

```
Expected output

```python
[Synset(kitu.n.4), Synset(kitu.n.2), Synset(kitu.n.3), Synset(kitu.n.1)]

```
Select any of the synsets above to query its synonym, you can also use Swahili words to make query such as visawe in place of synonyms

```python
#English and Swahili quering
print("=======single object results===========")
print(syn[0].synonym, syn[0].visawe) #get synonym for object at index 0

print("=======loop results====================")
for synobj in syn: #loop through to get synset of all object
    print(synobj.synonym)
```
Expected output 

```python
=======single object results======================
[Synset(kitu chake.n.1)] [Synset(kitu chake.n.1)]

=======loop results===============================
[Synset(kitu chake.n.1)]
[]
[]
[]
```
To get the hypernym of an object, we do the same as above, rather than accessing the synonym we access the hypernyms. Let's get the hypernym of the last index.
We can also access it using swahili, hipanimu 

```python
print(sw[-1].hypernyms, sw[-1].hipanimu) #get hypernym for object in the last index
```
Expected output

```python
Synset(kitu kamili.n.1) Synset(kitu kamili.n.1)
```
To get other relations such as hyponyms either in Swahili or English access, see the table below:

| English | Swahili |
| --- | --- |
| hyponyms | hiponimu |
| synonym  | visawe |
| hypernyms|hipanimu |
| noun_class  | ngeli |
| plural  | wingi |
| definition  | maana |
| usage  | mfano |
| lemma  | _ |
