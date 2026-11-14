from typing import Optional, List, Callable
from fastapi import Request, HTTPException, Depends
from jose import JWTError, jwt
from pydantic import BaseModel, Field


class UserRole:
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class UserInfo(BaseModel):
    sub: str  # Keycloak user UUID
    preferred_username: str
    email: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)


def _check_role(required_roles: List[str]) -> Callable:
    """Dependency factory that checks if user has required roles."""

    async def role_dependency(request: Request) -> UserInfo:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

        token = auth_header[len("Bearer "):]
        try:
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,  # Will be True in production with real Keycloak keys
                    "verify_aud": False,
                    "verify_exp": True,
                },
            )
            user_info = UserInfo(
                sub=payload.get("sub", ""),
                preferred_username=payload.get("preferred_username", ""),
                email=payload.get("email"),
                roles=payload.get("realm_access", {}).get("roles", []),
                permissions=payload.get("resource_access", {}).get("api://axiom-foundry", {}).get("roles", []),
            )
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid authentication token: {str(e)}")

        user_roles = set(user_info.roles)
        required_set = set(required_roles)
        if not user_roles.intersection(required_set):
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required: {required_roles}, "
                       f"Have: {list(user_roles)}",
            )

        return user_info

    return role_dependency


def check_role(required_roles: List[str]) -> Callable:
    """Deprecated: use _check_role instead. Kept for backwards compatibility."""
    return _check_role(required_roles)


def check_viewer() -> Callable:
    """Dependency to require viewer role or higher."""
    return _check_role([UserRole.VIEWER, UserRole.OPERATOR, UserRole.ADMIN])


def check_operator() -> Callable:
    """Dependency to require operator role or higher."""
    return _check_role([UserRole.OPERATOR, UserRole.ADMIN])


def check_admin() -> Callable:
    """Dependency to require admin role."""
    return _check_role([UserRole.ADMIN])
