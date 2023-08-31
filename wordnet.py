""""
    'synonyms':'visawe',
    'antonyms':'kinyume',
    'hypernym':'',
    'hyponym':'vipengele',
    'noun_class':'ngeli',
    'plural':'wingi',
"""


import gc
import re
import copy
import lzma
import gzip
import bz2
from collections import defaultdict
from dataclasses import dataclass
from lxml import etree
from stemmer import Stemmer


@dataclass
class Synsetobj:
    """Hold synsets attributes"""
    Id:int
    word:list
    ngeli:str
    plural:str
    lemma:str
    definition:str
    usage:list
    synonym:list
    hyponyms:list=None
    hypernyms:list=None

    def __repr__(self):
        return f"Synset({self.word})"
    def __str__(self):
        return f"Synset({self.word})"

    def set_hypernym(self, hId, hword, hngeli, hplural, hlemma, hdefinition, husage, synonym):
        """creates hypernym object"""
        self.hypernyms = Synsetobj(hId, hword, hngeli, hplural,
                        hlemma, hdefinition, husage,synonym)

    def set_hyponym(self, hId, hword, hngeli, hplural, hlemma, hdefinition, husage, synonym):
        """creates hyponym object"""
        self.hyponyms = Synsetobj(hId, hword, hngeli, hplural,
                        hlemma, hdefinition, husage,synonym)
        #self.hyponyms.append(self.hyponym)
        
class Wordnet:
    """loads query synset, and find
        general statistics of the provided
        wordnet
    """
    def __init__(self):
        self.root = None
        self.results = defaultdict(list)
        self.hypernyms = defaultdict(list)
        self.hyponyms = defaultdict(list)
        self.total_words =[]

    def load(self, file):
        """ create a parse to the file and
            calls summary function
        """
        tree = etree.parse(file)
        self.root = tree.getroot()
        self.summary()

    def find(self, word, pos):
        """
        finds all the synset that matches the qiven word
        if a part of speech was given, first check if its
        available in the allowed list of pos i.e
        ['n', 'a', 'v', 'b'], if the pos is not available
        the query returns all the availabel pos that matches
        the query word
        """
        search =f"SYNSET/SYNONYM/LITERAL/[.='{word}']"
        
        try:
            for value in self.root.findall(search):
                sn_parent = value.getparent()
                synset_parent  = sn_parent.getparent()
                if pos is not None:
                    if pos in ['n', 'a', 'v', 'b']:
                        try:
                            synset_parent = synset_parent.find(f"POS/[.='{pos}']").getparent()
                        except AttributeError:
                            print(f'No synset with pos={pos}\nreturning results on available word')
                self.get_details(synset_parent, value, self.results)
                self.get_relations(synset_parent)
                if len(self.hypernyms['SYN']) ==0:
                    xh = defaultdict(list)
                else:
                    xh = self.hypernyms
                self.results['hypernyms'].append(xh)
                self.get_hyponyms(synset_parent)
        except Exception as e:
            print(f'word {word} -> Error: {e}')
            raise
            
        return self.results

    def get_relations(self, synset_parent):
        """
        get relations ie hypernym of the specified sysnsets
        """
        for child in synset_parent:
            if child.tag =='ILR':
                if child.get('type') == 'hypernym':
                    Id = child.text
                    search = f"SYNSET/ID/[.='{Id}']" #get Element
                    for value in self.root.findall(search):
                        sn_parent = value.getparent()
                        self.get_details(sn_parent, value, self.hypernyms)

    def get_hyponyms(self, synset_parent):
        for child in synset_parent.getchildren():
            if child.tag == 'ID':
                search = f"SYNSET/ILR/[.='{child.text}']"
                for value in self.root.findall(search):
                    sn_parent = value.getparent()
                    self.get_details(sn_parent, value, self.hyponyms)
                        
    def synset(self, word, pos=None):
        """
        get synset
        """
        final_res = []
        self.find(word, pos=pos)
        #self.hypernyms.clear()
        for index in range(0, len(self.results['SYN'])):
            words = check_string(self.results['SYN'][index]) + '.' + check_string(self.results['POS'][index]) + '.' + check_string(self.results['SENSE'][index])

            s1, s2 = self.check_ngeli(index, results=self.results)

            syns = Synsetobj(Id=self.results['ID'][index],
                             word=words,
                             usage=self.results['USAGE'][index],
                             ngeli=s1,
                             plural=s2,
                             lemma = self.get_lemma(self.results['SYN'][index]),
                             definition=self.results['DEF'][index],
                             synonym=None)

            new_obj=self.calc_synonym(syns, index, results=self.results)
            syns.synonym = new_obj
            self.hypernyms = self.results['hypernyms'][index]

            if len(self.hypernyms['SYN']) !=0:
                words = check_string(self.hypernyms['SYN'][0]) + '.' + check_string(self.hypernyms['POS'][0]) + '.' + check_string(self.hypernyms['SENSE'][0])
                s1, s2 = self.check_ngeli(index, results=self.hypernyms)

                syns.set_hypernym(hId=self.hypernyms['ID'][0],
                                  hword=words,
                                  husage=self.hypernyms['USAGE'][0],
                                  hngeli=s1,
                                  hplural=s2,
                                  hlemma = self.get_lemma(self.hypernyms['SYN'][0]),
                                  hdefinition=self.hypernyms['DEF'][0],
                                 synonym=None)
                new_hobj=self.calc_synonym(syns.hypernyms, 0, results=self.hypernyms)
                syns.hypernyms.synonym = new_hobj
            
            # self.hyponyms = self.results['hyponyms'][index] #get all hyponym for that word

            if len(self.hyponyms['SYN']) !=0:
                hyp = []
                for hindex in range(0, len(self.hyponyms['SYN'])):
                    words = check_string(self.hyponyms['SYN'][hindex]) + '.' + check_string(self.hyponyms['POS'][hindex]) + '.' + check_string(self.hyponyms['SENSE'][hindex])
                    s1, s2 = self.check_ngeli(hindex, self.hyponyms)

                    syns.set_hyponym(hId=self.hyponyms['ID'][hindex],
                                      hword=words,
                                      husage=self.hyponyms['USAGE'][hindex],
                                      hngeli=s1,
                                      hplural=s2,
                                      hlemma = self.get_lemma(self.hyponyms['SYN'][hindex]),
                                      hdefinition=self.hyponyms['DEF'][hindex],
                                     synonym=None)
                    new_hobj=self.calc_synonym(syns.hyponyms, hindex, results=self.hyponyms)
                    syns.hyponyms.synonym = new_hobj
                    hyp.append(syns.hyponyms)
                syns.hyponyms = hyp
            final_res.append(syns)
        self.results.clear()
        self.hypernyms.clear()
        self.hyponyms.clear()
        gc.collect()
        return final_res

    def check_ngeli(self, index, results, ctx=0):
        """
        separates noun class with the plural perfix
        """
        txt = None
        try:
            if len(results['NGELI'][index]) !=0:
                txt = results['NGELI'][index][ctx]
            s1, s2 = self.get_ngeli_plural(txt)
        except:
            s1, s2 = None, None
        return s1, s2

    def calc_synonym(self, obj, index, results):
        """extracts all the synonyms"""
        syn_obj = []
        pos = results['POS'][index]
        synonym = results['SYNOMYM'][index]

        for count, syn in enumerate(synonym.keys()):
            s1, s2 = self.check_ngeli(index, results=results, ctx=count+1)
            new_obj = copy.copy(obj)
            new_obj.word = syn + '.' + pos + '.' + synonym.get(syn)
            new_obj.ngeli = s1
            new_obj.wingi = s2
            syn_obj.append(new_obj)

        return syn_obj

    def get_details(self, parent, lt, hdict):
        """
        get synsets details such as usage, ID
        """
        ngeli = []
        for child in parent.getchildren():
            if child.tag == 'DEF':
                if child.text is not None:
                    hdict['DEF'].append(child.text)
                else:
                    hdict['DEF'].append('')
            elif child.tag == 'POS':
                hdict['POS'].append(child.text)
            elif child.tag == 'ID':
                hdict['ID'].append(child.text)
            elif child.tag == 'SYNONYM':
                self.get_synonym(child, lt, hdict)
            elif child.tag == 'SNOTE':
                ngeli.append(child.text)

        hdict['USAGE'].append(tuple([child.text for child in parent.getchildren() if child.tag == 'USAGE']))
        hdict['NGELI'].append(tuple(ngeli))
        return hdict

    def get_lemma(self, txt):
        """
        calls the stemmer class and finds the root word
        """
        if txt is not None:
            try:
                stem = Stemmer()
                res = stem.input([txt.strip()])
            except Exception:
                res = None
            if res is None:
                res = txt
        return txt

    def get_synonym(self, child, lt, hdict):
        """get synonym"""
        grand_child = child.getchildren()
        if lt.tag == 'ID':
            #get parent and pick the first grandchild and update the lt
            for great_gchild in grand_child:
                if great_gchild.tag == 'LITERAL':
                    lt = great_gchild
                    break
        elif lt.tag == 'ILR':
            #get parent and pick the first grandchild and update the lt
            for great_gchild in grand_child:
                if great_gchild.tag == 'LITERAL':
                    lt = great_gchild
                    break

        hdict['SYN'].append(lt.text)
        hdict['SENSE'].append(lt.get('sense'))

        res = {}
        for value in grand_child:
            if value.tag == 'LITERAL':
                if value != lt:
                    res.update({value.text:value.get('sense')})
        hdict['SYNOMYM'].append(res)

    def get_ngeli_plural(self, txt):
        """separates the noun class from the plural prefix"""
        sn1, sn2 = '', ''
        if txt is not None:
            snf = re.findall('\(+(.*?)\)',txt)
            if len(snf) == 1:
                sn1, sn2 = snf[0], ''
            elif len(snf)>1:
                sn1, sn2= snf[0], snf[1]
        return sn1, sn2

    def get_descendant(self):
        """get descendant"""
        words_n, words_a, words_v, words_b = [], [], [], []
        for descendant in self.root.iter():
            if descendant.tag == 'SYNSET':
                for child in descendant.getiterator():
                    if child.text == 'n':
                        words_n.append(descendant)

                    elif child.text == 'a':
                        words_a.append(descendant)

                    elif child.text == 'v':
                        words_v.append(descendant)

                    elif child.text == 'b':
                        words_b.append(descendant)
        return words_n, words_a, words_v, words_b

    def get_total_synsets(self, syn_list):
        """get the total number of synsets"""
        words = []
        for syn in syn_list:
            for child in syn.getiterator():
                if child.tag == 'SYNONYM':
                    for grandchild in child.getchildren():
                        if grandchild.tag == 'LITERAL':
                            words.append(grandchild.text)
        return words

    def summary(self):
        """generates summary of the wordent"""
        words_n, words_a, words_v, words_b = self.get_descendant()
        noun = self.get_total_synsets(words_n)
        verb = self.get_total_synsets(words_v)
        adj = self.get_total_synsets(words_a)
        adv = self.get_total_synsets(words_b)

        self.total_words = noun + verb + adj + adv

        print("#poS\t\t#synsets\t#word senses\t#words")
        print(f"Nouns\t\t{len(words_n)}\t\t{len(noun)}\t\t{len(set(noun))}")
        print(f"Verbs\t\t{len(words_v)}\t\t{len(verb)}\t\t{len(set(verb))}")
        print(f"Adjectives\t{len(words_a)}\t\t{len(adj)}\t\t{len(set(adj))}")
        print(f"Adverbs\t\t{len(words_b)}\t\t{len(adv)}\t\t{len(set(adv))}")

def check_string(word):
    if word is None:
        word = '<Unk>'
    return word

def open_file(source):
    """
    open wordent in various format (supported format ) are:
        1.xz
        2.bz2
        3.gz
    the compressed file is assumed to be in DebVisdic format
    """
    if source.endswith('.xz'):
        file_w = lzma.open(source, 'rb')
    elif source.endswith('.bz2') or source.endswith('.bz2'):
        file_w = bz2.open(source, 'rb')
    elif source.endswith('.gz'):
        file_w = gzip.open(source, 'rb')
    else:
        file_w = open(source, 'rb')
    return file_w


def load(wordnet_src='corpus/v1wn_sw.xml'):
    """
    load the file into memory
    """
    wn_file = wordnet_src
    if isinstance(wn_file, str):
        wn_file = open_file(wn_file)

    wnt = Wordnet()
    wnt.load(wn_file)
    wn_file.close()
    return wnt
