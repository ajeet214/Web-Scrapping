import asyncio
import aiohttp
import os
import base64
from config import Config
# from aiosocks.connector import ProxyClientRequest
from aiosocksy.connector import ProxyConnector, ProxyClientRequest
from modules.caps_client import CapsClient
from minio import Minio
import hashlib
from minio.error import ResponseError

minioClient = Minio(Config.MINIO_URI,
                    access_key=Config.MINIO_ACCESS_KEY,
                    secret_key=Config.MINIO_SECRET_KEY,
                    secure=False)


async def minio_upload(object_url,bucket_name):
    # print(object_url)
    # conn = ProxyConnector(verify_ssl=False, remote_resolve=True)
    # try:
    # print('1111')
    # print(object_url)
    url_hash_object = hashlib.md5(object_url.encode())
    filename = url_hash_object.hexdigest()
    # print(filename)

    proxy_obj = CapsClient()
    proxy = proxy_obj.get_proxy_random()
    connector = ProxyConnector()

    response = dict()
    # proxy_dict = _get_proxy()
    # print(object_url)
    if object_url.startswith('http'):

        proxy_str = str('socks5://' + proxy['host'] + ':' + proxy['port'])

        async with aiohttp.ClientSession(connector=connector, request_class=ProxyClientRequest) as session:
            # with aiohttp.ClientSession(loop=loop, request_class=ProxyClientRequest) as session:
            #     the_results = loop.run_until_complete(
            #         fetch_all(session, object_url))

            async with session.get(object_url,
                                   proxy=proxy_str) as resp:
                if resp.status == 200:
                    image_bytes = await resp.read()
                    with open(filename, 'wb') as f:
                        f.write(image_bytes)
                        f.close()

                    minioClient.fput_object(bucket_name, filename, filename)
                    os.remove(filename)

                    response['status'] = 200
                    # response['type'] = object_url[1]
                    response['file_url'] = filename

                else:
                    response['status'] = 500
                    # response['type'] = None
                    response['file_url'] = None

                # print(response)
                return response

    elif object_url.startswith('data:image/'):

        object_url = object_url.replace('data:image/jpeg;base64,', '')
        # print('********************')
        # decoding the base64 image
        image_bytes = base64.b64decode(object_url)
        with open(filename, 'wb') as f:
            f.write(image_bytes)
            f.close()

        minioClient.fput_object(bucket_name, filename, filename)
        os.remove(filename)

        response['status'] = 200
        # response['type'] = object_url[1]
        response['file_url'] = filename

        return response


async def process_all_urls(urls, bucket_name):
    results = await asyncio.gather(
        *[minio_upload(url, bucket_name) for url in urls],
        return_exceptions=False  # default is false, that would raise
    )
    # print('####')
    # print(results)
    return results


def start_uploading(file_urls, bucket_name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    final_result = loop.run_until_complete(process_all_urls(file_urls, bucket_name))
    # print(final_result)
    return final_result


if __name__ == '__main__':
    file_urls = ['https://scontent-frt3-1.xx.fbcdn.net/v/t1.0-1/p50x50/52391268_2246038305649975_4506594052799463424_n.png?_nc_cat=102&_nc_ht=scontent-frt3-1.xx&oh=bd95f18343b01a05e1b4931ae21c6c8f&oe=5D36C669', 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAEEAdAMBIgACEQEDEQH/xAAbAAABBQEBAAAAAAAAAAAAAAABAAIDBAUGB//EADkQAAEDAgQCBwQIBwAAAAAAAAEAAgMEEQUSITEycQYTIjNBUWEUgbHBIzRScpGh0fAHJTZCc3TC/8QAGQEAAwEBAQAAAAAAAAAAAAAAAQIDAAQF/8QAHBEBAQADAQEBAQAAAAAAAAAAAAECESEDMRJB/9oADAMBAAIRAxEAPwDxYoHZEoHhRYAp4+6PNQBTx90eaFY1OCCKRRpwn6NvJOO6ji4G8lId0ihjxqkzQgoy6IDwT34X+pnG6mFLOQCY8oO2YgX9xU0LhRsiIaDUTNzNcderb4Eeptut3BYSLSFoLiVPWu007yOYljfG3ttsPPcKF2y744Eys7T4LOcBmLdrrmukGByYaOtaLwl+Xl5fNNhZfjZ4XH6t9GOkdDhGHvp6umnke6UvBjYwixAHiR5JLl/ekqpaZRQOycd008KKYBTxd0eagCsRdy7mhRNRCCKRRoRcLeSkO6ji4G8lKBcm6VUJBomHYKV4GVNDHPc1jAS5xDQPMlNbwNdbLqOYVXtEjAWkWa1o2aABv6bLdwasErjeEDLpe+iqOlhfHGRI1z4XOY4Z9z5gfvRT4Ldz+oDspI0JXLlndddmPljLx2GCSSNlNm5xe9h8Ef4hw0lX0ZqpOrMUsbQ8X8SD+x71hOw7pRSud7DWMYw9oB8Qy2/DmqfTbGMUjoxhFYyJ7ZYWPdUNNiTcGwbuPBbGXc0bOz83ccFZJEjVJdrzmS5NPCnOTTsiiAViLuXc1XarEPdO5oUTUgkikVX4uBvJTeJUMPC3krMjRBE2Wc5Q8XYy/aePPl6pZ2qb1DWMMjmtzBoJ1cdmjzK1MCOHy4jVU1QHMjqcrYHE2ILdtfAk2PMLGMj6jsgZI/st+fmpRHlAa4Gx4VWRG5bdBPQy4W5zJO20EEOtxC26fSyOFQHwPAN2gXWtgv8APcIdTVDiaiLsmQi520d7/HkVzMMj8LxN1DirOrc118w1uPMei5/Xys7HZ4+0upXZHpBWVdNGylMNRLESJabrsjibaAG3yXMdLsbGLVVOOoEJpouqcL3u4HXXxV3GXxU+HiqilpKnOGsjzRAva77QO4IHyXJHhQ8sZvZvfO6/Jxd6JJqS6dOTbIKYeFPcmO4UagDVZh7p3NVmqzB3T+aFEzxRSSukUXo5GwxtkkbmaBw/aPgFAZZKmd00zi+R2rnH97eiNULUsGuriTb8v1TYvo2B4F2nQ+iOM4Gd3WhRWFi4aHRXXCzWvb/abkeYWcXZWgtOm6t0M4kzNJ1CcrZ6O1stDisToCy830VpD2bna/pe35qp0kqqmTEY5ath9rDjE54blynxFvxCoscWZ4tQWHS2mnh+nuWp0yrRX0GE4o4Bss9VNnA8w2MH87/iszEij60kRsOc7Bo3Pkp8Qw2uw4M9upZIc/CXDQ+/ZGiqPYpevABOfs3XSdI+kMNd0fp6KVsfXPe2Tsg9gNB11J1N7cr7Iam9mmWuOPSUjOpkGZxLfL1ST7jfpjOTXcKCSWpg1WYO6dzSSQogmpJJFVir7qn+6fihF9Vk5pJJonfqYfVo+RUmF/WHc0kkwLlR9Yb90o47/T2E/wCxN/ykksKCbgi5j4BNxnvYv8Q+JRSWBWO6SSSzP//Z']
    bucket_name = 'google-service'
    print(start_uploading(file_urls, bucket_name))