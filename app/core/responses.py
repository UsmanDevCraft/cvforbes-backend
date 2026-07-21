from app.schemas.api_response import ApiResponse


def success_response(
    data,
    message: str = "Success",
):
    return ApiResponse(
        success=True,
        message=message,
        data=data,
    )
