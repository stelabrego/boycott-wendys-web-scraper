from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import csv
from selenium.common.exceptions import TimeoutException

# delete csv file if it exists
filename = "emich-student-orgs.csv"
fileObj = Path(filename)
if fileObj.exists():
    fileObj.unlink()
    fileObj.touch()
csvFile = open(filename, 'w', newline='')

# prepare csv writer
writer = csv.DictWriter(csvFile, ["org_name", "first_name", "last_name", "email"])
writer.writeheader()

# disable images for optimization
firefox_profile = webdriver.FirefoxProfile()
firefox_profile.set_preference('permissions.default.image', 2)
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

# set up selenium driver
driver = webdriver.Firefox(firefox_profile=firefox_profile)
driver.implicitly_wait(5) # seconds
driver.get("https://www.emich.edu/campuslife/student-orgs/getinvolved.php")

navTable = driver.find_element_by_css_selector("table.osw-portals-letter-table")
navButtons = navTable.find_elements_by_css_selector("button")
navButtons = navButtons[1:]

orgUrls = []

for button in navButtons:
    print(button.text)
    button.click()
    linkContainers = driver.find_elements_by_css_selector("div.osw-portals-list-item")
    for linkContainer in linkContainers:
        linkTag = linkContainer.find_element_by_css_selector("a")
        orgUrls.append(linkTag.get_attribute("href"))

wait = WebDriverWait(driver, 5)

for orgUrl in orgUrls:
    print("processing: " + orgUrl)
    driver.get(orgUrl)
    profileLinkTag = driver.find_element_by_css_selector("a[data-tab='profile']")
    profileLinkTag.click()
    # pause execution for a second so the js can execute on the browser
    orgName = driver.find_element_by_css_selector("h1").text

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-profile a")))
        email = driver.find_element_by_css_selector(".form-profile a").text
    except Exception as e:
        email = None

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.position-name span")))
        fullName = driver.find_element_by_css_selector("div.position-name span").text
        fullNameArray = fullName.split(" ")
        firstName = fullNameArray[0]
        lastName = fullNameArray[-1]
    except:
        firstName = None
        lastName = None
    finalDict = {
        "org_name": orgName,
        "first_name": firstName,
        "last_name": lastName,
        "email": email
    }
    writer.writerow(finalDict)
    print(str(finalDict))


driver.close()