#!/usr/bin/env python3

"""
----------------------------------------------------------------------------
Authors:     FRC Team 4145

Description: This script uses a generated CV2 pipeline to process a camera
             stream and publish results to NetworkTables.  This script is
             designed to work on the FRCVision Raspberry Pi image.
----------------------------------------------------------------------------
"""

import cv2
import numpy
import math
from enum import Enum


class Pipeline:
    """
    An OpenCV pipeline used to filter an image and find contours
    """
    
    def __init__(self):
        """
        Initializes filter values and pipeline setup
        """

        # Values used for HSV Color Filtering (Adjust these values to find specific colors)
        self.hsv_threshold_hue = [50.0, 84.0]
        self.hsv_threshold_saturation = [0.0, 255.0]
        self.hsv_threshold_value = [50.0, 255.0]

        # Values used to filter contours (Adjust these values to match desired sizes)
        self.filter_contours_min_area = 0.0
        self.filter_contours_min_perimeter = 0.0
        self.filter_contours_min_width = 5.0
        self.filter_contours_max_width = 100.0
        self.filter_contours_min_height = 10.0
        self.filter_contours_max_height = 1000.0
        self.filter_contours_solidity = [70.0, 100.0]
        self.filter_contours_max_vertices = 1000000.0
        self.filter_contours_min_vertices = 0.0
        self.filter_contours_min_ratio = 0.0
        self.filter_contours_max_ratio = 1000.0

        # Pipeline setup (These values typically don't need to be updated)
        self.hsv_threshold_output = None

        self.cv_erode_src = self.hsv_threshold_output
        self.cv_erode_kernel = None
        self.cv_erode_anchor = (-1, -1)
        self.cv_erode_iterations = 1.0
        self.cv_erode_bordertype = cv2.BORDER_CONSTANT
        self.cv_erode_bordervalue = (-1)
        self.cv_erode_output = None

        self.mask_input = self.cv_erode_output
        self.mask_mask = self.hsv_threshold_output
        self.mask_output = None

        self.find_contours_input = self.mask_output
        self.find_contours_external_only = False
        self.find_contours_output = None

        self.filter_contours_contours = self.find_contours_output
        self.filter_contours_output = None


    def process(self, source):
        """
        Runs the pipeline and sets all outputs to new values.
        """

        # Step HSV Threshold: Filter out image by HSV color values
        self.hsv_threshold_input = source
        (self.hsv_threshold_output) = self.hsv_threshold(self.hsv_threshold_input, self.hsv_threshold_hue, self.hsv_threshold_saturation, self.hsv_threshold_value)

        # Step CV Erode: Filter out noise from image
        self.cv_erode_src = self.hsv_threshold_output
        (self.cv_erode_output) = self.cv_erode(self.cv_erode_src, self.cv_erode_kernel, self.cv_erode_anchor, self.cv_erode_iterations, self.cv_erode_bordertype, self.cv_erode_bordervalue)

        # Step Mask: Remove the noise using the CV Errode output
        self.mask_input = self.cv_erode_output
        self.mask_mask = self.hsv_threshold_output
        (self.mask_output) = self.mask(self.mask_input, self.mask_mask)

        # Step Find Contours: Find solid areas of the filtered image 
        self.find_contours_input = self.mask_output
        (self.find_contours_output) = self.find_contours(self.find_contours_input, self.find_contours_external_only)

        # Step Filter Contours: Filter out contours that are too small/large/etc
        self.filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.filter_contours(self.filter_contours_contours, self.filter_contours_min_area, self.filter_contours_min_perimeter, self.filter_contours_min_width, self.filter_contours_max_width, self.filter_contours_min_height, self.filter_contours_max_height, self.filter_contours_solidity, self.filter_contours_max_vertices, self.filter_contours_min_vertices, self.filter_contours_min_ratio, self.filter_contours_max_ratio)


    @staticmethod
    def hsv_threshold(input, hue, sat, val):
        """
        Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """

        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))


    @staticmethod
    def cv_erode(src, kernel, anchor, iterations, border_type, border_value):
        """
        Expands area of lower value in an image.
        Args:
           src: A numpy.ndarray.
           kernel: The kernel for erosion. A numpy.ndarray.
           iterations: the number of times to erode.
           border_type: Opencv enum that represents a border type.
           border_value: value to be used for a constant border.
        Returns:
            A numpy.ndarray after erosion.
        """

        return cv2.erode(src, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)


    @staticmethod
    def mask(input, mask):
        """
        Filter out an area of an image using a binary mask.
        Args:
            input: A three channel numpy.ndarray.
            mask: A black and white numpy.ndarray.
        Returns:
            A three channel numpy.ndarray.
        """

        return cv2.bitwise_and(input, input, mask=mask)


    @staticmethod
    def find_contours(input, external_only):
        """
        Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """

        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        contours, hierarchy = cv2.findContours(input, mode=mode, method=method)
        return contours


    @staticmethod
    def filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """
        Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """

        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output
