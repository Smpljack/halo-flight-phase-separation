## Segmentation of HALO flights during EUREC4A

The HALO Research Flights (RFs) during EUREC4A can be divided into different segments. 
For example circles and straight legs were purposefully conducted maneuvers during which 
a distinct sampling behaviour of the various instruments can be assumed. For future analyses
based on specific kinds of flight segments (e.g. only based on circles) it is desired to use a 
common set of start- and end-times to assure consistency between the studies. This repository 
provides the start- and end-times of the flight-segments for each RF together with some  very 
general information about the RF or special events during the RF.

## Methodology to determine flight segments

A flight segment is a period of some constant characteristics during a RF. For example during a 
circle segment, the roll angle and the temporal change in aircraft heading can be assumed to be
constant. The circles during EUREC4A were especially associated with the regular launch of 
dropsondes, most of the time 12 per circle, every 30 ° heading. Such general characteristics 
of the various flight segments and a first idea about the flight patterns from the flight
reports (available on [aeris](https://observations.ipsl.fr/aeris/eurec4a/#/)) are used as a starting point
to approach the flight phase segmentation. The BAHAMAS datasets and the dropsonde launch 
times are then analysed to consistently determine the specific flight segment timestamps. For this 
purpose, BAHAMAS and dropsonde datasets provided by Heike Konow that are projected on a 
unified (time, lat, lon) grid are used, which are for example available on this ftp server:

> ftp-projects.mpimet.mpg.de

The following flight segments are identified, where names in brackets directly correspond to the 
segment-kinds in the YAML files. The criteria to determine the start- and end-times of the segments 
are noted below each flight segment.

#### circle (circle):

#### circle break (circle_break):

#### straight leg (straight_leg):

#### lidar calibration (lidar_calibration):

#### radar calibration with wiggle (radar_cal_wiggle):

#### radar calibration with constant bank (radar_cal_tilted):

These criteria are applied by making use of the FlightPhaseTools.py python module in jupyter 
notebooks for each individual RF. This module rather provides useful functions to search for the 
start- and end-times of the flight segments than to automate this process. To validate whether the 
found timestamps for the different segments are plausible, they are scattered into a set of standard 
BAHAMAS timeseries. An example is given below. 

![Set of BAHAMAS data timeseries with timestamps denoting start- and end-times of flight segments.](https://raw.githubusercontent.com/smpljack/flight-phase-seperation/master/plots/flight_phase_seperation_example.png)

It is clear that this process is to some degree always going to be subjective, but due to the individuality 
of the different RFs (unforeseeable track-deviations, dropsonde failures, complexity of maneuvers) and the managable 
amount of them, this methodology appears plausible.

The module FlightPhaseTools.py contains functions that help to determine 
distinct timestamps in order to identify the flight phases. It is based on
input from the unified HALO datasets of BAHAMAS and the dropsondes. These 
datasets can for example be obtained from:

> ftp-projects.mpimet.mpg.de

For each research flight there is a jupyter notebook that makes use of the 
FlightPhaseTools module to determine the flight phases. Within each notebook 
a set of base BAHAMAS plots are made to sanity check the obtained timestamps. 
The flight reports are used here as a reference.Finally, the notebook stores 
the determined timestamps in a NetCDF4 file.

What should the README contain?
- Brief explanation of what this is about.
- Structure of the repository
- Methodology to determine timestamps.
- Definitions of the different flight phases, what criteria are used?
- Note on obtaining data as NetCDF.



