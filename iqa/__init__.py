
from .nlp.nlu import NLU
import sys
from . import nlp
sys.modules['nlp'] =nlp
nlu = NLU()
def get_answer(text, message_id=None, user_id=None, bot_id=None):

    """
        Exemplo de retorno da função a ser implementada.
    """

    re= nlu.get_response(text)
    return re
