import asyncio
import aiofiles

from streamlink.plugin import Plugin
from streamlink.session import Streamlink
from streamlink.exceptions import PluginError


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
            stream = streams[stream_name]
        except PluginError as err:
            if retry == 0:
                raise err
            await asyncio.sleep(1.1 * (4 - retry))
            retry -= 1
            continue

        retry = 3

        stream_fd = async_wrap(stream.open())
        try:
            while buff := await stream_fd.read(8*1024):
                yield buff
        finally:
            await stream_fd.close()


def resolve(url, session_args=None):
    sl = Streamlink(session_args)
    pluginname, pluginclass, resolved_url = sl.resolve_url(url)
    plugin = pluginclass(sl, resolved_url, {})
    return pluginname, plugin


def async_wrap(io_base):
    return aiofiles.threadpool.AsyncBufferedIOBase(io_base, None, None)
