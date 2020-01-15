from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler
import finTrack

def emailTest(task_id):
    msg = Message("Hello, task id is {}".format(task_id),
                  sender="342049327@qq.com",
                  recipients=["xumenglove@icloud.com"])
    finTrack.mail.send(msg)


def scheduleEmail():
    scheduler = BackgroundScheduler()
    scheduler.add_job(emailTest())
    scheduler.start()