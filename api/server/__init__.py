from api.server.settings import app
from api.server.resources import bp

app.register_blueprint(bp)
