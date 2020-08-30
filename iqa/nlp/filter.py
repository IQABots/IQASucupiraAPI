import pandas as pd
from .utils import *

def process_filter(entities,last_data,last_question_type):
    """
    O método faz a operação show, que recebe as entidades detectadas bem como o ultimo resultado e o tipo da ultima questão.
    
    Parameters
    ----------
    entities : list
                Lista das entidades detectadas na questão.
    last_data : pd.DataFrame
                Dados do ultimo resultado.
    last_question_type : str 
                Se a ultima questão perguntada foi de teses,artigos ou revistas
    
    Returns
    -------
    dict
        dicionario com os dados de resultado.
    """


    available_attrs = []
    if last_question_type=='teses':
        available_attrs = ['uni','keyword','prof']
    elif last_question_type=='artigos':
        available_attrs = ['uni','periodicos','anais']
    elif last_question_type=='revistas':
        available_attrs = ['qualis']


    print('intent filter!!')
    print('available attrs:',available_attrs)
    df = last_data
    print(df)
    return_data={}
    if(len(df)>0):
        print('filtering results...')
        print('entities: ',entities)
        dict_ents = {}
        for ent in entities:
            dict_ents[ent['entity']]=ent['value']

        print('dict entities: ',dict_ents)
        #checar os prefixos
        has_filter = False
        if({"termo", "teses","mono"} <= dict_ents.keys()):
            if('science_terms' in dict_ents):
                val = dict_ents['science_terms']

        if('uni' in dict_ents and 'uni' in available_attrs):
            if('unis_names' in dict_ents):
                val = dict_ents['unis_names']
                field = 'NM_ENTIDADE_ENSINO'
                has_filter = True

            if('unis_siglas' in dict_ents):
                val = dict_ents['unis_siglas']
                field = 'SG_ENTIDADE_ENSINO'
                has_filter = True

        if('keyword' in dict_ents and 'keyword' in available_attrs):
            if('science_terms' in dict_ents):
                val = dict_ents['science_terms']
                field = 'DS_PALAVRA_CHAVE'
                has_filter = True

        if('prof' in dict_ents and 'prof' in available_attrs):
            if('names' in dict_ents):
                val = dict_ents['names']
                field = 'NM_ORIENTADOR'
                has_filter = True

        if('periodicos' in dict_ents and 'periodicos' in available_attrs):
            val = dict_ents['periodicos']
            data=df.loc[df['NM_SUBTIPO_PRODUCAO']=='ARTIGO EM PERIÓDICO']
            return {
                "text": "Resultados filtrados:",
                "results":data[["NM_PRODUCAO"]],
            }

        if('anais' in dict_ents and 'anais' in available_attrs):
            val = dict_ents['anais']
            data=df.loc[df['NM_SUBTIPO_PRODUCAO']=='TRABALHO EM ANAIS']
            return {
                "text": "Resultados filtrados:",
                "results":data[["NM_PRODUCAO"]],
            }

        if('qualis' in dict_ents and 'qualis' in available_attrs):
            if('qualis_term' in dict_ents):
                val = dict_ents['qualis_term']
                data=df[df['Estrato'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.contains(val,case=False,na=False)]
                #print('results data:',data)
                return {
                    "text": "Resultados filtrados:",
                    "results":data,
                }

        if(has_filter):
            print(df[field].head())
            print('filtering and returning...')
            print(val)

            data=df[df[field].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.contains(val,case=False,na=False)]
            return {
                "text": "Resultados filtrados:",
                "results":data[["NM_PRODUCAO"]],
            }

    results ={
        "text": "Sem resultados",
        "results":pd.DataFrame([]),
    }
    return results 



