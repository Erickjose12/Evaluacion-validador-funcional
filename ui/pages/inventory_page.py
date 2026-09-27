from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class InventoryPage(BasePage):
    TITULO = (By.CLASS_NAME, "title")
    CONTADOR = (By.CLASS_NAME, "shopping_cart_badge")
    CARRITO = (By.CLASS_NAME, "shopping_cart_link")

    def esta_cargada(self):
        self.wait.until(EC.url_contains("inventory.html"))
        return self.texto(self.TITULO) == "Products"

    def agregar(self, producto_id):
        """producto_id: sufijo del boton, ej. 'sauce-labs-backpack'."""
        self.clic((By.ID, f"add-to-cart-{producto_id}"))
        self.visible((By.ID, f"remove-{producto_id}"))

    def contador(self):
        return self.texto(self.CONTADOR)

    def ir_al_carrito(self):
        self.clic(self.CARRITO)
        self.wait.until(EC.url_contains("cart.html"))
