#!/usr/bin/env python3

"""
----------------------------------------------------------------------------
Authors:     FRC Team 4145

Description: This script uses a generated CV2 pipeline to process a camera
             stream and publish results to NetworkTables.  This script is
             designed to work on the FRCVision Raspberry Pi image.
----------------------------------------------------------------------------
"""


class Constants:

    # Enable debug logging
    ENABLE_DEBUG = False

    # Enable/Disable Custom Camera Output (i.e. custom vision overlay)
    ENABLE_CUSTOM_STREAM = True

    # Enable/Disable saving of images
    ENABLE_IMAGE_SAVE = True

    # Number of frames between saving images
    FRAME_INTERVAL = 25
