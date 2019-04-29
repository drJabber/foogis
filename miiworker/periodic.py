import asyncio
from contextlib import suppress
from asgiref.sync import sync_to_async

class Periodic:
    def __init__(self, obj, func, time):
        self.func = func
        self.obj=obj
        self.time = time
        self.is_started = False
        self._task = None

    async def start(self):
        if not self.is_started:
            self.is_started = True
            # Start task to call func periodically:
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        if self.is_started:
            self.is_started = False
            # Stop task and await it stopped:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            await self.func()
            await asyncio.sleep(self.time)
