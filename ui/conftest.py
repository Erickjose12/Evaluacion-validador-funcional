import os
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.support.events import AbstractEventListener, EventFiringWebDriver

SAUCE_URL = "https://ondemand.us-west-1.saucelabs.com:443/wd/hub"
REPORTES = Path(__file__).parent / "reports"


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Ver el navegador (por defecto headless)")
    parser.addoption("--remote", action="store_true", help="Ejecutar en Sauce Labs")
    parser.addoption("--lento", type=float, default=0, metavar="SEGUNDOS",
                     help="Modo demostracion: pausa entre acciones y resalta cada elemento. "
                          "Solo para presentar; las pruebas normales no tienen pausas.")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    setattr(item, "rep_" + rep.when, rep)


class ModoDemostracion(AbstractEventListener):
    """Resalta en rojo el elemento antes de usarlo y hace una pausa despues de cada accion.

    Se engancha al driver desde afuera, asi que los Page Objects y las pruebas no cambian.
    """

    RESALTE = "arguments[0].style.outline='3px solid #e5383b'; arguments[0].style.outlineOffset='2px';"

    def __init__(self, segundos):
        self.segundos = segundos

    def _resaltar(self, elemento, driver):
        try:
            driver.execute_script(self.RESALTE, elemento)
            time.sleep(self.segundos / 2)
        except Exception:
            pass  # el resalte es solo visual; nunca debe hacer fallar la prueba

    def before_click(self, element, driver):
        self._resaltar(element, driver)

    def before_change_value_of(self, element, driver):
        self._resaltar(element, driver)

    def after_click(self, element, driver):
        time.sleep(self.segundos)

    def after_change_value_of(self, element, driver):
        time.sleep(self.segundos)

    def after_navigate_to(self, url, driver):
        time.sleep(self.segundos)


def _opciones(headed):
    opts = webdriver.ChromeOptions()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,900")
    # Evita el aviso de "contrasena filtrada" de Chrome, que tapa la pantalla
    opts.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    return opts


@pytest.fixture
def driver(request):
    remoto = request.config.getoption("--remote")
    lento = request.config.getoption("--lento")
    opts = _opciones(request.config.getoption("--headed"))

    if remoto:
        opts.browser_version = "latest"
        opts.platform_name = "Windows 11"
        opts.set_capability("sauce:options", {
            "username": os.environ["SAUCE_USERNAME"],
            "accessKey": os.environ["SAUCE_ACCESS_KEY"],
            "name": request.node.name,
            "build": os.getenv("BUILD_NAME", "local"),
        })
        drv = webdriver.Remote(command_executor=SAUCE_URL, options=opts)
    else:
        drv = webdriver.Chrome(options=opts)

    if lento > 0:
        drv = EventFiringWebDriver(drv, ModoDemostracion(lento))

    yield drv

    try:
        rep = getattr(request.node, "rep_call", None)
        fallo = rep is None or rep.failed
        if fallo:
            REPORTES.mkdir(exist_ok=True)
            drv.save_screenshot(str(REPORTES / f"{request.node.name}.png"))
        if remoto:
            drv.execute_script(f"sauce:job-result={'failed' if fallo else 'passed'}")
        if lento > 0:
            time.sleep(lento * 2)  # deja ver la pantalla final antes de cerrar
    finally:
        drv.quit()
