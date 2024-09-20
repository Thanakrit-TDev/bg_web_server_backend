import time

now = int(time.time())
new = now

while True:
    now = int(time.time())
    # print(now)
    if(now == new):
        new = now+5
        print(new)
