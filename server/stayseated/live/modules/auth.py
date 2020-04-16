from channels.db import database_sync_to_async

from stayseated.core.services.user import get_user, update_user
from stayseated.core.services.world import get_world_config_for_user
from stayseated.core.utils.jwt import decode_token


class AuthModule:
    async def login(self):
        if not self.content[1] or "token" not in self.content[1]:
            client_id = self.content[1].get("client_id")
            if not client_id:
                await self.consumer.send_error(code="auth.missing_id_or_token")
                return
            user = await get_user(self.world, with_client_id=client_id)
        else:
            token = await decode_token(self.content[1]["token"], self.world)
            if not token:
                await self.consumer.send_error(code="auth.invalid_token")
                return
            user = await get_user(self.world, with_token=token)
        self.consumer.user = user
        await database_sync_to_async(self.consumer.scope["session"].save)()
        await self.consumer.send_json(
            [
                "authenticated",
                {
                    "user.config": user,
                    "world.config": await get_world_config_for_user(self.world, user),
                },
            ]
        )

    async def update(self):
        new_data = await update_user(
            self.world, self.consumer.user["id"], public_data=self.content[2]
        )
        self.consumer.user = new_data
        await self.consumer.send_success()

    async def dispatch_command(self, consumer, content):
        self.consumer = consumer
        self.content = content
        self.world = self.consumer.scope["url_route"]["kwargs"]["world"]
        if content[0] == "authenticate":
            await self.login()
        elif content[0] == "user.update":
            await self.update()
        else:
            await self.consumer.send_error(code="user.unknown_command")