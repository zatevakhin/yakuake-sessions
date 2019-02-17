#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from ConfigManager import ConfigManager
from PyQt5 import QtDBus
import argparse
import logging
import os


Yakuake = namedtuple('Yakuake', ['sessions', 'tabs', 'window'])


LAYOUTS = {
    "1F": "addSession",
    "2H": "addSessionTwoHorizontal",
    "2V": "addSessionTwoVertical",
    "4Q": "addSessionQuad"
}


class YakuakeSessions:
    def __init__(self, config):
        self.__config: ConfigManager = ConfigManager(config)
        self.__yakuake = Yakuake(
            sessions=QtDBus.QDBusInterface("org.kde.yakuake", "/yakuake/sessions", "org.kde.yakuake"),
            tabs=QtDBus.QDBusInterface("org.kde.yakuake", "/yakuake/tabs", "org.kde.yakuake"),
            window=QtDBus.QDBusInterface("org.kde.yakuake", "/yakuake/window", "org.kde.yakuake")
        )

    def __find_saved_session(self, alias):
        for session in list(self.__config.get("sessions", [])):
            if session.get("alias", None) == alias:
                return session


    def __create_session(self, layout: str):
        return list(map(int, self.__yakuake.sessions.call(layout).arguments())).pop()

    def __get_terminal_ids_for_session(self, sessionId):
        first = list(self.__yakuake.sessions.call("terminalIdsForSessionId", sessionId).arguments()).pop()
        return list(map(int, first.split(",")))

    def __yakuake_run_command(self, terminalId, command):
        self.__yakuake.sessions.call("runCommandInTerminal", terminalId, command);

    def run(self, args):
        if args.run is None:
            logging.error("Nothing to run")
            return

        aliases = list(str(args.run).split(","))

        for alias in aliases:
            self.__execute_session(self.__find_saved_session(alias))

    def __execute_session(self, session):
        layout = LAYOUTS.get(session.get("layout"), None)
        if not layout:
            logging.error("not layout")
            return

        title = session.get("title", None)
        if not title:
            logging.error("not title")
            return

        commands = session.get("commands", None)
        if not commands:
            logging.error("not commands")
            return

        sessionId = self.__create_session(layout)
        self.__yakuake.tabs.call("setTabTitle", sessionId, title);

        terminalIds = self.__get_terminal_ids_for_session(sessionId)

        commands = list(reversed(commands))

        for terminalId in terminalIds:
            if not commands:
                continue

            self.__yakuake_run_command(terminalId, commands.pop())


def main():
    configLocation = os.path.join(os.getenv("HOME"), '.yakuake-sessions.json')

    yakuake = YakuakeSessions(configLocation)

    parser = argparse.ArgumentParser()

    parser.add_argument('--run')
    args = parser.parse_args()

    yakuake.run(args)

if __name__ == '__main__':
    main()
