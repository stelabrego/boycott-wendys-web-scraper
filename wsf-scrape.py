from selenium import webdriver
import time
import re
import csv

driver = webdriver.Firefox()
driver.implicitly_wait(5) # seconds
driver.get("https://maizepages.umich.edu/organizations?categories=3648")

buttonDiv = driver.find_element_by_css_selector("#org-search-results + div")
loadMoreButton = buttonDiv.find_element_by_css_selector("button")
print("Button Text: " + loadMoreButton.text)
dropdownButton = driver.find_element_by_css_selector("span.Select-arrow-zone")
# dropdownButton.click()

# 500 is good
for x in range(0, 500):
    try:
        loadMoreButton.click()
        time.sleep(.1)
    except:
        break
time.sleep(10)

print("Search Result Line Count:")
orgSearchResults = driver.find_element_by_id("org-search-results")
print(orgSearchResults.text.count("\n"))

links = orgSearchResults.find_elements_by_css_selector("a")
info = []
for link in links:
    textArray = str.splitlines(link.text)
    name = textArray[0]
    url = link.get_attribute("href")
    driver2 = webdriver.Firefox()
    driver2.get(url)
    goodText = driver2.find_element_by_css_selector("html").text
    match = re.search(r'[\w\.-]+@[\w\.-]+', goodText)
    email = match.group(0)
    info.append({"org_name": name, "email": email})
    driver2.close()

with open('umich-org-emails.csv', 'w', newline='') as csvfile:
    fieldnames = ['org_name', 'email']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(info)

