from flask import jsonify
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError


def register_error_handlers(app):
    @app.errorhandler(BadRequest)
    async def handle_bad_request(e):
        return jsonify({"message": str(e.description)}), 400

    @app.errorhandler(NotFound)
    async def handle_not_found(e):
        return jsonify({"message": "Resource not found"}), 404

    @app.errorhandler(InternalServerError)
    async def handle_internal_server_error(e):
        return jsonify({"message": "Internal server error"}), 500

    @app.errorhandler(Exception)
    async def handle_unexpected_error(e):
        return jsonify({"message": "An unexpected error occurred"}), 500
