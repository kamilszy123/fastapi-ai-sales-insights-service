class HealthService:
    async def get_status(self) -> dict:
        return {"status": "ok"}
