import schedule
import subprocess
import time
import datetime

def run_cmd_sh():
    # Execute the cmd.sh script using subprocess
    subprocess.run(["/bin/bash", "/path/to/cmd.sh"])

# Define the time in UTC for 7:00 PM IST
target_time_utc = datetime.time(13, 30)  # 7:00 PM IST is 13:30 UTC

# Schedule the task to run daily at the target time in UTC
schedule.every().day.at(target_time_utc.strftime("%H:%M")).do(run_cmd_sh)

# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(60)  # Adjust the interval as needed

