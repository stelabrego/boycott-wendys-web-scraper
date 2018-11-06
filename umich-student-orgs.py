from selenium import webdriver
import time
import re
from pathlib import Path
import csv
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

filename = "umich-all-org-emails.csv"
fileObj = Path(filename)
if fileObj.exists():
    fileObj.unlink()
    fileObj.touch()
csvFile = open(filename, 'w', newline='')

# disable images for optimization
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

driver = webdriver.Firefox(firefox_profile=firefox_profile)
driver.implicitly_wait(0.5) # seconds
driver.get("https://maizepages.umich.edu/organizations")

buttonDiv = driver.find_element_by_css_selector("#org-search-results + div")
loadMoreButton = buttonDiv.find_element_by_css_selector("button")
print("Button Text: " + loadMoreButton.text)

# 500 is good
for x in range(0, 1000):
    try:
        loadMoreButton.click()
        time.sleep(.1)
    except:
        break

orgSearchResults = driver.find_element_by_id("org-search-results")

linkTags = orgSearchResults.find_elements_by_css_selector("a")
orgPageUrls = [link.get_attribute("href") for link in linkTags]

emailPattern = re.compile('(?:EmailAddress":")(.+?)(?:")')
namePattern = re.compile('(?:"name":")(.+)(?:","short)')
writer = csv.DictWriter(csvFile, ["name", "email"])

for orgPageUrl in orgPageUrls:
    print("orgPageUrl: " + orgPageUrl)
    raw_html = simple_get(orgPageUrl)
    html = BeautifulSoup(raw_html, 'html.parser')
    emailSearch = emailPattern.search(html.find("body").text)
    if emailSearch == None:
        email = ""
    else:
        email = emailSearch.group(1).strip()
    nameSearch = namePattern.search(html.find("body").text)
    if nameSearch == None:
        name = ""
    else:
        name = nameSearch.group(1).strip()
    writer.writerow({"name":name, "email":email})
    print(str({"name":name, "email":email}))

csvFile.close()
driver.close()
