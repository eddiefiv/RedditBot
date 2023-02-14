import json
import re
import os
import ctypes

from playwright.sync_api import ViewportSize, sync_playwright

from utils.console import print_step, print_substep
#TODO: Get title screenshots for stories, and speak them
def get_screenshots(submission, screenshot_num: int = 0):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png
    Args:
        submission (Reddit Submission): Submission to read data from
        screenshot_num (int): Number of screenshots to download
    """

    W = 1080
    H = 1920

    print_step("Downloading screenshots...")

    if os.path.exists(f"screenshots/{submission.id}"):
        pass
    else:
        os.makedirs(f"screenshots/{submission.id}")

    with sync_playwright() as p:
        print_substep("Launching Headless Browser...", style="bold blue")

        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Device scale factor (or dsf for short) allows us to increase the resolution of the screenshots
        # When the dsf is 1, the width of the screenshot is 600 pixels
        # so we need a dsf such that the width of the screenshot is greater than the final resolution of the video
        dsf = (W // 600) + 1

        context = browser.new_context(
            locale="en-us",
            color_scheme="dark",
            viewport=ViewportSize(width=W, height=H),
            device_scale_factor=dsf
        )

        cookie_file = open("utils/data/cookie-dark-mode.json", encoding="utf-8")

        cookies = json.load(cookie_file)
        cookie_file.close()

        context.add_cookies(cookies)

        page = context.new_page()
        page.goto(submission.url, timeout=0)
        page.set_viewport_size(ViewportSize(width=W, height=H))

        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button

            print_substep("Post is NSFW.")
            page.locator('[data-testid="content-gate"] button').click()
            page.wait_for_load_state() # Wait for page to fully load

            if page.locator('[data-click-id="text"] button').is_visible():
                page.locator('[data-click-id="text"] button').click() # Remove "Click to see nsfw" Button in screenshot

        page.get_by_text(submission.title).screenshot(path=f"screenshots/{submission.id}/png/title.png")
        page.locator('[data-click-id="text"]').first.screenshot(path=f"screenshots/{submission.id}/png/story_content.png")

        browser.close()

    print_substep("Screenshots downloaded successfully.", style="bold green")