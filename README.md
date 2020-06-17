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
circle segment, the roll angle and the temporal change in aircraft heading can be assumed to roughly be
constant. The circles during EUREC4A were especially associated with the regular launch of 
dropsondes, most of the time 12 per circle, every 30 ° heading. Such general characteristics 
of the various flight segments and a first idea about the flight patterns from the flight
reports (available on [aeris](https://observations.ipsl.fr/aeris/eurec4a/#/)) are used as a starting point
to approach the flight phase segmentation. The BAHAMAS datasets and the dropsonde launch 
times are then analysed to consistently determine the specific flight segment timestamps. For this 
purpose, the BAHAMAS dataset provided by Heike Konow which is projected on a 
unified (time, lat, lon) grid (for example available [here](https://owncloud.gwdg.de/index.php/s/qOq3xGhnQgKrbH4)
and the JOANNE dropsonde dataset provided by Geet George (available soon [here](https://github.com/Geet-George/JOANNE) or by request) 
are used.

To precisely determine the periods of flight segments, a rather manual approach is taken where the 
flight reports and the dropsonde launch times are used as first indicators to determine the segment periods.
The exact times are then found iteratively by the dataset creator (see contact entry in each segment file) 
with a set of standardized plots of the BAHAMAS data and after undergoing a set of tests that depend on the 
particular "kinds" of the flight segment. Because of this simple procedure the only relevant place that 
denotes the segment times are the YAML segmentation files. The reference or "true" segment times are defined to always be
in these files! Users of the YAML segmentation files are encouraged to use these files with any tool of their choice and may suggest
adjustments or additions by simply uploading their new version of a YAML file via a Pull Request on GitHub, which may then be
reviewed and accepted to work towards new versions of this dataset. It is expected that users of different sub-communities
may have different ideas of how segments are defined, so feel encouraged to bring up your suggestions!


The following flight segments are identified, where the names directly correspond to entries in  
segment "kinds" in the YAML files. The criteria to determine the start- and end-times of the segments 
are noted below each flight segment.

#### circle:
- Starts 1 minute prior to the first dropsonde of a circle to improve comparability of dropsonde and 
remote sensing data. Ends after 360° when aircraft passes starting point, assuring there is no overlap.
- If there is a BAD dropsonde at the circle start, it is still considered for defining the circle start. 

#### circle_break: 
- Periods between two consecutive circles, during which no dropsondes were launched.
- Circle breaks stand out to breaks between for example a circle and a straight-leg because during these it 
is assured that the aircraft remained on the circle track.
- Circle breaks may be used to obtain all the available remote sensing data from circles, neglecting availability 
of dropsonde data.

#### circling:
- Period during which the aircraft was on the standard circling track with roughly 3° roll angle.
- Periods without dropsonde launches are included here (e.g. circle_break).
- Useful when wanting to loop over the full period HALO was on the circle track.

#### clover_leg:
- Defined as the long legs of a clover flight pattern with close to 2° roll angle.
- Dropsondes were launched every 30° along clover legs. 
- The transitions between circle pattern and clover pattern are excluded, because of steep roll angles of about 30°. 
- Clover legs are not defined via launch times of first and last dropsonde, because they don't always represent the 
whole leg.

#### clover_turn:
- Periods between two consecutive clover legs (smooth transition), with steeper roll angles of about 6°.
- These periods are constrained to the periods during the clover pattern where the aircraft roll angle deviates clearly from 2°.
- During these turns no dropsondes were launched. 

#### straight_leg:
- Period with constant aircraft heading and close to 0° roll angle (max. 3° roll for short periods).
- Straight legs were flown with various purposes, which are more closely described by the straight leg 
"name"-Parameter in the YAML files and is in some cases also expressed by additional entries in the segment "kinds" attribute.

#### lidar_calibration:
- Maneuver typically conducted during the final descent of most RFs in FL160.
- Defined as the period of the aircraft being in FL160. 
- If roll angle was close to 0° the whole time, the segment is also of kind "straight_leg".

#### radar_calibration_wiggle:
- Maneuver typically conducted during straight legs, where the aircraft tilts to a roll angle of first -20° and then +20°.
- If conducted during a straight leg, the straight leg is split into three flight segments: 
1.) straight_leg, 2.) radar_cal_wiggle, 3.) straight_leg.
- Segments start and end at about 0° roll angle.

#### radar_calibration_tilted:
- Maneuver typically conducted at the end of a straight leg, where a narrow circle pattern with a constant 10° bank is flown.
- A constant roll angle of about 10° is used to define the period of a "radar_cal_tilted" segment.

#### baccardi_calibration:
- Defined by 4 turns indicated by roll angles of about 25° (1 turn: -25°, 3 turns: +25°).


**Note on data format**: The flight segmentation data is provided in so called YAML files. YAML is a text based
human readable data format that uses python-like indentation for structuring its contents. It is often used for configuration
files and due to its great human readability very suited for version control, which is one reason we wanted to use it here.
For python users, the module [PyYAML](https://pyyaml.org) (included in Anaconda) 
offers an easy to use way to read the data from the yaml files into plane python objects like lists and dictionaries. 
Here is an example to read a file and print the circle start- and endtimes from that file:

```
import yaml 
flightinfo = yaml.load(open("HALO_RF04_20200126_info.yaml"))
print([(c["start"], c["end"]) for c in flightinfo["segments"] if "circle" in c["kinds"]])
``` 
