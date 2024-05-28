#! /usr/bin/python3

import logging
import xml.etree.ElementTree as et

from datetime import datetime


class DataTransformer:
    def __init__(self):
        logging.config.fileConfig("gnss-ui/assets/log.ini")
        self.logger = logging.getLogger("app")

    def to_gpx(self, rec_info, data, filename="track.gpx"):
        gpx = et.Element("gpx")
        metadata = et.SubElement(gpx, "metadata")
        et.SubElement(metadata, "name").text = rec_info["name"]
        et.SubElement(metadata, "desc").text = rec_info["description"]
        et.SubElement(metadata, "author").text = "gnss-ui"

        ts = datetime.fromtimestamp(rec_info["ts_start"])
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")

        et.SubElement(metadata, "time").text = ts_str

        trk = et.SubElement(gpx, "trk")
        et.SubElement(trk, "name").text = "track [" + ts_str + "]"

        invalid_record = True
        trkseg = None

        for i in range(0, len(data) - 1):
            if data[i][1] == 0.0 and data[i][2] == 0.0:
                invalid_record = True
                trkseg = None
                continue

            if data[i][1] != 0.0 and data[i][2] != 0.0 and invalid_record:
                trkseg = et.SubElement(trk, "trkseg")
                invalid_record = False

            trkpt = et.SubElement(
                trkseg, "trkpt", lat=str(data[i][1]), lon=str(data[i][2])
            )

            ts = datetime.fromtimestamp(data[i][9])
            ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
            et.SubElement(trkpt, "time").text = ts_str
            et.SubElement(trkpt, "ele").text = str(data[i][3])
            et.SubElement(trkpt, "hdop").text = str(data[i][5])
            et.SubElement(trkpt, "pdop").text = str(data[i][6])
            et.SubElement(trkpt, "vdop").text = str(data[i][7])

        et.indent(gpx)
        # et.dump(gpx)
        # self.logger.debug("GPX:" + str(et.tostring(gpx, encoding="utf-8")))
        tree = et.ElementTree(gpx)
        with open(filename, "w") as f:
            tree.write(f, encoding="unicode", xml_declaration=True)

    # def to_kml(self, rec_info, data, filename="track.kml"):
    #    kml = et.Element("kml")

    #    self.logger.debug("KML: %s", et.tostring(kml))

    #    return kml
