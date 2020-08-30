from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_refresh_token_required,
    jwt_required,
)
from flask_restx import Api, Resource, fields

from api.server.models import RevokedTokenModel, UserModel
from api.server.settings import bcrypt, db
from iqa import get_answer

bp = Blueprint("IQASucupira-API", __name__)


api = Api(
    app=bp,
    version="0.0.1",
    title="IQASucupira API",
    description="Consulta de informações da plataforma Sucupira.",
    default="Api",
    default_label="Endpoints",
    license_url="https://github.com/QApedia/QASucupira-API/blob/master/LICENSE",
)

model = api.model(
    "Auth",
    {
        "username": fields.String(
            required=True, description="Nome de usuário."
        ),
        "password": fields.String(
            required=True, description="Senha de acesso do usuário.",
        ),
    },
)

namespace = api.namespace("auth")
parser = namespace.parser()
parser.add_argument(
    "Authorization", location="headers", required=True, help="Bearer <JWT>"
)


class UserRegisterAPI(Resource):
    """
    Realiza o cadastro do usuário no banco.
    """

    @api.doc(
        responses={
            201: "User registered",
            202: "User already exists.",
            400: "Something wrong",
        }
    )
    @api.expect(model)
    def post(self):
        post_data = request.get_json()
        user_exists = UserModel.query.filter_by(
            username=post_data.get("username")
        ).first()
        if not user_exists:
            try:
                # Adicionar novo usuário no banco de dados
                user = UserModel(
                    username=post_data.get("username"),
                    password=post_data.get("password"),
                )
                db.session.add(user)
                db.session.commit()

                # Gerar tokens de acesso do usuário
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)

                # Retornar os tokens de acesso ao usuário
                response_json = {
                    
                    "msg": f"User {user.username} was registered",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
                return response_json, 201
            except Exception as e:
                print(e)
                response_json = {
                    
                    "msg": "Some error occurred. Please try again.",
                }
                return response_json, 400

        else:
            response_json = {
                
                "msg": "User already exists. Please Log in.",
            }
            return response_json, 202


class UserLoginAPI(Resource):
    """
    Permite o login de um usuário cadastrado.
    """

    @api.doc(
        responses={
            200: "Login successfully",
            401: "Wrong password",
            404: "User not found",
            500: "Something wrong",
        }
    )
    @api.expect(model)
    def post(self):
        post_data = request.get_json()
        try:
            # Obter o usuário, dado o seu nome de usuário
            user = UserModel.query.filter_by(
                username=post_data.get("username")
            ).first()
            if user:
                if bcrypt.check_password_hash(
                    user.password, post_data.get("password")
                ):
                    # Criar token de acesso para o usuário
                    access_token = create_access_token(identity=user.id)
                    refresh_token = create_refresh_token(identity=user.id)

                    # Retornar os tokens de acesso
                    response_json = {
                        "msg": f"Logged in as {user.username}",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }
                    return response_json, 200
                else:
                    response_json = {
                        
                        "msg": "Incorrect password, please try again.",
                    }
                    return response_json, 401
            else:
                response_json = {
                    
                    "msg": "User does not exist.",
                }
                return response_json, 404
        except Exception as e:
            print(e)
            response_json = { "msg": "Try again"}
            return response_json, 500


class LogoutAPIAccess(Resource):
    """
    Revoga o token de acesso.
    """

    @api.doc(
        responses={
            200: "Successfully logged out",
            401: "Token already revoked",
            403: "Invalid Token",
            422: "Malformed token",
        }
    )
    @api.expect(parser)
    @jwt_required
    def post(self):
        auth_token = get_raw_jwt()["jti"]
        if auth_token:
            blacklist_token = RevokedTokenModel(token=auth_token)
            try:
                db.session.add(blacklist_token)
                db.session.commit()
                response_json = {
                    "msg": "Successfully logged out.",
                }
                return response_json, 200
            except Exception as e:
                response_json = { "msg": e}
                return response_json, 200
        else:
            response_json = {
                "msg": "Provide a valid access token.",
            }
            return response_json, 403


class LogoutAPIRefresh(Resource):
    """
    Revoga o token de atualização.
    """

    @api.doc(
        responses={
            200: "Successfully logged out",
            401: "Token already revoked",
            403: "Invalid Token",
            422: "Malformed token",
        }
    )
    @api.expect(parser)
    @jwt_refresh_token_required
    def post(self):
        auth_token = get_raw_jwt()["jti"]
        if auth_token:
            blacklist_token = RevokedTokenModel(token=auth_token)
            try:
                db.session.add(blacklist_token)
                db.session.commit()
                response_json = {
                    "msg": "Successfully logged out.",
                }
                return response_json, 200
            except Exception as e:
                response_json = { "msg": e}
                return response_json, 200
        else:
            response_json = {
                "msg": "Provide a valid refresh token.",
            }
            return response_json, 403


class TokenRefreshAPI(Resource):
    """
    Obtém um novo token de acesso a partir do token de atualização.
    """

    @api.doc(
        responses={
            200: "Access token successfully created",
            422: "Malformed token",
        }
    )
    @api.expect(parser)
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {"access_token": access_token}


class QASucupira(Resource):
    """
    Endpoint para a consulta de informações sobre a base do Sucupira.
    """

    @api.doc(
        responses={
            200: "Search carried out successfully",
            400: "Missing parameters",
            401: "Token already revoked",
            422: "Malformed token",
        },
        params={
            "q": "Pergunta escrita em linguagem natural.",
            "uid": "Identificador do usuário." ,
            "mid": "Identificador da mensagem do usuário.",
            "bid": "Identificador do bot."
        },
    )
    @api.expect(parser)
    @jwt_required
    def get(self):
        try:
            query = request.args.get("q")
            user_id = request.args.get("uid")
            msg_id = request.args.get("mid")
            bot_id = request.args.get("bid")
            if query:
                # Obtém a resposta de acordo com a query informada
                return get_answer(query, msg_id, user_id, bot_id), 200
            else:
                response_json = {
                    
                    "msg": "Parameter is missing in the query string.",
                }
                return response_json, 400
        except Exception as e:
            response_json = { "msg": e}
            return response_json, 500


# Definir as rotas de acesso
api.add_resource(UserRegisterAPI, "/register")
api.add_resource(UserLoginAPI, "/login")
api.add_resource(LogoutAPIAccess, "/logout/access")
api.add_resource(LogoutAPIRefresh, "/logout/refresh")
api.add_resource(TokenRefreshAPI, "/refresh")
api.add_resource(QASucupira, "/search")
