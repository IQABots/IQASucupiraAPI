import pytest
  
from iqa.nlp import search 
import pandas as pd

def test_search(nlu_obj):
    results = nlu_obj.get_response('teses da area de computaçao')
    #print(results)
    
    rasa_entities = nlu_obj._interpreter.parse('me mostre o autor do 1')
    entities = rasa_entities['entities']
    df = pd.DataFrame({'NM_DISCENTE':['a','b','c']})
    results = search.semantic_search(term,data,embeddings,embed)
    assert len(results['results'])==1

def test_fail_search(nlu_obj):
    results = nlu_obj.get_response('teses da area de computaçao')
    #print(results)
    rasa_entities = nlu_obj._interpreter.parse('me mostre o autor do 10')
    entities = rasa_entities['entities']
    df = pd.DataFrame({'NM_DISCENTE':['a','b','c']})
    results = search.semantic_search(term,data,embeddings,embed)

    assert len(results['results'])==0

