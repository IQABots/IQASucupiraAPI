from api.server.settings import app, bcrypt, db


class UserModel(db.Model):
    """
    Classe responsável por salvar as informações do usuário no banco.

    ...

    Attributes
    ----------
    id : int
        Identificador do usuário.
    username : str
        nome de usuário informado pelo usuário, deve ser único.
    password : str
        senha informada pelo usuário

    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, password, admin=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(
            password, app.config.get("BCRYPT_LOG_ROUNDS")
        ).decode()
        self.admin = admin


class RevokedTokenModel(db.Model):
    """
    Classe responsável por salvar as informações de TOKENS no banco.

    ...

    Attributes
    ----------
    id : int
        Identificador do token na tabela.
    token : str
        Token de autenticação.

    Methods
    -------
    check_is_revoked(auth_token)
        Verifica se um token foi revogado.

    """

    __tablename__ = "revoked_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return "<id: token: {}".format(self.token)

    @staticmethod
    def check_is_revoked(auth_token):
        res = RevokedTokenModel.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
