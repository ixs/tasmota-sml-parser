#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from sml_decoder import TasmotaSMLParser
import json

app = Flask(__name__)
Bootstrap(app)
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
app.debug = False
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

        tas = TasmotaSMLParser()
        msgs = tas.decode_messages(data)
        messages = []
        for msg in msgs:
            details = tas.get_message_details(msg)
            tasmota_script = tas.build_meter_def(msg)
            messages.append({"msg": details, "tas": tasmota_script})

        messages = sorted(messages, key=lambda x: x["msg"]["obis"])
        print(json.dumps(messages))

        return render_template(
            "decode.html",
            smldump=data,
            parse_errors=tas.parse_errors,
            messages=messages,
        )


if __name__ == "__main__":
    app.run()
