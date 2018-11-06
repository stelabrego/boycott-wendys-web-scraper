from selenium import webdriver
import time
import re
from pathlib import Path
import csv

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
dropdownButton = driver.find_element_by_css_selector("span.Select-arrow-zone")

# 500 is good
for x in range(0, 1000):
    try:
        loadMoreButton.click()
        time.sleep(.1)
    except:
        break

print("Search Result Line Count:")
orgSearchResults = driver.find_element_by_id("org-search-results")
print(orgSearchResults.text.count("\n"))

links = orgSearchResults.find_elements_by_css_selector("a")

driver2 = webdriver.Firefox(firefox_profile=firefox_profile)
pattern = re.compile('[\w\.-]+@[\w\.-]+')
writer = csv.DictWriter(csvFile, ["name", "email"])

for link in links:
    textArray = str.splitlines(link.text)
    name = textArray[0]
    url = link.get_attribute("href")
    driver2.get(url)
    goodText = driver2.find_element_by_css_selector("body").text
    search = pattern.search(goodText)
    if search == None:
        email = ""
    else:
        email = search.group(0)
    writer.writerow({"name":name, "email":email})
    print(str({"name":name, "email":email}))

csvFile.close()
driver.close()
driver2.close()
