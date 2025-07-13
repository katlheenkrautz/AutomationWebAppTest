import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import DesiredCapabilities

# Do not modify this function
def retrieve_phone_code(driver) -> str:
    """
    Retrieves the phone verification code from browser logs.
    Use this only after the code has been requested within the application.
    Returns the code as a string.
    """
    import json
    import time
    from selenium.common import WebDriverException
    code = None
    for i in range(10):
        try:
            logs = [log["message"] for log in driver.get_log('performance') if log.get("message")
                    and 'api/v1/number?number' in log.get("message")]
            for log in reversed(logs):
                message_data = json.loads(log)["message"]
                body = driver.execute_cdp_cmd('Network.getResponseBody',
                                              {'requestId': message_data["params"]["requestId"]})
                code = ''.join([x for x in body['body'] if x.isdigit()])
        except WebDriverException:
            time.sleep(1)
            continue
        if not code:
            raise Exception("Phone verification code not found.\n"
                            "Use 'retrieve_phone_code' only after the code has been requested in your application.")
        return code

# Page Object Model for the Urban Routes web app
class UrbanRoutesPage:
    # Element locators
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    comfort_fare_button = (By.ID, 'comfort-fare')  # Comfort fare button
    phone_field = (By.ID, 'phone')  # Phone number input field
    card_input_field = (By.ID, 'code')  # CVV input field
    link_button = (By.ID, 'link')  # Link card button
    message_field = (By.ID, 'controller-message')  # Driver message input
    blanket_checkbox = (By.ID, 'blanket')  # Blanket checkbox
    tissues_checkbox = (By.ID, 'tissues')  # Tissues checkbox
    ice_cream_button = (By.ID, 'ice-cream')  # Ice cream request button
    taxi_search_modal = (By.ID, 'taxi-search-modal')  # Taxi search modal
    driver_info_modal = (By.ID, 'driver-info-modal')  # Driver info modal

    def __init__(self, driver):
        self.driver = driver

    # Set origin address
    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    # Set destination address
    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    # Get origin address from input
    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    # Get destination address from input
    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    # Step 2: Select the Comfort fare
    def select_comfort_fare(self):
        comfort_button = self.driver.find_element(*self.comfort_fare_button)
        comfort_button.click()

    # Step 3: Enter phone number
    def set_phone_number(self, phone_number):
        self.driver.find_element(*self.phone_field).send_keys(phone_number)

    # Step 4: Add credit card details
    def add_credit_card(self, card_number, expiration_date, cvv):
        self.driver.find_element(By.ID, 'card-number').send_keys(card_number)
        self.driver.find_element(By.ID, 'expiration-date').send_keys(expiration_date)
        self.driver.find_element(*self.card_input_field).send_keys(cvv)

        # Click outside to trigger validation
        self.driver.find_element(By.TAG_NAME, 'body').click()

        # Wait until the 'Link' button becomes clickable and click it
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.driver.find_element(*self.link_button))
        )
        self.driver.find_element(*self.link_button).click()

    # Step 5: Write a message to the driver
    def write_controller_message(self, message):
        self.driver.find_element(*self.message_field).send_keys(message)

    # Step 6: Request blanket and tissues
    def request_blanket_and_tissues(self):
        self.driver.find_element(*self.blanket_checkbox).click()
        self.driver.find_element(*self.tissues_checkbox).click()

    # Step 7: Request a number of ice creams
    def request_ice_creams(self, quantity):
        for _ in range(quantity):
            self.driver.find_element(*self.ice_cream_button).click()

    # Step 8: Wait for the taxi search modal to appear
    def wait_for_taxi_modal(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.taxi_search_modal)
        )

    # Step 9: Wait for the driver info modal to appear
    def wait_for_driver_info(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.driver_info_modal)
        )


# Test class using Pytest or unittest-style setup/teardown
class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        """
        Sets up the browser with performance logging enabled before running the tests.
        """
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}
        cls.driver = webdriver.Chrome(desired_capabilities=capabilities)

    def test_request_taxi(self):
        """
        Full end-to-end test: fill in trip details, choose fare, enter payment and extras, and wait for driver modal.
        """
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

        # Step 1: Set trip origin and destination
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

        # Step 2: Select Comfort fare
        routes_page.select_comfort_fare()

        # Step 3: Enter phone number
        phone_number = "123456789"
        routes_page.set_phone_number(phone_number)

        # Step 4: Add credit card
        routes_page.add_credit_card("4111111111111111", "12/25", "123")

        # Step 5: Write message to the driver
        controller_message = "Llevarme rápido"
        routes_page.write_controller_message(controller_message)

        # Step 6: Request blanket and tissues
        routes_page.request_blanket_and_tissues()

        # Step 7: Request 2 ice creams
        routes_page.request_ice_creams(2)

        # Step 8: Wait for the taxi search modal to appear
        routes_page.wait_for_taxi_modal()

        # Step 9: Wait for the driver info modal to appear
        routes_page.wait_for_driver_info()

    @classmethod
    def teardown_class(cls):
        """
        Closes the browser after all tests have completed.
        """
        cls.driver.quit()
