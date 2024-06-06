from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from starlette.responses import Response

from auth.jwt_manager import USER_SESSION_EXPIRY_DURATION_IN_DAYS
from auth.models import UserResponse
from auth.user import create_or_fetch_user, authenticate_user, get_jti_from_request, logout_user_session, UserRequest, get_current_user
from auth.jwt_manager import USER_SESSION_EXPIRY_DURATION_IN_DAYS, create_access_token, store_user_session, TokenCreationError
from data.database import read_only_session
from data.tables import User, Organization, UserSession
from log import logger
from pydantic import BaseModel

router = APIRouter()


@router.post(
    "/auth/login",
    operation_id="login",
    description="Login user and create a user session."
)
async def login(user_request: UserRequest):
    try:
        token = create_or_fetch_user(user_request)
        response = Response()
        response.delete_cookie("access_token")
        response.set_cookie(
            key="access_token",
            value=token,
            max_age=int(timedelta(days=USER_SESSION_EXPIRY_DURATION_IN_DAYS).total_seconds()),
            domain=None,
            secure=False,
            httponly=False,
            samesite="lax",
        )
        return response
    except Exception as e:
        logger.error(f"Exception occurred during auth: {e}")
        raise HTTPException(status_code=500, detail="Exception occurred during auth")

@router.post(
    "/auth/logout",
    operation_id="logout",
    description="Logout user."
)
async def logout(request: Request, response: Response, user: User = Depends(authenticate_user)):
    jti = get_jti_from_request(request)
    logout_user_session(user.id, jti)
    response.delete_cookie("access_token")
    return response


@router.get(
    "/auth/me",
    operation_id="currentUser",
    description="Get the current user.",
    response_model=UserResponse,
)
async def me(user: User = Depends(authenticate_user)) -> UserResponse:
    with read_only_session() as session:
        user_data = session.query(
            User.id,
            User.email,
            User.name,
            User.is_internal,
            User.profile_image,
            User.organization_id,
            User.created_at,
            User.updated_at,
            User.status,
        ).filter(User.email == user.email).first()

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        organization_name = None
        if user_data.organization_id:
            organization = session.query(Organization.name).filter_by(id=user_data.organization_id).first()
            organization_name = organization.name if organization else None

        return UserResponse(
            id=user_data.id,
            email=user_data.email,
            name=user_data.name,
            organization_name=organization_name,
            is_internal=user_data.is_internal,
            profile_image=user_data.profile_image,
            created_at=user_data.created_at,
            updated_at=user_data.updated_at,
            status=user_data.status,
        )

class ImpersonateRequest(BaseModel):
    client_user_id: str
    impersonator_id: str

@router.post(
    "/auth/impersonate",
    operation_id="impersonateUser",
    description="Impersonate a user and create an impersonation session."
)
async def impersonate_user(impersonate_request: ImpersonateRequest):
    try:
        with read_only_session() as session:
            client_user = session.query(User).filter_by(id=impersonate_request.client_user_id).first()

            impersonator = session.query(User).filter_by(id=impersonate_request.impersonator_id).first()

            if not client_user:
                raise HTTPException(status_code=404, detail="Client user not found")
            if not impersonator:
                raise HTTPException(status_code=404, detail="Impersonator user not found")

            print(f"Client User: {client_user.name}, is_internal: {client_user.is_internal}")
            print(f"Impersonator: {impersonator.name}, is_internal: {impersonator.is_internal}")

        jti, token = create_access_token(impersonate_request.client_user_id)
        print(f"Token created: {token}")

        store_user_session(impersonate_request.client_user_id, jti, impersonate_request.impersonator_id)

        response = Response()
        response.set_cookie(
            key="access_token",
            value=token,
            max_age=int(timedelta(hours=24).total_seconds()),
            domain=None,
            secure=False,
            httponly=False,
            samesite="lax",
        )
        print("Response set with cookie")
        return response
    except HTTPException as e:
        print(f"HTTP Exception during impersonation: {e.detail}")
        raise e
    except Exception as e:
        print(f"Error during impersonation: {e}")
        raise HTTPException(status_code=500, detail="Error during impersonation")

@router.post("/auth/stop_impersonation")
def stop_impersonation(current_user: User = Depends(get_current_user)):
    with read_only_session() as session:
        user_session = session.query(UserSession).filter(UserSession.user_id == current_user.id).order_by(UserSession.created_at.desc()).first()
        if user_session and user_session.impersonator_id:
            impersonator = session.query(User).filter(User.id == user_session.impersonator_id).first()
            if impersonator:
                jti, token = create_access_token(impersonator.id)
                store_user_session(impersonator.id, jti, None)
                response = Response()
                response.set_cookie(
                    key="access_token",
                    value=token,
                    max_age=int(timedelta(days=USER_SESSION_EXPIRY_DURATION_IN_DAYS).total_seconds()),
                    domain=None,
                    secure=False,
                    httponly=False,
                    samesite="lax",
                )
                return response
    raise HTTPException(status_code=400, detail="No active impersonation session found")

@router.get("/auth/session")
async def get_user_session(user: User = Depends(get_current_user)):
    with read_only_session() as session:
        user_session = session.query(UserSession).filter(UserSession.user_id == user.id).order_by(UserSession.created_at.desc()).first()
        if user_session and user_session.impersonator_id:
            impersonator = session.query(User).filter(User.id == user_session.impersonator_id).first()
            if impersonator:
                print(f"Impersonator name: {impersonator.name}")
                return {"impersonator_name": impersonator.name}
        return {"impersonator_name": None}