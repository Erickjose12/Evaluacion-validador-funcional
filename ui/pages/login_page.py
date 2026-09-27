from selenium.webdriver.common.by import By

from .base_page import BASE_URL, BasePage


class LoginPage(BasePage):
    USUARIO = (By.ID, "user-name")
    CLAVE = (By.ID, "password")
    BOTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def abrir(self):
        self.driver.get(BASE_URL)
        self.visible(self.USUARIO)
        return self

    def ingresar(self, usuario, clave):
        if usuario:
            self.escribir(self.USUARIO, usuario)
        if clave:
            self.escribir(self.CLAVE, clave)
        self.clic(self.BOTON)

    def mensaje_error(self):
        return self.texto(self.ERROR)
