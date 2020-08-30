"""
Módulo responsável pela construção de inverted_index.
"""
import nltk
from collections import defaultdict
from nltk.stem.snowball import EnglishStemmer  # Assuming we're working with English
import pickle
import os

nltk.download("stopwords")
nltk.download("punkt")



class Index:
    """ Inverted index datastructure """

    def __init__(self, tokenizer=None, stemmer=None, stopwords=None):
        """
        Parameters
        ----------
        tokenizer : None
            NLTK compatible tokenizer function
        stemmer : None
            NLTK compatible stemmer
        stopwords : list
            list of ignored words
        """
        self.tokenizer = nltk.word_tokenize
        self.stemmer = EnglishStemmer()
        self.index = defaultdict(list)
        self.documents = {}
        self.__unique_id = 0
        if not stopwords:
            self.stopwords = set()
        else:
            self.stopwords = set(nltk.corpus.stopwords.words("english"))

    def lookup(self, word: str):
        """
        Lookup a word in the index

        Parameters
        ----------
        word : str
            words
        """
        word = word.lower()
        if self.stemmer:
            word = self.stemmer.stem(word)

        return [self.documents.get(id, None) for id in self.index.get(word)]

    def add(self, document):
        """
        Add a document string to the index

        Parameters
        ----------
        document : str
            document

        """
        for token in [t.lower() for t in nltk.word_tokenize(document)]:
            if token in self.stopwords:
                continue

            if self.stemmer:
                token = self.stemmer.stem(token)

            if self.__unique_id not in self.index[token]:
                self.index[token].append(self.__unique_id)

        self.documents[self.__unique_id] = document
        self.__unique_id += 1


import pickle
p=pickle.load(open("models/inv_index_teses.p",'rb'))
pickle.dump(p,open('models/inv_index_teses.p','wb'))
print(p)
