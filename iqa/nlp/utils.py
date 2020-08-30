"""
módulo que possui diversas funções de uso aos demais módulos do programa.
"""

import unicodedata
import numpy as np
import pandas as pd

from .constants import areas
from .constants import vocab
import difflib
		
def get_area_name_correct(word,codes2Name):
        """
        função que recebe uma palavra que deve corresponder a uma area, verifica no vocabulario a Area mais similar(para tratar casos de erros gramaticais) e a substitui, e mapeia a area para  opadrão entendido pelo programa.
       
        Parameters
        ----------
        word : str
               palavra identificada como entidade area.
        codes2Name : dict
                     dicionário que mapeia palavra para a categoria de areas entedida pelo programa.
        
        Returns
        -------
        str
        a categoria da area correspondente a palavra


        """
        p_area=difflib.get_close_matches(word,vocab,n=2,cutoff=0)
        code = areas[p_area[0]]
        correct_name = codes2Name[code]
        return correct_name

def terms_filter(sentence):
      """
        função que recebe uma string, e filtra termos considerados desnecessários. 

        Parameters
        ----------
        sentence : str
               sentença a ser filtrada
        
        Returns
        -------
        str
        a sentença filtrada 

      """
      exclude_terms=['da','do','de','esse','essa','desse','dessa','a','e','i','o','u','em','na','para','com','que','faz','fez']
      sub_terms=[]
      sub_terms = sentence.split()
      if(len(sub_terms)<=1):
        return sub_terms[0]
      new_sentence=''
      for t in sub_terms:
        if len(t)<3:
          continue
        if(t in exclude_terms):
          continue
        new_sentence+=t+'|'
      return new_sentence[:-1]

def strip_accents(s):
   """
    Função que retira acentos de uma string e a normaliza

    Parameters
    ----------
    sentence : str
               String 
    
    Returns
    -------
    str
    String normalizada 

   """
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

def filter_by_column(data,column_name,val):
  """
    Função que extrai uma coluna da tabela pandas, que contem o parametro val. 

    Parameters
    ----------
    data : pandas.DataFrame
           Dados
    column_name : str
           Nome da coluna
    val : str
          valor utilizado para busca
    
    Returns
    -------
    pandas.DataFrame
    coluna da tabela especificada que contém o valor buscado. 

  """
  print('filter by column')
  sub_data=data.loc[data[column_name].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.contains(val,case=False,na=False),:]
  return sub_data

def get_prod_stripped_names(df,column_name = "NM_PRODUCAO"):
  """
    Função que extrai uma coluna da tabela pandas, e a retorna normalizada, sem acentuações ou carateres especiais. 

    Parameters
    ----------
    data : pandas.DataFrame
           Dados
    column_name : str
           Nome da coluna
    
    Returns
    -------
    list 
    lista com valores da coluna da tabela normalizados. 

  """
  names=[]
  original_names_index_dict={}
  df_names = df.loc[:,column_name].values
  c = 0
  for n in df_names:
    stripped_name=strip_accents(str(n)).lower()
    names.append(stripped_name)
    original_names_index_dict[stripped_name]=c
    c+=1
  return names


def sort_by_similarity(termo,sentences,embeddings,embed):
  """
    Função que que ordena sentenças pela similaridade com um termo designado.

    Parameters
    ----------
    termo : str
            Termo designado
    sentences : list
            Lista de strings
    embeddings : numpy.array
            Lista numpy de representações vetoriais do dados que contém as sentenças
    embed : Pytorch
            Modelo em pytorch para extração de embeddings do termo

    
    Returns
    -------
     
    list
    lista contendo listas de nomes e seus indices 

  """
  print('sort_by_similarity')
  #for key in matched_names.keys(): 
  #  print(key)
  print(len(sentences))
  sentence_embeddings=[]
  errors_count=0
  #se o inverted index axou documentos contendo os subtermos da busca
  #devemos rankear eles pelas embeddings
  if(len(sentences)>0):
    names=[]
    print('filling up sentences..')
    for sentence in sentences:
      name = sentence
      try:
        #print(name)
        sentence_embeddings.append(embeddings[name])
        names.append(name)
      except KeyError:
        errors_count+=1
      
    names = np.asarray(names)
    print('number of errors: ',errors_count)

    sentence_embeddings = np.asarray(sentence_embeddings)
    #print(embeddings.shape)
    emb =np.asarray( embed.encode([termo]))
    #print(emb.shape)
    similarity_matrix_it = np.inner(sentence_embeddings, emb)
    similarity_matrix_it=similarity_matrix_it.reshape(similarity_matrix_it.shape[0])
    #print(similarity_matrix_it)
    inds = np.argsort(similarity_matrix_it)
    #print('inds:',inds)
    inds = inds[::-1]#inverte a ordem
    names=names[inds]
    
    return names,inds

