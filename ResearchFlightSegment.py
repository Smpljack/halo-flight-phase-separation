class ResearchFlightSegment:
    def __init__(self, kinds, name, irregularities, segment_id, start, end, good_dropsondes=None):
        """
        Initialize the attributes of a research flight segment.
        :param kind: The general kind (or type) of the research flight segment.
        :param name: The particular name of the research flight segment.
        :param start: Start time of the research flight segment in unix time.
        :param end: End time of the research flight segment in unix time.
        """
        self.kinds = kinds
        self.name = name
        self.start = start
        self.end = end
        if 'circle' in self.kinds or 'circling' in self.kinds:
            self.good_dropsondes = good_dropsondes
        self.irregularities = irregularities
        self.segment_id = segment_id

    def to_dictionary(self):
        """
        Return the attributes of a research flight segment as a dictionary.
        :return: Dictionary containing the attributes of the research flight segment.
        """
        rf_segment_dict = {
            'kinds': self.kinds,
            'name': self.name,
            'irregularities': self.irregularities,
            'segment_id': self.segment_id,
            'start': self.start,
            'end': self.end,
        }
        if 'circle' in self.kinds or 'circling' in self.kinds:
            rf_segment_dict['good_dropsondes'] = self.good_dropsondes
        return rf_segment_dict
