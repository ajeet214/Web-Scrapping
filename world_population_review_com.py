"""
Project : 
Author : Ajeet
Date : June 27, 2023
"""

import json
import requests
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', str)

soup = BeautifulSoup(requests.get('https://worldpopulationreview.com/countries').text, 'html.parser')
population_list = json.loads(soup.select_one('script#__NEXT_DATA__').get_text())['props']['pageProps']['data']

df = pd.DataFrame(population_list)
print(df.head())

"""
output:

   place     pop1980      pop2000      pop2010      pop2022      pop2023      pop2030      pop2050        country      area  landAreaKm cca2 cca3  netChange  growthRate  worldPercentage  density  densityMi  rank
0    356 696828385.0 1059633675.0 1240613620.0 1417173173.0 1428627663.0 1514994080.0 1670490596.0          India 3287590.0   2973190.0   IN  IND     0.4184      0.0081           0.1785 480.5033  1244.5036     1
1    156 982372466.0 1264099069.0 1348191368.0 1425887337.0 1425671352.0 1415605906.0 1312636325.0          China 9706961.0   9424702.9   CN  CHN    -0.0113     -0.0002           0.1781 151.2696   391.7884     2
2    840 223140018.0  282398554.0  311182845.0  338289857.0  339996563.0  352162301.0  375391963.0  United States 9372610.0   9147420.0   US  USA     0.0581       0.005           0.0425  37.1686    96.2666     3
3    360 148177096.0  214072421.0  244016173.0  275501339.0  277534122.0  292150100.0  317225213.0      Indonesia 1904569.0   1877519.0   ID  IDN     0.0727      0.0074           0.0347 147.8196   382.8528     4
4    586  80624057.0  154369924.0  194454498.0  235824862.0  240485658.0  274029836.0  367808468.0       Pakistan  881912.0    770880.0   PK  PAK     0.1495      0.0198             0.03 311.9625   807.9829     5

reference:
https://stackoverflow.com/questions/76284251/how-to-scrape-a-table-from-a-website-and-create-a-dataframe
"""
