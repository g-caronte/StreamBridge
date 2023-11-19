import asyncio
import functools

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


@functools.cache
def _resolve(url):
    """Cached plugin resolution"""
    return Streamlink().resolve_url(url)


def resolve(url, params=None):
    pluginname, pluginclass, resolved_url = _resolve(url)
    # Apparently session doesn't forward params to plugin like cli does
    prefix = f"{pluginname}-"
    plugin_params = {k.replace(prefix, ""): params[k] for k in params if k.startswith(prefix)}
    plugin = pluginclass(Streamlink(params), resolved_url, plugin_params)
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
