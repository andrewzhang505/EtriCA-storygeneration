import json
from phonemizer.separator import Separator
from phonemizer.backend import FestivalBackend, EspeakBackend
import re

from nltk.corpus import wordnet

class RhymeAugmenter:
    def __init__(self, n_jobs = 4):
        self.festival = FestivalBackend('en-us')
        self.sep = Separator(phone="-", word=' ', syllable='|')
        self.n_jobs = n_jobs  
    
    def eval(self, w1, w2):
        syn = self.synonyms(w2)
        phomenes = self.phonemes([w1] + syn)
        
        for i, w in enumerate(phomenes[1:]):
            if self.check_rhyme(phomenes[0], w):
                return syn[i]
        return w2

    def synonyms(self, w):
        synonyms = set()
        for syn in wordnet.synsets(w):
            for l in syn.lemmas():
                synonyms.add(" ".join(l.name().split("_")))
        return list(synonyms)

    # Get phonemes for list of strings using specified encoder
    def phonemes(self, data):
        return self.festival.phonemize(data, separator=self.sep, strip=True, njobs = self.n_jobs)

    # Check if two pairs of lines rhyme
    def check_rhyme(self, phone1, phone2):
        p1 = phone1.split("-")
        p2 = phone2.split("-")

        if len(p1) < len(p2):
            return p1[1:] == p2[len(p2)-len(p1)+1:]
        else:
            return p1[len(p1)-len(p2)+1:] == p2[1:]
    
    

