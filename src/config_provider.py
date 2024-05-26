#! /usr/bin/python3

import os
import json
import logging

from datetime import datetime


class ConfigProvider:
    def __init__(self):
        self.config_filename = "./appconfig.json"
        self.config = dict()

        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("config")

        self.__load_config()

    def __get_config_from_file(self):
        config_str = ""

        try:
            with open(self.config_filename, "r", encoding="utf-8") as jsonfile:
                self.logger.debug("config: '%s'", os.path.abspath(self.config_filename))
                config_str = jsonfile.read()
                self.logger.debug("(1) config file contents:")
                self.logger.debug("-----------------------------------")
                self.logger.debug(config_str)
                self.logger.debug("-----------------------------------")
                jsonfile.close()
        except FileNotFoundError as err:  # should this ever happen with "w+" ?
            self.logger.warn("config file not found: %s", repr(err))
            self.logger.warn("config: '%s'", os.path.abspath(self.config_filename))
            self.__create_initial_config()

            try:
                with open(self.config_filename, "r", encoding="utf-8") as jsonfile:

                    self.logger.debug(
                        "config: '%s'", os.path.abspath(self.config_filename)
                    )
                    config_str = jsonfile.read()
                    self.logger.debug("(2) config file contents:")
                    self.logger.debug("-----------------------------------")
                    self.logger.debug(config_str)
                    self.logger.debug("-----------------------------------")
                    jsonfile.close()
            except:
                self.logger.fatal("still no config!")

        return config_str

    def __load_config(self):
        self.logger.debug("loading config file ...")
        config_str = self.__get_config_from_file()

        if not config_str == None and len(config_str) > 0:
            try:
                self.config = json.loads(config_str)
                self.logger.debug("read config file successful")
            except json.JSONDecodeError as err:
                self.logger.warn("reading JSON from config file failed: %s", repr(err))
                self.__create_initial_config()

    def save(self):
        self.logger.debug("saving config file ...")
        with open(self.config_filename, "w+", encoding="utf-8") as jsonfile:

            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            self.config["last_update"] = date_time

            self.logger.debug("config: '%s'", os.path.abspath(self.config_filename))
            jsonfile.write(json.dumps(self.config, ensure_ascii=False, indent=4))
            self.logger.debug("Write successful")
            jsonfile.close()

    def __create_initial_config(self):
        self.logger.debug("creating initial config file structure ...")

        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        self.config = {
            "created": date_time,
            "last_update": date_time,
            "general": {
                "panel_refresh_cycle_sec": 10,
                "resolution": {"height": 800, "width": 1200},
            },
            "gpsd": {"hostname": "localhost", "port": 2947},
            "startup": {
                "connect_to_gpsd": True,
                "panels_shown": ["map", "satellites_list"],
            },
            "map_panel": {
                "auto_center": True,
                "initial_zoom_level": 5,
                "show_satellites_dashboard": True,
                "show_position_dashboard": True,
                "start_latitude": 0.0,
                "start_longitude": 0.0,
            },
        }

        self.save()

    def get(self):
        return self.config

    def get_param(self, path, default=None):
        # self.logger.debug("++++ path: %s", path)
        pparts = path.replace("//", "/").split("/")

        val = None

        found = False
        d = self.config
        idx = 0
        while len(pparts) > idx:
            part = pparts[idx]
            # self.logger.debug("part: %s", part)
            val = d.get(part)

            if part == "":
                idx = idx + 1
                continue

            if val != None:
                # self.logger.debug(" --->  %s: %s", part, repr(val))
                idx = idx + 1
                d = val
                found = True
            else:
                # self.logger.debug(" --->  %s: %s", part, repr(val))
                found = False
                break

        if not found:
            val = default
            self.logger.warn(
                "config parameter '%s' not found, using default: [%s]",
                path,
                repr(default),
            )

        self.logger.debug("(found: %s): %s = %s", repr(found), path, repr(val))
        return val
