#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
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
    from azure.monitor.opentelemetry import configure_azure_monitor
    
    configure_azure_monitor()
    
    # Custom logger for Azure
    from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
    from opentelemetry._logs import set_logger_provider
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    
    set_logger_provider(LoggerProvider())
    exporter = AzureMonitorLogExporter()
    logger_provider = set_logger_provider(LoggerProvider())
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler()
    logger.addHandler(handler)
else:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

Bootstrap(app)

# Initialize OpenTelemetry Flask instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor
FlaskInstrumentor().instrument_app(app)


@app.route("/")
def index():
    return render_template("index.html", navbar_title="Tasmota SML Decoder")


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
            navbar_title="Tasmota SML Decoder",
        )


if __name__ == "__main__":
    logger.info("Startup")
    app.run(debug=True)
