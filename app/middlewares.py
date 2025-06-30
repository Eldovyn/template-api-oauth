import datetime
from flask import request, jsonify
from werkzeug.exceptions import BadRequest


def register_middlewares(app):
    @app.after_request
    async def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.before_request
    async def before_request():
        request.timestamp = datetime.datetime.now(datetime.timezone.utc)
