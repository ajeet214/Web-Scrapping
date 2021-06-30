import asyncio
import indicoio
import concurrent.futures
from modules.caps_client import CapsClient
indicoio.config.api_key = CapsClient().get_credential_random('indico', 'api_key')['api_key']['access_token']


async def main(result_list):
    lst = []
    print(result_list)
    print(len(result_list))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

        loop = asyncio.get_event_loop()
        urls = result_list
        # print(urls)

        # futures = [loop.run_in_executor(executor, indicoio.sentiment, i['content'])for i in urls]
        futures = []
        for i in urls:
            if i['content'] is None:

                futures.append(loop.run_in_executor(executor, indicoio.sentiment, 'null'))
                pass
            else:
                futures.append(loop.run_in_executor(executor, indicoio.sentiment, i['content']))

        for response in await asyncio.gather(*futures):
            # print(response.text)
            lst.append(response)

    print(lst)
    print(len(lst))
    for i in range(len(result_list)):

        if lst[i] > 0.5000000000000000:
            result_list[i]['polarity'] = 'positive'
        elif lst[i] == 0.031184496628274796:
            result_list[i]['polarity'] = 'neutral'
        elif lst[i] < 0.5000000000000000:
            result_list[i]['polarity'] = 'negative'

    # print(result_list)
    return {'data': result_list}
