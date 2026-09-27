import os
from pathlib import Path

import pytest
from selenium import webdriver

SAUCE_URL = "https://ondemand.us-west-1.saucelabs.com:443/wd/hub"
REPORTES = Path(__file__).parent / "reports"


def pytest_addoption(parser):
    parser.addoption("--headed", action="store_true", help="Ver el navegador (por defecto headless)")
    parser.addoption("--remote", action="store_true", help="Ejecutar en Sauce Labs")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    setattr(item, "rep_" + rep.when, rep)


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

    yield drv

    try:
        rep = getattr(request.node, "rep_call", None)
        fallo = rep is None or rep.failed
        if fallo:
            REPORTES.mkdir(exist_ok=True)
            drv.save_screenshot(str(REPORTES / f"{request.node.name}.png"))
        if remoto:
            drv.execute_script(f"sauce:job-result={'failed' if fallo else 'passed'}")
    finally:
        drv.quit()
