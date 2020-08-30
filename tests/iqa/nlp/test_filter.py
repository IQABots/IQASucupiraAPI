import pytest

from iqa.nlp import show
import pandas as pd

def test_process_filter(nlu_obj):
    results = nlu_obj.get_response('teses da area de computaçao')
    #print(results)
    rasa_entities = nlu_obj._interpreter.parse('me filtre pela faculdade da puc')
    entities = rasa_entities['entities']
    df = pd.DataFrame({'NM_DISCENTE':['a','b','c']})
    results = show.process_show(entities,df,'teses')
    assert len(results['results'])==1 

def test_fail_process_filter(nlu_obj):
    results = nlu_obj.get_response('teses da area de computaçao')
    #print(results)
    rasa_entities = nlu_obj._interpreter.parse('me filtre pela faculdade da puc')
    entities = rasa_entities['entities']
    df = pd.DataFrame({'NM_DISCENTE':['a','b','c']})
    results = show.process_show(entities,df,'teses')

    assert len(results['results'])==0 

