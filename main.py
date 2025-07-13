import data
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import DesiredCapabilities


# No modificar
def retrieve_phone_code(driver) -> str:
    """Este código devuelve un número de confirmación de teléfono y lo devuelve como un string.
    Utilízalo cuando la aplicación espere el código de confirmación para pasarlo a tus pruebas.
    El código de confirmación del teléfono solo se puede obtener después de haberlo solicitado en la aplicación."""
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
            raise Exception("No se encontró el código de confirmación del teléfono.\n"
                            "Utiliza 'retrieve_phone_code' solo después de haber solicitado el código en tu aplicación.")
        return code


class UrbanRoutesPage:
    # Localizadores de los campos
    from_field = (By.ID, 'from')
    to_field = (By.ID, 'to')
    comfort_fare_button = (By.ID, 'comfort-fare')  # **Se agregó el localizador para la tarifa Comfort**
    phone_field = (By.ID, 'phone')  # **Se agregó el localizador para el campo de teléfono**
    card_input_field = (By.ID, 'code')  # **Se agregó el localizador para el campo CVV de tarjeta**
    link_button = (By.ID, 'link')  # **Se agregó el localizador para el botón "Link"**
    message_field = (By.ID, 'controller-message')  # **Se agregó el localizador para el campo de mensaje al controlador**
    blanket_checkbox = (By.ID, 'blanket')  # **Se agregó el localizador para la manta**
    tissues_checkbox = (By.ID, 'tissues')  # **Se agregó el localizador para los pañuelos**
    ice_cream_button = (By.ID, 'ice-cream')  # **Se agregó el localizador para el botón de helado**
    taxi_search_modal = (By.ID, 'taxi-search-modal')  # **Se agregó el localizador para el modal de búsqueda de taxi**
    driver_info_modal = (By.ID, 'driver-info-modal')  # **Se agregó el localizador para el modal de información del conductor**

    def __init__(self, driver):
        self.driver = driver

    def set_from(self, from_address):
        self.driver.find_element(*self.from_field).send_keys(from_address)

    def set_to(self, to_address):
        self.driver.find_element(*self.to_field).send_keys(to_address)

    def get_from(self):
        return self.driver.find_element(*self.from_field).get_property('value')

    def get_to(self):
        return self.driver.find_element(*self.to_field).get_property('value')

    # **Paso 2: Método para seleccionar la tarifa Comfort**
    def select_comfort_fare(self):
        comfort_button = self.driver.find_element(*self.comfort_fare_button)
        comfort_button.click()

    # **Paso 3: Método para rellenar el número de teléfono**
    def set_phone_number(self, phone_number):
        self.driver.find_element(*self.phone_field).send_keys(phone_number)

    # **Paso 4: Método para agregar tarjeta de crédito**
    def add_credit_card(self, card_number, expiration_date, cvv):
        self.driver.find_element(By.ID, 'card-number').send_keys(card_number)
        self.driver.find_element(By.ID, 'expiration-date').send_keys(expiration_date)
        self.driver.find_element(*self.card_input_field).send_keys(cvv)

        # Simular el clic para cambiar de foco (enfoque fuera del campo CVV)
        self.driver.find_element(By.TAG_NAME, 'body').click()

        # **Esperar a que el botón 'Link' se active antes de hacer clic**
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable(self.driver.find_element(*self.link_button))
        )
        self.driver.find_element(*self.link_button).click()

    # **Paso 5: Método para escribir mensaje al controlador**
    def write_controller_message(self, message):
        self.driver.find_element(*self.message_field).send_keys(message)

    # **Paso 6: Método para pedir manta y pañuelos**
    def request_blanket_and_tissues(self):
        self.driver.find_element(*self.blanket_checkbox).click()
        self.driver.find_element(*self.tissues_checkbox).click()

    # **Paso 7: Método para pedir helados**
    def request_ice_creams(self, quantity):
        for _ in range(quantity):
            self.driver.find_element(*self.ice_cream_button).click()

    # **Paso 8: Método para esperar el modal de búsqueda de taxi**
    def wait_for_taxi_modal(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.taxi_search_modal)
        )

    # **Paso 9: Método para esperar la información del conductor**
    def wait_for_driver_info(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located(self.driver_info_modal)
        )


class TestUrbanRoutes:

    driver = None

    @classmethod
    def setup_class(cls):
        # Configurar el navegador con logging habilitado
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {'performance': 'ALL'}
        cls.driver = webdriver.Chrome(desired_capabilities=capabilities)

    def test_request_taxi(self):
        self.driver.get(data.urban_routes_url)
        routes_page = UrbanRoutesPage(self.driver)

        # Paso 1: Configurar dirección
        address_from = data.address_from
        address_to = data.address_to
        routes_page.set_from(address_from)
        routes_page.set_to(address_to)
        assert routes_page.get_from() == address_from
        assert routes_page.get_to() == address_to

        # **Paso 2: Seleccionar tarifa Comfort**
        routes_page.select_comfort_fare()

        # **Paso 3: Rellenar número de teléfono**
        phone_number = "123456789"
        routes_page.set_phone_number(phone_number)

        # **Paso 4: Agregar tarjeta de crédito**
        routes_page.add_credit_card("4111111111111111", "12/25", "123")

        # **Paso 5: Escribir mensaje para el controlador**
        controller_message = "Llevarme rápido"
        routes_page.write_controller_message(controller_message)

        # **Paso 6: Pedir manta y pañuelos**
        routes_page.request_blanket_and_tissues()

        # **Paso 7: Pedir 2 helados**
        routes_page.request_ice_creams(2)

        # **Paso 8: Esperar modal de búsqueda de taxi**
        routes_page.wait_for_taxi_modal()

        # **Paso 9: Esperar la información del conductor**
        routes_page.wait_for_driver_info()

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()

