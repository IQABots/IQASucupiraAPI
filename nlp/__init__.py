def get_answer(text, message_id=None, user_id=None, bot_id=None):
    """
        Exemplo de retorno da função a ser implementada.
    """
    return {
        "text": f"Você escreveu: {text}",
        "results": {
            "coluna_1": [1,2,3,4,5,6,7,8,9,10],
            "coluna_2": ["a", "b", "c","d", "e", "f", "g", "h", "i", "j"]
        }
    }
