from GetSaveNews import SaveToDb
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

# @sched.scheduled_job('interval', hours=10)
# def timed_job():
#     print('This job is run every 10 hours.')
#     SaveToDb()

# @sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
# def scheduled_job():
#     print('This job is run every weekday at 5pm.')


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    SaveToDb()



sched.start()


