from apscheduler.schedulers.blocking import BlockingScheduler
import urllib.request
from datetime import datetime

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour='8-23', minute='*/5')
def scheduled_job():
    
    print('========== APScheduler CRON =========')
        # 馬上讓我們瞧瞧
    print('This job runs every day */2 min.')
    # 利用datetime查詢時間
    print(f'{datetime.now().ctime()}')
    
    print('========== APScheduler CRON =========')
    url = "https://cbare.herokuapp.com"
    conn = urllib.request.urlopen(url)
        
    for key, value in conn.getheaders():
        print(key, value)

sched.start()