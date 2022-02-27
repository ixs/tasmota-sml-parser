#!/usr/bin/env python3

import binascii
from smllib.sml_frame import SmlFrame
from smllib.const import OBIS_NAMES, UNITS
from pprint import pprint

file = "test-data.txt"


class TasmotaSMLParser:
    def __init__(self):
        self.obis_decoded = []
        self.obis_errors = []
        self.parse_errors = []

    def parse_input(self, input):
        """Parse a line into a frame"""
        if " : 77 " in input.strip():
            # Remove the spaces and return a bytestring
            try:
                frame = binascii.a2b_hex("".join((input.split(" : ", 1)[1]).split()))
            except binascii.Error:
                self.parse_errors.append(input)
                return

        elif input.startswith("77 "):
            try:
                frame = binascii.a2b_hex("".join(input.split()))
            except binascii.Error:
                self.parse_errors.append(input)
                return
        else:
            self.parse_errors.append(input)
            return

        return frame

    def decode_frame(self, frame):
        f = SmlFrame(frame)
        try:
            msgs = f.get_obis()
            if len(msgs) == 0:
                return False
        except Exception as e:
            self.obis_errors.append(
                {"frame": frame, "hex": binascii.b2a_hex(frame, b" "), "msg": e.args[0]}
            )
            return None
        return msgs

    def decode_messages(self, input):
        messages = []
        for line in input:
            frame = self.parse_input(line)
            if frame is None:
                continue
            msgs = self.decode_frame(frame)
            if msgs in [None, False]:
                continue
            for msg in msgs:
                if msg.obis in self.obis_decoded:
                    continue
                else:
                    self.obis_decoded.append(msg.obis)
                messages.append(msg)
        return messages

    def get_message_details(self, msg):
        name = OBIS_NAMES.get(msg.obis, "Unbekannter Datentyp")
        unit = UNITS.get(msg.unit, "Unbekannte Einheit")
        mqtt_topic = (
            "_".join(OBIS_NAMES.get(msg.obis, "Unbekanntes MQTT Topic").split())
            .replace("/", "-")
            .lower()
        )
        try:
            precision = msg.scaler * -1
        except TypeError:
            precision = 0

        try:
            human_readable = (
                f"{round(msg.value * pow(10, msg.scaler), precision)}{unit} ({name})"
            )
        except TypeError:
            if msg.unit in UNITS and msg.name in OBIS_NAMES:
                human_readable = f"{msg.value}{unit} ({name})"
            elif msg.unit in UNITS and msg.name not in OBIS_NAMES:
                human_readable = f"{msg.value}{unit}"
            else:
                human_readable = f"{msg.value}"

        data = {
            "obis": msg.obis,
            "obis_code": msg.obis.obis_code,
            "obis_short": msg.obis.obis_short,
            "name": name,
            "unit": unit,
            "topic": mqtt_topic,
            "precision": precision,
            "value": msg.value,
            "status": msg.status,
            "val_time": msg.val_time,
            "unit_raw": msg.unit,
            "scaler": msg.scaler,
            "value_signature": msg.value_signature,
            "human_readable": human_readable,
        }

        return data

    def build_meter_def(self, msg):
        data = self.get_message_details(msg)
        return f"1,7707{data['obis'].upper()}@1,{data['name']},{data['unit']},{data['topic']},{data['precision']}"

    def pretty_print(self, msg):
        print(msg.format_msg())


def main():
    tas = TasmotaSMLParser()
    msgs = []
    with open(file, "r") as fp:
        msgs = tas.decode_messages(fp.read().splitlines())

        for msg in msgs:
            tas.pretty_print(msg)
            details = tas.get_message_details(msg)
            print("Tasmota SML Script meter definition:")
            print(tas.build_meter_def(msg))
            print(80 * "#")

    if len(tas.obis_errors) > 0:
        pprint(tas.obis_errors)


if __name__ == "__main__":
    main()
