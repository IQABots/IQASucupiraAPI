import pytest



def test_get_response_success(nlu_obj):
    r = nlu_obj.get_response("Quais as revistas de matematica com o termo algebra?")
    assert len(r["results"]) > 0


def test_get_response_fail(nlu_obj):
    r = nlu_obj.get_response("pergunta sem resposta")
    print(r["results"])
    assert len(r["results"])==0 
