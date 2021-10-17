import spacy
import numpy as np
import nltk
from nltk.tokenize.toktok import ToktokTokenizer
import re
from bs4 import BeautifulSoup
import unicodedata
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, hamming_loss

"""Functions are found in this article:"""
"""https://towardsdatascience.com/a-practitioners-guide-to-natural"""
"""-language-processing-part-i-processing-understanding-text-9f4abfd13e72"""

nlp = spacy.load("en_core_web_sm")
# nlp_vec = spacy.load('en_vecs', parse = True, tag=True, #entity=True)
tokenizer = ToktokTokenizer()
stopword_list = nltk.corpus.stopwords.words("english")
stopword_list.remove("no")
stopword_list.remove("not")


def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text()
    return stripped_text


def remove_accented_chars(text):
    text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("utf-8", "ignore")
    )
    return text


def remove_special_characters(text, remove_digits=False):
    pattern = r"[^a-zA-z0-9\s]" if not remove_digits else r"[^a-zA-z\s]"
    text = re.sub(pattern, "", text)
    return text


def simple_stemmer(text):
    ps = nltk.porter.PorterStemmer()
    text = " ".join([ps.stem(word) for word in text.split()])
    return text


def lemmatize_text(text):
    text = nlp(text)
    text = " ".join(
        [
            word.lemma_ if word.lemma_ != "-PRON-" else word.text
            for word in text
        ]
    )
    return text


def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [
            token for token in tokens if token not in stopword_list
        ]
    else:
        filtered_tokens = [
            token for token in tokens if token.lower() not in stopword_list
        ]
    filtered_text = " ".join(filtered_tokens)
    return filtered_text


def tok(text):
    tokenizer = ToktokTokenizer()
    return tokenizer.tokenize(text)


def normalize_corpus(
    corpus,
    html_stripping=True,
    contraction_expansion=True,
    accented_char_removal=True,
    text_lower_case=True,
    text_lemmatization=True,
    special_char_removal=True,
    stopword_removal=True,
    remove_digits=True,
):

    normalized_corpus = []
    # normalize each document in the corpus
    for doc in corpus:
        # strip HTML
        if html_stripping:
            doc = strip_html_tags(doc)
        # remove accented characters
        if accented_char_removal:
            doc = remove_accented_chars(doc)
        # lowercase the text
        if text_lower_case:
            doc = doc.lower()
        # remove extra newlines
        doc = re.sub(r"[\r|\n|\r\n]+", " ", doc)
        # lemmatize text
        if text_lemmatization:
            doc = lemmatize_text(doc)
        # remove special characters and\or digits
        if special_char_removal:
            # insert spaces between special characters to isolate them
            special_char_pattern = re.compile(r"([{.(-)!}])")
            doc = special_char_pattern.sub(" \\1 ", doc)
            doc = remove_special_characters(doc, remove_digits=remove_digits)
        # remove extra whitespace
        doc = re.sub(" +", " ", doc)
        # remove stopwords
        if stopword_removal:
            doc = remove_stopwords(doc, is_lower_case=text_lower_case)

        normalized_corpus.append(doc)

    return normalized_corpus


"""#############"""
"""VISUALIZATION"""
"""#############"""


def plot_top_words(model, feature_names, n_top_words, title):
    fig, axes = plt.subplots(2, 5, figsize=(30, 15), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]

        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f"Topic {topic_idx +1}", fontdict={"fontsize": 30})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=20)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=40)

    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    plt.show()


"""#######"""
"""METRICS"""
"""#######"""


def print_evaluation_scores(y_test, predicted):
    print(
        "Subset Accuracy: ",
        accuracy_score(y_test, predicted, normalize=True, sample_weight=None),
    )
    print(
        "Hamming Loss (Misclassification Ratio): ",
        hamming_loss(y_test, predicted),
    )
    print("F1-score Micro: ", f1_score(y_test, predicted, average="micro"))
    print("F1-Score Macro: ", f1_score(y_test, predicted, average="macro"))


def hamming_score(y_test, y_pred, normalize=True, sample_weight=None):
    acc_list = []
    for i in range(y_test.shape[0]):
        set_true = set(np.where(y_test[i])[0])
        set_pred = set(np.where(y_pred[i])[0])
        tmp_a = None
        if len(set_true) == 0 and len(set_pred) == 0:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred)) / float(
                len(set_true.union(set_pred))
            )
        acc_list.append(tmp_a)
    return np.mean(acc_list)


def print_score(y_test, y_pred):
    print(
        "Hamming loss (Misclassification Ratio): {}".format(
            hamming_loss(y_test, y_pred)
        )
    )
    print("Label-Based Accuracy: {}".format(hamming_score(y_test, y_pred)))
    print(
        "Subset Accuracy: ",
        accuracy_score(y_test, y_pred, normalize=True, sample_weight=None),
    )
    print("F1-score Micro: ", f1_score(y_test, y_pred, average="micro"))
