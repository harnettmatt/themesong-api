"""Auth0 token verification utils.py"""

import os
from configparser import ConfigParser

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

token_auth_scheme = HTTPBearer()


def get_config():
    """Sets up configuration for the app"""

    env = os.getenv("ENV", ".config")

    if env == ".config":
        config = ConfigParser()
        config.read(".config")
        config = config["AUTH0"]
    else:
        config = {
            "DOMAIN": os.getenv("DOMAIN", "your.domain.com"),
            "API_AUDIENCE": os.getenv("API_AUDIENCE", "your.audience.com"),
            "ISSUER": os.getenv("ISSUER", "https://your.domain.com/"),
            "ALGORITHMS": os.getenv("ALGORITHMS", ["RS256"]),
        }
    return config


def verify_token(token=Depends(token_auth_scheme), config=Depends(get_config)) -> dict:
    # This gets the 'kid' from the passed token
    jwks_url = f'https://{config["DOMAIN"]}/.well-known/jwks.json'
    try:
        signing_key = jwt.PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key
    except jwt.exceptions.PyJWKClientError as error:
        return {"status": "error", "msg": error.__str__()}
    except jwt.exceptions.DecodeError as error:
        return {"status": "error", "msg": error.__str__()}

    try:
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[config["ALGORITHMS"]],
            audience=config["API_AUDIENCE"],
            issuer=config["ISSUER"],
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return payload


def get_current_user_id(
    token=Depends(token_auth_scheme), config=Depends(get_config)
) -> str:
    response = verify_token(token=token, config=config)
    if response.get("status"):
        raise HTTPException(
            status_code=400, detail=response.get("message", "Auth Error")
        )
    user_id = response.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=400, detail="token is valid, but user could not be identified"
        )
    return user_id
