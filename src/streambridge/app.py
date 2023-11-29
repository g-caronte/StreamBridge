from flask import Flask, request
from streamlink.exceptions import PluginError, NoPluginError

import streambridge.bridge as bridge

app = Flask(__name__)

app.config['RESPONSE_TIMEOUT'] = 60 * 60 * 24 * 7


config = {}


@app.route("/config", methods=["GET", "POST", "DELETE"])
def config_handler():
    if request.method == "POST":
        config.update(request.get_json(force=True))
    elif request.method == "DELETE":
        config.clear()
    return config


DLNA_CF_HEADER = "DLNA.ORG_PN=MPEG_TS_HD_NA_MPEG1_L2_ISO;DLNA.ORG_FLAGS=8d700000000000000000000000000000;"
DLNA_HEADERS = {"transferMode.dlna.org": "Streaming", "contentFeatures.dlna.org": DLNA_CF_HEADER}
VIDEO_HEADERS = {"Content-Type": "video/unknwon", **DLNA_HEADERS}


@app.route("/<path:url>", methods=['HEAD', 'GET', 'OPTIONS'])
def restream_handler(url, stream: str = "best"):
    try:
        pname, plugin = bridge.resolve(url, config)
    except NoPluginError:
        return {"error": {"message": "no plugin"}}, 501

    try:
        restreamer = bridge.get_restreamer(plugin, stream)
    except PluginError as ex:
        return {"error": {"message": f"{ex}"}, "plugin": pname}, 501

    if request.method == "OPTIONS":
        return {"plugin": pname, "streams": list(plugin.streams().keys()), "metadata": plugin.get_metadata()}, 200

    return app.response_class(
        restreamer if request.method == "GET" else "",
        headers=VIDEO_HEADERS,
        status=200
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
