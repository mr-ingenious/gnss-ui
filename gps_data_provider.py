#! /usr/bin/python3

from observer import Observer

class GpsDataProvider:
    _observer: Observer
    
    def __init__(self, observer: Observer):
        self._observer = observer
    