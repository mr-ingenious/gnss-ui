#! /usr/bin/python3

import time
import json
import pprint
import logging
import math


class DataModel:
    def __init__(self):

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("datamodel")

        self.__setup_structure()

    def __setup_structure(self):
        self.position = dict()
        self.position["update_ts"] = 0
        self.position["data"] = {
            "dop": {"hdop": 0.0, "vdop": 0.0, "pdop": 0.0},
            "latitude": {
                "string": "",
                "decimal": 0.0,
                "direction": "",
            },
            "longitude": {
                "string": "",
                "decimal": 0.0,
                "direction": "",
            },
            "cog": {"cog_deg": 0.0, "magvar_deg": 0.0},
            "gps_quality": {"indicator": 0, "description": ""},
            "altitude": 0.0,
            "geoid_separation": 0.0,
            "sog": {"kts": 0.0, "kph": 0.0},
            "satellites_in_use": 0,
            "status": "",
        }

        self.time = dict()
        self.time["update_ts"] = 0
        self.time["data"] = dict()

        self.satellites = dict()
        self.satellites["update_ts"] = 0
        self.satellites["data"] = dict()

        self.other = dict()
        self.other["update_ts"] = 0
        self.other["data"] = dict()

        self.last_values_update = 0

    def reset(self):
        self.logger.info("resetting data structure")
        self.__setup_structure()

    def update(self, msg):
        pass

    def __convert_coordinates_to_decimal(self, degree, direction):
        degree_tmp = float(degree) / 100
        decimal = math.floor(degree_tmp)
        fract = (degree_tmp - decimal) / 0.6
        decimal += fract

        if direction == "S" or direction == "W":
            decimal = -1 * decimal

        return decimal

    def __create_gmaps_link(self, lat, lat_dir, lon, lon_dir):
        return (
            "https://www.google.com/maps/place/"
            + str(lat)
            + lat_dir
            + "/"
            + str(lon)
            + lon_dir
        )

    def updateNMEA(self, msg):
        # self.logger.debug("DataModel: NMEA update, msg: %s", msg["type"])
        if msg["type"] == "RMC":
            lat_dec = 0.0
            lon_dec = 0.0

            if msg["latitude"] != "" and msg["longitude"] != "":
                lat_dec = self.__convert_coordinates_to_decimal(
                    msg["latitude"], msg["latitude_dir"]
                )

                lon_dec = self.__convert_coordinates_to_decimal(
                    msg["longitude"], msg["longitude_dir"]
                )

            if msg["status"] == "A":
                status = "Valid"
            elif msg["status"] == "V":
                status = "Receiver warning"
            else:
                status = "Unknown"

            self.position["data"]["latitude"] = {
                "string": msg["latitude"],
                "decimal": lat_dec,
                "direction": msg["latitude_dir"],
            }

            self.position["data"]["longitude"] = {
                "string": msg["longitude"],
                "decimal": lon_dec,
                "direction": msg["longitude_dir"],
            }

            self.position["data"]["status"] = status

            cog_deg = 0.0
            if msg["cog_deg"] != "":
                cog_deg = float(msg["cog_deg"])

            magvar_deg = 0.0
            if msg["magvar_deg"] != "":
                magvar_deg = float(msg["magvar_deg"])

            self.position["data"]["cog"] = {
                "cog_deg": cog_deg,
                "magvar_deg": magvar_deg,
            }

            self.position["update_ts"] = time.time()

            # json_object = json.dumps(self.position, indent=4)
            # self.logger.debug("Datamodel - position: %s", json_object)

            # json_object = json.dumps(self.satellites, indent=4)
            # self.logger.debug("Datamodel - satellites: %s", json_object)

            # self.logger.debug("Datamodel - time: %s", self.time)

        elif msg["type"] == "GSV":
            # self.logger.debug("GSV: " + repr(msg))

            for i in range(1, 5):
                try:
                    if msg["sat_" + str(i) + "_num"] != "":
                        name = msg["talker"] + "-" + msg["sat_" + str(i) + "_num"]

                        if None == self.satellites["data"].get(name):
                            self.logger.debug("creating new sat entry for %s", name)
                            self.satellites["data"][name] = {
                                "prn": "",
                                "system": "",
                                "elevation": -1,
                                "azimuth": -1,
                                "snr": -1,
                                "update_ts": 0,
                                "used": False,
                                "last_used_ts": time.time(),
                            }

                        el = -1
                        az = -1
                        snr = -1
                        if msg["sat_" + str(i) + "_elevation_deg"] != "":
                            el = int(msg["sat_" + str(i) + "_elevation_deg"])
                        if msg["sat_" + str(i) + "_azimuth_deg"] != "":
                            az = int(msg["sat_" + str(i) + "_azimuth_deg"])
                        if msg["sat_" + str(i) + "_snr_db"] != "":
                            snr = int(msg["sat_" + str(i) + "_snr_db"])

                        self.satellites["data"].update(
                            {
                                name: {
                                    "prn": msg["sat_" + str(i) + "_num"],
                                    "system": msg["talker"],
                                    "elevation": el,
                                    "azimuth": az,
                                    "snr": snr,
                                    "update_ts": time.time(),
                                    "used": self.satellites["data"][name]["used"],
                                    "last_used_ts": self.satellites["data"][name][
                                        "last_used_ts"
                                    ],
                                }
                            }
                        )
                except:
                    # satellite ID not found ...
                    pass

        elif msg["type"] == "GSA":
            self.logger.debug("GSA: " + repr(msg))

            if msg["talker"] == "GN":
                return

            for i in range(1, 13):
                if msg["id_" + str(i)] != "":
                    name = msg["talker"] + "-" + msg["id_" + str(i)]
                    self.logger.debug("GSA info for %s", name)

                    if None == self.satellites["data"].get(name):
                        self.logger.debug("creating new sat entry for %s", name)
                        self.satellites["data"][name] = {
                            "prn": msg["id_" + str(i)],
                            "system": msg["talker"],
                            "elevation": -1,
                            "azimuth": -1,
                            "snr": -1,
                            "update_ts": 0,
                            "used": True,
                            "last_used_ts": time.time(),
                        }

                    self.satellites["data"][name]["update_ts"] = time.time()
                    self.satellites["data"][name]["used"] = True
                    self.satellites["data"][name]["last_used_ts"] = time.time()

            hdop = 0.0
            if msg["hdop"] != "":
                hdop = float(msg["hdop"])

            pdop = 0.0
            if msg["pdop"] != "":
                pdop = float(msg["pdop"])

            vdop = 0.0
            if msg["vdop"] != "":
                vdop = float(msg["vdop"])

            self.position["data"].update(
                {"dop": {"hdop": hdop, "vdop": vdop, "pdop": pdop}}
            )

            self.position["update_ts"] = time.time()

            self.satellites["update_ts"] = time.time()

            keys = list(self.satellites["data"].keys())

            for k in keys:
                # self.logger.debug("--- %s", k)
                if k != "update_ts":
                    if (time.time() - self.satellites["data"].get(k)["update_ts"]) > 5:
                        self.logger.debug("sat %s: data too old, removing.", k)
                        self.satellites["data"].pop(k)
                    elif (
                        time.time() - self.satellites["data"].get(k)["last_used_ts"]
                        > 10
                    ):
                        # self.logger.debug(
                        #    "sat %s: last_used_ts too old, setting 'used' to 'false'.", k
                        # )
                        self.satellites["data"].get(k)["used"] = False
                        self.satellites["data"].get(k)["last_used_ts"] = time.time()

        elif msg["type"] == "GGA":
            # self.logger.debug("GGA: " + repr(msg))
            gqr = int(msg["gps_quality"])

            gq = "unknown"
            if gqr == 0:
                gq = "Invalid / unavail."
            elif gqr == 1:
                gq = "GPS (SPS)"
            elif gqr == 2:
                gq = "Diff. GPS (SPS)"
            elif gqr == 3:
                gq = "GPS (PPS)"
            elif gqr == 4:
                gq = "RTK fixed int."
            elif gqr == 5:
                gq = "RTK, float int."
            elif gqr == 6:
                gq = "Estimated (DR)"
            elif gqr == 7:
                gq = "Manual Input"
            elif gqr == 8:
                gq = "Simulator"

            self.position["data"]["gps_quality"] = {"indicator": gqr, "description": gq}

            altitude = 0.0
            if msg["antenna_asl"] != "":
                altitude = float(msg["antenna_asl"])

            self.position["data"]["altitude"] = altitude

            geosep = 0.0
            if msg["geosep"] != "":
                geosep = float(msg["geosep"])

            self.position["data"]["geoid_separation"] = geosep

            sat_in_use = 0
            if msg["satellites_in_use"] != "":
                sat_in_use = int(msg["satellites_in_use"])

            self.position["data"]["satellites_in_use"] = sat_in_use

            self.position["update_ts"] = time.time()

        elif msg["type"] == "VTG":
            # self.logger.debug("VTG: " + repr(msg))

            sog_kts = 0.0
            if msg["sog_kts"] != "":
                sog_kts = float(msg["sog_kts"])

            sog_kph = 0.0
            if msg["sog_kph"] != "":
                sog_kph = float(msg["sog_kph"])

            self.position["data"].update({"sog": {"kts": sog_kts, "kph": sog_kph}})
            self.position["update_ts"] = time.time()

        elif msg["type"] == "GNS":
            # self.logger.debug("GNS: ignored " + repr(msg))
            pass
        else:
            self.logger.debug("Datamodel: unsupported nmea msg type: %s", msg["type"])

        self.last_values_update = time.time()

    def updateJSON(self, jobject):
        # self.logger.debug("DataModel: JSON update, object:", repr(jobject))
        pass
