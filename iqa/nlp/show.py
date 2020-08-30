

import pandas as pd
from .utils import *

str_to_num={'primeira':1,'segunda':2,'terceira':3,'quarta':4,'quinta':5,'sexta':6,'setima':7,'oitava':8,'nona':9,'decima':10,'primeiro':1,'segundo':2,'terceiro':3,'quarto':4,'quinto':5,'sexto':6,'setimo':7,'oitavo':8,'nono':9,'decimo':10}

def process_show(entities,last_data,last_question_type):
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
         
    if last_question_type =='teses':
        available_attrs = ['uni','tipo','aluno','area_con','linha','keyword','resumo','prof','email','url','detalhe']
    elif last_question_type =='artigos':
        available_attrs = ['uni','tipo','area_con','linha','issn','veiculo','detalhe']

    print('show intent!!')
    
    print('available attrs:',available_attrs)
    df = last_data
    print(df)
    return_data={}
    if(len(df)>0):
        print('entities: ',entities)
        dict_ents = {}
        to_show= False
        show_all=False
        for ent in entities:
            dict_ents[ent['entity']]=ent['value']

        if('num' in dict_ents):
            ####TRATAR OS NUMERAIS 'PRIMEIRO','SEGUNDO',etc
            n = dict_ents['num']
            if n in str_to_num:
                num = str_to_num[n]
            else:
                try:
                    num = int(dict_ents['num'])
                except ValueError:
                    return {
                        "text": "Pergunta nao entendida.",
                        "results":pd.DataFrame([]),
                        }
            num=num-1

            if('detalhe' in dict_ents and 'detalhe' in available_attrs):
                show_all=True

            if('uni' in dict_ents and 'uni' in available_attrs):
                field = 'NM_ENTIDADE_ENSINO'
                to_show = True

            if('keyword' in dict_ents and 'keyword' in available_attrs):
                field = 'DS_PALAVRA_CHAVE'
                to_show = True
            if('email' in dict_ents and 'email' in available_attrs):
                field = 'DS_EMAIL_DISCENTE'
                to_show = True

            if('url' in dict_ents and 'url' in available_attrs):
                field = 'DS_URL_TEXTO_COMPLETO'
                to_show = True

            if('prof' in dict_ents and 'prof' in available_attrs):
                field = 'NM_ORIENTADOR'
                to_show = True
            if('aluno' in dict_ents and 'aluno' in available_attrs):
                field = 'NM_DISCENTE'
                to_show = True

            if('tipo' in dict_ents and 'tipo' in available_attrs):
                field = 'NM_SUBTIPO_PRODUCAO'
                to_show=True
            if('area_con' in dict_ents and 'area_con' in available_attrs):
                field ='NM_AREA_CONCENTRACAO'
                to_show=True
            if('resumo' in dict_ents and 'resumo' in available_attrs):
                field ='DS_RESUMO'
                to_show=True
            if('issn' in dict_ents and 'issn' in available_attrs):
                field ='CD_IDENTIFICADOR_VEICULO'
                to_show=True
            if('veiculo' in dict_ents and 'veiculo' in available_attrs):
                field ='DS_TITULO_PADRONIZADO'
                to_show=True
            if('linha' in dict_ents and 'linha' in available_attrs):
                field ='NM_LINHA_PESQUISA'
                to_show=True
            if(show_all):
                print('show all' )

                data=df.iloc[[num]]
                print(data)
                print(type(data))
                return {
                    "text": "Resultados filtrados:",
                    "results":data,
                }

            if(to_show):
                df = df[field]
                try:
                    data=df.iloc[num]
                except IndexError:
                    return {
                        "text": "Resultado nao encontrado.",
                        "results":pd.DataFrame([]),
                    }

                print(data)
                print('field: ',field)
                return {
                    "text": "Resultados filtrados:",
                    "results":pd.DataFrame([data]),
                }
                print('show one only' )
        else:
            return {
                    "text": "Não entendi a referencia",
                    "results":pd.DataFrame([]),
                    }

    return {
        "text": "Sem resultados para mostrar",
        "results":pd.DataFrame([]),
        }


