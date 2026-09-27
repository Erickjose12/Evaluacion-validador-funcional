import pytest

from pages import CartPage, CheckoutPage, InventoryPage, LoginPage


@pytest.mark.smoke
def test_login_agregar_checkout_confirmacion(driver):
    LoginPage(driver).abrir().ingresar("standard_user", "secret_sauce")

    inventario = InventoryPage(driver)
    assert inventario.esta_cargada()
    inventario.agregar("sauce-labs-backpack")
    assert inventario.contador() == "1"

    inventario.ir_al_carrito()
    carrito = CartPage(driver)
    assert carrito.productos() == ["Sauce Labs Backpack"]
    carrito.iniciar_checkout()

    checkout = CheckoutPage(driver)
    checkout.llenar_datos("Ana", "Lopez", "01001")
    assert checkout.total() == "Total: $32.39"   # 29.99 + 8% de impuesto

    assert checkout.finalizar() == "Thank you for your order!"
