#! /usr/bin/python3

# import pynmea2
from observer import Observer

import logging, logging.config
import json


class GpsdParser:
    _observer: Observer

    def __init__(self, observer: Observer):
        self._observer = observer
        self.data = ""

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("gpsd")

        # logging.basicConfig(
        #    level=logging.INFO,
        #    format="[%(asctime)s %(name)s] [%(levelname)s] %(message)s",
        #    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
        # )

    def add_data(self, new_data):
        self.data += new_data
        # print (new_data)
        self.__parse()

    def reset(self):
        self.data = ""

    def __parse(self):
        self.__parse_internal()

    def __parse_internal(self):
        # find first occurrence of "$" and "*" as start of checksum
        # print("###################################################################")

        if len(self.data) > 4000:
            self.logger.warning("parsing: HANDBRAKE !!!!")
            print("============================================================")
            self.logger.debug(self.data)
            print("============================================================")
            self.data = ""
            return

        # print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        # print("Buffer to parse: ")
        # print(self.data)
        # print(
        #    ">>> loop start, data_len:",
        #    len(self.data),
        #    ", first chars: ",
        #    self.data[0:10],
        # )
        while True:
            # print(">>> in loop ...")
            self.data = (
                self.data.replace("\r", "")
                .replace("\n", "")
                .replace("\r\n", "")
                .strip()
                .rstrip()
            )

            # print(
            #    ">>> loop,       data_len:",
            #    len(self.data),
            #    ", first chars: ",
            #    self.data[0:10],
            # )

            nmea_start = self.data.find("$", 0)
            json_start = self.data.find("{", 0)
            nmea_cs_start = self.data.find("*", nmea_start)

            if (
                nmea_start >= 0
                and nmea_cs_start != -1
                and (nmea_cs_start + 3) >= nmea_start
                and nmea_start < json_start
            ) or (
                nmea_start >= 0
                and nmea_cs_start != -1
                and (nmea_cs_start + 3) >= nmea_start
                and json_start == -1
            ):
                self.logger.debug("found complete NMEA string, try to parse ...")
                # found full NMEA string --> parse and remove from input buffer
                msg_str = self.data[nmea_start : nmea_cs_start + 3]
                self.logger.debug(
                    "NMEA:'%s', [%i, %i]", msg_str, nmea_start, nmea_cs_start
                )
                self.__parse_nmea_string(msg_str)
                self.data = self.data[nmea_cs_start + 3 :]
            else:
                if json_start >= 0:
                    self.logger.debug("JSON: found {, try to parse JSON ...")
                    self.__parse_json()

                    if self.data.find("$", 0) >= 0 and self.data.find("*", 0) >= 0:
                        # still more nmea strings found
                        continue
                    else:
                        break
                else:
                    # print(">>> NOTHING FOUND!")
                    # print(self.data)
                    break

            # print(">>> parsing   (end): ", len(self.data))
        # print(">>> loop done,  data_len:", len(self.data))

    def __parse_internal_bak(self):
        # find first occurrence of "$" and "*" as start of checksum
        # print("###################################################################")

        while True:
            # print(">>> in loop ...")
            self.data = (
                self.data.replace("\r", "")
                .replace("\n", "")
                .replace("\r\n", "")
                .strip()
                .rstrip()
            )
            nmea_start = self.data.find("$", 0)
            json_start = self.data.find("{", 0)
            n_cs_start = self.data.find("*", nmea_start)

            # print ("data to parse: '", self.data,  "'")
            # print(">>> n_start:   ", n_start)
            # print(">>> n_cs_start:", n_cs_start)
            # print(">>> str_len:   ", len(self.data))
            # check if string is long enough, then extract nmea string
            if (
                len(self.data) >= (n_cs_start + 3 - nmea_start)
                and nmea_start >= 0
                and n_cs_start > 0
            ):
                msg_str = self.data[nmea_start : n_cs_start + 3]
                # print(">>> NMEA:'", msg_str + "', [", n_start, ", ", n_cs_start, "]")
                self.__parse_nmea_string(msg_str)
                self.data = self.data[n_cs_start + 3 :]
                # print(">>> remaining: ", self.data)

            if n_cs_start == -1 and nmea_start >= 0:
                # print(">>> parsing done (case 1)")
                # print(">>> ", self.data)
                self.__parse_json()
                self.data = self.data[nmea_start:]
                break

            if nmea_start == -1:
                # print(">>> parsing done (case 2)")
                # print(">>> ", self.data)
                self.__parse_json()
                self.data = ""
                break
        # msg_string = self.data.split ("$")

    # https://gpsd.gitlab.io/gpsd/gpsd_json.html
    def __parse_json(self):

        n_start = self.data.find("{", 0)

        if n_start > 0:
            self.logger.debug("JSON: correcting string")
            self.data = self.data[n_start:]

        bct = 0
        i = 0

        while True:
            if i == 0:
                # print(
                #    "----------------------------------------------------------------------------"
                # )
                pass

            if i >= len(self.data):
                # print("JSON: index exceeded. break")
                break

            # print(self.data[i], end="")
            if self.data[i] == "{":
                if bct == 0:
                    n_start = i
                # print("+", end="")
                bct += 1

            elif self.data[i] == "}":
                # print("-", end="")
                bct -= 1

            if bct == 0:
                try:
                    msg_str = self.data[n_start : i + 1]
                    # print(
                    #    "JSON: done data_len=", len(msg_str), ",i=", i
                    # )  # , ", chars: " , self.data[0])
                    n_start = 0
                    y = json.loads(msg_str)
                    self.logger.debug("JSON: %s", json.dumps(y, indent=4))
                    self._observer.updateJSON(y)
                    self.data = self.data[i + 1 :]
                    self.data = (
                        self.data.replace("\r", "")
                        .replace("\n", "")
                        .replace("\r\n", "")
                        .strip()
                        .rstrip()
                    )

                    i = 0
                    return
                except Exception as e:
                    self.logger.warning(
                        "\nJSON: exception ("
                        + str(e)
                        + "), string:\n'"
                        + msg_str
                        + "'\n"
                    )
                    self.logger.debug("JSON: exception. break")
                    break

            if len(self.data) == 0:
                # print("JSON: len = 0. break.")
                break

            i += 1
        # print(
        # "JSON: parsing done, remaining symbols:",
        # self.data[0:10],
        # ", length: ",
        #    len(self.data),
        # )

    def __parse_nmea_string(self, msg_str):
        fields = msg_str.split("*")
        self.logger.debug("=== payload: %s", fields[0])
        self.logger.debug("=== checksum: %s", fields[1])
        payload = fields[0].split(",")
        msg = dict()

        msg["talker"] = payload[0][1:3]
        msg["type"] = payload[0][3:]
        msg["checksum"] = fields[1]
        msg["payload_raw"] = fields[0]
        msg["valid"] = False

        if msg["type"] == "RMC":
            self.__parse_nmea_rmc(msg, payload)
        elif msg["type"] == "GSA":
            self.__parse_nmea_gsa(msg, payload)
        elif msg["type"] == "GSV":
            self.__parse_nmea_gsv(msg, payload)
        elif msg["type"] == "GGA":
            self.__parse_nmea_gga(msg, payload)
        elif msg["type"] == "GSV":
            self.__parse_nmea_gsv(msg, payload)
        elif msg["type"] == "VTG":
            self.__parse_nmea_vtg(msg, payload)
        elif msg["type"] == "GNS":
            self.__parse_nmea_gns(msg, payload)
        else:
            self.logger.debug("parse_nmea_string: unsupported nmea message!")

        if msg["valid"] == True:
            self._observer.updateNmea(msg)

    def __parse_nmea_rmc(self, msg, payload):
        if len(payload) < 12:
            self.logger.debug("malformed nmea string: '%s'", payload)
            return

        msg["time_utc"] = payload[1]
        msg["status"] = payload[2]
        msg["latitude"] = payload[3]
        msg["latitude_dir"] = payload[4]
        msg["longitude"] = payload[5]
        msg["longitude_dir"] = payload[6]
        msg["sog_kts"] = payload[7]  # speed over ground
        msg["cog_deg"] = payload[8]  # course over ground, degrees, true north
        msg["date"] = payload[9]
        msg["magvar_deg"] = payload[10]
        msg["e_w"] = payload[11]
        msg["valid"] = True

    def __parse_nmea_gns(self, msg, payload):
        if len(payload) < 13:
            self.logger.warn("malformed nmea string: '%s'", payload)
            return

        msg["time_utc"] = payload[1]
        msg["latitude"] = payload[2]
        msg["latitude_dir"] = payload[3]
        msg["longitude"] = payload[4]
        msg["longitude_dir"] = payload[5]
        msg["mode"] = payload[6]
        msg["satellites_in_use"] = payload[7]
        msg["hdop"] = payload[8]
        msg["ortho_height_meters"] = payload[9]
        msg["age_diff_data"] = payload[10]
        msg["ref_station_id"] = payload[11]
        msg["safe_position"] = payload[12]
        msg["valid"] = True

    def __parse_nmea_gsa(self, msg, payload):
        if len(payload) < 18:
            self.logger.warn("malformed nmea string: '%s'", payload)
            return

        msg["smode"] = payload[1]
        msg["mode"] = payload[2]
        msg["id_1"] = payload[3]
        msg["id_2"] = payload[4]
        msg["id_3"] = payload[5]
        msg["id_4"] = payload[6]
        msg["id_5"] = payload[7]
        msg["id_6"] = payload[8]
        msg["id_7"] = payload[9]
        msg["id_8"] = payload[10]
        msg["id_9"] = payload[11]
        msg["id_10"] = payload[12]
        msg["id_11"] = payload[13]
        msg["id_12"] = payload[14]
        msg["pdop"] = payload[15]
        msg["hdop"] = payload[16]
        msg["vdop"] = payload[17]
        msg["valid"] = True

        if len(payload) > 18:
            # print("GSA: found extra system ID")
            msg["system_id"] = payload[18]

    def __parse_nmea_gsv(self, msg, payload):
        if len(payload) < 8:  # TODO: check correct condition
            self.logger.warn("malformed nmea string: '%s'", payload)
            return

        msg["num_msg"] = payload[1]
        msg["msg_num"] = payload[2]
        msg["satellites_in_view"] = payload[3]

        num_fields = 3
        num_sat_info = 0
        # print("payload_len", len(payload))
        # print("range_end", (1 + int((len(payload) - 4) / 4)))
        for i in range(1, (1 + int((len(payload) - 4) / 4))):
            msg["sat_" + str(i) + "_num"] = payload[4 * i]
            msg["sat_" + str(i) + "_elevation_deg"] = payload[(4 * i) + 1]
            msg["sat_" + str(i) + "_azimuth_deg"] = payload[(4 * i) + 2]
            msg["sat_" + str(i) + "_snr_db"] = payload[(4 * i) + 3]
            num_sat_info += 1
            msg["num_sat_info_in_msg"] = num_sat_info
            num_fields += 4

        msg["valid"] = True

        if len(payload) % 4 > 0:
            # print("GSV: found extra system ID")
            msg["system_id"] = payload[++num_fields]

    def __parse_nmea_gga(self, msg, payload):
        if len(payload) < 15:
            self.logger.warn("malformed nmea string: '%s'", payload)
            return

        msg["time_utc"] = payload[1]
        msg["latitude"] = payload[2]
        msg["latitude_dir"] = payload[3]  # N/S
        msg["longitude"] = payload[4]
        msg["longitude_dir"] = payload[5]  # E/W
        msg["gps_quality"] = payload[6]
        # GPS quality:
        # 0 = Fix not available or invalid,
        # 1 = GPS SPS Mode, fix valid,
        # 2 = Differential GPS, SPS Mode, fix valid,
        # 3 = GPS PPS Mode, fix valid,
        # 4 = Real Time Kinematic. System used in RTK mode with fixed integers,
        # 5 = Float RTK. Satellite system used in RTK mode, floating integers,
        # 6 = Estimated (dead reckoning) Mode,
        # 7 = Manual Input Mode,
        # 8 = Simulator Mode
        msg["satellites_in_use"] = payload[7]
        msg["hdop"] = payload[8]
        msg["antenna_asl"] = payload[9]
        msg["antenna_asl_unit_meters"] = payload[10]
        msg["geosep"] = payload[11]
        msg["geosep_unit_meters"] = payload[12]
        msg["gps_data_age"] = payload[13]
        msg["ref_station_id"] = payload[14]
        msg["valid"] = True

    def __parse_nmea_vtg(self, msg, payload):
        if len(payload) < 10:
            self.logger.warn("malformed nmea string: '%s'", payload)
            return

        msg["cog_deg_true"] = payload[1]  # course over ground, degrees true
        msg["true_north"] = payload[2]
        msg["cog_mag"] = payload[3]  # course over ground, degrees magnetic
        msg["cog_mag_relative_north"] = payload[4]
        msg["sog_kts"] = payload[5]  # speed over ground, knots
        msg["unit_kts"] = payload[6]  # N
        msg["sog_kph"] = payload[7]  # speed over ground, kph
        msg["unit_kph"] = payload[8]  # K
        msg["mode"] = payload[
            9
        ]  # a: autonomous, d: differential, e: estimated, m: manual, s: simulator, n: invalid data
        msg["valid"] = True
