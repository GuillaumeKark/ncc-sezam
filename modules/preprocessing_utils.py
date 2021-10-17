"""
This file implements different preprocessing utils functions.
"""

import pandas as pd
import re
from stopwords import stopwords_nltk, stopwords_specific
import spacy
import unicodedata

def preprocess_string(nlp, input_string):
    """
    Wraps all operations to ensure common normalization.
    """
    processed_string = input_string.lower()
    processed_string = special_structures(processed_string)
    #NA for match processed_string = remove_stopwords(processed_string)
    processed_string = replace_digit(processed_string)
    processed_string = remove_trailings(processed_string)
    processed_string = strip_accents(processed_string)
    #processed_string = lemmatize(nlp, processed_string)
    return processed_string


"""#############"""
"""Sub-functions"""
"""#############"""

def lemmatize(nlp, input_string):
    """
    Lemmatizes an input string
    """
    # Can use spacy pipeline to increase speed
    doc = nlp(input_string)
    return " ".join([token.lemma_ for token in doc])
    

def remove_stopwords(input_string):
    """
    This function removes stopwords from an input string.
    """
    stopwords = stopwords_nltk + stopwords_specific
    output_string = " ".join(
        [word for word in input_string.split() if word not in stopwords]
    )
    return output_string


def replace_digit(input_string):
    """
    Remove all digits from an input string (Slow on large corpuses).
    """
    output_string = "".join([i for i in input_string if not i.isdigit()])
    return output_string


def remove_trailings(input_string):
    """
    Remove duplicated spaces.
    """
    output_string = " ".join(input_string.split())
    return output_string


def special_structures(input_string):
    """
    Replace some special structures by space.
    """
    input_string = input_string.replace("'", " ")
    input_string = input_string.replace("(", " ")
    input_string = input_string.replace(")", " ")
    input_string = input_string.replace("1er ", " ")
    input_string = input_string.replace(",", " ")
    input_string = input_string.replace("«", " ")
    input_string = input_string.replace("»", " ")
    output_string = input_string.replace("n°", " ")

    return output_string

def strip_accents(text):
    """
    Removes accents.
    """
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

# UNUSED
def regex_loi(input_series: pd.Series) -> pd.Series:
    """
    Finds the law patterns that match a given token.
    """
    token = r"(\w+).*\s\d{4}\s"
    replace_by = "<LOI> "

    # Finds patterns that match tokens
    types = input_series.apply(
        lambda s: m.group(1).lower() if (m := re.match(token, s)) else None
    )
    types = set(types)
    types.discard(None)

    # Change "arrêté du ... 2021" en <LOI>
    patterns = [rf"{type_loi}(.*?)\s\d{{4}}\s" for type_loi in types]

    for pattern in patterns:
        output_series = input_series.apply(
            lambda s: re.sub(pattern, replace_by, s, flags=re.IGNORECASE)
        )

    return output_series
