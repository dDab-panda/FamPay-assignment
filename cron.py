from apscheduler.schedulers.background import BackgroundScheduler as scheduler

import functions

sch = scheduler(daemon=True)
sch.add_job(functions.get_data_from_yt_api, 'interval', seconds=10)
sch.start()

try:
    print('Scheduler started, ctrl-c to exit!')
    while 1:
        pass    
except KeyboardInterrupt:
    if sch.state:
        sch.shutdown()