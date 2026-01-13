
from playwright.sync_api import sync_playwright, expect

def test_dashboard(page):
    # Navigate to the dashboard
    page.goto("http://localhost:8347")

    # Check title
    expect(page).to_have_title("MoDEM Dashboard")

    # Check accessibility: "for" attribute on Mode label
    # Note: Playwright doesn't easily check 'for' attribute directly with user-facing locators,
    # but we can check if clicking the label focuses the input.
    page.get_by_text("Mode", exact=True).click()
    expect(page.locator("#mode-select")).to_be_focused()

    # Check accessibility: "for" attribute on Prompt label
    page.get_by_text("Prompt / Objective").click()
    expect(page.locator("#prompt-input")).to_be_focused()

    # Switch to Simulation Mode to check Simulation output changes (we can't easily run a job without backend,
    # but we can mock the response or check the UI state)

    # Select Simulation mode
    page.select_option("#mode-select", "simulation")

    # Check if Experiment Controls appear
    expect(page.locator("#experiment-controls")).to_be_visible()

    # Check accessibility: "for" attribute on Probe Protocol label
    page.get_by_text("Probe Protocol").click()
    expect(page.locator("#probe-protocol")).to_be_focused()

    # Check accessibility: "for" attribute on Probe Count label
    page.get_by_text("Probe Count").click()
    expect(page.locator("#probe-count")).to_be_focused()

    # Take a screenshot
    page.screenshot(path="verification/dashboard_verified.png", full_page=True)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            test_dashboard(page)
            print("Verification successful!")
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="verification/failure.png")
        finally:
            browser.close()
