import pytest
import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from api.server import app
from api.server.settings import db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)

@manager.command
def cov():
    """    
    Nesta função realizamos a execução dos testes e a geração do relatório de cobertura deles.   
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    coverage_dir = os.path.join(base_dir, 'tmp/coverage')
    pytest.main([
        '--cov=tests',  f'--cov-report=html:{coverage_dir}'
    ])


@manager.command
def test():
    """    
    Esta função permite executar os testes do projeto.    
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    tests_dir = os.path.join(base_dir, 'tests')
    pytest.main([tests_dir])


@manager.command
def create_db():
    """
    Esta função permite a criação das tabelas no banco.
    """
    db.create_all()


@manager.command
def drop_db():
    """
    Esta função permite deletar todas as tabelas no banco.
    """
    db.drop_all()


if __name__ == "__main__":
    manager.run()
