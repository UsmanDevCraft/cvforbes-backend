from app.models.generated_cv import GeneratedCV


class GenerationRepository:
    async def create(self, **kwargs) -> GeneratedCV:
        generation = GeneratedCV(**kwargs)
        await generation.insert()
        return generation

    async def save(self, generation: GeneratedCV):
        await generation.save()
        return generation
