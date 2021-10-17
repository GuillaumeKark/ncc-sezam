import json
import datetime
import requests
from rdflib import Graph
from bs4 import BeautifulSoup
import sys
import pandas as pd


def retrieve_law(url):
    payload = ""
    response = requests.request("GET", url, data=payload)
    if response.status_code == 200:
        return response.text
    else:
        print("ERROR")


def call_sparql(start_date, end_date):
    url = f"http://publications.europa.eu/webapi/rdf/sparql?default-graph-uri=&query=PREFIX+cdm%3A%3Chttp%3A%2F%2Fpublications.europa.eu%2Fontology%2Fcdm%23%3E%0D%0APREFIX+skos%3A%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0D%0APREFIX+dc%3A%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Felements%2F1.1%2F%3E%0D%0APREFIX+xsd%3A%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0D%0APREFIX+rdf%3A%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+owl%3A%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0D%0ASELECT+%0D%0ADISTINCT+%28group_concat%28distinct+%3Fwork%3Bseparator%3D%22%2C%22%29+as+%3FcellarURIs%29%0D%0A%28group_concat%28distinct+%3Ftitle_%3Bseparator%3D%22%2C%22%29+as+%3Ftitle%29%0D%0A%3FlangIdentifier%0D%0A%28group_concat%28distinct+%3Fmtype%3Bseparator%3D%22%2C%22%29+as+%3Fmtypes%29%0D%0A%28group_concat%28distinct+%3Fthumbnail%3Bseparator%3D%22%2C%22%29+as+%3Fthumbnails%29+%0D%0A%28group_concat%28distinct+%3FresType%3Bseparator%3D%22%2C%22%29+as+%3FworkTypes%29+%0D%0A%28group_concat%28distinct+%3FagentName%3Bseparator%3D%22%2C%22%29+as+%3Fauthors%29%0D%0A%28group_concat%28distinct+%3FprivateAgentName%3Bseparator%3D%22%3B%22%29+as+%3FprivateAuthors%29%0D%0A%3Fdate%0D%0A%28group_concat%28distinct+%3FsubjectLabel%3Bseparator%3D%22%2C%22%29+as+%3Fsubjects%29%0D%0A%28group_concat%28distinct+%3FworkId_%3Bseparator%3D%22%2C%22%29+as+%3FworkIds%29%0D%0AWHERE+%0D%0A%7B%0D%0A++++%3Fwork+rdf%3Atype+%3FresType+.%0D%0A++++%3Fwork+cdm%3Awork_date_document+%3Fdate+.%0D%0A++++%3Fwork+cdm%3Awork_id_document+%3FworkId_.%0D%0A++++%3Fwork+cdm%3Awork_is_about_concept_eurovoc+%3Fsubject.+graph+%3Fgs+%0D%0A++++%7B+%3Fsubject+skos%3AprefLabel+%3FsubjectLabel++filter+%28lang%28%3FsubjectLabel%29%3D%22fr%22%29+%7D.%0D%0A++++graph+%3Fge+%7B+%0D%0A++++%3Fexp+cdm%3Aexpression_belongs_to_work+%3Fwork+.%0D%0A+++++%3Fexp+cdm%3Aexpression_title+%3Ftitle_+%0D%0Afilter%28lang%28%3Ftitle_%29%3D%22fr%22+or+lang%28%3Ftitle_%29%3D%22fra%22+or+lang%28%3Ftitle_%29%3D%27%27+%29.%0D%0A+++++%3Fexp+cdm%3Aexpression_uses_language+%3Flg.+%0D%0Agraph+%3Flgc+%7B+%3Flg+dc%3Aidentifier+%3FlangIdentifier+.%7D%0D%0A%7D%0D%0A++++graph+%3Fgm+%7B%0D%0A++++%3Fmanif+cdm%3Amanifestation_manifests_expression+%3Fexp+.%0D%0A++++%7B%3Fmanif+cdm%3Amanifestation_type+%3Fmtype+.%7D%0D%0A++++OPTIONAL+%7B%3Fmanif+cdm%3Amanifestation_has_thumbnail+%3Fthumbnail%7D%0D%0A%7D%0D%0A++++OPTIONAL+%7B++++++++graph+%3Fgagent+%7B+%7B%3Fwork+cdm%3Awork_contributed_to_by_agent+%3Fagent+.%7D%0D%0A+++++++++++union+%0D%0A+++++++++++%7B%3Fwork+cdm%3Awork_created_by_agent+%3Fagent+%7D%0D%0A+++++++++++union+%0D%0A+++++++++++%7B%3Fwork+cdm%3Awork_authored_by_agent+%3Fagent+%7D%0D%0A+++++++%7D+++++++graph+%3Fga+%7B+%3Fagent+skos%3AprefLabel+%3FagentName++%0D%0A+++++++++++++++++++++++filter+%28lang%28%3FagentName%29%3D%22fr%22%29+.++++++++++++++++++%7D%7D.%0D%0A++++OPTIONAL+%7Bgraph+%3FpersAuthor+%7B+%7B%3Fwork+cdm%3Awork_contributed_to_by_agent+%3FprivateAgent+.%7D%0D%0A+++++++++++union+%0D%0A+++++++++++%7B%3Fwork+cdm%3Awork_authored_by_agent+%3FprivateAgent+%7D%0D%0A%7D%0D%0A%3FprivateAgent+rdf%3Atype+cdm%3Aperson+.%0D%0A%3FprivateAgent+cdm%3Aagent_name+%3FprivateAgentName+%0D%0A%7D%0D%0A+%7B+SELECT+DISTINCT+%3Fwork+WHERE+%7B+%0D%0A++++%3Fwork+rdf%3Atype+%3FresType+.%0D%0A++++%3Fwork+cdm%3Awork_date_document+%3Fdate+.%0D%0A++++FILTER%28+%3Fdate+%3E+%22{start_date}%22%5E%5Exsd%3Adate+AND+%3Fdate+%3C%3D+%22{end_date}%22%5E%5Exsd%3Adate%29%0D%0A++++%3Fwork+cdm%3Awork_id_document+%3FworkId_.%0D%0A%7D+%0D%0ALIMIT+5000%0D%0A%7D%0D%0A%7D%0D%0AGROUP+BY+%3Fwork++%3Fdate+%3FlangIdentifier%0D%0AOFFSET+0&format=application%2Fsparql-results%2Bjson&timeout=0&debug=on&run=+Run+Query+"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    payload = ""
    response = requests.request("GET", url, data=payload, headers=headers)
    # print(url)

    if response.status_code == 200:
        return response.text
    else:
        sys.exit(f"Error on file {start_date}_{end_date}")


if __name__ == "__main__":
    start_date = datetime.datetime(2021, 9, 1)
    end_date = datetime.datetime(2021, 10, 16)
    name_end = end_date
    df = pd.DataFrame(columns=[])
    while end_date > start_date:
        day_before = end_date - datetime.timedelta(days=1)
        data = json.loads(
            call_sparql(
                f"{day_before.strftime('%Y-%m-%d')}",
                f"{end_date.strftime('%Y-%m-%d')}",
            )
        )
        for i, j in enumerate(data["results"]["bindings"]):
            if "oj:" in (j.get("workIds").get("value")):
                oj = (
                    j.get("workIds").get("value").split("oj:")[1].split(",")[0]
                )
                g = Graph()
                g.parse(f"http://publications.europa.eu/resource/oj/{oj}.FRA")
                for s, p, o in g:
                    if "cellar" in str(s):
                        text_url = f"{s}.03/DOC_1"
                        soup = BeautifulSoup(
                            retrieve_law(text_url), features="html.parser"
                        )
                        # print(j['title']['value'])
                        df = df.append(
                            {
                                "title": j["title"]["value"],
                                "topics": j["subjects"]["value"],
                                "date": j["date"]["value"],
                                "text": str(soup.get_text()),
                            },
                            ignore_index=True,
                        )
        end_date -= datetime.timedelta(days=1)
        df.to_csv(
            f'{start_date.strftime("%Y-%m-%d")}_{name_end.strftime("%Y-%m-%d")}.csv',
            index=False,
        )
