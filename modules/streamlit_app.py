"""
This file implements the streamlit display application.
"""

import streamlit as st
import pandas as pd
import spacy
from streamlit.state.session_state import SessionState
import preprocessing_utils as utils


def show():
    """
    This function loads datasets and displays the streamlit app.
    """
    # Reads datasets
    if "dataset" not in st.session_state:
        st.session_state.dataset = pd.read_parquet(
            "C:/Users/karkl/Desktop/NCC/datasets/output2.parquet"
        )

        # Loads (keywords), TODO: Simplify too long.
        keywords_topics = pd.read_excel(
            "C:/Users/karkl/Desktop/NCC/datasets/topic_knownledge.xlsx"
        )

        nlp = spacy.load("fr_core_news_sm")

        keywords_topics = pd.DataFrame(
            keywords_topics.stack().droplevel(0), columns=["words"]
        )
        keywords_topics["words"] = keywords_topics["words"].apply(
            lambda x: utils.preprocess_string(nlp, x)
        )
        keywords_topics = keywords_topics.reset_index().rename(
            columns={"index": "topic"}
        )
        st.session_state.keywords_topics = (
            keywords_topics.groupby(["topic"])
            .agg({"words": lambda x: list(x)})
            .reset_index()
        )

    st.title("Displaying topics for LégiFrance")

    sidebar(st.session_state.keywords_topics, st.session_state.dataset)
    _filter_text(st.session_state.dataset)


def sidebar(keywords_topic, dataset):
    topic_list = keywords_topic.iloc[:, 0].tolist()
    keywords_list = keywords_topic.iloc[:, 1].tolist()

    st.session_state.selected_topic = st.sidebar.selectbox(
        "Topic: ", topic_list
    )
    topic_index = topic_list.index(st.session_state.selected_topic)

    st.session_state.selected_word = st.sidebar.multiselect(
        "Words to select from: ",
        keywords_list[topic_index],
    )

    st.session_state.selected_emetteur = st.sidebar.multiselect(
        "Emetteur: ",
        dataset["emetteur"].drop_duplicates().tolist(),
    )

    st.session_state.selected_nature = st.sidebar.multiselect(
        "Nature: ",
        dataset["nature"].drop_duplicates().tolist(),
    )


def _filter_text(dataset):
    try:
        filtered = dataset[
            dataset["topics"].apply(
                lambda x: st.session_state.selected_topic in x
            )
        ]

        filtered = filtered[
            filtered["words"].apply(
                lambda x: st.session_state.selected_word in x
            )
        ]

        filtered = filtered[
            filtered["emetteur"].apply(
                lambda x: x in st.session_state.selected_emetteur
            )
        ]

        filtered = filtered[
            filtered["nature"].apply(
                lambda x: x in st.session_state.selected_nature
            )
        ]
        if len(filtered) == 0:
            raise ValueError("Empty selection.")
        st.text(f"There are {len(filtered)} document(s) matching selection.")

        # Display table
        try:
            filtered = filtered["titre"][:10]
            st.text("Displaying top 10 texts: ")
            st.table(filtered)

        except:
            st.table(filtered)
    except:
        st.text("No documents matching selection.")


if __name__ == "__main__":
    show()
