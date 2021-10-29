from os import makedirs
import requests
import time
import errno
import threading
import trio
import logging
import pyfuse3
import json as jsondumper

from sanic import Sanic
from sanic.response import json
from sanic.request import Request

from fs import Operations

app = Sanic(__name__)
log = logging.getLogger(__name__)


def fuse_loop():
    operations = Operations("/dev/shm/mirrors")
    log.debug('Mounting...')
    fuse_options = set(pyfuse3.default_options)
    fuse_options.add('fsname=EIOfs')
    fuse_options.add('debug')
    pyfuse3.init(operations, "/root/fs", fuse_options)
    log.debug('Entering main loop..')
    trio.run(pyfuse3.main)


def init_logging(debug=False):
    formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(threadName)s: '
                                  '[%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if debug:
        handler.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


@app.route("/", methods=['GET'])
async def root_check(request: Request):
    return json({"code": 0})


@app.route("/health", methods=['GET'])
async def health_check(request: Request):
    return json({"code": 0})


@app.before_server_start
async def before_server_start(app, loop):
    requests.post("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a37c81dd-37be-4670-9274-b3577ad8d267", data=jsondumper.dumps({
        "msgtype": "text",
        "text": {
            "content": "EIO QA平台测试: \ntime: " + time.asctime(time.localtime(time.time()))
        }
    }))

    init_logging(True)
    app.ctx.extra_thread = threading.Thread(target=fuse_loop, daemon=True)
    app.ctx.extra_thread.start()


@app.after_server_stop
async def after_server_stop(app, loop):
    log.debug('Exit main loop..')
    pyfuse3.close(unmount=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, workers=1)
