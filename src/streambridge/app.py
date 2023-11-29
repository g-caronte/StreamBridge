from flask import Flask, request
from streamlink.exceptions import NoPluginError, PluginError

from streambridge import bridge

app = Flask(__name__)

app.config["RESPONSE_TIMEOUT"] = 60 * 60 * 24 * 7


app.restream_config = {}


@app.route("/config", methods=["GET", "POST", "PUT", "DELETE"])
def config_handler():
    if request.method in ("DELETE", "POST"):
        app.restream_config.clear()

    if request.method in ("POST", "PUT"):
        app.restream_config.update(request.get_json(force=True))

    return app.restream_config


DLNA_CF_HEADER = "DLNA.ORG_PN=MPEG_TS_HD_NA_MPEG1_L2_ISO;DLNA.ORG_FLAGS=8d700000000000000000000000000000;"
DLNA_HEADERS = {"transferMode.dlna.org": "Streaming", "contentFeatures.dlna.org": DLNA_CF_HEADER}
VIDEO_HEADERS = {"Content-Type": "video/unknwon", **DLNA_HEADERS}


@app.route("/<path:url>", methods=["HEAD", "GET", "OPTIONS"])
def restream_handler(url, stream: str = "best"):
    try:
        pname, plugin = bridge.resolve(url, app.restream_config)
    except NoPluginError:
        return {"error": {"message": "no plugin"}}, 501

    try:
        restreamer = bridge.get_restreamer(plugin, stream)
    except PluginError as ex:
        return {"error": {"message": f"{ex}"}, "plugin": pname}, 501

    if request.method == "OPTIONS":
        return {"plugin": pname, "streams": list(plugin.streams().keys()), "metadata": plugin.get_metadata()}, 200

    return app.response_class(restreamer if request.method == "GET" else "", headers=VIDEO_HEADERS, status=200)
