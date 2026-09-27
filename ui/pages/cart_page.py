from selenium.webdriver.common.by import By

from .base_page import BasePage


class CartPage(BasePage):
    NOMBRES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT = (By.ID, "checkout")

    def productos(self):
        self.visible(self.NOMBRES)
        return [e.text for e in self.driver.find_elements(*self.NOMBRES)]

    def iniciar_checkout(self):
        self.clic(self.CHECKOUT)
