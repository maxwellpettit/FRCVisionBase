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
import numpy as np
import cv2
import json
from . import CameraHost, Connection, Constants, Pipeline, Logger


class ContourData:
    def __init__(self, cx, cy, box):
        # X coordinate of the contour center
        self.cx = cx
        # Y coordinate of the contour center
        self.cy = cy
        # Minimum containing box of contour
        self.box = box

    # Convert contour data to string
    def __str__(self):
        return '{cx: ' + str(self.cx) + ', cy: ' + str(self.cy) + '}'


class VisionProcessor:

    def __init__(self, logger: Logger, connection: Connection, camera_host: CameraHost):
        self.logger = logger
        self.connection = connection
        self.camera_host = camera_host
        self.pipeline = Pipeline()

    def processFrame(self, frame, pipeline: Pipeline):
        """
        Performs extra processing on the pipeline's outputs.
        :param pipeline: The pipeline that just processed an image
        :return: The center coordinates of the target
        """

        contour_data = []

        try:
            # Process the CV2 Pipeline
            pipeline.process(frame)

            # Populate data from contours
            contour_data = self.calculateContourData(pipeline)

        except (ZeroDivisionError):
            self.logger.logMessage("Divide by 0 exception in Pipeline")

        return contour_data

    def calculateContourData(self, pipeline: Pipeline):
        """
        Populate the various contour data used in future caluculations.
        """
        contour_data = []

        # Find the bounding boxes of the contours to get x, y, width, and height
        for contour in pipeline.filter_contours_output:
            # Find the centers of mass of the contours
            # https://docs.opencv.org/3.4.2/dd/d49/tutorial_py_contour_features.html

            moments = cv2.moments(contour)
            m00 = moments['m00']
            if (m00 != 0):
                cx = int(moments['m10'] / m00)
                cy = int(moments['m01'] / m00)

                box = self.calculateBox(contour)

                contour_data.append(ContourData(cx, cy, box))

        return contour_data

    def calculateBox(self, contour):
        """
        Calculate the minimum containing box of the contour
        """

        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        return [box]

    def writeFrame(self, frame, contour_data):
        """
        Ouput vision frame with custom overlays
        """

        # Draw blue border surrounding contours
        if (Constants.ENABLE_CUSTOM_STREAM):
            for contour in contour_data:
                cv2.drawContours(frame, contour.box, -1, (255, 0, 0), 2)

            # Output frame to camera stream
            self.camera_host.outputVisionFrame(frame)

            # Save frame to USB drive
            if (Constants.ENABLE_IMAGE_SAVE):
                self.logger.saveFrame(frame)

    def processVision(self):
        """
        Read the latest frame and process using the CV2 Pipeline.
        """

        start = time.time()

        frame = self.camera_host.readVisionFrame()
        if (frame is not None):
            contour_data = self.processFrame(frame, self.pipeline)

            self.connection.publishValues(contour_data)

            self.writeFrame(frame, contour_data)

        end = time.time()

        self.logger.logMessage('Frame process time: ' + str(end - start) + ' s\n', True)
