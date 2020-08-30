import pytest
  
from iqa.nlp import query 
from iqa.utils import * 
import pandas as pd
from pyQualis import Search

def test_process_query(nlu_obj):
    rasa_entities = nlu_obj._interpreter.parse('teses da area de computacao')
    entities = rasa_entities['entities']
    embeddings =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/teses_dict_embeddings.p','rb'))
    embed = SentenceTransformer('distiluse-base-multilingual-cased')
    codes2Name = pickle.load(
            open("/home/navi1921/QASucupira-API/iqa/models/codes2Name.b","rb")
        )
    df1 = pd.read_csv("/home/navi1921/QASucupira-API/iqa/data/br-capes-btd-2017-2018-08-01_2017.csv", sep=";", encoding="ISO-8859-1")
    df2 = pd.read_csv("/home/navi1921/QASucupira-API/iqa/data/br-capes-btd-2018-2019-09-09_2018.csv", sep=";", encoding="ISO-8859-1")
    data_teses = pd.concat([df1,df2])
    df1 = pd.read_csv('/home/navi1921/QASucupira-API/iqa/data/br-capes-colsucup-producao-2017a2020-2020-06-30-bibliografica-artpe.csv',encoding  = 'latin',sep=';')
    df2 = pd.read_csv('/home/navi1921/QASucupira-API/iqa/data/br-capes-colsucup-producao-2017a2018-2019-08-07-bibliografica-anais.csv',encoding  = 'latin',sep=';')
    data_artigos = pd.concat([df1,df2])
    qualis_search = Search()
    #load revista data
    qualis_table = qualis_search.get_table(event=event)
    revistas_names = get_prod_stripped_names(qualis_table,column_name="Título")
    qualis_table['names'] =revistas_names


    results = process_query  
    results = query.process_query(rasa_entities,qualis_table,data_artigos,data_teses,embeddings,embed,codes2Name)

    assert type(results)==dict
    assert len(results['results'])>0

def test_fail_process_query(nlu_obj):
    rasa_entities = nlu_obj._interpreter.parse('sem pergunta')
    entities = rasa_entities['entities']
    embeddings =  pickle.load(open('/home/navi1921/QASucupira-API/iqa/embeddings/teses_dict_embeddings.p','rb'))
    embed = SentenceTransformer('distiluse-base-multilingual-cased')
    codes2Name = pickle.load(
            open("/home/navi1921/QASucupira-API/iqa/models/codes2Name.b","rb")
        )
    df1 = pd.read_csv("/home/navi1921/QASucupira-API/iqa/data/br-capes-btd-2017-2018-08-01_2017.csv", sep=";", encoding="ISO-8859-1")
    df2 = pd.read_csv("/home/navi1921/QASucupira-API/iqa/data/br-capes-btd-2018-2019-09-09_2018.csv", sep=";", encoding="ISO-8859-1")
    data_teses = pd.concat([df1,df2])
    df1 = pd.read_csv('/home/navi1921/QASucupira-API/iqa/data/br-capes-colsucup-producao-2017a2020-2020-06-30-bibliografica-artpe.csv',encoding  = 'latin',sep=';')
    df2 = pd.read_csv('/home/navi1921/QASucupira-API/iqa/data/br-capes-colsucup-producao-2017a2018-2019-08-07-bibliografica-anais.csv',encoding  = 'latin',sep=';')
    data_artigos = pd.concat([df1,df2])
    qualis_search = Search()
    #load revista data
    qualis_table = qualis_search.get_table(event=event)
    revistas_names = get_prod_stripped_names(qualis_table,column_name="Título")
    qualis_table['names'] =revistas_names


    results = process_query  
    results = query.process_query(rasa_entities,qualis_table,data_artigos,data_teses,embeddings,embed,codes2Name)

    assert type(results)==dict
    assert len(results['results'])==0


