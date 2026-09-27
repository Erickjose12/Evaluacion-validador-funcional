from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.saucedemo.com/"
TIMEOUT = 10


class BasePage:
    """Acciones comunes. Todas usan esperas explicitas; no hay pausas fijas."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def clic(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def escribir(self, locator, texto):
        campo = self.visible(locator)
        campo.clear()
        campo.send_keys(texto)

    def texto(self, locator):
        return self.visible(locator).text
