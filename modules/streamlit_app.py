"""
This file implements the streamlit display application.
"""

import streamlit as st
import pandas as pd
import spacy
import preprocessing_utils as utils
from collections import Counter
import plotly.graph_objects as go
import networkx as nx


def show():
    """
    This function loads datasets and displays the streamlit app.
    """
    # Reads datasets
    if "dataset" not in st.session_state:
        st.session_state.dataset = pd.read_parquet(
            "C:/Users/karkl/Desktop/NCC/datasets/output3.parquet"
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

    st.title("Explorateur de catégories sur LégiFrance")

    st.session_state.page = (
        st.session_state.selected_topic
    ) = st.sidebar.selectbox("Module: ", ["Textes", "Network", "Graphique"])

    if st.session_state.page == "Textes":
        sidebar(st.session_state.keywords_topics, st.session_state.dataset)
        _filter_text(st.session_state.dataset)
    elif st.session_state.page == "Network":
        st.session_state.network_chart = create_graph_chart(
            st.session_state.dataset
        )
        st.plotly_chart(st.session_state.network_chart)
        pass
    elif st.session_state.page == "Graphique":
        topic_list = st.session_state.keywords_topics.iloc[:, 0].tolist()
        st.session_state.selected_topic = st.sidebar.selectbox(
            "Topic: ", topic_list
        )
        st.plotly_chart(
            create_bar_chart(
                st.session_state.dataset,
                "nature",
                st.session_state.selected_topic,
            )
        )


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

    st.session_state.selected_emetteur = st.sidebar.selectbox(
        "Emetteur: ",
        dataset["emetteur"].drop_duplicates().tolist(),
    )

    st.session_state.selected_nature = st.sidebar.selectbox(
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
                lambda x: not set(st.session_state.selected_word).isdisjoint(x)
            )
        ]

        filtered = filtered[
            filtered["emetteur"].apply(
                lambda x: x == st.session_state.selected_emetteur
            )
        ]

        filtered = filtered[
            filtered["nature"].apply(
                lambda x: x == st.session_state.selected_nature
            )
        ]

        # filtered["link"] = filtered["id"].apply(
        #    lambda x: "https://www.legifrance.gouv.fr/jorf/id/" + str(x)
        # )

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


# Present charts


def create_graph_chart(df: pd.DataFrame):
    """
    Creates the network chart.
    """
    # create graph
    G = _create_graph(df)

    # data for plotly
    data = []

    # create edges
    weights = []
    edges_x = []
    edges_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]["pos"]
        x1, y1 = G.nodes[edge[1]]["pos"]
        edges_x.append((x0, x1))
        edges_y.append((y0, y1))
        weights.append(G.get_edge_data(edge[0], edge[1])["weight"])

    for edge_x, edge_y, weight in zip(edges_x, edges_y, weights):
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=weight * 5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )
        data.append(edge_trace)

    # create nodes
    node_x = []
    node_y = []
    texts = list(G.nodes())
    for node in G.nodes():
        x, y = G.nodes[node]["pos"]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=texts,
        textposition="top center",
        marker=dict(color="orange", size=10),
    )

    data.append(node_trace)

    fig = go.Figure(
        data=data,
        layout=go.Layout(
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig


def _create_graph(df: pd.DataFrame):
    """
    Internal function to plot charts.
    """
    # co-occurences counter
    ct = Counter()
    for topics in df["topics"]:
        for i in range(len(topics)):
            for j in range(i):
                topic1, topic2 = sorted((topics[i], topics[j]))
                ct[(topic1, topic2)] += 1

    # normalize weight
    max_weight = max(weight for weight in ct.values())
    cooc = {topic: weight / max_weight for topic, weight in ct.items()}

    # graph from counter
    G = nx.Graph()
    for edge, weight in cooc.items():
        topic1, topic2 = edge
        G.add_edge(topic1, topic2, weight=weight)

    # add position to display in plotly
    pos = nx.spring_layout(G, weight="weights")
    for n, p in pos.items():
        G.nodes[n]["pos"] = p

    return G


def create_bar_chart(df, colname, topic):
    df_filter = df[df["topics"].apply(lambda s: topic in s)]
    df_count = df_filter.groupby(colname).count()
    fig = go.Figure(
        go.Bar(x=df_count["id"], y=df_count.index, orientation="h")
    )
    fig.update_layout(
        title="Nombre de textes par catégorie", width=800, height=1000
    )
    fig.update_xaxes(title="Nombre de textes")
    fig.update_yaxes(ticksuffix="  ")
    return fig


if __name__ == "__main__":
    show()
