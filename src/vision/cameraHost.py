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
import json
from cscore import CameraServer, VideoSource, UsbCamera
from .constants import Constants


class CameraHost:

    # Vision camera
    vision_camera = None
    # Source for outputting OpenCV frames
    cv_source = None

    def __init__(self, logger, camera_configs, connection):
        self.logger = logger
        self.camera_configs = camera_configs
        self.connection = connection

        self.startCamera()

    def startCamera(self):
        """
        Start the camera listed first in the camera config
        """

        if (len(self.camera_configs) > 0):
            # Start vision camera
            camera_config = self.camera_configs[0]
            (parsed_width, parsed_height) = self.parseDimensions(camera_config)
            self.vision_camera = self.startVisionCamera(camera_config)
            time.sleep(1)

            # Start custom output stream
            if (Constants.ENABLE_CUSTOM_STREAM):
                self.cv_source = self.startOutputSource(parsed_width, parsed_height)

    def startVisionCamera(self, config):
        """
        Start running the vision camera.
        """

        self.logger.logMessage("Starting camera '{}' on {}".format(config.name, config.path))
        inst = CameraServer.getInstance()
        camera = UsbCamera(config.name, config.path)

        camera.setConfigJson(json.dumps(config.config))
        camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        return camera

    def parseDimensions(self, camera_config):
        """
        Parse the width and height of the camera.
        """

        width = None
        height = None
        try:
            width = camera_config.config["width"]
            height = camera_config.config["height"]
        except KeyError:
            self.logger.logMessage("Could not read camera width/height")

        return (width, height)

    def startOutputSource(self, width, height):
        """
        Create an output source and server to ouput custom frames.
        """

        self.logger.logMessage("Starting Custom Output Stream...")

        inst = CameraServer.getInstance()
        cv_source = inst.putVideo("vision", width, height)

        return cv_source

    def readVisionFrame(self):
        """
        Reads the latest frame from the camera server instance to pass to opencv.
        :param camera: The camera to read from
        :return: The latest frame
        """

        frame = None
        if (self.vision_camera is not None):
            inst = CameraServer.getInstance()
            cv_sink = inst.getVideo(camera=self.vision_camera)

            (frame_time, frame) = cv_sink.grabFrame(None)

        return frame

    def outputVisionFrame(self, frame):
        """
        Output an OpenCV frame to the custom vision camera server.
        """

        if (self.cv_source is not None):
            self.cv_source.putFrame(frame)
