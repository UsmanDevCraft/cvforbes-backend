from typing import Final

USAGE_TRACKED_ROUTES: Final = {
    ("POST", "/api/v1/tailor-cv"),
}

ADMIN_ROUTES: Final = ("/api/v1/admin",)

PUBLIC_ROUTES: Final = {
    "/health",
    "/docs",
    "/openapi.json",
}
