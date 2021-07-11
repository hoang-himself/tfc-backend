from django_cron import CronJobBase, Schedule

import datetime

class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Fuck'

    def do(self):
        print(f'Fuck {datetime.datetime.now()}')

class MyCronJob1(CronJobBase):
    RUN_EVERY_MINS = 2

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Unfuck'

    def do(self):
        print(f'Unfuck {datetime.datetime.now()}')