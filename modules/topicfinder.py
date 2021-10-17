"""
This file implements the topic finder to assign words/topics to a document.
"""

import pandas as pd


class TopicFinder:
    def __init__(self, topic_word_table: pd.DataFrame):
        """
        Loads the topic/word table to find topics on.
        """
        self.topic_column = topic_word_table["topic"]
        self.words_column = topic_word_table["words"]

    def column_extract_topics(self, find_on: pd.Series) -> pd.DataFrame:
        """
        Returns distinct words and topics
        from topic_word_table found in column find_on.
        """
        output_dataframe = pd.DataFrame()
        # Creates columns of lists
        output_dataframe["words"], output_dataframe["topics"] = zip(
            *find_on.map(self.extract_topics)
        )
        return output_dataframe

    def extract_topics(self, input_string: str) -> tuple:
        """
        Returns distinct words and topics
        from topic_word_table found in the input string.
        """
        words_found = []
        topics_found = []

        # For each topic
        for topic_name, list_words in zip(
            self.topic_column, self.words_column
        ):
            # Find matches
            matches = list(
                {match for match in input_string.split() if match in list_words}
            )
            
            # If there is at least one match, the topic is present
            if matches != []:
                topics_found.append(topic_name)
                words_found += matches
                
        # Returns the distinct lists of words and topics
        return list(set(words_found)), topics_found
