"""
Este módulo realiza o tratamento dos dados enviados pelo usuário. Utilizamos
o framework RASA NLU para extração de entidades e relacionamentos.
"""
import pathlib
import os
import pickle
import numpy as np
import pandas as pd
from typing import List
from pyQualis import Search
from pandas import DataFrame
#import tensorflow_text
#import tensorflow_hub as hub
from rasa.nlu.model import Interpreter
import json
import nltk
from collections import defaultdict
from nltk.stem.snowball import EnglishStemmer  # Assuming we're working with English
import pickle
import os
import shelve
from .inv_index import Index 
import unicodedata
import difflib
from sentence_transformers import SentenceTransformer
from datetime import datetime
from .utils import *
from .show import process_show
from .query import process_query
from .filter import process_filter
from .search import semantic_search


_ROOT = pathlib.Path(__file__).parent.parent.absolute()
class NLU:
    """
    Nesta classe realizamos o tratamento dos dados enviados pelo usuário, tais como
    identificação de entidades e relacionamentos via o framework RASA NLU.
    """

    def __init__(self, event="quadriênio"):
        """
        Nesta classe são carregadas os dados dos artigos, revistas e teses/dissertações, os modelos de embeddings 

        """
        self.embeddings={}
        self.qualis_search = Search()
        self.embed = SentenceTransformer('distiluse-base-multilingual-cased')

        # Had to extract the tar.gz model file before running this code
        self._interpreter = Interpreter.load(
            #os.path.join(_ROOT, "models/20200612-221138/nlu")
            os.path.join(_ROOT, "models/nlu")
        )
        
        #load revista data 
        self.qualis_table = self.qualis_search.get_table(event=event)
        revistas_names = get_prod_stripped_names(self.qualis_table,column_name="Título")
        self.qualis_table['names'] =revistas_names 
        self.embeddings['revistas'] =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/revistas_dict_embeddings.p','rb'))

        print(os.path.join(_ROOT, "models/inverted_indexes.b"))
        self._inverted_indexes = pickle.load(
          open(os.path.join(_ROOT, "models/inverted_indexes.b"), "rb")
        )
        self._count_vect = pickle.load(
            open(os.path.join(_ROOT, "models/count_vect.b"), "rb")
        )
        self._codes2Name = pickle.load(
            open(os.path.join(_ROOT, "models/codes2Name.b"), "rb")
        )
        self._area_names = pickle.load(open("/home/navi1921/QASucupira-API/iqa/models/journal_area_names.p", "rb"))

        
        #load teses data
        print('loading teses data...')
        self._inv_index_teses = pickle.load(open("/home/navi1921/QASucupira-API/iqa/data/teses_inv_indexes.p", "rb"))
        self.embeddings['teses'] =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/teses_dict_embeddings.p','rb'))

        df1 = pd.read_csv("/home/navi1921/QASucupira-API/iqa/data/br-capes-btd-2017-2018-08-01_2017.csv", sep=";", encoding="ISO-8859-1")
        df2 = pd.read_csv("/home/navi1921/QASucupira-API/iqa/data/br-capes-btd-2018-2019-09-09_2018.csv", sep=";", encoding="ISO-8859-1")
        self.data_teses = pd.concat([df1,df2])
        df1=[]
        df2=[]
        teses_names = get_prod_stripped_names(self.data_teses)
        self.data_teses['names'] = teses_names


        #load artigos data
        print('loading artigos data...')
        self.embeddings['artigos'] =pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/artigos_dict_embeddings.p','rb'))

        df1 = pd.read_csv('/home/navi1921/QASucupira-API/iqa/data/br-capes-colsucup-producao-2017a2020-2020-06-30-bibliografica-artpe.csv',encoding  = 'latin',sep=';')
        df2 = pd.read_csv('/home/navi1921/QASucupira-API/iqa/data/br-capes-colsucup-producao-2017a2018-2019-08-07-bibliografica-anais.csv',encoding  = 'latin',sep=';')

        self.data_artigos = pd.concat([df1,df2])
        df1=[]
        df2=[]
        artigos_names = get_prod_stripped_names(self.data_artigos)
        self.data_artigos['names'] = artigos_names


        #self.get_response('artigos da área de computação')
        #self.get_response('teses da área de computação')
        #self.get_response('teses da área de computação sobre o termo epilepsia')
        #data=self.get_response('filtre pela palavra-chave EEG')
        #data=self.get_response('filtre pela faculdade da USP')
        #data=self.get_response('filtre pela Pontificia universidade catolica')
        #data=self.get_response('filtre pelo orientador Sergio')
        #data=self.get_response('me mostre a universidade desse 1')
        #print('filter results: ',data)
        self.get_response('Quais os artigos de computação com o termo inteligência artificial?')

        #dataframe_results=self.get_artigos('evolucao',self.data_artigos,self.artigos_embeddings_shelf)
        #print(dataframe_results["NM_PRODUCAO"])

        
    def get_response(self, text: str) -> DataFrame:
        """Obtém a resposta de acordo com a pergunta.

        Dado uma pergunta, nesta função iremos consultar a nossa
        base de dados e se algum resultado por encontrado, este será
        retornado pela função.

        Parameters
        ----------
        text : str
            Pergunta informada pelo usuário.

        Returns
        --------
        DataFrame
            Tabela contendo todos os resultados encontrados.
        """
        # extrair entidades e intenções
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

        text = strip_accents(text).lower()
        text = text.replace('.','')
        text = text.replace(',','')
        text = text.replace("'",'')
        text = text.replace('"','')
        rasa_nlu = self._interpreter.parse(text)
        print(rasa_nlu)
        #intent = rasa_nlu['intent']
        #print(intent)
        entities = rasa_nlu["entities"]
        intent = rasa_nlu["intent"]
        if(intent['name'] == 'query'):
            results = process_query(entities,self.qualis_table,self.data_artigos,self.data_teses,self.embeddings,self.embed,self._codes2Name)
            self.last_data =results[1] 
            self.last_question_type = results[2]
            results[0]['results']=results[0]['results'].to_dict()
            return results[0]
        elif(intent['name'] == 'show'):
            results = process_show(entities,self.last_data,self.last_question_type)
            results['results']=results['results'].to_dict()
            return results

        elif(intent['name'] == 'filter'):
            results = process_filter(entities,self.last_data,self.last_question_type)
            results['results']=results['results'].to_dict()
            return results

        else:
            results = {
                "text": "Desculpe, não entendi sua pergunta"
               
                }

        #print(results)
       # print(len(results['results']))

        return results
    
