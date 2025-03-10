#!/usr/bin/env python
import time
import threading
from datetime import datetime, timezone
import serial
import requests
from pathlib import Path
from pyndigo.driver import *
from pyndigo.utils import print_msg as pp


class MARCOTRoofDevice(StandardDriverDevice):
    def __init__(self, dri):
        super().__init__(dri, "MARCOT Roof")

        self._thread = None
        self._stop_thread = False

        prop = self.add_switch_property(
            "COMMAND",
            STATE_OK,
            PERM_RW,
            RULE_ONE_OF_MANY,
            label="Command",
            group="Control",
        )
        prop.add_switch("OPEN", SWITCH_OFF, label="Open")
        prop.add_switch("CLOSE", SWITCH_OFF, label="Close")
        prop.add_switch("STATUS", SWITCH_OFF, label="Manual get status")
        self.add_property_listener(prop, self.command_received)

        prop = self.add_text_property(
            "ROOF_STATUS",
            STATE_IDLE,
            PERM_RO,
            label="Roof status",
            group="Control",
        )
        prop.add_text("WEST_ROOF", "Unknown", label="West Roof")
        prop.add_text("EAST_ROOF", "Unknown", label="East Roof")
        prop.add_text("REMOTE", "Unknown", label="Remote")
        prop.add_text("CHECKING", "", label="Checking")

        prop = self.add_text_property(
            "HOST",
            STATE_OK,
            PERM_RW,
            label="Host",
            group="Main",
        )
        prop.add_text("IP", "10.70.1.195", label="Host IP")
        self.add_property_listener(prop, self.ip_received)

    def ip_received(self, prop: PyndigoProperty, items: dict):
        prop.set_busy()
        self.send_property_update(prop)

        new_ip = items.get("IP").get("value")

        self.set_value(prop, "IP", new_ip).set_ok()
        self.send_property_update(prop)

    def command_received(self, prop: PyndigoProperty, items: dict):
        if items.get("OPEN").get("value") == SWITCH_ON:
            if self.is_roof_closed() and self.is_remote_on():
                try:
                    requests.get(self.base_url() + "outputaccess0?PW=&State=ON&")
                except requests.exceptions.RequestException as e:
                    pp("Error abriendo: " + str(e))

            else:
                pp("Not opening, because roof is not closed or remote off")
        elif items.get("CLOSE").get("value") == SWITCH_ON:
            if self.is_roof_open() and self.is_remote_on():
                try:
                    requests.get(self.base_url() + "outputaccess1?PW=&State=ON&")
                except requests.exceptions.RequestException as e:
                    pp("Error cerrando: " + str(e))

            else:
                pp("Not closing, because roof is not opened or remote off")
        elif items.get("STATUS").get("value") == SWITCH_ON:
            self.get_roof_status()

    def base_url(self):
        return f"http://{self.get_property('HOST').get_item('IP').get_value()}/"

    def is_remote_on(self):
        self.get_roof_status()

        if self.get_value("ROOF_STATUS", "REMOTE") == SWITCH_ON:
            return True

        return False

    def is_roof_open(self):
        self.get_roof_status()

        if (
            self.get_value("ROOF_STATUS", "EAST_ROOF") == "Open"
            and self.get_value("ROOF_STATUS", "WEST_ROOF") == "Open"
        ):
            return True

        return False

    def is_roof_closed(self):
        self.get_roof_status()

        if (
            self.get_value("ROOF_STATUS", "EAST_ROOF") == "Closed"
            and self.get_value("ROOF_STATUS", "WEST_ROOF") == "Closed"
        ):
            return True

        return False

    def update_checking(self):
        dots = self.get_value("ROOF_STATUS", "CHECKING")
        if len(dots) < 3:
            dots = dots + "."
        else:
            dots = ""

        self.set_value("ROOF_STATUS", "CHECKING", dots)

    def get_roof_status(self):
        try:
            r = requests.get(self.base_url() + "input?PW=&")
        except requests.exceptions.RequestException:
            self.set_value("ROOF_STATUS", "EAST_ROOF", "Unknown")
            self.set_value("ROOF_STATUS", "WEST_ROOF", "Unknown")
            self.set_value("ROOF_STATUS", "REMOTE", "Unknown")
            self.update_checking()
            self.set_alert("ROOF_STATUS")
            self.send_property_update("ROOF_STATUS")
            return

        status_hex = str(r.content).split(";")[1][:-1]
        status_decimal = int(status_hex, 16)
        status_binary = bin(status_decimal)[2:]

        status_binary = status_binary.zfill(12)

        east_roof_closed = int(status_binary[-5])
        east_roof_open = int(status_binary[-4])
        west_roof_closed = int(status_binary[-3])
        west_roof_open = int(status_binary[-2])
        remote = int(status_binary[-1])

        self.set_ok("ROOF_STATUS")

        if remote:
            self.set_value("ROOF_STATUS", "REMOTE", SWITCH_ON)
        else:
            self.set_value("ROOF_STATUS", "REMOTE", SWITCH_OFF).set_alert()

        if east_roof_closed:
            self.set_value("ROOF_STATUS", "EAST_ROOF", "Closed")
        elif east_roof_open:
            self.set_value("ROOF_STATUS", "EAST_ROOF", "Open")
        else:
            self.set_value("ROOF_STATUS", "EAST_ROOF", "Moving").set_busy()

        if west_roof_closed:
            self.set_value("ROOF_STATUS", "WEST_ROOF", "Closed")
        elif west_roof_open:
            self.set_value("ROOF_STATUS", "WEST_ROOF", "Open")
        else:
            self.set_value("ROOF_STATUS", "WEST_ROOF", "Moving").set_busy()

        self.update_checking()

        self.send_property_update("ROOF_STATUS")

    def client_ask_connect(self):
        pp("Connecting")

        if self._thread is None:

            self._stop_thread = False

            self._thread = threading.Thread(target=self._continuous_read)

            self._thread.start()

    def client_ask_disconnect(self):
        pp("Disconnecting")

        if self._thread is not None:
            self._stop_thread = True

    def _continuous_read(self):
        while not self._stop_thread:
            self.get_roof_status()
            time.sleep(1)

        self._stop_thread = False
        self._thread = None


class GPSDevice(StandardDriverDevice):
    def __init__(self, driver):
        super().__init__(driver, "Mi GPS")

        prop = self.add_text_property(
            "GEOGRAPHIC_COORDINATES",
            STATE_ALERT,
            PERM_RO,
            label="Geographic coordinates",
            group="Main",
        )
        prop.add_text("LATITUDE", "-", label="Latitude")
        prop.add_text("LONGITUDE", "-", label="Longitude")
        prop.add_text("ELEVATION", "-", label="Elevation")

        prop = self.add_text_property(
            "DEVICE_PORT",
            STATE_OK,
            PERM_RW,
            label="Device Port",
            group="Main",
        )
        prop.add_text("PORT", "/dev/ttyACM0", label="Port")

        self.stop_thread = False

    def client_ask_connect(self):
        pp("Connecting")

        thread = None

        self.stop_thread = False

        thread = threading.Thread(
            target=self._read_gps,
            args=(
                "lalala.csv",
                self.get_property("DEVICE_PORT").get_item("PORT").get_value(),
                9600,
            ),
        )

        thread.start()

    def _read_gps(self, csvFile, gpsPort, baudrate):
        f = open(csvFile, "w")

        ser = serial.Serial(gpsPort, baudrate=baudrate)

        # Open SerialPort
        if not ser.isOpen():
            ser.open()

        alreadyBegunToSaveTimes = False

        while not self.stop_thread:
            line = ser.readline()
            timePc = datetime.now(timezone.utc)
            line2 = line.decode("latin-1").strip()
            pp(line2)
            if (
                line2[0:2] == "$G" and line2[3:6] == "RMC"
            ):  # Read the line start with G*RMC
                splitted = line2.split(",")
                valid = splitted[2]
                time = splitted[1]
                date = splitted[9]
                latitude = splitted[3]
                latitudeNS = splitted[4]
                longitude = splitted[5]
                longitudeEW = splitted[6]

                if (len(time) > 0) and (valid == "A"):
                    alreadyBegunToSaveTimes = True

                    gpsTime = (
                        "20"
                        + date[4:6]
                        + "-"
                        + date[2:4]
                        + "-"
                        + date[0:2]
                        + " "
                        + time[0:2]
                        + ":"
                        + time[2:4]
                        + ":"
                        + time[4:]
                    )

                    pcTime = str(timePc)

                    lat = int(latitude[0:2]) + float(latitude[2:]) / 60.0
                    if latitudeNS == "S":
                        lat = lat * -1

                    lon = int(longitude[0:3]) + float(longitude[3:]) / 60.0
                    if longitudeEW == "W":
                        lon = lon * -1

                    p = self.get_property("GEOGRAPHIC_COORDINATES")
                    p.get_item("LATITUDE").set_value(str(lat))
                    p.get_item("LONGITUDE").set_value(str(lon))
                    p.set_ok()
                    self.send_property_update(p)
                else:
                    p = self.get_property("GEOGRAPHIC_COORDINATES")
                    p.get_item("LATITUDE").set_value("-")
                    p.get_item("LONGITUDE").set_value("-")
                    p.set_busy()
                    self.send_property_update(p)

        f.close()

        return

    def client_ask_disconnect(self):
        pp("Disconnecting")
        self.stop_thread = True




class ExampleDevice(StandardDriverDevice):
    def __init__(self, driver):
        super().__init__(driver, "Example Device")

        prop = self.add_text_property(
            "TEST_TEXT",
            STATE_ALERT,
            PERM_RW,
            label="Test Text",
            group="Main",
        )
        prop.add_text("TEXT", "-", label="Text")

        prop = self.add_blob_property(
            "BLOB_TEST",
            STATE_OK,
            PERM_RO,
            label="Test BLOB",
            group="Main",
        )

        prop.add_blob("BLOB", "", label="Blob", blob_format=".fits")


    def client_ask_connect(self):
        pp("Connecting")

        p = self.get_property("BLOB_TEST")
        i = p.get_item("BLOB")

        p.set_busy()
        self.send_property_update(p)

        data = Path('/home/zerjillo/lala.jpg').read_bytes()

        i.set_value(data)
        i.set_blob_format(".jpg")

        p.set_ok()

        self.send_property_update(p)






    def client_ask_disconnect(self):
        pp("Disconnecting")




dr = PyndigoDriver("Mi driver chupiguay")

dev = ExampleDevice(dr)
#dev = GPSDevice(dr)

#dev = MARCOTRoofDevice(dr)

dr.read()
