# TripAdvisor

https://www.tripadvisor.com/Search?q=hanoi%2C%20vietnam&ssrc=e

https://www.tripadvisor.com/Search?q=hanoi%2C%20vietnam&searchSessionId=2A198A102B715C3AB206A52F8D7E4D581688098364143ssid&sid=30DB688F4D82488FB76AFA60033111151688098365296&blockRedirect=true&geo=1

## Restaurants:
### Data to scrape for restaurants, below are the column names of the data:

- restaurant_name
- restaurant_address
- restaurant_neighborhoods
- restaurant_website
- email_id
- mobile_number
- restaurant_about
- price_range
- cuisines	
- image_urls

url: https://www.tripadvisor.com/Search?q=hanoi%2C%20vietnam&ssrc=e

##### url query parameters:
- query: q= (any string)
- pagination: o= (30 for 2nd page, 60 for 3rd page and so on)
- category: ssrc= (e for restaurants, h for hotels, A for things to do).

##### restaurant image links:
- l: small
- t: thumbnail
- o: original
- s: large
- f: medium

### Data to scrape for hotels, below are the column names of the data:

- hotel_name
- hotel_address
- restaurant_neighborhoods
- hotel_website
- email_id
- mobile_number
- hotel_about
- whatsapp
- Property amenities
- Room features
- Room types
- locations data
- image_urls
- q&a
- 
Json data:
- pageManifest:
    - dict_keys(['messages', 'features', 'urqlCache', 'redux', 'assets', 'bundles', 'lazyLoadedModules', 'renders', 'hydrations'])
	    - redux:
		    - dict_keys(['i18n', 'api', 'page', 'travelerInfo', 'auth', 'route', 'lithiumRoute', 'overlays', 'meta', 'tracking'])
	 		    - api: dict_keys(['requests', 'responses'])

url: https://www.tripadvisor.com/Search?q=hanoi%2C%20vietnam&ssrc=h

### Data to scrape for "things to do", below are the column names of the data:

url: https://www.tripadvisor.com/Search?q=hanoi%2C%20vietnam&ssrc=A


### different languages with their domain:
- countries/languages with https://www.tripadvisor.xx
  - ca
  - cl
  - co
  - it
  - es
  - de
  - fr
  - se
  - nl
  - dk
  - ie
  - at
  - pt
  - ru
  - ch
  - be
  - jp
  - cn
  - in


 - countries/languages with https://www.tripadvisor.com.xx

    - br
    - mx
    - ar
    - pe
    - ve
    - tr
    - gr
    - au
    - my
    - ph
    - sg
    - vn
    - tw
    - hk
    - eg
 
 - countries/languages with https://www.tripadvisor.co.xx

    - uk
    - nz
    - id
    - kr
    - za
    - il
 
 - countries/languages with https://xx.tripadvisor.com

    - cn
    - ar
    - th
    - no

 - countries/languages with https://xx.tripadvisor.xx

    - fr, ca
    - fr, ch
    - it, ch
    - fr, be
   

https://en.tripadvisor.com.hk
 
--------------------------------------------------------------------------------------------------------------
### Please follow the steps below to setup the environment and run the script:
1. unzip the project folder.
2. open the terminal inside the project folder named *Tripadvisor_Service*.
3. install the required libraries using 
   -  **pip install requirements**

4. To scrape the restaurant urls from the tripadvisor restaurant section,  please follow the command below:
    - *run the below command on the terminal to search for restaurants in tokyo,japan*:
    - python main.py -q tokyo,japan -c r

5. To scrape the hotel urls from the tripadvisor hotel section,  please follow the command below:
    - *run the below command on the terminal to search for hotels in hanoi*:
    - python main.py -q hanoi -c h

6. To scrape the things to do urls from the tripadvisor things to do section,  please follow the command below:
    - *run the below command on the terminal to search for things to do in hanoi,vietnam*:
    - python main.py -q hanoi,vietnam -c t

7. after the completion of execution of each of the above scripts, the data gets saved into a csv file inside the project folder, namely
   - restaurant_urls.csv 
   - hotel_urls.csv
   - things_to_do_urls.csv

You may also check the log history of all the scripts in this project in the tripadvisor_log_url.log

To run the script to scrape the data from a restaurant, run the below command on the terminal:
   - python tripadvisor_restaurants.py -u restaurant_url
   - for example, python tripadvisor_restaurants.py -u https://www.tripadvisor.com/Restaurant_Review-g293924-d6508772-Reviews-Namaste_Hanoi-Hanoi.html

