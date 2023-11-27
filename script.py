import requests
import re
from email.utils import format_datetime
from dateutil import parser
from datetime import datetime


gbif_mgnify_page = "https://hosted-datasets.gbif.org/mgnify/"
selected_datasets = ["MGYS00005294"]

response = requests.get(gbif_mgnify_page)
data = response.text

p = re.compile(">(MGY.*).zip</a>.*>([0-9\-\s:]+)</td>")
lines = re.findall(p, data)

channel_pubdate = format_datetime(datetime.now())
output = f"<rss><channel><pubDate>{channel_pubdate}</pubDate>"

for line in lines:
    if line[0] in selected_datasets:
        (dataset_id, time) = line
        d = parser.parse(time.strip().replace(" ", "T"))
        pubdate = format_datetime(d)
        output = output + f"<item><title>{dataset_id}</title><link>https://hosted-datasets.gbif.org/mgnify/{dataset_id}.zip</link><ipt:dwca>https://hosted-datasets.gbif.org/mgnify/{dataset_id}.zip</ipt:dwca><pubDate>{pubdate}</pubDate></item>"

output = output + "</channel></rss>"

file = open("feed.rss", "w")
file.write(output)
file.close()
