"""
Small script to preprocess titles and run a LDA.
"""

import pandas as pd
from gensim.models import LdaMulticore
from gensim.corpora.dictionary import Dictionary
from sklearn.feature_extraction.text import CountVectorizer
from . import utils as utils

# Your local path here...
PATH_TO_CSV = ""
data = pd.read_csv(PATH_TO_CSV)

"""#############"""
"""Preprocessing"""
"""#############"""

# String preprocessing
data["titre"] = data["titre"].apply(lambda x: x.lower())
data["titre"] = data["titre"].apply(lambda x: utils.special_structures(x))
data["titre"] = data["titre"].apply(lambda x: utils.remove_stopwords(x))
data["titre"] = data["titre"].apply(lambda x: utils.replace_digit(x))
data["titre"] = data["titre"].apply(lambda x: utils.remove_trailings(x))

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
