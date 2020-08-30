import pytest
from iqa.nlp.inv_index import Index



def test_valid_add():
    """Testa a insercao de um novo documento"""
    inv_index = Index()
    inv_index.add("Ciencia da computaçao")
    assert len(inv_index.documents) == 1


def test_invalid_add():
    inv_index = Index()
    with pytest.raises(TypeError):
        inv_index.add(1)
    

def test_valid_lookup():
    """Testa a insercao de um novo documento"""
    inv_index = Index()
    inv_index.add("Ciencia da computaçao")
    a=inv_index.lookup("computaçao")
    assert type(a)==list


def test_invalid_lookup():
    inv_index = Index()
    inv_index.add("Ciencia da computaçao")
    with pytest.raises(AttributeError):
        a=inv_index.lookup(0)
    
