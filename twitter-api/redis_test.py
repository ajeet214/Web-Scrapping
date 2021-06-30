import requests
import json
import redis
import time

# ab = requests.get('http://127.0.0.1:5000/search?q=tom hardy').text
ab = requests.get('http://127.0.0.1:5000/search/profiles?q=bill gates').text

# ab = requests.get('http://127.0.0.1:5000/profile/friends/martin').text
# ab = requests.get('http://127.0.0.1:5000/profile/followers/vvvoler').text

# ab = requests.get('http://127.0.0.1:5000/search/posts?q=trump&time_duration=past_month').text
print(ab)
ac = json.loads(ab)
print(ac)
cl_id = ac['channel_id']
print(cl_id)
r = redis.Redis(host='127.0.0.1', port=6379)
p = r.pubsub()
p.subscribe(cl_id)
time.sleep(5)

count = 0
while True:
    msg = p.get_message()
    print(msg)
    try:
        if msg['data'] == b'EOF':
            break
    except TypeError:
        pass
    time.sleep(1)
    count += 1

    # print('#')
    # time.sleep(1)

print(count-1)