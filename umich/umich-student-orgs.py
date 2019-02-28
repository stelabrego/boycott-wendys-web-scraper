from selenium import webdriver
import time
import re
from pathlib import Path
import csv
import json
from requestHandler import get_souped

# delete csv file if it exists
filename = "umich-all-org-emails.csv"
fileObj = Path(filename)
if fileObj.exists():
    fileObj.unlink()
    fileObj.touch()
csvFile = open(filename, 'w', newline='')

# prepare csv writer
writer = csv.DictWriter(csvFile, ["org_name", "first_name", "preferred_first_name", "last_name", "email"])
writer.writeheader()

# disable images for optimization
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

# set up selenium driver
driver = webdriver.Firefox(firefox_profile=firefox_profile)
driver.implicitly_wait(0.5) # seconds
driver.get("https://maizepages.umich.edu/organizations")

# get the "load more" button from page
buttonDiv = driver.find_element_by_css_selector("#org-search-results + div")
loadMoreButton = buttonDiv.find_element_by_css_selector("button")

# range (0,0) for quick test
# range (0, 1000) for production
for x in range(0, 1000):
    try:
        loadMoreButton.click()
        time.sleep(.1)
    except:
        break

# get all the urls to the individual org pages
orgSearchResults = driver.find_element_by_id("org-search-results")
linkTags = orgSearchResults.find_elements_by_css_selector("a")
orgPageUrls = [link.get_attribute("href") for link in linkTags]

#regex patterns for the html response
orgNamePattern = re.compile('(?:"name":")(.+)(?:","short)')
primaryContactPattern = re.compile('(?:"primaryContact":)(.+?)(?:,"isBranch")')

# loop through the urls
for orgPageUrl in orgPageUrls:
    print("orgPageUrl: " + orgPageUrl)
    #get a beautiful soup object with url response loaded
    html = get_souped(orgPageUrl).text
    #search the html for the org name
    orgNameSearch = orgNamePattern.search(html)
    if orgNameSearch is None:
        print("ERROR: name not found at " + orgPageUrl)
        break
    else:
        orgName = orgNameSearch.group(1)
    #search the html for the primary contact json object
    primaryContactSearch = primaryContactPattern.search(html)
    if primaryContactSearch is None:
        print("ERROR: primaryContactInfo not found at " + orgPageUrl)
        break
    else:
        # load it as a python dict (nulls get turned into Nones)
        primaryContactDict = json.loads(primaryContactSearch.group(1))

    #if there is no primaryContact json object then skip this org
    if primaryContactDict is None:
        continue

    # construct dict to write to csv file
    finalDict = {
        "org_name": orgName,
        "first_name": primaryContactDict["firstName"],
        "preferred_first_name": primaryContactDict["preferredFirstName"],
        "last_name": primaryContactDict["lastName"],
        "email": primaryContactDict["primaryEmailAddress"]
    }
    writer.writerow(finalDict)
    print(finalDict)

# close system resources
csvFile.close()
driver.close()
