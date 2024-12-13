from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import base64
import pytest
from pathlib import Path

TEST_IMAGE_PATH = str(Path(__file__).parent / "food_pic.jpeg")

class TestBrowserInteractions:
    @pytest.fixture(scope="class")
    def browser(self):
        driver = webdriver.Chrome()
        driver.get("http://34.136.111.103.sslip.io/")  # the public deployed url
        yield driver
        driver.quit()

    def test_full_workflow_with_browser(self, browser):
        # Step 1: Upload an image
        # Locate the hidden input element for file upload
        upload_input = browser.find_element(By.XPATH, '//input[@type="file" and contains(@class, "hidden")]')

        # Locate the clickable upload area
        upload_button = browser.find_element(By.XPATH, '//div[contains(@class, "cursor-pointer") and contains(@class, "border-dashed")]')

        # Open the file
        with open(TEST_IMAGE_PATH, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Simulate file upload by interacting with the hidden input
        upload_input.send_keys(TEST_IMAGE_PATH)

        # check if the image preview is displayed
        image_preview = browser.find_element(By.XPATH, '//img[contains(@class, "object-contain")]')
        assert image_preview.is_displayed(), "Image preview is not displayed"

        # Wait for the table
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "w-full")]'))
        )
        table = browser.find_element(By.XPATH, '//table[contains(@class, "w-full")]')

        # Ensure the table is displayed
        assert table.is_displayed(), "Table is not displayed after image upload"

        # Validate the table rows in the table body
        rows = table.find_elements(By.XPATH, './/tbody/tr')
        assert len(rows) > 0, "No rows found in the table"

        # Locate the buttons
        llm_button = browser.find_element(By.XPATH, '//button[contains(@class, "button-primary") and text()="AI Assistant (LLM)"]')

        for i in range(10):
            # Scroll by 500 pixels at a time
            browser.execute_script("window.scrollBy(0, 500);")
        # Click the desired button
        actions = ActionChains(browser)
        actions.move_to_element(llm_button).click().perform()       



        # Step 2: Start a chat using detected items
        WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "chat-message chat-message-user")]'))
        )
        detected_items_message = browser.find_element(By.XPATH, '//div[contains(@class, "prose prose-invert max-w-none")]/p')
        detected_items_text = detected_items_message.text  # Get the text content
        print(f"Detected Items: {detected_items_text}")

        # Validate the detected items
        assert detected_items_text, "Detected items are not displayed as expected"

        # Wait for the chat response
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "chat-message chat-message-assistant")]'))
        )
        assistant_message = browser.find_element(By.XPATH, '//div[contains(@class, "chat-message chat-message-assistant")]/div[contains(@class, "rounded-2xl") and contains(@class, "p-4") and contains(@class, "shadow-sm")]')
        response_text = assistant_message.text
        print(f"Chatbot Response:\n{response_text}")

        # Validate the chatbot response
        assert "Title:" in response_text, "Expected recipe title not found in chatbot response"


        # Step 3: Search on Youtube
        buttons = browser.find_elements(By.XPATH, '//button[contains(@class, "MuiButtonBase-root") and contains(@class, "MuiIconButton-root")]')
        buttons[0].click()

        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "w-full")]'))
        )

        table = browser.find_element(By.XPATH, '//table[contains(@class, "w-full")]')
        rows = table.find_elements(By.XPATH, './/tbody/tr')
        assert len(rows) > 0, "No rows found in the table."
