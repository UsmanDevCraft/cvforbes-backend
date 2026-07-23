from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.core.route_policies import USAGE_TRACKED_ROUTES
from app.core.constants import (
    COOKIE_NAME,
    COOKIE_MAX_AGE,
)

from app.core.exceptions import (
    DailyLimitExceeded,
    ClientBanned,
)

from app.services.client_identity_service import (
    ClientIdentityService,
)

from app.services.anonymous_user_service import (
    AnonymousUserService,
)

from app.services.abuse_service import (
    AbuseService,
)


class IPGuardMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):

        super().__init__(app)

        self.identity_service = ClientIdentityService()

        self.anonymous_service = AnonymousUserService()

        self.abuse_service = AbuseService()

    async def dispatch(
        self,
        request,
        call_next,
    ):

        if (request.method, request.url.path) not in USAGE_TRACKED_ROUTES:
            return await call_next(request)

        identity = self.identity_service.get_identity(request)

        user = None

        try:
            if await self.abuse_service.is_banned(identity.fingerprint):
                raise ClientBanned()

            user = await self.anonymous_service.get_or_create(identity)

            await self.anonymous_service.validate_request(user)

            request.state.anonymous_user = user
            request.state.identity = identity

            response = await call_next(request)

        except DailyLimitExceeded:
            # await self.abuse_service.increase_score(
            #     user=user,
            #     identity=identity,
            #     points=DAILY_LIMIT,
            #     reason="Daily limit exceeded",
            # )

            return JSONResponse(
                status_code=429,
                content={"detail": "Daily limit reached."},
            )

        except ClientBanned:
            return JSONResponse(
                status_code=403,
                content={"detail": "You have been banned."},
            )

        if request.cookies.get(COOKIE_NAME) is None:
            response.set_cookie(
                key=COOKIE_NAME,
                value=identity.cookie_id,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=COOKIE_MAX_AGE,
            )

        return response
