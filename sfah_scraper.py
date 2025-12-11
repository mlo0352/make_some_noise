import requests
import json
import re
import time

SUBREDDIT = "ScenesFromAHat"     # or "ScriptsFromAHat" if you meant that one
MIN_SCORE = 5
USER_AGENT = "script:sfah_crawler:1.0 (by u_yourusername)"  # be nice to Reddit

BASE_URL = f"https://www.reddit.com/r/{SUBREDDIT}/.json"
HEADERS = {"User-Agent": USER_AGENT}

def clean_title(title: str) -> str:
    """
    Strip leading 'SFAH: ' (case-insensitive) + common variants like 'SFAH - '.
    """
    return re.sub(r"^\s*SFAH[:\-\s]+", "", title, flags=re.IGNORECASE).strip()

def crawl_subreddit():
    all_posts = []
    after = None

    while True:
        params = {"limit": 100}
        if after:
            params["after"] = after

        resp = requests.get(BASE_URL, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json().get("data", {})

        children = data.get("children", [])
        if not children:
            break

        for child in children:
            post = child.get("data", {})
            score = post.get("score", 0)
            if score < MIN_SCORE:
                continue

            raw_title = post.get("title", "")
            title = clean_title(raw_title)
            permalink = "https://www.reddit.com" + post.get("permalink", "")

            all_posts.append({
                "title": title,
                "score": score,
                "permalink": permalink,
            })

        after = data.get("after")
        if not after:
            break

        # Be polite to Reddit, avoid hammering
        time.sleep(1)

    return all_posts

if __name__ == "__main__":
    posts = crawl_subreddit()
    with open("scenes_from_a_hat_prompts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(posts)} posts with score ≥ {MIN_SCORE}")
