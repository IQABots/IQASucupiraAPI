import os





basedir = os.path.abspath(os.path.dirname(__file__))
postgres_connection_uri = os.getenv("DB_URL")


class BaseConfig:
    """Configuração básica.

    Configuração básica das configurações do flask, flask_bcrypt,
    flask_sqlalchemy e flask_jwt_extended

    """

    JWT_SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]


class DevelopmentConfig(BaseConfig):
    """Configurações de desenvolvimento.

    Além das configurações básica, contém as configurações do Banco de Dados.

    """

    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_connection_uri


class TestingConfig(BaseConfig):
    """Configurações para o teste.

    Além das configurações básica, contém as configurações do Banco de Dados
    utilizadas no teste.

    """

    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = postgres_connection_uri + "_test"
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Configurações da produção.

    Além das configurações básica, contém as configurações do Banco de Dados
    que serão utilizadas na produção.

    """

    JWT_SECRET_KEY = "secret-key"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = postgres_connection_uri
