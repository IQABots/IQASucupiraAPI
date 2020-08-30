from .utils import *
from .search import semantic_search



def process_query(entities,qualis_table,data_artigos,data_teses,embeddings_dict,embed,codes2Name):
    """
    O método faz a operação de processamento principal, que recebe as entidades detectadas da questão, os dados das revistas, artigos e teses juntos com seus respectivos embeddings. A função processa as informações e retorna o resultados requerido em forma tabelada.   

    Parameters
    ----------
    entities : list
                Lista das entidades detectadas na questão.
    qualis_table : pd.DataFrame
                Dados dos qualis em forma tabelada.
    data_artigos : pd.DataFrame
                Dados dos artigos em forma tabelada
    data_teses : pd.DataFrame
                Dados das teses em forma tabelada
    embeddings_dict : dict
                     Dicionário conténdo o embeddings do conjunto de dados (artigos,revistas,teses)
    embed : PyTorch
            Modelo de embeddings
    codes2Name : dict
            Dicionario que mapeia o codigo de uma área de conhecimento para seu nome
    
    Returns
    -------
    list

        Lista contendo em ordem: dicionario com os dados de resultado, os dados resultantes, e o tipo da questão perguntada('revistas','artigos','teses',...)
    """
    artigos_embeddings = embeddings_dict['artigos']
    teses_embeddings = embeddings_dict['teses']
    revistas_embeddings = embeddings_dict['revistas']
    print('process query')
    if len(entities) == 1:
        print('area only')
        area_name = entities[0]["value"]
        area_name = get_area_name_correct(area_name,codes2Name)
        df = qualis_table[
            qualis_table["Área de Avaliação"] == area_name[0]
        ]
        df = df.reset_index()
        last_data =df 
        last_question_type ='area' 
         
        return {
            "text": "Resultado(s) encontrado(s):",
            "results": df,
        },last_data,last_question_type
    
    revista_search = False
    artigo_search = False
    tese_search = False
    mono_search = False
    has_area = False
    has_term = False
    question_type = 'None'
    for ent in entities:
        if ent["entity"] == "area":
            has_area = True
            area_name = ent["value"]
            print("area_name: ", area_name)
        if ent["entity"] == "revistas":
            search_term = ent["value"]
            print("search_term: ", search_term)
            revista_search = True
            question_type = 'revistas'

        if ent["entity"] == "artigos":
            search_term = ent["value"]
            print("search_term: ", search_term)
            artigo_search = True
            question_type = 'artigos'

        if ent["entity"] == "teses":
            search_term = ent["value"]
            print("search_term: ", search_term)
            tese_search = True
            question_type = 'teses'

        if ent["entity"] == "mono":
            search_term = ent["value"]
            print("search_term: ", search_term)
            tese_search = True
            mono_search = True
            question_type = 'teses'

        if ent["entity"] == "science_terms":
            search_term = ent["value"]
            has_term= True
            print("search_term: ", search_term)

    if(has_area==False):
        print('no area!!')
        last_data = pd.DataFrame([])
        last_question_type = question_type
            
        return {
                "text": "Especifique uma área/campo/matéria:",
                "results": pd.DataFrame([]),
            },last_data,last_question_type

    if(artigo_search):
        print('artigo search!')
        print('filtering...')
        filters_fields_dict = {'area':'NM_AREA_CONCENTRACAO','linha':'NM_LINHA_PESQUISA',
                'tipo':'NM_SUBTIPO_PRODUCAO','entidade':'NM_ENTIDADE_ENSINO',
                'sigla':'SG_ENTIDADE_ENSINO','revista':'DS_TITULO_PADRONIZADO'}

        c=0
        print('data artigos:',len(data_artigos))
        sub_df = data_artigos
        print('entities:',entities)
        for e in entities:
          try:
              print(e)
              if(e['entity']=='area'):
                  continue
              if(c==0):
                sub_df = filter_by_column(data_artigos,filters_fields_dict[e['entity']],strip_accents(e['value']).lower())
              else:
                sub_df = filter_by_column(sub_df,filters_fields_dict[e['entity']],strip_accents(e['value']).lower())
          except KeyError:
              print('key error')
              continue
          c+=1
        print('sub df:',len(sub_df))
        if(has_term==False):
            sub_df=sub_df.reset_index()
            last_data = sub_df
            last_question_type = question_type
            return {
                "text": "Resultados:",
                "results": sub_df[["NM_PRODUCAO"]],
            },last_data,last_question_type
        if(len(sub_df)>5000):
            sub_df = sub_df[:5000]
        dataframe_results=semantic_search(search_term,sub_df,artigos_embeddings,embed)
        exact_matches = dataframe_results.loc[dataframe_results['names'].str.contains(search_term,na=False),:]
        
        print(len(dataframe_results))

        if(len(dataframe_results)>100):
            dataframe_results = dataframe_results[:100]
        dataframe_results = pd.concat([exact_matches,dataframe_results]).drop_duplicates().reset_index(drop=True)
        del dataframe_results['names']
        titles_results=dataframe_results[["NM_PRODUCAO"]]
        last_data = dataframe_results             
        last_question_type = question_type

        return {
                "text": "Resultado(s) encontrado(s):",
                "results": titles_results,
            },last_data,last_question_type

    elif(tese_search): 
        print('tese search!!')
        
        filters_fields_dict = {'area':'NM_AREA_CONCENTRACAO','linha':'NM_LINHA_PESQUISA',
                'tipo':'NM_SUBTIPO_PRODUCAO','entidade':'NM_ENTIDADE_ENSINO',
                'sigla':'SG_ENTIDADE_ENSINO','palavra-chave':'DS_PALAVRA_CHAVE'}

        c=0
        #print("****",self.data_teses['NM_SUBTIPO_PRODUCAO'])
        if(mono_search==False):
            sub_df = data_teses[data_teses['NM_SUBTIPO_PRODUCAO']=='TESE']
        else:
            sub_df = data_teses[data_teses['NM_SUBTIPO_PRODUCAO']=='DISSERTAÇÃO']
        #sub_df = self.data_teses[:50]
        for e in entities:
          try:
              print(e)
              if(e['entity']=='area'):
                  continue
              if(c==0):
                sub_df = filter_by_column(data_teses,filters_fields_dict[e['entity']],strip_accents(e['value']).lower())
              else:
                sub_df = filter_by_column(sub_df,filters_fields_dict[e['entity']],strip_accents(e['value']).lower())
          except KeyError:
              continue
          c+=1
        if(has_term==False):
            sub_df=sub_df.reset_index()
            last_data = sub_df             
            last_question_type = question_type

            return {
                "text": "Resultados:",
                "results": sub_df[["NM_PRODUCAO"]],
            },last_data,last_question_type

        if(len(sub_df)>5000):
            sub_df = sub_df[:5000]
        dataframe_results=semantic_search(search_term,sub_df,teses_embeddings,embed)
        exact_matches = dataframe_results.loc[dataframe_results['names'].str.contains(search_term,na=False),:]
        if(len(dataframe_results)>100):
            dataframe_results = dataframe_results[:100]
        dataframe_results = pd.concat([exact_matches,dataframe_results]).drop_duplicates().reset_index(drop=True)
        del dataframe_results['names']
        titles_results=dataframe_results[["NM_PRODUCAO"]]
        last_data = dataframe_results            
        last_question_type = question_type


        return {
                "text": "Resultado(s) encontrado(s):",
                "results": titles_results,
            },last_data,last_question_type

    elif(revista_search):
        print('Revista Search!!')
        
        area_name = get_area_name_correct(area_name,codes2Name)
        print('corrected area name: ',area_name)
        df = qualis_table[qualis_table["Área de Avaliação"] == area_name[0]]
        if(has_term==False):
            last_data = df             
            last_question_type = question_type
            return {
                "text": "Resultados da área especificada:",
                "results": df,
            },last_data,last_question_type
        print('df:',len(df))
        dataframe_results=semantic_search(search_term,df,revistas_embeddings,embed)
        exact_matches = dataframe_results.loc[dataframe_results['names'].str.contains(search_term,na=False),:]
        if(len(dataframe_results)>100):
            dataframe_results = dataframe_results[:100]
        dataframe_results = pd.concat([exact_matches,dataframe_results]).drop_duplicates().reset_index(drop=True)

        del dataframe_results['names']
        if(len(dataframe_results)>100):
            dataframe_results = dataframe_results[:100]

        last_data = dataframe_results            
        last_question_type = question_type

        return {
                "text": "Resultado(s) encontrado(s):",
                "results": dataframe_results,
                },last_data,last_question_type
    else:
        print('no search found')
