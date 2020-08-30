===============
Guia de usuário
===============

Configurando
-------------

Primeiramente, para utilizar a nossa API é necessário instalar as suas dependências ao executar o seguinte comando na pasta do projeto. Sugerimos a criação de um ambiente virtual, como *virtualenv* ou *conda*.

.. code-block:: console

     $ pip install -r requirements.txt


Antes de executar o projeto é necessário criar dois bancos de dados, o de desenvolvimento e o de teste no PostgreSQL, sendo que o banco de teste deve possuir o mesmo nome do outro acrescido do sufixo :code:`_test`. Em seguida, devemos renomear o arquivo .env.sample para .env e alterar o valor das seguintes variáveis:

- **SECRET_KEY**: Chave utilizada para a geração dos *tokens* de acesso e atualização.
- **DB_URL**: `URI de conexão`_ ao banco do PostgreSQL (sem o :code:`_test`)



Executando
------------

Com o ambiente ativado, no terminal execute as seguintes instruções para inicializar e configurar as tabelas no banco de dados.

.. code-block:: console

    $ python manage.py create_db
    $ python manage.py db init
    $ python manage.py db migrate


Por fim, podemos executar aplicação ao utilizar:

.. code-block:: console

    $ python manage.py runserver


Caso queira especificar uma outra porta (-p) ou *host* (-h), informe-os como no exemplo abaixo:

.. code-block:: console

   $ python manage.py runserver -h 0.0.0.0 -p 3000

Você poderá visualizá-la acessando o seguinte endereço http://127.0.0.1:5000/, caso não tenha definido outro *host* ou porta. Na Figura abaixo mostramos a aparência da nossa API:

.. image:: ./_static/iqasucupira-api.png
   :scale: 60 %
   :alt: API IQASucupira
   :align: center

Como usar a API?
----------------
A nossa API possui 6 operações, conforme mostramos na imagem anterior. A primeira operação a ser realizada é a solicitação dos *tokens* de acesso e atualização, os quais são fornecidos ao se registrar através *endpoint* :code:`/register`. É necessário fornecer um nome de usuário que não foi cadastrado previamente no banco de dados e uma senha. Caso você já tenha realizado um cadastro, você pode obter ambos *tokens* ao logar (acessar :code:`/login`) informando os dados cadastrados. Em caso de sucesso, será exibido os campos do *access_token* e *refresh_token*.

.. code-block:: javascript

   {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1OTg2Mjg1ODUsIm5iZiI6MTU5ODYyODU4NSwianRpIjoiOGI1MmRjYTctMmExYS00ODg2LThlYmYtMTM5MWRlZjdmZTdjIiwiZXhwIjoxNTk4NjI5NDg1LCJpZGVudGl0eSI6MSwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.q4N8GafsVXtxYc3bCM_b7nj5oUZreTmwsPU-OKqV5gk",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1OTg2Mjg1ODUsIm5iZiI6MTU5ODYyODU4NSwianRpIjoiNzNmOTVkM2MtMmE3Yy00MmFiLWE3NzEtMmUxMTVhNzE2ZTU0IiwiZXhwIjoxNjAxMjIwNTg1LCJpZGVudGl0eSI6MSwidHlwZSI6InJlZnJlc2gifQ.yKD378KsDDETmU9zqtzj_sMmGN2_9UUHhFR1wj5tAnI"
    }

Deixamos o tempo de expiração *default* de 15min para o **Access Token** e 30 dias para o *Refresh Token*, caso o *token* de acesso tenha expirado, você pode solicitar um novo ao informar o *token* de atualização no endpoint :token:`/refresh`. 


Realizando consultas
''''''''''''''''''''

O *endpoint* responsável pela consulta ao IQA é o :code:`/search`, e como o objetivo é facilitar a integração com interfaces de chatbots, é necessário fornecer os seguintes parâmetros:

- A consulta escrita em linguagem natural
- Um número inteiro correspondendo ao id do usuário que enviou a consulta
- Um número inteiro referente ao id da mensagem
- Número identificando o bot que solicitou o IQA

Também é necessário fornecer no *header* o **Access Token** no campo *Authorization* escrito na seguinte forma :code:`Bearer ACCESS_TOKEN`. Na Figura abaixo ilustramos o *endpoint* de consulta.

.. image:: ./_static/search.png
   :scale: 60 %
   :alt: Endpoint de Consulta ao IQA
   :align: center


Integrando com um chatbot
'''''''''''''''''''''''''
Para critérios demonstrativos, utilizamos a API de *chatbots* do `Telegram`_ devido a sua facilidade como caso de uso do **IQASucupira**. Utilizamos a biblioteca `python-telegram-bot`_ para esta tarefa e teremos a seguinte estrutura.

::

    project
    ├── demo.py
    ├── model
    │   ├──__init__.py        
    │   ├── iqa_sucupira_api.py
    │   └── iqanswer.py
    ├── bot.cfg          
    ├── requirements.txt
    └── data

Primeiro começaremos a escrever o submódulo *model*, o :code:`iqa_sucupira_api.py` construímos a classe que irá se comunicar com a nossa API via requisições POST e GET. O método :code:`refresh_token_decorator` é utilizado para requisitar um novo **Access Token** sempre que esse estiver próximo de expirar. Com o nossa classe :code:


.. code-block:: python
   :emphasize-lines: 5,23,73 

    import time
    import requests
    import os

    def refresh_token_decorator(func):
        """
            Decorador utilizado para atualizar o TOKEN de acesso.
        """
        def wrapper(api,*args,**kwargs):
            try:
                if time.time() > api.access_token_expiration:
                    api.get_access_token()
                return func(api,*args,**kwargs)
            except TypeError:
                print("Missing Access Token!")
                return 404, {
                    "status": "fail",
                    "message": "Missing Access Token!"
                }
        return wrapper


    class IQASucupiraAPI:
        """
            Classe que realiza a comunicação com a API
        """

        access_token = None
        refresh_token = None
        access_token_expiration = None

        def __init__(self, username, password, endpoint):
            self.endpoint = endpoint
            try:
                endpoint_login = self.endpoint + "login"
                data = {
                    "username": username,
                    "password": password
                }
                response = requests.post(endpoint_login, json=data)
                resp = response.json()
                if response.status_code == 200:
                    # Obtém os tokens fornecidas pela API
                    self.access_token = resp["access_token"]
                    self.refresh_token = resp["refresh_token"]
                    # Define o tempo de expiração da token de acesso
                    self._update_access_token_expiration()
                    
            except Exception as e:
                print(e)

        def get_access_token(self):
            """ Método utilizado para obter o TOKEN de acesso da API
            """
            endpoint_refresh = self.endpoint + "refresh"
            head = {'Authorization': 'Bearer ' + self.refresh_token}
            try:
                response = requests.post(endpoint_refresh, headers=head)
                self.access_token = response.json()['access_token']
                self._update_access_token_expiration()
                return self.access_token
            except Exception as e:
                print(e)
                return None

        def _update_access_token_expiration(self, seconds = 840):
            """
                Método utilizado para definir o tempo quando o token de acesso deverá se atualizado.
            """
            self.access_token_expiration = time.time() + seconds   

        @refresh_token_decorator
        def search(self, query, user_id, message_id, bot_id):
            """ Realiza consultas à API
            """
            try:
                endpoint_search = self.endpoint + "search"
                head = {'Authorization': 'Bearer ' + self.access_token}
                params = {
                    "q": query, "uid": user_id, "mid": message_id, "bid": bot_id
                }
                response = requests.get(
                    endpoint_search, params=params, headers=head
                )
                return response.status_code, response.json()
            except Exception as e:
                return response.status_code, {
                    "status": "fail",
                    "message": e
                }


Com a nossa classe :code:`IQASucupiraAPI` construída, estamos prontos para criar o nosso arquivo :code:`demo.py` que irá conter a função que se comunicará com o método `search` da nossa classe. Para critério de simplicidade, limitados os resultados para os 5 primeiros.



.. code-block:: python
   :emphasize-lines: 5

    import pandas as pd
    import numpy as np


    def get_answer(api, text, user_id=None, message_id=None, bot_id=None):
        """
        Se sucesso retorna um dicionário com os campos "results" e "text",
        caso contrário retorna uma string.

        Parameters
        ----------
        api : IQASucupiraAPI
            instância do objeto que se comunica com a API
        text : str
            Mensagem a ser analisada pela API
        user_id : int
            ID de usuário do Telegram
        message_id : int
            ID da mensagem do usuário do Telegram
        bot_id : int
            ID do bot no Telegram
        Returns
        -------
            dict
                Dicionário contendo os resultados encontrados
            str
                Mensagem informando que ocorreu um erro ao se comunicar com o IQA

        """
        status, response = api.search(text, user_id, message_id, bot_id)
        if response and status == 200:
            response["results"] = pd.DataFrame(response["results"]).head(5)
            return response
        else:
            return "Algum erro aconteceu, tente novamente mais tarde."


Em seguida adicionamos os métodos da biblioteca *python-telegram-bot* e a classe do nosso bot a qual nomeamos de :code:`TelegramBot`.


.. code-block:: python

    from telegram import (
        InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
    )
    from telegram.ext import (
        Updater,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        Filters
    )


    class TelegramBot:
        def __init__(self, dispatcher, sucupira_api):
            print("Bot inicializado!")
            self.dispatcher = dispatcher
            self.sucupira_api = sucupira_api
            self.__process_handlers()

        def start_cmd(self,update, context):
            """
                Sempre que o usuário invocar o comando /start, será mensagem a string abaixo.
            """
            update.message.reply_text("Olá, eu estou aqui para te ajudar a consultar informações na plataforma Sucupira. Se você precisar de ajuda, utilize os comandos /examples ou /help.", parse_mode="markdown")

        def help_cmd(self, update, context):
            """
                Sempre que o usuário invocar o comando /help, será mensagem a string abaixo e a mensagem contendo exemplos
            """
            update.message.reply_text("Este bot responde perguntas básicas sobre teses, dissertações, revistas e artigos.", parse_mode="markdown")
            self.examples_cmd(update, context)

        def about_cmd(self, update, context):
            """
                Sempre que o usuário invocar o comando /about, será mensagem a string abaixo.
            """
            update.message.reply_text("Este bot é uma demonstração de uso da [IQASucupiraAPI](https://github.com/IQABots/QASucupira-API).", parse_mode="markdown")

        def examples_cmd(self, update, context):
            """
                Sempre que o usuário invocar o comando /examples, será mensagem a string abaixo.
            """
            update.message.reply_text("**Estes são alguns exemplos de perguntas que você pode experimentar:**\n\n- Revistas da área de computação.\n- Teses da área de computação com termo redes de computadores.\n- Artigos da área de computação com termo Internet da Coisas.", parse_mode="markdown")

        def format(self, data):
            """Transforma dataframe em string
            """
            text = ""
            columns = data.columns.values

            for _, row in data.iterrows():
                for col in columns:
                    text += f"*{col}*: {row[col]}\n"
                text += "==============\n"

            return text

        def answer(self, update, context):

            # Envia mensagem do usuário para a API
            nlu_answer = get_answer(
                self.sucupira_api,
                update.message.text,
                user_id=update.message.from_user.id,
                message_id=update.message.message_id,
                bot_id=context.bot.getMe().id
            )

            if type(nlu_answer) == dict:
                text = self.format(nlu_answer["results"])
                # enviar mensagem ao usuário
                update.message.reply_text(nlu_answer["text"])
                update.message.reply_text(text, parse_mode="markdown")
            else:
                update.message.reply_text(nlu_answer)


        def __process_handlers(self):
            self.dispatcher.add_handler(CommandHandler("start", self.start_cmd))
            self.dispatcher.add_handler(CommandHandler("help", self.help_cmd))
            self.dispatcher.add_handler(CommandHandler("about", self.about_cmd))
            self.dispatcher.add_handler(
                CommandHandler("examples", self.examples_cmd)
            )
            self.dispatcher.add_handler(
                MessageHandler(Filters.text & ~Filters.command, self.answer)
            )


Ainda no arquivo :code:`demo.py` adicionamos a chamada das nossas classes TelegraBot para iniciar o bot e IQASucupiraBot. No trecho destacado no código abaixo carregamps o arquivo :code:`bot.cfg` que contém os valores das variáveis que permitem acessar tanto a nossa API quanto a API de bots no Telegram.

.. code-block:: python
    :emphasize-lines: 7

    if __name__ == "__main__":

        from iqa_sucupira_api import IQASucupiraAPI
        import configparser

        config = configparser.ConfigParser()
        config.read('bot.cfg')


        # Inicializa a API
        api = IQASucupiraAPI(
            config["DEFAULT"]["username"],
            config["DEFAULT"]["password"],
            config["DEFAULT"]["endpoint"]
        )

        # Inicializar bot do Telegram
        updater = Updater(token=config["DEFAULT"]["token"], use_context=True)
        TelegramBot(updater.dispatcher, api)
        updater.start_polling()
        updater.idle()


Agora, podemos realizar consultas e, nossa API através de um chatbot do Telegram. Na Figura abaixo mostramos os *screenshots* dos resultados retornados pela nossa API e exibidos no cliente Android do Telegram.

.. _URI de conexão: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
