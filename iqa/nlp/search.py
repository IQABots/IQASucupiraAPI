"""
módulo contendo operações de busca nos dados do termo especificado.
"""

import pandas as pd
from .utils import *

def semantic_search(term,data,embeddings,embed):
      """
        Função que que ordena sentenças pela similaridade com um termo designado.

        Parameters
        ----------
        termo : str
                Termo designado
        data : pandas.DataFrame
               Dados onde será realizada a busca 
        embeddings : numpy.array
                Lista numpy de representações vetoriais do dados
        embed : Pytorch
                Modelo em pytorch para extração de embeddings do termo

        
        Returns
        -------
         
        pandas.DataFrame
        Tabela com resultados semânticamente similares

      """
      print('semantic search !!!')
      term = strip_accents(term).lower()
      subterms = term.split()
      #cuidado quando usuario colocar termos nao entendiveis
      sub_data=data
      teses_names = sub_data['names'].values
      context_search=False
      if(len(teses_names)==0):
        #if(is_filtered):
        context_search=True
        #teses_names  = data['names'].values
        #else:
        #print('termo nao encontrado')
        #return ['termo nao encontrado']
      print('sort by similarity')
      names,inds=sort_by_similarity(term,teses_names,embeddings,embed)
      results=[]
      for i in inds:
        if(context_search):
          results.append(data.iloc[i])
        else:
          results.append(sub_data.iloc[i])
      results = pd.DataFrame(results)
      return results


