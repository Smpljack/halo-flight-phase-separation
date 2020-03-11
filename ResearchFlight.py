import os
import yaml


class ResearchFlight:
    def __init__(self, name, mission, flight_id, contacts,
                 date, takeoff, landing, events, remarks):
        """
        Initialize the research flight attributes.

        :param name: Research flight name.
        :param mission: Research flight mission.
        :param flight_id: Research flight ID.
        :param contacts: List of contact persons.
        :param date: Date of the research flight.
        :param takeoff: Research flight takeoff time.
        :param landing: Research flight landing time.
        :param events: Timestamps of events during the research flight.
        :param remarks: General remarks on the research flight.
        """
        self.name = name
        self.mission = mission
        self.flight_id = flight_id
        self.contacts = contacts
        self.date = date
        self.takeoff = takeoff
        self.landing = landing
        self.events = events
        self.remarks = remarks

        self.segments = []

    def append_segment(self, segment):
        """
        Append a flight segment.
        :param segment: ResearchFlightSegment object.
        """
        self.segments.append(segment)

    def append_segments(self, segments):
        """
        Append a flight segment.
        :param segments: List of ResearchFlightSegment objects.
        """
        [self.segments.append(segment) for segment in segments]

    def to_dictionary(self):
        """
        Return the attributes of a research flight as a dictionary.
        :return: Dictionary containing the research flight attributes.
        """
        rf_dict = {
            'name': self.name,
            'mission': self.mission,
            'flight_id': self.flight_id,
            'contacts': self.contacts,
            'date': self.date,
            'takeoff': self.takeoff,
            'landing': self.landing,
            'events': self.events,
            'remarks': self.remarks,
            'segments': [segment.to_dictionary() for segment in self.segments],
        }
        return rf_dict

    def to_yaml(self, dirname, filename):
        """
        Store the flight phase attributes to a .yaml file.

        :param dirname: Directory path to store the file to.
        :param filename: Name of the file, ending with .yaml.
        """
        with open(os.path.join(dirname, f"{filename}"), 'w') as outfile:
            yaml.dump([self.to_dictionary()], outfile, default_flow_style=False)
