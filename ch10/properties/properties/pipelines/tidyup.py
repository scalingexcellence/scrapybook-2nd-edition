from datetime import datetime


class TidyUp(object):
    """A pipeline that does some basic post-processing"""

    def process_item(self, item, spider):
        """
        Pipeline's main method. Formats the date as a string.
        """

        item['date'] = [datetime.isoformat(i) for i in item['date']]

        return item
