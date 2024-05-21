#! /usr/bin/python3

from abc import ABC, abstractmethod

class Observer (ABC):
    @abstractmethod
    def updateNmea (self, msg) -> None:
        pass

    @abstractmethod
    def updateJSON (self, msg) -> None:
        pass

''''
class Subject (ABC):
    @abstractmethod
    def attach (self, observer: Observer) -> None:
        pass

    @abstractmethod
    def detach (self, observer: Observer) -> None:
        pass

    @abstractmethod
    def notify (self) -> None:
        pass
'''
