from app.repositories.generation_repository import GenerationRepository


class GenerationService:
    def __init__(self):
        self.repository = GenerationRepository()

    async def save_generation(
        self,
        *,
        anonymous_user,
        filename: str,
        provider: str,
        model: str,
        generation_time_ms: int,
        ats_score: int,
        parse_score: int,
        parsed_resume: dict,
        tailored_resume: dict,
        cover_letter: str,
        status: str = "success",
        error: str | None = None,
    ):

        return await self.repository.create(
            anonymous_user_id=str(anonymous_user.id),
            email=anonymous_user.email,
            original_filename=filename,
            provider=provider,
            model=model,
            generation_time_ms=generation_time_ms,
            ats_score=ats_score,
            parse_score=parse_score,
            parsed_resume=parsed_resume,
            tailored_resume=tailored_resume,
            cover_letter=cover_letter,
            status=status,
            error=error,
        )
