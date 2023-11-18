import asyncio

from streamlink.plugin import Plugin
from streamlink.session import Streamlink
from streamlink.exceptions import PluginError
from streamlink.stream.stream import Stream


async def get_restreamer(plugin: Plugin, stream_name: str):
    gen = restream(plugin, stream_name)

    first_chunk = await gen.__anext__()

    async def fn():
        yield first_chunk
        async for chunk in gen:
            yield chunk

    return fn()


async def restream(plugin: Plugin, stream_name: str):
    retry = 3
    while True:
        try:
            streams = plugin.streams()
            stream: Stream = streams[stream_name]
        except PluginError as err:
            if retry == 0:
                raise err
            await asyncio.sleep(1.1 * (4 - retry))
            retry -= 1
            continue

        retry = 3

        astream = await AsyncStream(stream).open()
        try:
            while buff := await astream.read(8 * 1024):
                yield buff
        finally:
            await astream.close()


def resolve(url, session_args=None):
    sl = Streamlink(session_args)
    pluginname, pluginclass, resolved_url = sl.resolve_url(url)
    plugin = pluginclass(sl, resolved_url, {})
    return pluginname, plugin


class AsyncStream:
    def __init__(self, stream: Stream) -> None:
        self.loop = asyncio.get_event_loop()
        self.sync_stream = stream
        self.sync_reader = None

    def _arun(self, fn):
        return self.loop.run_in_executor(None, fn)

    async def read(self, size: int) -> bytes:
        return await self._arun(lambda: self.sync_reader.read(size))

    async def open(self) -> "AsyncStream":
        await self._arun(self._open)
        return self

    async def close(self):
        return await self._arun(self._close)

    def _open(self):
        self.sync_reader = self.sync_stream.open()

    def _close(self):
        self.sync_reader.close()
        self.sync_reader = None
