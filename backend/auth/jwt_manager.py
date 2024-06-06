# jwt_manager.py

import datetime
import os
import uuid
from datetime import timedelta
import jwt
from typing import Optional

from data.database import read_write_session
from data.tables import UserSession

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
USER_SESSION_EXPIRY_DURATION_IN_DAYS = 180

def create_access_token(user_id: str):
    """
    Create a JWT access token for the given user ID.

    Args:
        user_id (str): The user ID for which the token is being created.
        impersonator_id (Optional[str]): The ID of the impersonator, if any.

    Returns:
        str: A JWT token as a string.
    """
    try:
        jti = str(uuid.uuid4())
        issuer = "wolfia"  # Issuer of the token
        expiration = datetime.datetime.now(datetime.UTC) + timedelta(days=USER_SESSION_EXPIRY_DURATION_IN_DAYS)

        payload = {
            "sub": user_id,  # Subject of the JWT
            "iss": issuer,  # Issuer of the JWT
            "jti": jti,  # Unique identifier for the JWT
            "exp": expiration,  # Expiration time
            "iat": datetime.datetime.now(datetime.UTC),  # Issued at
        }
        return jti, jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    except Exception as e:
        raise TokenCreationError(f"Error creating token for user {user_id}: {e}")

def store_user_session(user_id: str, jti: str, impersonator_id: Optional[str] = None):
    """
    Store a new user session in the database.

    Args:
        user_id (str): The user ID for the session.
        jti (str): The JWT token ID.
        impersonator_id (Optional[str]): The ID of the impersonator, if any.

    Returns:
        str: The ID of the created user session.
    """
    with read_write_session() as session:
        user_session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            jti=jti,
            impersonator_id=impersonator_id,
            created_at=datetime.datetime.now(datetime.UTC),
            expires_at=datetime.datetime.now(datetime.UTC)
            + timedelta(days=USER_SESSION_EXPIRY_DURATION_IN_DAYS),
        )
        session.add(user_session)
        session.commit()
        return user_session.id

class TokenCreationError(Exception):
    """Raised when there is an issue in creating a JWT token."""
