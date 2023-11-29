import functools
from time import sleep

from streamlink.exceptions import PluginError
from streamlink.plugin import Plugin
from streamlink.session import Streamlink
from streamlink.stream.stream import Stream


def get_restreamer(plugin: Plugin, stream_name: str):
    gen = restream(plugin, stream_name)

    first_chunk = gen.__next__()

    def fn():
        yield first_chunk
        yield from gen

    return fn()


def restream(plugin: Plugin, stream_name: str):
    retry = 3
    while True:
        try:
            streams = plugin.streams()
            stream: Stream = streams[stream_name]
        except PluginError as err:
            if retry == 0:
                raise err
            sleep(1.1 * (4 - retry))
            retry -= 1
            continue

        retry = 3

        astream = stream.open()
        try:
            while buff := astream.read(8 * 1024):
                yield buff
        finally:
            astream.close()


@functools.cache
def _resolve(url):
    """Cached plugin resolution"""
    return Streamlink().resolve_url(url)


def resolve(url, params=None):
    pluginname, pluginclass, resolved_url = _resolve(url)
    # Apparently session doesn't forward params to plugin like cli does
    prefix = f"{pluginname}-"
    plugin_params = {k.replace(prefix, ""): params[k] for k in (params or {}) if k.startswith(prefix)}

    plugin = pluginclass(Streamlink(params), resolved_url, plugin_params)
    return pluginname, plugin
