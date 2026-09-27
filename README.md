# Evaluación Validador Funcional: automatización

Pruebas automatizadas de la Parte B2 de la evaluación técnica de e-Solutions.

| Carpeta | Qué prueba | Herramientas |
|---|---|---|
| `ui/` | saucedemo.com: login inválido con validación del mensaje, y flujo login → agregar producto → checkout → confirmación | Python, Selenium 4, pytest, Page Object Model |
| `api/` | restful-booker.herokuapp.com: token único, crear, consultar y eliminar una reserva, más casos negativos | Node.js, Jest, fetch nativo |
| `azure-pipelines.yml` | Ejecuta ambas suites, publica los resultados JUnit y detiene el despliegue si falla cualquier prueba | Azure DevOps |

## Requisitos

- Python 3.10 o superior
- Node.js 18 o superior (usa `fetch` nativo)
- Google Chrome (Selenium Manager descarga el driver automáticamente)

## Pruebas de interfaz (`ui/`)

```bash
cd ui
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt     # Windows
.venv\Scripts\python.exe -m pytest                               # headless
.venv\Scripts\python.exe -m pytest --headed                      # ver el navegador
.venv\Scripts\python.exe -m pytest --junitxml=reports/junit-ui.xml
```

En macOS/Linux usa `.venv/bin/python` en lugar de `.venv\Scripts\python.exe`.

**Opcional, en Sauce Labs:** define `SAUCE_USERNAME` y `SAUCE_ACCESS_KEY` como variables de entorno y ejecuta `pytest --remote`.

### Diseño

- **Page Object Model** (`ui/pages/`): una clase por pantalla (`LoginPage`, `InventoryPage`, `CartPage`, `CheckoutPage`). Las pruebas no contienen localizadores.
- **Esperas explícitas**: `BasePage` centraliza `WebDriverWait` + `expected_conditions`. No hay `sleep` ni esperas implícitas.
- **Login inválido parametrizado**: contraseña incorrecta, usuario vacío, contraseña vacía y usuario bloqueado; se valida el texto exacto del mensaje.
- Si una prueba falla, se guarda una captura en `ui/reports/`.

## Pruebas de API (`api/`)

```bash
cd api
npm install
npm test
```

El reporte JUnit queda en `api/reports/junit-api.xml`.

| Prueba | Validación |
|---|---|
| `beforeAll`: POST /auth | Se obtiene el token **una sola vez** para toda la suite |
| POST /booking | 200, `bookingid` entero, el cuerpo devuelto es igual al enviado |
| GET /booking/:id | 200 y el cuerpo es igual a la reserva creada |
| DELETE /booking/:id (con token) | 201 `Created` |
| GET de la reserva eliminada | 404 `Not Found` |
| **Negativo:** DELETE sin token | 403 `Forbidden` |
| **Negativo:** GET de un id inexistente | 404 `Not Found` |
| **Negativo:** POST /auth con clave incorrecta | No entrega token; `{"reason":"Bad credentials"}` |

### Observaciones sobre la API

- `POST /auth` con credenciales inválidas responde **200** en lugar de 401.
- `DELETE /booking/:id` responde **201 Created** en lugar de 200/204.
- `POST /booking` con cuerpo incompleto responde **500** en lugar de 400.

Las pruebas validan el comportamiento actual del servicio y dejan documentadas estas diferencias frente al estándar HTTP.

## Pipeline

`azure-pipelines.yml` tiene dos etapas:

1. **Pruebas:** los jobs `API` y `UI` corren en paralelo. Cada uno publica su reporte JUnit con `PublishTestResults@2` (`condition: succeededOrFailed()` para publicarlo aunque haya fallos, y `failTaskOnFailedTests: true`).
2. **Desplegar:** depende de `Pruebas` con `condition: succeeded()`, así que **no se ejecuta si falla cualquier prueba**.
