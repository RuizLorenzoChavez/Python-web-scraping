from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import datetime as dt
import os
import pandas as pd

print("Initializing YahooFinSpider")

#  URL for Yahoo Finance
url = "https://finance.yahoo.com/crypto/?offset=0&count=100"

#  calls locally installed chromedriver.exe
driver_path = os.getenv("WEBDRIVER") + "\chromedriver.exe"

#  enables headless mode
options = Options()
options.headless = True
options.add_argument("--window-size=1920,1200")
options.add_experimental_option("excludeSwitches", ["enable-logging"])

#  initializes HEADLESS Chrome webdriver (COMMENT WHEN DEBUGGING)
driver = webdriver.Chrome(options=options, service=Service(driver_path))

#  initializes Chrome webdriver (UNCOMMENT WHEN DEBUGGING)
# driver = webdriver.Chrome(service=Service(driver_path))

#  get page's URL
driver.get(url)

#  list of features
features = [
    "date_scraped",
    "symbol",
    "name",
    "price",
    "change",
    "change_perc",
    "market_cap",
    "vol_utc",
    "vol_24",
    "total_vol",
    "circ_supply",
]

#  page counter variable
page_num = 0

#  dictionary for scraped data
crypto_dict = {}

#  loop populating the crypto_dict with lists for each key
for feature in features:
    crypto_dict[feature] = []

#  TODO: Make this into a function so that it can be automatically iterated whenever the spider does not reach the target

while True:

    #  track how many pages have been scraped
    page_num += 1

    #  to prevent StaleElementReferenceException
    driver.refresh()
    driver.implicitly_wait(15)

    #  scrape entire table
    print(f"Extracting data table {page_num} from the site")
    table = driver.find_elements(By.XPATH, "//tbody/tr")

    try:
        #  scrape specific features per row
        print(f"Extracting data from table {page_num}")
        for row in table:
            date_scraped = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            symbol = row.find_element(By.XPATH, ".//td[@aria-label='Symbol']").text
            name = row.find_element(By.XPATH, ".//td[@aria-label='Name']").text
            price = row.find_element(
                By.XPATH, ".//td[@aria-label='Price (Intraday)']"
            ).text
            change = row.find_element(By.XPATH, ".//td[@aria-label='Change']").text
            change_perc = row.find_element(
                By.XPATH, ".//td[@aria-label='% Change']"
            ).text
            market_cap = row.find_element(
                By.XPATH, ".//td[@aria-label='Market Cap']"
            ).text
            vol_utc = row.find_element(
                By.XPATH, ".//td[@aria-label='Volume in Currency (Since 0:00 UTC)']"
            ).text
            vol_24 = row.find_element(
                By.XPATH, ".//td[@aria-label='Volume in Currency (24Hr)']"
            ).text
            total_vol = row.find_element(
                By.XPATH, ".//td[@aria-label='Total Volume All Currencies (24Hr)']"
            ).text
            circ_supply = row.find_element(
                By.XPATH, ".//td[@aria-label='Circulating Supply']"
            ).text

            #  list of features as variables
            var_features = [
                date_scraped,
                symbol,
                name,
                price,
                change,
                change_perc,
                market_cap,
                vol_utc,
                vol_24,
                total_vol,
                circ_supply,
            ]

            #  append scraped data from to the dictionary
            for feats, var in zip(features, var_features):
                crypto_dict[feats].append(var)

        #  allows indefinite page traversal (one-way)
        try:
            nxt_button = driver.find_element(
                By.XPATH,
                "//button[@class='Va(m) H(20px) Bd(0) M(0) P(0) Fz(s) Pstart(10px) O(n):f Fw(500) C($linkColor)']",
            )
            nxt_button.click()
            print(f"Page {page_num} done")
        except:
            print("No more pages (Exit 2)")
            break
    except:
        print("No more pages (Exit 1)")
        break

#  log the date and time scraping was finished
scraped_date = dt.datetime.now()
print(f"Finished scraping: {scraped_date.strftime('%Y-%m-%d %H:%M:%S')}")

#  shut down webdriver
driver.close()

#  transfer crypto dictionary to pandas DataFrame
crypto_df = pd.DataFrame(crypto_dict)

print(f"Number of Entries Scraped: {crypto_df.shape[0]}")

#  check if spider scraped data
if crypto_df.shape[0] != 0:
    #  if the spider did actually collect data
    file_name = f"crypto\{scraped_date.strftime('%Y-%m-%d')}_cryptocurrency.csv"
    crypto_df.to_csv(file_name)

    #  confirm if the current file has actually been saved in the folder
    #  also log scraping activities to log.txt (feature as of 25 September 2022)
    log = open("log.txt", "a")

    # TODO: evaluate the necessity of this if statement
    if os.path.isfile(file_name):
        print("File has been saved successfully.")
        log.write(
            f"\nFile has been saved succesfully: {scraped_date.strftime('%Y-%m-%d %H:%M:%S')}\nNumber of Entries Scraped: {crypto_df.shape[0]}\n "
            )
        log.close()
    else:
        print("File does not exist.")
        log.write("Unable to save file.\n")
        log.close()

print("Extraction process terminated.")
