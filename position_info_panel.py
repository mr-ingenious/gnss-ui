#! /usr/bin/python3

import gi
import time

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from panel import ScrolledPanel


class PositionInfoPanel(ScrolledPanel):
    def __init__(self):
        super().__init__()
        self.last_rmc_update = time.time()
        self.last_gns_update = time.time()
        self.last_gsa_update = time.time()
        self.last_gga_update = time.time()

        self.set_css_classes(["position_panel", "panel"])

        self.grid = Gtk.Grid()

        self.grid.set_row_spacing(10)
        self.grid.set_column_spacing(10)

        self.grid.insert_column(1)
        self.grid.insert_column(1)

        self.panel_label = Gtk.Label(label="Position")
        self.panel_label.set_css_classes(["panel_title"])
        self.set_child(self.panel_label)
        self.set_child(self.grid)

        self.__add_to_grid("rmc.latitude", "Latitude:", 1)
        self.__add_to_grid("rmc.latitude_dir", "Latitude direction:", 2)
        self.__add_to_grid("rmc.longitude", "Longitude:", 3)
        self.__add_to_grid("rmc.longitude_dir", "Longitude direction:", 4)

        self.__add_to_grid("rmc.speed_ovr_grnd", "Speed over ground:", 5)
        self.__add_to_grid("rmc.true_course", "True course:", 6)

        self.__add_to_grid("rmc.status", "Status:", 7)
        self.__add_to_grid("gns.num_sats", "Number of satellites:", 8)
        self.__add_to_grid("gns.altitude", "Altitude:", 9)

        self.__add_to_grid("gns.hdop", "HDOP:", 10)
        self.__add_to_grid("gsa.pdop", "PDOP:", 11)
        self.__add_to_grid("gsa.vdop", "VDOP:", 12)

        self.__add_to_grid("gga.gps_qual", "GPS quality:", 13)
        self.__add_to_grid("gga.horizontal_dil", "Horizontal dilution:", 14)
        self.__add_to_grid("gga.ref_station_id", "Reference station ID:", 15)

        self.set_vexpand(True)

    def __add_to_grid(self, _name, _label, _row):
        self.grid.insert_row(_row)

        new_label = Gtk.Label(name=_name + "_label", label=_label)
        new_label.set_css_classes(["label"])
        self.grid.attach(new_label, 1, _row, 1, 1)

        new_value = Gtk.Label(name=_name + "_value", label="---")
        new_value.set_css_classes(["value"])
        self.grid.attach(new_value, 2, _row, 1, 1)

    def __change_value(self, name, value):
        next_element = self.grid.get_first_child()

        while next_element != None:
            if next_element.get_name() == name + "_value":
                next_element.set_label(value)
                break
            else:
                next_element = next_element.get_next_sibling()

    def update(self, msg):
        if msg["type"] == "RMC" and (time.time() - self.last_rmc_update >= 1):
            self.last_rmc_update = time.time()

            self.__change_value("rmc.latitude", msg["latitude"])
            self.__change_value("rmc.latitude_dir", msg["latitude_dir"])
            self.__change_value("rmc.longitude", msg["longitude"])
            self.__change_value("rmc.longitude_dir", msg["longitude_dir"])
            self.__change_value("rmc.status", msg["status"])
            self.__change_value("rmc.speed_ovr_grnd", msg["speed"])
            self.__change_value("rmc.true_course", msg["track_deg"])

        if msg["type"] == "GNS" and (time.time() - self.last_gns_update >= 1):
            self.last_gns_update = time.time()

            self.__change_value("gns.hdop", msg["hdop"])
            self.__change_value("gns.num_sats", msg["satellites_in_view"])
            self.__change_value("gns.altitude", msg["ortho_height_meters"])

        if msg["type"] == "GSA" and (time.time() - self.last_gsa_update >= 1):
            self.last_gsa_update = time.time()

            self.__change_value("gsa.pdop", msg["pdop"])
            self.__change_value("gsa.hdop", msg["hdop"])
            self.__change_value("gsa.vdop", msg["vdop"])

        if msg["type"] == "GGA" and (time.time() - self.last_gga_update >= 1):
            self.last_gga_update = time.time()

            self.__change_value("gga.lat", msg["latitude"])
            self.__change_value("gga.lat_dir", msg["latitude_dir"])
            self.__change_value("gga.lon", msg["longitude"])
            self.__change_value("gga.lon_dir", msg["longitude_dir"])
            self.__change_value("gga.gps_qual", msg["gps_quality"])
            self.__change_value("gga.num_sats", msg["satellites_in_view"])
            self.__change_value("gga.horizontal_dil", msg["hdop"])
            self.__change_value("gga.altitude", msg["antenna_asl"])
            self.__change_value("gga.altitude_units", msg["antenna_asl_unit_meters"])
            self.__change_value("gga.geo_sep", msg["geosep"])
            self.__change_value("gga.geo_sep_units", msg["geosep_unit_meters"])
            self.__change_value("gga.age_gps_data", msg["gps_data_age"])
            self.__change_value("gga.ref_station_id", msg["ref_station_id"])

        # if msg["type"] == "VTG":
        #    self.__change_value ( "vtg.true_track", str(msg.true_track))
        #    self.__change_value ( "vtg.true_track_sym", str(msg.true_track_sym))
        #    self.__change_value ( "vtg.mag_track", str(msg.mag_track))
        #    self.__change_value ( "vtg.mag_track_sym", str(msg.mag_track_sym))
        #    self.__change_value ( "vtg.spd_over_grnd_kts", str(msg.spd_over_grnd_kts))
        #    self.__change_value ( "vtg.spd_over_grnd_kts_sym", str(msg.spd_over_grnd_kts_sym))
        #    self.__change_value ( "vtg.spd_over_grnd_kmph", str(msg.spd_over_grnd_kmph))
        #    self.__change_value ( "vtg.spd_over_grnd_kmph_sym", str(msg.spd_over_grnd_kmph_sym))
        #    self.__change_value ( "vtg.faa_mode", str(msg.faa_mode))
