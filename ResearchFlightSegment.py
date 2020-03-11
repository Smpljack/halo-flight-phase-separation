class ResearchFlightSegment:
    def __init__(self, kind, name, start, end):
        """
        Initialize the attributes of a research flight segment.
        :param kind: The general kind (or type) of the research flight segment.
        :param name: The particular name of the research flight segment.
        :param start: Start time of the research flight segment in unix time.
        :param end: End time of the research flight segment in unix time.
        """
        self.kind = kind
        self.name = name
        self.start = start
        self.end = end

    def to_dictionary(self):
        """
        Return the attributes of a research flight segment as a dictionary.
        :return: Dictionary containing the attributes of the research flight segment.
        """
        rf_segment_dict = {
            'kind': self.kind,
            'name': self.name,
            'start': self.start,
            'end': self.end,
        }
        return rf_segment_dict
