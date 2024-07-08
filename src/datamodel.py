#! /usr/bin/python3

import time
import json
import pprint
import logging
import math

import logger


class DataModel:
    def __init__(self):

        self.logger = logger.get_logger("datamodel")

        self.__setup_structure()

    def __setup_structure(self):
        self.position = dict()
        self.position["update_ts"] = 0
        self.position["data"] = {
            "dop": {"hdop": 0.0, "vdop": 0.0, "pdop": 0.0, "gdop": 0.0, "xdop": 0.0, "ydop": 0.0, "tdop": 0.0},
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
            "ecef": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "p_acc": 0.0,
                "vx": 0.0,
                "vy": 0.0,
                "vz": 0.0,
            },
            "cog": {"deg": 0.0, "mag_deg": 0.0, "magvar_deg": 0.0},
            "gps_quality": {
                "indicator": 0,
                "description": "",
                "error": {
                    "epx": 0.0,
                    "epy": 0.0,
                    "epv": 0.0,
                    "eph": 0.0,
                    "eps": 0.0,
                    "epc": 0.0,
                    "epd": 0.0,
                    "ept": 0.0,
                    "sep" : 0.0
                },
            },
            "altitude": {"hae": 0.0, "msl": 0.0},
            "geoid_separation": 0.0,
            "sog": {"kts": 0.0, "kph": 0.0},
            "satellites_in_use": 0,
            "status": "unknown",
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
            if msg["talker"] == "GN":
                self.logger.debug("RMC: talker GN: " + repr(msg))

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

            mag_deg = cog_deg + magvar_deg
            
            self.position["data"]["cog"] = {
                "deg": cog_deg,
                "mag_deg": mag_deg,
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

            # if msg["talker"] == "GN":
            #    self.logger.debug("GSV: talker GN: " + repr(msg))

            for i in range(1, 5):
                try:
                    if msg.get("sat_" + str(i) + "_num") != None:
                        name = msg["talker"] + "-" + msg["sat_" + str(i) + "_num"]

                        if msg["sat_" + str(i) + "_num"] == "":
                            self.logger.debug(
                                "GSV: got sat data without PRN, skipping."
                            )
                            continue

                        if None == self.satellites["data"].get(name):
                            self.logger.debug(
                                "GSV: creating new sat entry for %s", name
                            )
                            self.logger.debug("GSV: msg: %s", msg)

                            self.satellites["data"][name] = {
                                "prn": msg["sat_" + str(i) + "_num"],
                                "system": "",
                                "elevation": -1.0,
                                "azimuth": -1.0,
                                "snr": -1.0,
                                "update_ts": time.time(),
                                "used": False,
                                "last_used_ts": 0.0,
                            }

                        el = -1.0
                        az = -1.0
                        snr = -1.0

                        if msg["sat_" + str(i) + "_elevation_deg"] != "":
                            el = float(msg["sat_" + str(i) + "_elevation_deg"])
                        if msg["sat_" + str(i) + "_azimuth_deg"] != "":
                            az = float(msg["sat_" + str(i) + "_azimuth_deg"])
                        if msg["sat_" + str(i) + "_snr_db"] != "":
                            snr = float(msg["sat_" + str(i) + "_snr_db"])

                        self.satellites["data"][name] = {
                            "id": msg["sat_" + str(i) + "_num"],
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

                except Exception as e:
                    # maybe satellite ID not found ...
                    self.logger.warn("GSV: Exception; %s", str(e))
                    pass

        elif msg["type"] == "GSA":
            # self.logger.debug("GSA: " + repr(msg))

            if msg["talker"] == "GN":
                if msg["system_id"] == "1":
                    self.logger.debug("GSA: GN -> setting talker to GP")
                    msg["talker"] = "GP"
                elif msg["system_id"] == "2":
                    self.logger.debug("GSA: GN -> setting talker to GL")
                    msg["talker"] = "GL"
                elif msg["system_id"] == "3":
                    self.logger.debug("GSA: GN -> setting talker to GA")
                    msg["talker"] = "GA"
                else:
                    # self.logger.debug("GSA: ignoring GN talker, system ID unknown")
                    # self.logger.debug("GSA: " + repr(msg))
                    return

            for i in range(1, 13):
                if msg["id_" + str(i)] != "":
                    name = msg["talker"] + "-" + msg["id_" + str(i)]
                    # self.logger.debug("GSA info for %s", name)

                    if None == self.satellites["data"].get(name):
                        self.logger.debug("GSA: creating new sat entry for %s", name)
                        self.satellites["data"][name] = {
                            "prn": msg["id_" + str(i)],
                            "system": msg["talker"],
                            "elevation": -1.0,
                            "azimuth": -1.0,
                            "snr": -1.0,
                            "update_ts": 0.0,
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

            self.position["data"]["dop"]["hdop"] = hdop
            self.position["data"]["dop"]["vdop"] = vdop
            self.position["data"]["dop"]["pdop"] = pdop

            self.position["update_ts"] = time.time()

            self.satellites["update_ts"] = time.time()

            self.update_satellites_list()

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

            self.position["data"]["gps_quality"]["indicator"] = gqr
            self.position["data"]["gps_quality"]["description"] = self.get_gps_quality_desc(gqr)

            altitude = 0.0
            if msg["antenna_asl"] != "":
                altitude = float(msg["antenna_asl"])

            self.position["data"]["altitude"]["msl"] = altitude

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

    def get_gps_quality_desc(self, qval):
            gq = "unknown"
            if qval == 0:
                gq = "Invalid / unavail."
            elif qval == 1:
                gq = "GPS (SPS)"
            elif qval == 2:
                gq = "Diff. GPS (SPS)"
            elif qval == 3:
                gq = "GPS (PPS)"
            elif qval == 4:
                gq = "RTK fixed int."
            elif qval == 5:
                gq = "RTK, float int."
            elif qval == 6:
                gq = "Estimated (DR)"
            elif qval == 7:
                gq = "Manual Input"
            elif qval == 8:
                gq = "Simulator"
                
            return gq
        
    def update_satellites_list(self):
        keys = list(self.satellites["data"].keys())

        for k in keys:
            # self.logger.debug("--- %s", k)
            if k != "update_ts":
                u_tdiff = time.time() - self.satellites["data"].get(k)["update_ts"]
                lu_tdiff = time.time() - self.satellites["data"].get(k)["last_used_ts"]
                if u_tdiff > 10.0:
                    self.logger.debug("sat %s: data too old (%f), removing.", k, u_tdiff)
                    self.satellites["data"].pop(k)
                elif lu_tdiff > 10.0:
                    self.logger.debug(
                        "sat %s: last_used_ts too old (%f), setting 'used' to 'false'.",
                        k, lu_tdiff)
                    self.satellites["data"].get(k)["used"] = False
                    self.satellites["data"].get(k)["last_used_ts"] = time.time()
                        
                        
    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    def updateJSON(self, jobject):
        # self.logger.debug("DataModel: JSON update, object: %s", jobject)

        try:
            if jobject["class"] == "TPV":
                #self.logger.debug("JSON: --> TPV")
                #self.logger.debug("JSON: %s", jobject)
                """
                
                GPSD JSON EXAMPLE:
                
                {
                    'class': 'TPV',
                    'device': '/dev/ttyUSB1',
                    'mode': 3,
                    'time': '2024-06-08T13:53:22.500Z',
                    'ept': 0.005,
                    'lat': 49.3333333,
                    'lon': 11.33333333,
                    'altHAE': 334.9,
                    'altMSL': 287.9,
                    'alt': 287.9,
                    'epx': 27.14,
                    'epy': 18.687,
                    'epv': 23.0,
                    'track': 224.7,
                    'magtrack': 224.4,
                    'magvar': 0.3,
                    'speed': 0.0,
                    'climb': 0.0,
                    'eps': 108.56,
                    'epc': 92.0,
                    'geoidSep': 47.0,
                    'eph': 34.2,
                    'sep': 38.0
                }
                """
                self.position["data"]["longitude"]["decimal"] = self.__get_float_val(
                    jobject, "lon"
                )
                self.position["data"]["latitude"]["decimal"] = self.__get_float_val(
                    jobject, "lat"
                )
                self.position["data"]["altitude"]["hae"] = self.__get_float_val(
                    jobject, "altHAE"
                )
                self.position["data"]["altitude"]["msl"] = self.__get_float_val(
                    jobject, "altMSL"
                )
                self.position["data"]["sog"]["kph"] = 3.6 * self.__get_float_val(
                    jobject, "speed"
                )
                self.position["data"]["cog"]["deg"] = self.__get_float_val(
                    jobject, "track"
                )
                self.position["data"]["cog"]["mag_deg"] = self.__get_float_val(
                    jobject, "magtrack"
                )
                self.position["data"]["cog"]["magvar_deg"] = self.__get_float_val(
                    jobject, "magvar"
                )
                self.position["data"]["geoid_separation"] = self.__get_float_val(
                    jobject, "geoidSep"
                )

                self.position["data"]["ecef"]["x"] = self.__get_float_val(
                    jobject, "ecefx"
                )
                self.position["data"]["ecef"]["y"] = self.__get_float_val(
                    jobject, "ecefy"
                )
                self.position["data"]["ecef"]["z"] = self.__get_float_val(
                    jobject, "ecefz"
                )

                self.position["data"]["ecef"]["p_acc"] = self.__get_float_val(
                    jobject, "ecefpAcc"
                )

                self.position["data"]["ecef"]["vx"] = self.__get_float_val(
                    jobject, "ecefvx"
                )
                self.position["data"]["ecef"]["vy"] = self.__get_float_val(
                    jobject, "ecefvy"
                )
                self.position["data"]["ecef"]["vz"] = self.__get_float_val(
                    jobject, "ecefvz"
                )

                gqr = self.__get_int_val(jobject, "mode", defval = 0)
                self.position["data"]["gps_quality"]["indicator"] = gqr
                
                if gqr == 0:
                    self.position["data"]["gps_quality"]["description"] = "unknown"
                    self.position["data"]["status"]  ="unknown"
                elif gqr == 1:
                    self.position["data"]["gps_quality"]["description"] = "no fix"
                    self.position["data"]["status"]  ="no fix"
                elif gqr == 2:
                    self.position["data"]["gps_quality"]["description"] = "2D fix"
                    self.position["data"]["status"]  ="valid"
                elif gqr == 3:
                    self.position["data"]["gps_quality"]["description"] = "3D fix"
                    self.position["data"]["status"]  ="valid"
                
                self.position["data"]["gps_quality"]["error"]["epx"] = (
                    self.__get_float_val(jobject, "epx")
                )

                self.position["data"]["gps_quality"]["error"]["epy"] = (
                    self.__get_float_val(jobject, "epy")
                )

                self.position["data"]["gps_quality"]["error"]["epv"] = (
                    self.__get_float_val(jobject, "epv")
                )

                self.position["data"]["gps_quality"]["error"]["eps"] = (
                    self.__get_float_val(jobject, "eps")
                )

                self.position["data"]["gps_quality"]["error"]["eph"] = (
                    self.__get_float_val(jobject, "eph")
                )

                self.position["data"]["gps_quality"]["error"]["epc"] = (
                    self.__get_float_val(jobject, "epc")
                )

                self.position["data"]["gps_quality"]["error"]["epd"] = (
                    self.__get_float_val(jobject, "epd")
                )

                self.position["data"]["gps_quality"]["error"]["ept"] = (
                    self.__get_float_val(jobject, "ept")
                )
                
                self.position["data"]["gps_quality"]["error"]["sep"] = (
                    self.__get_float_val(jobject, "sep")
                )

                self.position["update_ts"] = time.time()

                self.logger.debug("JSON: %s", json.dumps(jobject, indent=4))
                # self.logger.debug("JSON: datamodel: %s", repr(self.position))

            elif jobject["class"] == "SKY":
                
                ''' EXAMPLE JSON:
                    {
                        'class': 'SKY',
                        'device': '/dev/ttyUSB1',
                        'gdop': 75.87,
                        'hdop': 1.4,
                        'pdop': 1.7,
                        'tdop': 47.29,
                        'xdop': 8.39,
                        'ydop': 37.14,
                        'vdop': 0.9,
                        'uSat': 6
                    }
                '''
                
                self.position["data"]["dop"]["hdop"] = self.__get_float_val(jobject, "hdop")
                self.position["data"]["dop"]["pdop"] = self.__get_float_val(jobject, "pdop")
                self.position["data"]["dop"]["vdop"] = self.__get_float_val(jobject, "vdop")
                self.position["data"]["dop"]["gdop"] = self.__get_float_val(jobject, "gdop")
                self.position["data"]["dop"]["tdop"] = self.__get_float_val(jobject, "tdop")
                self.position["data"]["dop"]["xdop"] = self.__get_float_val(jobject, "xdop")
                self.position["data"]["dop"]["ydop"] = self.__get_float_val(jobject, "ydop")
                
                self.position["data"]["satellites_in_use"] = self.__get_int_val(jobject, "uSat")
                
                '''
                {
                    "PRN": 28,
                    "gnssid": 0,
                    "svid": 28,
                    "az": 56.0,
                    "el": 22.0,
                    "ss": 19.0,
                    "used": true
                }
                '''
                
                if "satellites" in jobject:
                    for sat in jobject["satellites"]:
                        system_id = "GN"
                        
                        if sat["gnssid"] == 0:
                            system_id = "GP"
                        elif sat["gnssid"] == 1:
                            system_id = "SB"
                        elif sat["gnssid"] == 2:
                            system_id = "GA" # GALILEO
                        elif sat["gnssid"] == 3:
                            system_id = "PQ" # Beidou
                        elif sat["gnssid"] == 4:
                            system_id = "IM" # IMES
                        elif sat["gnssid"] == 5:
                            system_id = "QZ" # QZSS
                        elif sat["gnssid"] == 6:
                            system_id = "GL" # GLONASS
                        elif sat["gnssid"] == 7:
                            system_id = "NV" # NavIC
                        
                        name = system_id + "-" + str(sat["svid"])
                        
                        last_used_ts = 0.0
                        if sat["used"] == True:
                            last_used_ts = time.time()
                        elif name in self.satellites["data"]:
                                last_used_ts = self.satellites["data"][name]["last_used_ts"]                                
                                
                        self.satellites["data"][name] = {
                            "id": str(sat["svid"]),
                            "prn": str(sat["PRN"]),
                            "system": system_id,
                            "elevation": self.__get_float_val(sat, "el", defval=-1.0),
                            "azimuth": self.__get_float_val(sat, "az", defval=-1.0),
                            "snr": self.__get_float_val(sat, "ss", defval=-1.0),
                            "update_ts": time.time(),
                            "used": sat["used"],
                            "last_used_ts": last_used_ts
                        }                       
                        
                    self.satellites["update_ts"] = time.time()
                
                self.update_satellites_list()
                # self.logger.debug("JSON: SKY")
                # self.logger.debug("JSON: SKY: %s", json.dumps(jobject, indent=4))
                
                # self.logger.debug("JSON: datamodel: %s", repr(self.satellites))
            elif jobject["class"] == "DEVICES":
                self.logger.debug("JSON: %s: %s", jobject["class"], json.dumps(jobject, indent=4))
            elif jobject["class"] == "ERROR":
                self.logger.debug("JSON: %s: %s", jobject["class"], json.dumps(jobject, indent=4))
            elif jobject["class"] == "VERSION":
                self.logger.debug("JSON: %s: %s", jobject["class"], json.dumps(jobject, indent=4))
            elif jobject["class"] == "WATCH":
                self.logger.debug("JSON: %s: %s", jobject["class"], json.dumps(jobject, indent=4))
            else:
                self.logger.debug("JSON: UNSUPPORTED - %s: %s", jobject["class"], json.dumps(jobject, indent=4))
        except Exception as e:
            self.logger.warn("JSON parsing exception: %s", e)

    def __get_float_val(self, json_val, key, defval = 0.0):
        val = 0.0

        try:
            if key in json_val and json_val[key] != "":
                val = float(json_val[key])
            else:
                pass
                # self.logger.warn("JSON value not found!")
        except Exception as e:
            # self.logger.debug("JSON parsing exception (%s): %s", key, e)
            val = defval
        
        return val
    
    def __get_int_val(self, json_val, key, defval= 0):
        val = 0

        try:
            if json_val[key] != None and json_val[key] != "":
                val = int(json_val[key])
            else:
                self.logger.warn("JSON value not found!")
        except Exception as e:
            # self.logger.debug("JSON parsing exception (%s): %s", key, e)
            val = defval
        
        return val
