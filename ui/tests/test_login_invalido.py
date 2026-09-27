import pytest

from pages import LoginPage

CASOS = [
    pytest.param("standard_user", "clave_incorrecta",
                 "Epic sadface: Username and password do not match any user in this service",
                 id="clave-incorrecta"),
    pytest.param("", "secret_sauce", "Epic sadface: Username is required", id="usuario-vacio"),
    pytest.param("standard_user", "", "Epic sadface: Password is required", id="clave-vacia"),
    pytest.param("locked_out_user", "secret_sauce",
                 "Epic sadface: Sorry, this user has been locked out.", id="usuario-bloqueado"),
]


@pytest.mark.smoke
@pytest.mark.parametrize("usuario, clave, mensaje", CASOS)
def test_login_invalido_muestra_mensaje(driver, usuario, clave, mensaje):
    login = LoginPage(driver).abrir()

    login.ingresar(usuario, clave)

    assert login.mensaje_error() == mensaje
    assert "inventory.html" not in driver.current_url
