import schedule
import subprocess
import time

def run_cmd_sh():
    # Execute the cmd.sh script using subprocess
    subprocess.run(["/bin/bash", "/home/anurag3753/cmd.sh"])

# Schedule the task to run daily at 7:00 PM
schedule.every().day.at("19:00").do(run_cmd_sh)

# Run the scheduler continuously
while True:
    schedule.run_pending()
    time.sleep(60)  # Adjust the interval as needed
