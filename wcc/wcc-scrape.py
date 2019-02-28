from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import csv
import time

# delete csv file if it exists
filename = "wcc-student-orgs.csv"
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
# firefox_profile.set_preference('permissions.default.image', 2)
# firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

# set up selenium driver
driver = webdriver.Firefox(firefox_profile=firefox_profile)
driver.implicitly_wait(1) # seconds
driver.get("https://wccnet.edu")
wait = WebDriverWait(driver, 1)


wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.mywcc")))
myWCC = driver.find_element_by_css_selector("li.mywcc")
myWCC.click()

# wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='username']")))
username = driver.find_element_by_css_selector("#username")
username.send_keys("")
password = driver.find_element_by_css_selector("#password")
password.send_keys("")
submit = driver.find_element_by_css_selector("#CASsubmit")
submit.click()
driver.get("http://campusconnect.wccnet.edu")
driver.get("https://orgsync.com/browse_orgs/776")
print(driver.find_element_by_css_selector("html").get_attribute("outerHTML"))
orgUrls = []
for i in range(0,10):
    visibleOrgLinkTags = driver.find_elements_by_css_selector(".osw-portals-list-item a")
    for visibleOrgLinkTag in visibleOrgLinkTags:
        orgUrl = visibleOrgLinkTag.get_attribute("href")
        if orgUrl not in orgUrls:
            orgUrls.append(orgUrl)
    driver.execute_script("window.scrollBy(0,300)")
    time.sleep(1)
print(len(orgUrls))
for orgUrl in orgUrls:
    print("handling url: " + orgUrl)
    driver.get(orgUrl)
    profileButton = driver.find_element_by_css_selector("a[data-tab='profile']")
    profileButton.click()
    orgName = driver.find_element_by_css_selector("h1").text

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-profile a")))
        email = driver.find_element_by_css_selector(".form-profile a").text
    except Exception as e:
        email = None

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".form-profile")))
        formProfileDiv = driver.find_element_by_css_selector(".form-profile")
        nameDiv = formProfileDiv.find_element_by_css_selector("div.row.form_element.question.response:nth-child(3)")
        fullName = nameDiv.find_element_by_css_selector("p").text
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

# print(driver.find_element_by_css_selector("html").text)
# driver.close()
