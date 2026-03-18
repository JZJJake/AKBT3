from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        print("Navigating to http://localhost:8000")
        page.goto("http://localhost:8000")

        # Enable console logging to see frontend errors
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))

        # Wait for the main UI to load
        page.wait_for_selector(".chart-container")
        print("Chart container found.")

        # Click on the first stock in the list
        try:
            page.wait_for_selector("ul.stock-list li", timeout=5000)
            page.locator("ul.stock-list li").first.click()
            print("Clicked first stock.")
        except Exception as e:
            print("Could not click stock item:", e)

        # Wait a bit to ensure the API call finishes and chart renders
        print("Waiting for chart to render...")
        time.sleep(5)

        page.screenshot(path="terminal_view_wait.png")
        print("Screenshot saved to terminal_view_wait.png")
        browser.close()

run()
