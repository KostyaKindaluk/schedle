import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EMAIL = "user@gmail.com"
PASSWORD = "password"


driver = webdriver.Firefox()
driver.maximize_window()

try:
	driver.get("http://localhost:5173/login")

	wait = WebDriverWait(driver, 10)
	email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
	password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
	login_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))

	time.sleep(0.5)

	register_text = driver.find_element(By.XPATH, "//p[contains(text(), 'have an account yet?')]")
	assert "have an account yet?" in register_text.text

	email_input.send_keys(EMAIL)
	password_input.send_keys(PASSWORD)
	login_button.click()

	wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(),'My Schedulings')]")))
	time.sleep(0.5)

	new_sched_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Start new scheduling')]")
	assert new_sched_button.is_displayed()

	print("Test passed")
finally:
	driver.quit()