"""
Project : 
Author : Ajeet
Date : June 27, 2023
"""
import requests
from bs4 import BeautifulSoup
from PIL import Image


def save_image(img_url):
    filename = img_url.split('/')[-1]
    img = Image.open(requests.get(img_url, stream=True).raw)
    img.save(f"{filename}")
    print(f"saved image: {filename}\n")


url = "https://us.shein.com/Ditsy-Floral-Print-Knot-Cuff-Blouse-p-14155075-cat-1733.html?src_identifier=fc%3DWomen%60sc%3DCLOTHING%60tc%3D0%60oc%3D0%60ps%3Dtab01navbar05%60jc%3DitemPicking_001121425&src_module=topcat&src_tab_page_id=page_home1687813063116&mallCode=1"

data = requests.get(url).text
soup = BeautifulSoup(data, 'lxml')

images = soup.select_one('div.product-intro__main').select('img')
print(f"https:{images[0].get('src')}")
save_image(f"https:{images[0].get('src')}")

for image in images[1:]:
    print(f"https:{image.get('data-src')}")
    save_image(f"https:{image.get('data-src')}")


"""
output:

https://img.ltwebstatic.com/images3_pi/2023/04/22/1682132328cfa167169f129c340da4fc854d5587b4_thumbnail_600x.jpg
saved image: 1682132328cfa167169f129c340da4fc854d5587b4_thumbnail_600x.jpg

https://img.ltwebstatic.com/images3_pi/2023/04/22/16821323962950631a3b7546fcb3f7beea67915bf4_thumbnail_600x.jpg
saved image: 16821323962950631a3b7546fcb3f7beea67915bf4_thumbnail_600x.jpg

https://img.ltwebstatic.com/images3_pi/2023/04/22/16821323996e9b06f5553e4a23876b767e12051b7a_thumbnail_600x.jpg
saved image: 16821323996e9b06f5553e4a23876b767e12051b7a_thumbnail_600x.jpg

https://img.ltwebstatic.com/images3_pi/2023/04/22/1682132401e3e59b7a6a6b5fdd1e6b2585313ba4b1_thumbnail_600x.jpg
saved image: 1682132401e3e59b7a6a6b5fdd1e6b2585313ba4b1_thumbnail_600x.jpg

https://img.ltwebstatic.com/images3_pi/2023/04/22/168213240373037078a11f0977ef94ae97e16ebfe6_thumbnail_600x.jpg
saved image: 168213240373037078a11f0977ef94ae97e16ebfe6_thumbnail_600x.jpg

https://img.ltwebstatic.com/images3_pi/2023/04/22/1682132408646e8ffe0b156bad84ef44d34c3d4f88_thumbnail_600x.jpg
saved image: 1682132408646e8ffe0b156bad84ef44d34c3d4f88_thumbnail_600x.jpg

https://img.ltwebstatic.com/images3_pi/2023/04/22/1682132410a5bb9b65bc0abe32ec5182c35fa2a640_thumbnail_600x.jpg
saved image: 1682132410a5bb9b65bc0abe32ec5182c35fa2a640_thumbnail_600x.jpg

reference:
https://stackoverflow.com/questions/76560247/how-to-scrape-good-quality-images-from-a-site-python-selenium
"""

