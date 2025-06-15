from flask import current_app
import jwt


class AuthJwt:
    @staticmethod
    async def generate_jwt(user_id, datetime):
        payload = {"sub": user_id, "iat": datetime}
        private_key = current_app.config["PRIVATE_KEY"]
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token

    @staticmethod
    def verify_token(token):
        public_key = current_app.config["PUBLIC_KEY"]
        try:
            payload = jwt.decode(token, public_key, algorithms=["RS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
