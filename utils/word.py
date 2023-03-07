class Word:
    """A class representing a word form the JSON format for vosk speech recognition API"""

    def __init__(self, dict):
        """
        Parameters:
            dict(dict) dictionary from JSON, containing:
                conf(float): degree of confidence, from 0 to 1
                end(float): end time of pronouncing the word, in seconds
                start(float): start time of pronouncing the word, in seconds
                word(str): recognized word
        """

        self.conf = dict["conf"]
        self.end = dict["end"]
        self.start = dict["start"]
        self.word = dict["word"]

    def to_string(self):
        """Returns a string describing this instance"""
        return "{:20} from {:.2f} sec to {:.2f} sec, confidence is {:.2f}%".format(
            self.word, self.start, self.end, self.conf*100
        )

    def get_word(self):
        return self.word

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end