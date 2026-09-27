from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class CheckoutPage(BasePage):
    NOMBRE = (By.ID, "first-name")
    APELLIDO = (By.ID, "last-name")
    POSTAL = (By.ID, "postal-code")
    CONTINUAR = (By.ID, "continue")
    TOTAL = (By.CLASS_NAME, "summary_total_label")
    FINALIZAR = (By.ID, "finish")
    CONFIRMACION = (By.CLASS_NAME, "complete-header")

    def llenar_datos(self, nombre, apellido, postal):
        self.escribir(self.NOMBRE, nombre)
        self.escribir(self.APELLIDO, apellido)
        self.escribir(self.POSTAL, postal)
        self.clic(self.CONTINUAR)
        self.wait.until(EC.url_contains("checkout-step-two"))

    def total(self):
        return self.texto(self.TOTAL)

    def finalizar(self):
        self.clic(self.FINALIZAR)
        return self.texto(self.CONFIRMACION)
