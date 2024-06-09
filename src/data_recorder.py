#! /usr/bin/python3

import logging
import time

from enum import Enum

from datetime import datetime

import sqlite3


class DataRecorderStatus(Enum):
    RECORDING_IDLE = 1
    RECORDING_ACTIVE = 2
    RECORDING_PAUSED = 3


class RecordingInfo:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.description = ""
        self.type = ""
        self.ts_start = 0
        self.ts_end = 0


class DataRecorder:
    def __init__(self, capture_interval=1):
        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("recorder")

        self.schema_version = "0.0.1"

        self.capture_interval = capture_interval
        self.last_record_ts = 0
        self.state = DataRecorderStatus.RECORDING_IDLE
        self.current_recording = None

        self.__init_db()

    def start_pause_recording(self):
        if self.state == DataRecorderStatus.RECORDING_IDLE:
            self.state = DataRecorderStatus.RECORDING_ACTIVE
            if self.current_recording == None:
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%d %H:%M:%S")
                name_date_time = now.strftime("%Y%m%dT%H%M%S")

                self.current_recording = RecordingInfo
                self.current_recording.name = "Recording_" + name_date_time
                self.current_recording.description = "Recording from " + date_time
                self.current_recording.ts_start = time.time()
                self.current_recording.ts_end = 0
                self.current_recording.type = ""
                self.logger.info("recording '%s' started", self.current_recording.name)
                self.current_recording.id = self.__add_recording_info(
                    self.current_recording
                )
                return True
            else:
                self.logger.warn("current recording not None!")
                # TODO: close current recording, set to None and start a new one
                return False
        elif self.state == DataRecorderStatus.RECORDING_ACTIVE:
            self.state = DataRecorderStatus.RECORDING_PAUSED
            self.logger.info("recording '%s' paused", self.current_recording.name)
            return True
        elif self.state == DataRecorderStatus.RECORDING_PAUSED:
            self.state = DataRecorderStatus.RECORDING_ACTIVE
            self.logger.info("recording '%s' reactivated", self.current_recording.name)
            return True
        else:
            self.logger.warn("request to start/stop recording, but in wrong state")

        return False

    def stop_recording(self):
        if self.state != DataRecorderStatus.RECORDING_IDLE:
            self.state = DataRecorderStatus.RECORDING_IDLE
            self.current_recording.ts_end = time.time()
            self.__update_recording_info(self.current_recording)
            self.logger.info("recording '%s' stopped", self.current_recording.name)
            self.current_recording = None
            return True
        else:
            self.logger.warn("request to pause recording, but in wrong state")

        return False

    def get_status(self):
        return self.state

    def get_status_str(self):
        if self.state == DataRecorderStatus.RECORDING_ACTIVE:
            return "active"
        elif self.state == DataRecorderStatus.RECORDING_IDLE:
            return "idle"
        elif self.state == DataRecorderStatus.RECORDING_PAUSED:
            return "paused"

    def get_current_recording(self):
        return self.current_recording

    def update(self, data):
        if self.state == DataRecorderStatus.RECORDING_ACTIVE:
            if time.time() - self.last_record_ts > self.capture_interval:
                self.last_record_ts = time.time()
                self.logger.debug("capturing data ..")
                self.__add_position_info(data.position, self.current_recording)
                self.__add_satellites_info(data.satellites, self.current_recording)

    def __init_db(self):
        self.logger.info("initialize db")
        self.connection = sqlite3.connect("gnss_ui.db", check_same_thread=False)
        cursor = self.connection.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS version (schema, ts)")
        except sqlite3.OperationalError as e:
            self.logger.warn("version table: %s", str(e))

        try:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS recordings (id integer primary key autoincrement, name, description, type, ts_start, ts_end)"
            )
        except sqlite3.OperationalError as e:
            self.logger.warn("recordings table: %s", str(e))

        try:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS position_records (id integer primary key autoincrement, latitude, longitude, altitude, speed_kph, hdop, pdop, vdop, gps_quality, ts, recording_id)"
            )
        except sqlite3.OperationalError as e:
            self.logger.warn("position_records table: %s", str(e))

        try:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS satellite_records (id integer primary key autoincrement, prn, azimuth, elevation, snr, used, ts, recording_id)"
            )
        except sqlite3.OperationalError as e:
            self.logger.warn("satellite_records table: %s", str(e))

        self.connection.commit()

    def __add_recording_info(self, rec_info):
        sql = """ INSERT INTO recordings
                (name, description, type, ts_start, ts_end)
                VALUES (?,?,?,?,?)"""

        values = (
            rec_info.name,
            rec_info.description,
            rec_info.type,
            rec_info.ts_start,
            rec_info.ts_end,
        )
        cursor = self.connection.cursor()
        cursor.execute(sql, values)

        self.connection.commit()
        return cursor.lastrowid

    def __update_recording_info(self, rec_info):
        sql = """ UPDATE recordings SET
                name = ?, description = ? , type = ? , ts_start = ? , ts_end = ?
                where id = ?"""

        values = (
            rec_info.name,
            rec_info.description,
            rec_info.type,
            rec_info.ts_start,
            rec_info.ts_end,
            rec_info.id,
        )
        cursor = self.connection.cursor()
        cursor.execute(sql, values)

        self.connection.commit()

    def __add_position_info(self, position, rec_info):
        sql = """ INSERT INTO position_records
                (latitude, longitude, altitude, speed_kph,
                hdop, pdop, vdop, gps_quality, ts, recording_id)
                VALUES (?,?,?,?,?,?,?,?,?,?)"""
        values = (
            position["data"]["latitude"]["decimal"],
            position["data"]["longitude"]["decimal"],
            position["data"]["altitude"]["msl"],
            position["data"]["sog"]["kph"],
            position["data"]["dop"]["hdop"],
            position["data"]["dop"]["pdop"],
            position["data"]["dop"]["vdop"],
            position["data"]["gps_quality"]["indicator"],
            position["update_ts"],
            rec_info.id,
        )

        cursor = self.connection.cursor()
        cursor.execute(sql, values)
        self.connection.commit()
        return cursor.lastrowid

    def __add_satellites_info(self, satellites, rec_info):
        sql = """ INSERT INTO satellite_records
                (prn, azimuth, elevation, snr, used, ts, recording_id)
                VALUES (?,?,?,?,?,?,?)"""

        keys = sorted(satellites["data"].keys())

        idx = 0
        cursor = self.connection.cursor()

        for prn in keys:
            # self.logger.debug("--- satellite %s", k)
            currsat = satellites["data"].get(prn)

            used = currsat["used"]
            elevation = currsat["elevation"]
            azimuth = currsat["azimuth"]
            snr = currsat["snr"]

            idx += 1

            values = (
                prn,
                elevation,
                azimuth,
                snr,
                used,
                satellites["update_ts"],
                rec_info.id,
            )

            cursor.execute(sql, values)

        self.connection.commit()

    def get_recordings(self):
        sql = """ SELECT * FROM recordings"""

        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def get_recording_by_id(self, id):
        recording = dict()
        sql = """ SELECT * FROM recordings
                    WHERE id = ?"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        recordings = cursor.fetchall()

        if recordings != None:
            recording = {
                "id": recordings[0][0],
                "name": recordings[0][1],
                "description": recordings[0][2],
                "type": recordings[0][3],
                "ts_start": recordings[0][4],
                "ts_end": recordings[0][5],
            }

        return recording

    def delete_recording_by_id(self, recording_id):
        self.logger.info(
            "delete recording and all associated data with id %i", recording_id
        )
        sql_1 = """ DELETE FROM recordings
                WHERE id = ?"""
        sql_2 = """ DELETE FROM position_records
                WHERE recording_id = ?"""
        sql_3 = """ DELETE FROM satellite_records
                WHERE recording_id = ?"""
        cursor = self.connection.cursor()
        id = recording_id

        cursor.execute(sql_1, (id,))
        cursor.execute(sql_2, (id,))
        cursor.execute(sql_3, (id,))

        self.connection.commit()

    def get_position_data_by_id(self, id):
        sql = """ SELECT * FROM position_records where recording_id = ?"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        return cursor.fetchall()

    def get_position_data_count_by_id(self, id):
        sql = """ SELECT count(*) FROM position_records where recording_id = ?"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        return cursor.fetchone()[0]

    def get_position_data_count(self):
        sql = """ SELECT count(*) FROM position_records"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        return cursor.fetchone()[0]

    def get_satellite_data_by_id(self, id):
        sql = """ SELECT * FROM satellite_records where recording_id = ?"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        return cursor.fetchall()

    def get_satellite_data_count_by_id(self, id):
        sql = """ SELECT count(*) FROM satellite_records where recording_id = ?"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        return cursor.fetchone()[0]

    def get_satellite_data_count(self):
        sql = """ SELECT count(*) FROM satellite_records"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        return cursor.fetchone()[0]

    def reset(self):
        self.logger.info("db reset")
        cursor = self.connection.cursor()

        self.stop_recording()

        cursor.execute("DROP TABLE IF EXISTS recordings")
        cursor.execute("DROP TABLE IF EXISTS satellite_records")
        cursor.execute("DROP TABLE IF EXISTS position_records")

        self.connection.commit()

        self.__init_db()
        pass
