"""
Project : 
Author : Ajeet
Date : June 19, 2023
"""

from bs4 import BeautifulSoup
import pandas as pd
import requests

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def extract_data_from_table(table):
    countries = []
    regions_states = []
    start_dates = []
    end_dates = []
    prev_country = None
    if table:
        for row in table.find('tbody').find_all('tr'):
            try:
                country_col = row.find('th').text.strip()
                prev_country = country_col
            except AttributeError:
                pass

            other_col = row.find_all('td')
            if len(other_col) > 2:
                countries.append(prev_country)
                regions_states.append(other_col[0].text.strip())
                start_dates.append(other_col[1].text.strip())
                end_dates.append(other_col[2].text.strip())

        return pd.DataFrame({
            'Country': countries,
            'Regions/States': regions_states,
            'DST Start Date': start_dates,
            'DST End Date': end_dates
        })
    else:
        return None


data = requests.get('https://www.timeanddate.com/time/dst/2023.html', headers={"Accept-Language": "en"})
soup = BeautifulSoup(data.text, 'html.parser')

table = soup.find('table', class_='table table--inner-borders-all table--left table--striped table--hover')
df = extract_data_from_table(table)

if df is not None:
    print(df)

"""
To make sure that the result is in English, pass the headers along with requests. headers={"Accept-Language": "en"}

reference:
https://stackoverflow.com/questions/76504024/selenium-webdriverwait-timeoutexception-when-trying-to-fetch-data-into-pandas-da
"""
