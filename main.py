import os, sys, subprocess
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# run with window disabled
options = Options()
options.add_argument("--headless")

# loading the .env file
load_dotenv()
email = os.getenv('MAIL')
password = os.getenv('PASSWORD')
if not email or not password:
    raise ValueError("Missing MAIL or PASSWORD in .env file")

# opening the window on the website
driver = webdriver.Firefox(options=options)
driver.get('https://eduvulcan.pl/logowanie')

# closing the popup
iframe = WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.ID, 'respect-privacy-frame'))
)
driver.switch_to.frame(iframe)

WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Zgadzam')]"))
).click()

driver.switch_to.default_content()

# entering email and password into the form on the website
def both_elements_ready(driver):
    try:
        inputs = ['Alias', 'Password']
        input_visible = any(
            elems and elems[0].is_displayed()
            for i in inputs
            for elems in [driver.find_elements(By.ID, i)]
        )
        button = driver.find_element(By.ID, 'btNext')

        return input_visible and button.is_displayed()
    

    except:
        return False

try:
    if both_elements_ready(driver):
        driver.find_element(By.ID, 'Alias').send_keys(email)
        driver.find_element(By.ID, 'btNext').click()

        driver.find_element(By.ID, 'Password').send_keys(password)
        driver.find_element(By.ID, 'btLogOn').click()
except:
    raise Exception("Could not find elements on the login page,")

driver.get('https://wiadomosci.eduvulcan.pl/warszawamokotow/App/odebrane')

# finding all message subjects on the page
found_subjects = WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.column--temat'))
)
message_dates = WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.formatted-date'))
)
subjects_list = list(zip(found_subjects, message_dates))
for n, (found_subject, message_date) in enumerate(zip(found_subjects, message_dates), 1):
    print(f"{n:2}: {found_subject.text.ljust(70)} | {message_date.text}")

# saving messages to a file for easier reading
with open("message_list.txt", "w", encoding="utf-8") as file:
    for n, (found_subject, message_date) in enumerate(subjects_list, 1):
        file.write(f"{n:2}: {found_subject.text.ljust(70)} | {message_date.text} \n")

# ask for the message number(s) (can be one or many), then open them
while True:
    user_input = input("Enter message numbers separated by space [-1 to exit]: ")
    choices = [int(x) for x in user_input.split()]
    if -1 in choices:
        sys.exit("Program exited.")
    if all(1 <= c <= len(subjects_list) for c in choices):
        break
    print("Invalid number, try again.")

for choice in choices:
    selected_subject, selected_date = subjects_list[choice - 1]
    desired_message = found_subjects[choice - 1]

    subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
    print(f"\n ---Selected message subject: {desired_message.text}---")
    # Wait until the backdrop disappears, if it exists
    try:
        WebDriverWait(driver, 5).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.MuiBackdrop-root'))
        )
    except:
        pass  # If there is no backdrop, continue
    desired_message.click()
    message_content = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.info-column.info-text div'))
    )
    # print the formatted message content
    print("-"*20 + "\n")
    print(message_content.text)
    print("\n" + "-"*20 + "\n")
    i = input('Press enter to see the next message: ')

    if len(choices) > 1:
        # Close the modal if it is visible
        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.MuiButtonBase-root.MuiIconButton-root.button--icon.button--close.modal-button--close'))
            )
            close_button.click()
            # Wait until the modal/footer disappears
            WebDriverWait(driver, 5).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'footer.modal__footer'))
            )
        except:
            pass  # If there is no modal, continue
    else:
        break