Tools to seperate the HALO flights during EUREC4A into different phases. 

A flight phase is for example the period of a particular circle or 
calibration maneuver during a research flight. The idea behind this is to 
provide simple meta-data files (currently in NetCDF4 format) that contain 
the timestamps of the identified flight phases.

The module FlightPhaseTools.py contains functions that help to determine 
distinct timestamps in order to identify the flight phases. It is based on
input from the unified HALO datasets of BAHAMAS and the dropsondes. These 
datasets can for example be obtained from:

ftp-projects.mpimet.mpg.de

For each research flight there is a jupyter notebook that makes use of the 
FlightPhaseTools module to determine the flight phases. Within each notebook 
a set of base BAHAMAS plots are made to sanity check the obtained timestamps. 
The flight reports are used here as a reference.Finally, the notebook stores 
the determined timestamps in a NetCDF4 file.
