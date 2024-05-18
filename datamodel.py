#! /usr/bin/python3

import time
import json
import pprint


class DataModel:
    def __init__(self):
        self.position = dict()
        self.time = dict()
        self.satellites = dict()

        self.last_values_update = 0
        self.lon_dec = 0.0
        self.lat_dec = 0.0

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
        # print("DataModel: NMEA update, msg:", msg["type"])
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
            self.position["latitude"] = {
                "string": msg["latitude"],
                "decimal": self.lat_dec,
                "direction": msg["latitude_dir"],
            }

            self.position["longitude"] = {
                "string": msg["longitude"],
                "decimal": self.lon_dec,
                "direction": msg["longitude_dir"],
            }

            self.position["status"] = status
            self.position["heading"] = {
                "track": msg["track_deg"],
                "mag_var": msg["magvar_deg"],
            }

            # self.position["link"] = self.__create_gmaps_link(
            #    self.lat_dec, msg["latitude_dir"], self.lon_dec, msg["longitude_dir"]
            # )

            # speed = 0.0
            # if msg["speed"] != "":
            #    speed = float(msg["speed"])

            # self.position.update({"speed": {"knots": speed}})
            # self.position["speed"]["knots"] = speed
            self.position["update_ts"] = time.time()

            print("Datamodel - position: ", end="")
            pprint.pprint(self.position)
            # print("Datamodel - satellites: ", end="")
            # pprint.pprint(self.satellites)
            # print("Datamodel - time: ", end="")
            # pprint.pprint(self.time)

        elif msg["type"] == "GSV":
            # print("GSV: " + repr(msg))
            for i in range(1, 5):
                try:
                    if msg["sat_" + str(i) + "_num"] != "":
                        name = msg["talker"] + "-" + msg["sat_" + str(i) + "_num"]

                        el = 0
                        az = 0
                        snr = 0
                        if msg["sat_" + str(i) + "_elevation_deg"] != "":
                            el = int(msg["sat_" + str(i) + "_elevation_deg"])
                        if msg["sat_" + str(i) + "_azimuth_deg"] != "":
                            az = int(msg["sat_" + str(i) + "_azimuth_deg"])
                        if msg["sat_" + str(i) + "_snr_db"] != "":
                            snr = int(msg["sat_" + str(i) + "_snr_db"])

                        self.satellites.update(
                            {
                                name: {
                                    "elevation": el,
                                    "azimuth": az,
                                    "snr": snr,
                                    "update_ts": time.time(),
                                }
                            }
                        )
                except:
                    # satellite ID not found ...
                    pass

        elif msg["type"] == "GSA":
            # print("GSA: " + repr(msg))

            if msg["talker"] == "GN":
                return

            for i in range(1, 13):
                if msg["id_" + str(i)] != "":
                    name = msg["talker"] + "-" + msg["id_" + str(i)]
                    # self.satellites.update({name: {"used": True}})
                    self.satellites[name]["used"] = True

            hdop = 0.0
            if msg["hdop"] != "":
                hdop = float(msg["hdop"])

            pdop = 0.0
            if msg["pdop"] != "":
                pdop = float(msg["pdop"])

            vdop = 0.0
            if msg["vdop"] != "":
                vdop = float(msg["vdop"])

            self.position.update({"dop": {"hdop": hdop, "vdop": vdop, "pdop": pdop}})

            self.position["update_ts"] = time.time()

            self.satellites["update_ts"] = time.time()

        elif msg["type"] == "GGA":
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

            self.position["gps_quality"] = {"indicator": gqr, "description": gq}

            altitude = 0.0
            if msg["antenna_asl"] != "":
                altitude = float(msg["antenna_asl"])

            geosep = 0.0
            if msg["geosep"] != "":
                geosep = float(msg["geosep"])

            self.position["altitude"] = altitude
            self.position["geoid_separation"] = geosep

            self.position["update_ts"] = time.time()

        elif msg["type"] == "VTG":
            # print("VTG: " + repr(msg))

            speed_knots = 0.0
            if msg["speed_knots"] != "":
                speed_knots = float(msg["speed_knots"])

            speed_kph = 0.0
            if msg["speed_kph"] != "":
                speed_kph = float(msg["speed_kph"])
            self.position.update({"speed": {"knots": speed_knots, "kph": speed_kph}})
            self.position["update_ts"] = time.time()

        elif msg["type"] == "GNS":
            # print("GNS: " + repr(msg))
            pass
        else:
            print("Datamodel: unsupported nmea msg type:", msg["type"])

        self.last_values_update = time.time()

    def updateJSON(self, jobject):
        # print("DataModel: JSON update, object:", repr(jobject))
        pass
