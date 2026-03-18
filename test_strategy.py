from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        print("Navigating to http://localhost:8000")
        page.goto("http://localhost:8000")

        # Click on Strategy view
        print("Clicking strategy view...")
        page.locator("a[href='/strategy']").click()

        # Wait for the run button
        page.wait_for_selector("button.btn-primary")
        print("Running strategy...")
        page.locator("button.btn-primary").click()

        # Wait for results
        time.sleep(3)
        page.screenshot(path="strategy_view_wait.png")
        print("Screenshot saved to strategy_view_wait.png")
        browser.close()

run()
