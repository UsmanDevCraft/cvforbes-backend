from datetime import datetime, timezone

from app.models.anonymous_user import AnonymousUser


class AnonymousRepository:
    async def get_by_fingerprint(self, fingerprint: str):
        return await AnonymousUser.find_one(AnonymousUser.fingerprint == fingerprint)

    async def create(self, **kwargs):
        user = AnonymousUser(**kwargs)
        await user.insert()
        return user

    async def save(self, user: AnonymousUser):
        user.updated_at = datetime.now(timezone.utc)
        await user.save()
        return user

    async def delete(self, user: AnonymousUser):
        await user.delete()
