# selenium_cookies_example.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json

# --- config ---
URL = "https://finance.yahoo.com/quote/AAPL"   # page to visit
HEADLESS = True

# --- create Chrome driver (auto-download driver via webdriver-manager) ---
chrome_opts = Options()
if HEADLESS:
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--no-sandbox")
chrome_opts.add_argument("--disable-dev-shm-usage")
chrome_opts.add_argument("start-maximized")
chrome_opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_opts)

try:
    driver.get(URL)

    # optional: wait for page to load / a known element to appear
    time.sleep(3)   # simple sleep; replace with WebDriverWait for robust scripts

    # get cookies as list of dicts
    cookies_list = driver.get_cookies()
    print("Selenium cookies (list):")
    print(json.dumps(cookies_list, indent=2))

    # --- Option A: convert to requests.Session cookies ---
    sess = requests.Session()
    for c in cookies_list:
        # requests expects name and value; domain/path and others are optional but can be supplied
        cookie = requests.cookies.create_cookie(name=c['name'], value=c['value'],
                                                domain=c.get('domain'), path=c.get('path'))
        sess.cookies.set_cookie(cookie)

    # now do a requests GET using the session (will send cookies)
    resp = sess.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL", 
                    headers={"User-Agent": "Mozilla/5.0"})
    print("requests status:", resp.status_code)
    try:
        print(resp.json())   # may be JSON or an error depending on endpoint and permissions
    except Exception:
        print(resp.text[:500])

    # --- Option B: build a Cookie header string (useful for manual headers) ---
    cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies_list])
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie_header
    }
    resp2 = requests.get("https://query1.finance.yahoo.com/v7/finance/quote?symbols=AAPL", headers=headers)
    print("requests with Cookie header status:", resp2.status_code)

    # --- Option C: save cookies to disk and load later ---
    with open("cookies.json", "w") as f:
        json.dump(cookies_list, f, indent=2)

    # Later you can load them:
    # with open("cookies.json") as f:
    #     cookies_list = json.load(f)
    #     for c in cookies_list:
    #         sess.cookies.set_cookie(requests.cookies.create_cookie(name=c['name'], value=c['value']))
finally:
    driver.quit()
