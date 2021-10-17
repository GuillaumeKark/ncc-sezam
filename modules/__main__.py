"""
This file wraps all operations for the topic finder pipeline.
"""
import pandas as pd
import preprocessing_utils as utils
from topicfinder import TopicFinder

CORPUS_PATH = "C:/Users/karkl/Desktop/NCC/datasets/legifrance.parquet"
KEYWORDS_TOPICS_PATH = "C:/Users/karkl/Desktop/NCC/datasets/topic_knownledge.xlsx"

# TODO: Same pipeline keywords / documents. Ensure priors formatted well.
def point_predict():
    """
    This function shows how to point predict the topics of a document.
    """
    keywords_topics = pd.read_excel(KEYWORDS_TOPICS_PATH)
    
    # Format keywords
    keywords_topics = pd.DataFrame(keywords_topics.stack().droplevel(0), columns=["word"])
    keywords_topics = keywords_topics.reset_index().rename(columns={"index": "topic"})
    keywords_topics = keywords_topics.groupby(["topic"]).agg({"word": lambda x: list(x)})
    

def predict():
    """
    This functions show how to predict topic from a batch of documents.
    """
    corpus = pd.read_parquet(CORPUS_PATH)
    keywords_topics = pd.read_excel(KEYWORDS_TOPICS_PATH)

    # Format keywords to ["topic", "keywords"] table
    keywords_topics = pd.DataFrame(keywords_topics.stack().droplevel(0), columns=["words"])
    keywords_topics = keywords_topics.reset_index().rename(columns={"index": "topic"})
    keywords_topics = keywords_topics.groupby(["topic"]).agg({"words": lambda x: list(x)}).reset_index()
    
    # String preprocessing
    corpus["text"] = corpus["text"].apply(utils.preprocess_string)
    corpus["titre"] = corpus["titre"].apply(utils.preprocess_string)

    # Find keywords and topics
    tfi = TopicFinder(keywords_topics)
    found_title = tfi.column_extract_topics(corpus["titre"])
    found_text = tfi.column_extract_topics(corpus["text"])
        
    # Join both datasets
    found_title["words"] += found_text["words"]
    found_title["topics"] += found_text["topics"]
    found_title["words"] = found_title["words"].apply(lambda x: list(set(x)))
    found_title["topics"] = found_title["topics"].apply(lambda x: list(set(x)))
    # Save an output table
    pd.concat([corpus)


if __name__ == "__main__":
    point_predict()
    predict()
