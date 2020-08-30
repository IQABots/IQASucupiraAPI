import pytest
from iqa.nlp import utils
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
def test_get_area_name_correct():
    r=utils.get_area_name_correct('word',{41:'2'})
    assert type(r)==str

def test_terms_filter():
    r=utils.terms_filter('ciencia da computacao')
    assert type(r)==str


def test_strip_accents():
    r=utils.strip_accents('computação')
    assert type(r)==str

def test_filter_by_column():
    r=utils.filter_by_column(pd.DataFrame({'c1':['1','2'],'c2':['1','2']}),'c1' ,'1' )
    assert type(r)==pd.DataFrame

def test_prod_stripped_names():
    r=utils.get_prod_stripped_names(pd.DataFrame({'c1':['1','2'],'c2':['1','2']}),'c1' )
    assert type(r)==list


def test_sort_by_similarity():
    embeddings =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/teses_dict_embeddings.p','rb'))
    embed = SentenceTransformer('distiluse-base-multilingual-cased')
    names=['gatinho','cachorro','pato']
    embs=np.asarray(embed.encode(names)) 
    embs_dict={}
    for i in range(len(names)):
        embs_dict[names[i]] = embs[i]
    r1,r2 = utils.sort_by_similarity('gato',names,embs_dict,embed)
    assert type(r1)==np.ndarray
    assert type(r2)==np.ndarray
