#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from sml_decoder import TasmotaSMLParser
import logging
import json
import os

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Check if running on Azure AppService
if os.getenv("ORYX_ENV_TYPE") == "AppService":
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.flask.flask_middleware import FlaskMiddleware

    logger.addHandler(AzureLogHandler())
    middleware = FlaskMiddleware(app, excludelist_paths=[])
else:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

app = Flask(__name__)
Bootstrap(app)
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
nav = Nav()
nav.init_app(app)
nav.register_element("frontend_top", Navbar(View("Tasmota SML Decoder", ".index")))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/decode", methods=["POST", "GET"])
def decode():
    if request.method == "GET":
        return redirect("/")
    elif request.method == "POST":
        data = request.form["smldump"].splitlines()
        data = [x.strip() for x in data]

        tas = TasmotaSMLParser()
        msgs = tas.decode_messages(data)
        messages = []
        for msg in msgs:
            details = tas.get_message_details(msg)
            tasmota_script = tas.build_meter_def(msg)
            messages.append({"msg": details, "tas": tasmota_script})

        messages = sorted(messages, key=lambda x: x["msg"]["obis"])
        logger.info(
            f'{request.remote_addr} - - - "{request.method} {request.path} {request.scheme}"',
            extra={
                "custom_dimensions": {
                    "remote_addr": request.headers.get(
                        "X-Forwarded-For", request.remote_addr
                    ),
                    "path": request.path,
                    "messages": json.dumps(messages),
                    "smldump": json.dumps(data),
                }
            },
        )
        return render_template(
            "decode.html",
            smldump=data,
            parse_errors=tas.parse_errors,
            obis_errors=tas.obis_errors,
            messages=messages,
        )


if __name__ == "__main__":
    logger.info("Startup")
    app.run(debug=True)
