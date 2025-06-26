from dataclasses import dataclass


@dataclass
class AccessTokenModel:
    access_token: str
    created_at: int
