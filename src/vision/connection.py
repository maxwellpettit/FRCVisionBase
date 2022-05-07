#!/usr/bin/env python3

"""
----------------------------------------------------------------------------
Authors:     FRC Team 4145

Description: This script uses a generated CV2 pipeline to process a camera
             stream and publish results to NetworkTables.  This script is
             designed to work on the FRCVision Raspberry Pi image.
----------------------------------------------------------------------------
"""

import time
import sys
from networktables import NetworkTablesInstance
import json


# Network Table constants
SMART_DASHBOARD = "SmartDashboard"
CONNECTION_STATUS = "connect"
VISION_TABLE = "vision"
CAMERA_SELECTION = "CameraSelection"


class Connection:

    def __init__(self, logger, server, team):
        self.logger = logger
        self.server = server
        self.team = team
        self.startNetworkTables()

    def startNetworkTables(self):
        """
        Connect to the Network Tables as a client or start the server locally.
        """

        ntinst = NetworkTablesInstance.getDefault()

        if self.server:
            self.logger.logMessage("Setting up NetworkTables server...")
            ntinst.startServer()
        else:
            self.logger.logMessage("Setting up NetworkTables client for team {}".format(self.team))
            ntinst.startClientTeam(self.team)

    def publishValues(self, contour_data):
        """
        Publish coordinates/values to the 'vision' network table.
        """

        ntinst = NetworkTablesInstance.getDefault()
        table = ntinst.getTable(SMART_DASHBOARD).getSubTable(VISION_TABLE)

        contour_string = self.convertToString(contour_data)
        table.putValue("contour_data", contour_string)

        self.logger.logMessage(contour_string)

    def convertToString(self, contour_data):
        """
        Output list of all contour_data in JSON format
        """
        contour_string = '[' + ', '.join(map(str,contour_data)) + ']'

        return contour_string
