"""
Project : it examms questions
Author : Ajeet
Date : July 21, 2023
"""

import requests
from bs4 import BeautifulSoup

s = requests.session()
res = s.get(url='https://www.itexams.com/accounts/login/').text
soup = BeautifulSoup(res, 'html.parser')
csrf_token = soup.select_one('input[name="csrfmiddlewaretoken"]').get('value')

payload = {
    "csrfmiddlewaretoken": csrf_token,
    "username": "username",
    "password": "password",
    "next": "/"
}
headers = {
"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
res2 = s.get(url='https://www.itexams.com/', data=payload, headers=headers)
soup2 = BeautifulSoup(res2.text, 'html.parser')


data = s.get('https://www.itexams.com/exam/Professional-Cloud-Architect?').text
soup3 = BeautifulSoup(data, 'html.parser')

container = soup3.select('div.card')
print(f"Total Questions: {len(container)}")

for card in container:
    print('----------------------------------------')
    question = card.select_one('div.question_text').text
    print(question.strip())
    options = card.select('ul.choices-list.list-unstyled>li')
    for option in options:
        print(option.text.strip())
    answer = card.select_one('div.answer_block.green.accent-1')
    print(f"Answer: {answer.get('data-answer').strip()}")

