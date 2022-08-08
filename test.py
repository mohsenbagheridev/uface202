import schedule
import time

def job():
    print("I'm working...")

schedule.every().minute.at(":17").do(job)


while True:
    schedule.run_pending()
    time.sleep(1)