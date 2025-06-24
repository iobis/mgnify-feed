import requests
import re
from email.utils import format_datetime
from dateutil import parser
from datetime import datetime


def check_if_marine(study_accession: str):
    keywords = {"marine", "ocean"}

    url = f"https://www.ebi.ac.uk/metagenomics/api/v1/studies/{study_accession}"
    res = requests.get(url=url)
    data = res.json().get("data", None)
    if data is None:
        return False

    study_abstract = data.get("attributes", {}).get("study-abstract", "").lower(),
    study_name = data.get("attributes", {}).get("study-name", "").lower(),

    if any(kw in text for text in [study_name, study_abstract] for kw in keywords):
        return study_name

    biome_ids = [biome.get("id", "").lower() for biome in data.get("relationships", {}).get("biomes", {}).get("data", [])]
    if any(kw in biome for biome in biome_ids for kw in keywords):
        return study_name

    return False


gbif_mgnify_page = "https://hosted-datasets.gbif.org/mgnify/"

response = requests.get(gbif_mgnify_page)
data = response.text

p = re.compile(">(MGY.*).zip</a>.*>([0-9\-\s:]+)</td>")
lines = re.findall(p, data)

channel_pubdate = format_datetime(datetime.now())
output = f"<rss><channel><pubDate>{channel_pubdate}</pubDate>"

for i, line in enumerate(lines[:100]):
    print(f"{i+1} of {len(lines)}")
    study_accession = line[0]
    marine_study = check_if_marine(study_accession)
    if marine_study:
        (dataset_id, time) = line
        d = parser.parse(time.strip().replace(" ", "T"))
        pubdate = format_datetime(d)
        item = f"""
            <item>
                <title>{dataset_id} - {marine_study}</title>
                <link>https://hosted-datasets.gbif.org/mgnify/{dataset_id}.zip</link>
                <ipt:dwca>https://hosted-datasets.gbif.org/mgnify/{dataset_id}.zip</ipt:dwca>
                <pubDate>{pubdate}</pubDate>
            </item>
        """
        print(item)
        output = output + item

output = output + "</channel></rss>"

file = open("feed.rss", "w")
file.write(output)
file.close()
