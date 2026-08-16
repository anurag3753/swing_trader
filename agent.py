from playwright.sync_api import sync_playwright
import os
import time

# Strictly require environment variables
USERNAME = os.environ.get("PA_USERNAME")
PASSWORD = os.environ.get("PA_PASSWORD")
DEBUG = os.environ.get("PA_DEBUG", "0").lower() in ("1", "true", "yes")
RUN = os.environ.get("PA_RUN", "0").lower() in ("1", "true", "yes")

def run_agent():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not DEBUG, slow_mo=50 if DEBUG else 0)
        page = browser.new_page()

        try:
            print("Authenticating...")
            page.goto("https://www.pythonanywhere.com/login/")
            page.fill('input[name="auth-username"]', USERNAME)
            page.fill('input[name="auth-password"]', PASSWORD)
            page.click('button:has-text("Log in")')

            # Natively wait for the logout form to appear to confirm login success
            page.wait_for_selector('form[action="/logout/"]', timeout=60000)
            print("Login successful.")

            print("Scanning Tasks Tab...")
            page.goto(f"https://www.pythonanywhere.com/user/{USERNAME}/tasks_tab/")
            
            # Use Playwright's locator to count buttons without needing explicit sleeps
            task_buttons = page.locator('button.extend_scheduled_task')
            task_count = task_buttons.count()
            
            if task_count > 0:
                print(f"Found {task_count} task(s) to extend.")
                for i in range(task_count):
                    if RUN:
                        task_buttons.nth(i).click()
                        print(f"-> Task {i+1} expiry extended.")
                        time.sleep(1) # Small buffer between clicks
                    else:
                        print("-> Dry-run: would click task extend button.")
            else:
                print("-> No tasks require extension.")

            print("Scanning Web Apps Tab...")
            page.goto(f"https://www.pythonanywhere.com/user/{USERNAME}/webapps_tab/")
            
            web_buttons = page.locator('input.webapp_extend')
            web_count = web_buttons.count()
            
            if web_count > 0:
                print(f"Found {web_count} web app(s) to extend.")
                for i in range(web_count):
                    if RUN:
                        web_buttons.nth(i).click()
                        print(f"-> Web app {i+1} expiry extended.")
                        time.sleep(1)
                    else:
                        print("-> Dry-run: would click webapp extend control.")
            else:
                print("-> No web apps require extension.")

            print("Terminating session...")
            # Safely log out using the POST form evaluated in the DOM
            page.evaluate('document.querySelector("form[action=\'/logout/\']").submit()')
            print("Autonomous execution complete.")

        except Exception as e:
            print(f"Workflow failed: {e}")
            if DEBUG:
                page.pause()
        finally:
            browser.close()

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        print("Error: PA_USERNAME and PA_PASSWORD environment variables must be set.")
    else:
        run_agent()
