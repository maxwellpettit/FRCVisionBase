# FRC Vision Base
This directory contains Python scripts that can be used to run a CV2 Pipeline via the Raspberry Pi FRC Web Console. This web console can be accessed by opening a web browser to http://frcvision.local or `http://PI_IP_ADDRESS` (replacing PI_IP_ADDRESS with the local IP address of the pi).

## Documentation
For Raspberry Pi setup instructions, see the [Official FRC Raspberry Pi Documentation](https://docs.wpilib.org/en/stable/docs/software/vision-processing/wpilibpi/using-the-raspberry-pi-for-frc.html).

The `src/main.py` script should be uploaded to the Raspberry Pi using the FRC Vision web console. Navigate to the "Application" tab and select the "Uploaded Python file" option.

The entire `src/vision` directory should be manually uploaded to the `/home/pi/` directory of the Raspberry Pi. This can be done using a tool like [WinSCP](https://winscp.net/eng/index.php) to copy files from your computer to the Pi.

## Resources
Camera configuration files and Pipelines are located in the resources folder of this repository.

## Viewing Output Streams
Output streams can be viewed by opening: http://frcvision.local:1181/stream.mjpg in a web browser (your computer must be connected to robot wifi/ethernet).

If not connected to the robot, the stream can be viewed at:
 `http://PI_IP_ADDRESS:1181/stream.mjpg` (replacing `PI_IP_ADDRESS` with the local IP address of the pi).
