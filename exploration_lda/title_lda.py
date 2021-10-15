"""
Small script to preprocess titles and run a LDA.
"""

import pandas as pd
from gensim.models import LdaMulticore
from gensim.corpora.dictionary import Dictionary
from sklearn.feature_extraction.text import CountVectorizer
from stopwords import stopwords_nltk, stopwords_specific

# Your local path here...
PATH_TO_CSV = ""

data = pd.read_csv(PATH_TO_CSV)

"""###############"""
"""Utils functions"""
"""###############"""


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
    Remove all digits from an input string (very slow on large corpuses).
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
    input_string = input_string.replace("-", " ")
    input_string = input_string.replace("(", " ")
    input_string = input_string.replace(")", " ")
    input_string = input_string.replace("1er ", " ")
    input_string = input_string.replace(",", " ")
    input_string = input_string.replace("«", " ")
    input_string = input_string.replace("»", " ")
    output_string = input_string.replace("n°", " ")

    return output_string


"""#############"""
"""Preprocessing"""
"""#############"""

# String preprocessing
data["titre"] = data["titre"].apply(lambda x: x.lower())
data["titre"] = data["titre"].apply(lambda x: special_structures(x))
data["titre"] = data["titre"].apply(lambda x: remove_stopwords(x))
data["titre"] = data["titre"].apply(lambda x: replace_digit(x))
data["titre"] = data["titre"].apply(lambda x: remove_trailings(x))

# TODO: study why duplicates
data = data.drop_duplicates("titre")

# Tokenize with CountVectorizer
data["titre_tokenized"] = data["titre"].apply(lambda _: [])
vectorizer = CountVectorizer(min_df=2, ngram_range=(1, 1))
sparsed = vectorizer.fit_transform(data["titre"])
sparsed = sparsed.nonzero()
vocab = vectorizer.get_feature_names()
for doc_id, word_id in zip(sparsed[0], sparsed[1]):
    word = vocab[word_id]
    data.iloc[doc_id, 4].append(word)

"""#########################"""
"""Exploring topics with LDA"""
"""#########################"""
# Create a corpus from a list of texts
gensim_dictionary = Dictionary(data["titre_tokenized"])
corpus = [gensim_dictionary.doc2bow(text) for text in data["titre_tokenized"]]

# Train the model on the corpus.
lda = LdaMulticore(
    corpus,
    num_topics=25,
    passes=10,
    id2word=gensim_dictionary,
    random_state=42,
)

lda.show_topic(4, topn=10)
