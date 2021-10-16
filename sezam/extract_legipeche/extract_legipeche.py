"""
This file is used to recover texts from the LEGIFRANCE API.
"""
import os
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

CLIENT_ID = ""
CLIENT_SECRET = ""

API_URL = "https://api.piste.gouv.fr/dila/legifrance-beta/lf-engine-app"
TOKEN_URL = "https://oauth.piste.gouv.fr/api/oauth/token"


def get_token():
    """
    Format token for LEGIFRANCE.
    """
    token = requests.post(
        TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "client_credentials",
            "scope": "openid",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    print(token.json())
    return token.json()["access_token"]


def get_last_n_jorf_cont_id(n: int, token) -> pd.DataFrame:
    """Extract the ids of the official journal for the last n-days.

    Args:
        n (int): Number of days
        token ([type]): API token

    Returns:
        pd.DataFrame: List of ids of official journals of the last n days.
    """
    url = API_URL + "/consult/lastNJo"
    headers = {
        "Authorization": "Bearer " + token,
    }
    r = requests.post(url, headers=headers, json={"nbElement": n})
    r.raise_for_status()
    return pd.DataFrame.from_records(r.json()["containers"])


def get_jorf_cont(jorf_cont_id: str, token) -> dict:
    """Fetches the content of an official journal

    Args:
        jorf_cont_id (str): id of an official journal
        token ([type]): API token

    Returns:
        dict: structured data of the content of an official journal
    """
    url = API_URL + "/consult/jorfCont"
    headers = {"Authorization": "Bearer " + token}

    r = requests.post(
        url,
        headers=headers,
        json={"id": jorf_cont_id, "pageNumber": 1, "pageSize": 1},
    )

    r.raise_for_status()
    data = r.json()["items"][0]["joCont"]["structure"]
    return data


def extract_text_ids_from_jorf_cont(jorf_cont: dict) -> list:
    """Rcursively extracts text ids from an official journal content object.

    Args:
        jorf_cont (dict): [description]

    Returns:
        list: [description]
    """
    res = []

    if "liensTxt" in jorf_cont:
        # For unintesreting types of texts, return an empty list
        if jorf_cont["titre"] in {
            "Mesures nominatives",
            "Informations parlementaires",
            "Annonces",
            "Avis et communications",
        }:
            return res

        # For other types of (interesting) texts,
        # return the ids of the texts listed
        liensTxt = jorf_cont["liensTxt"]
        for lienTxt in liensTxt:
            res.append(
                {
                    "id": lienTxt["id"],
                    "emetteur": lienTxt["emetteur"],
                    "nature": lienTxt["nature"],
                    "titre": lienTxt["titre"],
                }
            )

    # In case of nested containers,
    # extract texts of each nested container recursively
    if "tms" in jorf_cont:
        tms = jorf_cont["tms"]
        for s in tms:
            res.extend(extract_text_ids_from_jorf_cont(s))
    return res


def get_text_list(
    n_jorf: int, token: str, output_filename: str = "textes.csv"
):
    """
    Extracts the list of all texts published over the last `n_jorf` days,
    saves the result as csv.

    Args:
        n_jorf (int): Number of days to extract
        token (str): API token
        output_filename (str, optional): csv filename to save results to.
        Defaults to "textes.csv".
    """
    jorf_cont_ids = get_last_n_jorf_cont_id(n_jorf, token)
    dfs = []
    for jorf_cont_id in tqdm(jorf_cont_ids["id"]):
        dfs.append(
            pd.DataFrame.from_records(
                extract_text_ids_from_jorf_cont(
                    get_jorf_cont(jorf_cont_id, token)
                )
            )
        )
    res = pd.concat(dfs)
    res.to_csv(output_filename, index=False)


def get_text(id: str, token: str) -> dict:
    """
    Fetches a text from its id,
    returns the structured object returned by the API.

    Args:
        id (str): text id
        token (str): API token

    Returns:
        dict: Structured object with the content of the text
    """
    url = API_URL + "/consult/jorf"
    headers = {"Authorization": "Bearer " + token}

    r = requests.post(
        url,
        headers=headers,
        json={
            "textCid": id,
        },
    )

    r.raise_for_status()
    data = r.json()
    return data


def extract_content_from_text(text: dict, textid: str) -> str:
    """Extracts raw text from structured text object.

    Args:
        text (dict): Structured text object returned by the API
        textid (str): text id

    Returns:
        str: human readable text contained in the text object.
    """
    content = []

    if text["articles"]:
        for article in text["articles"]:
            content.append(
                {
                    "int_ordre": article["intOrdre"],
                    "content": article["content"],
                }
            )

    if "sections" in text:
        for section in text["sections"]:
            section_content = extract_content_from_text(section, textid)
            content.append(
                {"int_ordre": section["intOrdre"], "content": section_content}
            )

    content = sorted(content, key=lambda x: x["int_ordre"])

    html = "".join([c["content"] for c in content])
    res = BeautifulSoup(html, features="html.parser").get_text("\n")

    return res


def write_to_file(jorf_text_content, folder_path, file_name):
    with open(os.path.join(folder_path, file_name), "w") as f:
        f.write(jorf_text_content)
        return file_name


if __name__ == "__main__":

    output_folder_path = "full_texts"
    csv_file_name = "textes.csv"

    print("Getting token")
    token = get_token()
    # Extract list of texts for the last 365 days

    print("Getting text list")
    get_text_list(2, token, output_filename=csv_file_name)

    print("Reading text list")
    df = pd.read_csv(csv_file_name)

    print("Fetching texts and writing to disk")
    for jorf_text_id in tqdm(df["id"]):
        try:
            jorf_text_content = extract_content_from_text(
                get_text(jorf_text_id, token=token), jorf_text_id
            )
        # TODO: which exceptions?
        except:
            token = get_token()
        write_to_file(
            jorf_text_content, output_folder_path, jorf_text_id + ".txt"
        )
