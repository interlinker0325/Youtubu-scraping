import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Set up the Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run Chrome in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920x1080")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_video_links(channel_url, scroll_times=5):
    """Extracts video links from a YouTube channel's videos page."""
    driver.get(channel_url)
    time.sleep(5)

    for _ in range(scroll_times):  # Scroll to load more videos
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    video_links = set()
    elements = driver.find_elements(By.TAG_NAME, "a")

    for elem in elements:
        link = elem.get_attribute("href")
        if link and "watch?" in link:
            video_links.add(link)

    return list(video_links)

def get_comments(video_url, max_scrolls=3):
    """Extracts comments, usernames, and timestamps from a YouTube video page."""
    driver.get(video_url)
    time.sleep(5)

    for _ in range(max_scrolls):  # Scroll down to load more comments
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    comments_data = []
    
    comments = driver.find_elements(By.CSS_SELECTOR, "yt-attributed-string#content-text")
    usernames = driver.find_elements(By.CSS_SELECTOR, "a#author-text span")
    timestamps = driver.find_elements(By.CSS_SELECTOR, "span#published-time-text a")

    for i in range(min(len(comments), len(usernames), len(timestamps))):
        comments_data.append({
            "Comment": comments[i].text.strip(),
            "Name": usernames[i].text.strip(),
            "Date": timestamps[i].text.strip(),
            "Video URL": video_url
        })

    return comments_data

try:
    # Step 1: Get video links
    channel_url = "https://www.youtube.com/@olliewride/videos"
    video_links = get_video_links(channel_url)

    print("\nExtracted Video Links:")
    for link in video_links:
        print(link)

    # Step 2: Get comments for each video
    all_comments = []

    for video_url in video_links[:3]:  # Limit to first 3 videos (adjust if needed)
        print(f"\nFetching comments for: {video_url}")
        comments = get_comments(video_url)
        all_comments.extend(comments)

    # Step 3: Save comments to an Excel file
    df = pd.DataFrame(all_comments)
    df.to_excel("youtube_comments.xlsx", index=False)

    print("\n✅ Comments saved to youtube_comments.xlsx")

finally:
    driver.quit()  # Close the browser
