# StreamBridge

A microservice to restream [streamlink](https://github.com/streamlink/streamlink) streams.

## Usage

```sh
$ hatch run serve
```

`HEAD /http://a-streamlink-supported.com/0000/`
`GET /http://a-streamlink-supported.com/0000/`
Restream the content, if possible.
`stream` to select one of the avaible streams

`OPTIONS /http://a-streamlink-supported.com/0000/`
Response example:
```json
{
    "plugin":"ASLPlugin",
    "streams":["worst", "best"]
}
```
