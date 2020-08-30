import pytest
  
from iqa.nlp import search 
import pandas as pd

def test_search(nlu_obj):
    data=['dog','cat','ant']
    term = 'canines'
    embeddings =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/teses_dict_embeddings.p','rb'))
    embed = SentenceTransformer('distiluse-base-multilingual-cased')
    assert type(r1)==np.ndarray
    assert type(r2)==np.ndarray
    results = search.semantic_search(term,data,embeddings,embed)
    assert len(results['results'])==3
    assert type(results['results'])==list

def test_fail_search(nlu_obj):
    data=['dog','cat','ant']
    term = ''
    embeddings =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/teses_dict_embeddings.p','rb'))
    embed = SentenceTransformer('distiluse-base-multilingual-cased')
    
    results = search.semantic_search(term,data,embeddings,embed)
    assert len(results['results'])==3
    assert type(results['results'])==list


