import dash
import dash_bootstrap_components as dbc
from flask import Flask

server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,
                prevent_initial_callbacks=True)


app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgres://fzdtbkhisirenm:518d4abf7afd20fb9fc1ea3ed9d6e34d7a1b7a1ff20338dcf93736c19024a2ef@ec2-34-255-134-200.eu-west-1.compute.amazonaws.com:5432/d9nj1hete0n8qc"

