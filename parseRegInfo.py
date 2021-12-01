import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os

### Setup

url = "https://www.reginfo.gov/public/jsp/EO/eoListingChart.jsp?days=0&tid=455069.1990316667&sid=0.10076941185805599"
res = requests.get(url)
soup = BeautifulSoup(res.content, 'html.parser')
today = datetime.today().strftime("%m/%d/%y")
today_for_file = datetime.today().strftime("%m_%d_%y")

### Cleaning up the HTML

td_s_raw = soup.find_all("td")
td_s = [t.get_text().replace("\n", "").strip() for t in td_s_raw]

agencies = [t.replace("AGENCY:", "").strip() for t in td_s if "AGENCY:" in t]
primary_agency = [a.split("-")[0] for a in agencies]
titles = [t.replace("TITLE:", "").strip() for t in td_s if "TITLE:" in t]
rins = [t.replace("RIN:", "").strip() for t in td_s if "RIN:" in t]
stages = [t.replace("STAGE:", "").strip() for t in td_s if "STAGE:" in t]
recived_dates = [t.replace("RECEIVED DATE:", "").strip() for t in td_s if "RECEIVED DATE:" in t]
status = [t.replace("Status:", "").strip() for t in td_s if "Status:" in t]
econ_sig = [t.replace("ECONOMICALLY SIGNIFICANT:", "").strip() for t in td_s if "ECONOMICALLY SIGNIFICANT:" in t]
legal_deadline = [t.replace("LEGAL DEADLINE:", "").strip() for t in td_s if "LEGAL DEADLINE:" in t]

rin_links = [t.find("a", href=re.compile("RIN")) for t in td_s_raw]
rin_links = ["https://www.reginfo.gov" + r["href"] for r in rin_links if r != None]

data = list(zip(agencies,primary_agency, titles, rins, stages, recived_dates, status, econ_sig, legal_deadline, rin_links))

### Creation of the main daily file

df = pd.DataFrame(data, columns =['Agency', 'Primary_Agency', 'Title', 'RIN', 'Stage', 'Recived_Date', 'Status', "Econ_Signficance", "Legal_Deadline", "RIN_Link"])
df["DayScraped"] = today
print(df)
df.to_csv(f"./data/regInfoListedRegs{today_for_file}.csv")

### Creation of the count file

df_counts = df.value_counts(['Primary_Agency'])
df_counts = df_counts.to_frame('Count').reset_index()
df_counts["DayScraped"] = today
print(df_counts)
if os.path.exists("./data/regPerAgencyCount.csv") == True:
    old_data = pd.read_csv("./data/regPerAgencyCount.csv")
    combined_data = pd.concat([df_counts, old_data])
    combined_data.to_csv("./data/regPerAgencyCount.csv")

else:
    df_counts.to_csv(f"./data/regPerAgencyCount.csv")

