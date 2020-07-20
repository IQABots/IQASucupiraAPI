from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from api.server import app
from api.server.settings import db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)


@manager.command
def create_db():
    """Criar tabelas.

    Esta função permite a criação das tabelas no banco.

    """
    db.create_all()


@manager.command
def drop_db():
    """Deletar tabelas.

    Esta função permite deletar todas as tabelas no banco.

    """
    db.drop_all()


if __name__ == "__main__":
    manager.run()
