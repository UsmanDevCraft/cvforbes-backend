from app.models.banned_ip import BannedIP


class BannedRepository:
    async def get_by_fingerprint(
        self,
        fingerprint: str,
    ) -> BannedIP | None:
        return await BannedIP.find_one(BannedIP.fingerprint == fingerprint)

    async def create(self, **kwargs):
        ban = BannedIP(**kwargs)

        await ban.insert()

        return ban

    async def save(self, ban: BannedIP):
        await ban.save()

        return ban

    async def delete(self, ban: BannedIP):
        await ban.delete()
