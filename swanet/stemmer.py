#!/usr/bin/env python

""" Stemming Algorithm
This is the stemming algorithm, 
An algorithm for SWAHILI prefix and suffix stripping, providing you with the core componets of a word in Swahili,
giving you the stem of the word, the English phrase of the word in a dictionary

bavin2009@gmail.com

The code was contribute by:
    1.ondieki (bavin2009@gmail.com)
    2.jimreesman Jim Reesman 

from https://github.com/ondieki/swahili/blob/master/Stemmer.py

"""

# import en
import sys
import string
import re
from collections import defaultdict

class Stemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.FTense = None
        self.j = 0   # j is a general offset into the string
        self.RESULT = defaultdict(lambda:[])
        self.DICT = defaultdict(lambda:'')

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        return 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def starts(self,s):
        """starts(s) is TRUE <=> k0...k starts with string s"""
        if(self.b.find(s, 0, len(s)) != -1):
            return True;
        else:
            return False;

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.
           walipikia  -> alipik~
           walipikiana ->  walipik
           walichukuliwa -> walichuku
           pikia      ->  pik
           pangiwa    ->  pang 

           #CASES
           pigiliwa
        """

        self.KEY = self.b

        if(len(self.b) > 4 and self.ends("kuwa")):
            J= len(self.b)
            self.b = self.b[0:J]
            self.k = J
        else:
            if self.b[self.k] == 'a':
                if self.ends("eshwa"):
                    self.RESULT[self.KEY].append("made to be")
                    self.k = self.k - 5
                if self.ends("lia"):
                    self.k = self.k - 3
                elif self.ends("liana"):
                    self.RESULT[self.KEY].append("on behalf of each other")
                    self.k = self.k - 5
                elif self.ends("eana") or self.ends("iana"):
                    self.k = self.k - 4
                    self.RESULT[self.KEY].append("at each other")
                elif self.ends("iliwa"):
                    self.k = self.k - 5
                elif self.ends("liwa"):
                    self.k = self.k - 4
                elif self.ends("iwa"):
                    self.k = self.k - 3
                elif self.ends("jika") or self.ends("lika"):
                    self.k = self.k - 3  #hitajika = hitaj, #kamilika = kamil
                elif self.ends("ana"):
                    self.k = self.k - 3
                    self.RESULT[self.KEY].append("each other")
                elif self.ends("ia"):
                    self.k = self.k - 2
                    self.RESULT[self.KEY].append("for")
                elif self.ends("a") and self.cons(self.k - 1):
                    self.k = self.k - 1

                self.b = self.b[0:self.k+1]
            
    def step1c(self):
        """step1c() Get rid of prefix complex Noun+verb, stripping off the propoun,tense,and object, leaving stem and suffix"""
        p = re.compile('(ni|u|a|tu|m|mu|wa|i|li|ya|ki|vi|zi|ku|pa)(li|ta|na)?[a-z]{4}')
        sol = p.match(self.b)
        if(not sol):    #this ones checks to see if word is a verb so we can stem it if it's a verb
            return False
        else: return True;
        

    def STO(self,token, K):

        if token == "kuwa": return "were|will be|was"

        if K == 0:
            #Subject Tokens
            if token == "ku": return "to"
            if token == "wa": return "they"
            if token == "ni": return "me"
            if token == "tu": return "us"
            if token == "mu":  return "you"
            if token == "u" : return "you"
            if token == "a": return "he"
            if token == "i": return "it"
            if token == "li": return "it" 
            if token == "ya": 
                #self.FTense = 'PT'
                return "have"


        if K == 1:
            #Time Tokens
            if token == "li": return "did,"      #"PT" #PAST TENSE
            if token == "na": return "is,"     #PRESENT TENSE
            if token == "ta": return "will,"   #FUTURE TENSE
            if token == "ki": return "while,"   #"PT-CT|PR-CT"
            if token == "mu": return "him,"
            if token == "me": return "has,"
            if token == "wa": return "them,"


        if K == 2:
            #Object Tokens
            if token == "m": return "him"
            if token == "wa": return "them"
            if token == "tu": return "us"
            if token == "ni": return "me"
            if token == "ki": return "it"

    def step2(self):
        """step2() checks to see the various prefixes
           #this checks to remove the first tokens that are for the Subject, Verb, Object. 
           #What remains is the root of the verb
        """
        p = re.compile('(ni|u|a|tu|m|wa|i|li|ya|ki|vi|zi|ku|pa)(li|ta|na)(o)?[a-z]{3}')
        p2 = re.compile('(ni|u|a|tu|m|wa|i|li|ya|ki|vi|zi|ku|pa)(me|li|ta|na)?(ni|tu|ku|mu|wa|cho)?[a-z]{2}')

        #regex 3 = (ni|u|a|tu|m|wa|i|li|ya|ki|vi|zi|ku|pa)(li|ta|na)(ni|tu|ku|mu|wa|cho)?[a-z]{4}
        
        original = self.b

        #storing tense of the action, to be converted in phrase
        TENSE = None

        #store the tokens here, which will be put together
        RESULT = []
        sol = p2.findall(self.b)
        T = list(map(list, sol))

        if len(T) > 0: 
            L = T[0]

        newL = []

        #Remove spaces in matching result
        for j in range(len(L)):
            t = L[j]
            if len(t) > 0:
                newL.append(t)
        
        L = newL
        
        #Now construct english phrase using dictionary and STO Lookup function above
        for i in range(len(L)):
            tok = L[i]
            if i == 1:
                w = self.STO(tok,i)
                w = w.split(',')
                TENSE = w[1]

            K = len(tok)
            if self.b == "kuwa": 
                RESULT.append(self.STO(self.b,i))
                break;
            if K > 0:
                RESULT.append(self.STO(tok,i)) #process the subject, tense and object
                self.b = self.b[K:]

        lemma = ''

        #remove any odd spaces around the stem
        self.b = self.b.strip()

        # print 'self.b',self.b
        # print 'self.KEY',self.KEY
    
        #if stemmed word not in dict, just extend stem as I may have accidentally chopped it off
        if(self.b not in self.DICT):
            FOUND = self.KEY.index(self.b)
            if(FOUND): 
                text = self.KEY[FOUND:]
                lemma = text
        else:
            lemma = self.DICT[self.b]
            
        # print 'lemma:',lemma
        #lemma = lemma[0].split(' ')[0]
              
        #keep track if the lemma is transformed and added so we don't add twice
        ADDED = 0

        #convert tense of english version of lemma at this point    
        if TENSE != None or self.FTense != None:
            if TENSE == 'PT' or self.FTense == 'PT':
                try:
                    lemma = en.verb.past(lemma)
                    ADDED = 1
                    RESULT.append(lemma)
                except:
                    pass
        elif TENSE == 'PR':
                try:
                    lemma = en.verb.present(lemma)
                    ADDED = 1
                    RESULT.append(lemma)
                except:
                    pass
         
        #Used with Nodebox English Engine to get Verb Tense
        self.FTense = None

        #Join to form phrase, ignoring the comma used for storing the Tense of Verb
        phrase = ' '.join(RESULT)
    
        phrase = phrase.split(',')[0]
        if(ADDED == 0):
            phrase +=' '+ lemma
    
       # if lemma == "throw": 
            #print lemma, " <=++++++++++++++ Lemma and Phrase +++++++++++=>", phrase
            #sys.exit()
        #If I have a suffix, I have some knowledge on objects at which action is directed
        
        OBJECTS = ''
        if len(self.RESULT[self.KEY]) == 1:
            OBJECTS == self.RESULT[self.KEY][0]
            self.RESULT[self.KEY] = []


        #print " self.RESULT[self.KEY]########", self.RESULT[self.KEY]

        #print lemma, " <=++++++++++++++ Lemma and Result +++++++++++^^^2 =>" ,RESULT, "\n <== PHRASE ==> ",phrase
    
        #Append this to a dictionary, with key as original word, value as the phrase   
        self.RESULT[self.KEY].append(lemma) #store stem in first index
        self.RESULT[self.KEY].append(phrase) #store result as a list whose key is the original word in sentence
       
    def stem(self, p, i=None, j=None):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # print 'stemming...',p
        if i is None:
            i = 0
        if j is None:
            j = len(p) - 1
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b 

        K = 0
        
        if(self.step1c()):
            K = 1
            self.step1ab() #only stem the verb form words rather than nouns
       
        #If complex V+N, stem the prefix in order to parse the complex verb+Noun
        if(K): 
            self.step2()

        return self.b[self.k0:self.k+1]
    
    def input(self, line):
        p = self
        word = line[0]
        output = ''
        output += p.stem(word, 0,len(word)-1)
        if len(self.RESULT[word]) == 2 : 
            return self.RESULT[word][1].split(' ')[-1]
        else: return None

