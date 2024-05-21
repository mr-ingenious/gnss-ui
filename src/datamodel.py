#! /usr/bin/python3

import time
import json
import pprint
import logging


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
            "heading": {"track": "", "mag_var": ""},
            "gps_quality": {"indicator": 0, "description": ""},
            "altitude": 0.0,
            "geoid_separation": 0.0,
            "speed": {"knots": 0.0, "kph": 0.0},
            "status": "",
        }

        self.time = dict()
        self.time["update_ts"] = 0
        self.time["data"] = dict()

        self.satellites = dict()
        self.satellites["update_ts"] = 0
        self.satellites["data"] = dict()

        self.last_values_update = 0
        self.lon_dec = 0.0
        self.lat_dec = 0.0

    def reset(self):
        self.logger.info("resetting data structure")
        self.__setup_structure()

    def update(self, msg):
        pass

    def __convert_coordinates_to_decimal(self):
        self.lat_dec = round(self.lat)
        lat_fract = self.lat - self.lat_dec
        lat_fract = lat_fract / 0.60
        self.lat_dec += lat_fract

        self.lon_dec = round(self.lon)
        lon_fract = self.lon - self.lon_dec
        lon_fract = lon_fract / 0.60
        self.lon_dec += lon_fract

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
            if msg["latitude"] != "" and msg["longitude"] != "":
                self.lat = float(msg["latitude"]) / 100
                self.lon = float(msg["longitude"]) / 100
                self.__convert_coordinates_to_decimal()
            else:
                self.lat = 0.0
                self.lon = 0.0
                self.__convert_coordinates_to_decimal()

            if msg["status"] == "A":
                status = "active"
            else:
                status = "void"
            self.position["data"]["latitude"] = {
                "string": msg["latitude"],
                "decimal": self.lat_dec,
                "direction": msg["latitude_dir"],
            }

            self.position["data"]["longitude"] = {
                "string": msg["longitude"],
                "decimal": self.lon_dec,
                "direction": msg["longitude_dir"],
            }

            self.position["data"]["status"] = status
            self.position["data"]["heading"] = {
                "track": msg["track_deg"],
                "mag_var": msg["magvar_deg"],
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
            # self.logger.debug("GSA: " + repr(msg))

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
                gq = "Fix not valid"
            elif gqr == 1:
                gq = "GPS Fix"
            elif gqr == 2:
                gq = "Differential GPS"
            else:
                gq = "unknown"

            self.position["data"]["gps_quality"] = {"indicator": gqr, "description": gq}

            altitude = 0.0
            if msg["antenna_asl"] != "":
                altitude = float(msg["antenna_asl"])

            geosep = 0.0
            if msg["geosep"] != "":
                geosep = float(msg["geosep"])

            self.position["data"]["altitude"] = altitude
            self.position["data"]["geoid_separation"] = geosep

            self.position["update_ts"] = time.time()

        elif msg["type"] == "VTG":
            # self.logger.debug("VTG: " + repr(msg))

            speed_knots = 0.0
            if msg["speed_knots"] != "":
                speed_knots = float(msg["speed_knots"])

            speed_kph = 0.0
            if msg["speed_kph"] != "":
                speed_kph = float(msg["speed_kph"])
            self.position["data"].update(
                {"speed": {"knots": speed_knots, "kph": speed_kph}}
            )
            self.position["update_ts"] = time.time()

        elif msg["type"] == "GNS":
            # self.logger.debug("GNS: " + repr(msg))
            pass
        else:
            self.logger.debug("Datamodel: unsupported nmea msg type: %s", msg["type"])

        self.last_values_update = time.time()

    def updateJSON(self, jobject):
        # print("DataModel: JSON update, object:", repr(jobject))
        pass
