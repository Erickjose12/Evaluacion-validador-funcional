# Evaluación Validador Funcional: guía de ejecución de la automatización

Pruebas automatizadas de la **Parte B2** de la evaluación técnica de e-Solutions, S.A.

**Autor:** Erick José Estrada Barrios

| Suite | Sitio probado | Qué valida |
|---|---|---|
| **Interfaz** (`ui/`) | https://www.saucedemo.com | Login inválido con validación del mensaje de error (4 variantes) y flujo login → agregar producto → checkout → confirmación |
| **API** (`api/`) | https://restful-booker.herokuapp.com | Token obtenido una sola vez; crear, consultar y eliminar una reserva validando código y cuerpo; 3 casos negativos |
| **Pipeline** (`azure-pipelines.yml`) | Azure DevOps | Ejecuta ambas suites, publica resultados JUnit y bloquea el despliegue si falla cualquier prueba |

---

## 1. Tecnologías utilizadas

| Herramienta | Versión usada | Para qué se usa |
|---|---|---|
| Python | 3.14 (compatible desde 3.10) | Lenguaje de las pruebas de interfaz |
| Selenium WebDriver | 4.49 | Controla el navegador |
| pytest | 9.1 | Ejecuta las pruebas de interfaz y genera el reporte JUnit |
| Google Chrome | 153 | Navegador donde corren las pruebas de interfaz |
| Node.js | 24 (compatible desde 18) | Entorno de las pruebas de API; usa `fetch` nativo |
| Jest | 30.5 | Ejecuta las pruebas de API |
| jest-junit | 16.0 | Genera el reporte JUnit de las pruebas de API |
| Azure Pipelines | — | Integración continua (`azure-pipelines.yml`) |

**Patrones aplicados:** Page Object Model, esperas explícitas (`WebDriverWait`) sin pausas fijas, pruebas parametrizadas, token de autenticación compartido (`beforeAll`) y limpieza de los datos de prueba.

---

## 2. Qué hay que instalar

Solo se necesitan tres programas. Selenium descarga automáticamente el driver de Chrome (Selenium Manager), así que **no hay que instalar ChromeDriver**.

| Programa | Dónde descargarlo | Nota importante |
|---|---|---|
| **Python 3.10 o superior** | https://www.python.org/downloads/ | En Windows, marcar la casilla **"Add python.exe to PATH"** durante la instalación |
| **Node.js 18 o superior** (versión LTS) | https://nodejs.org/ | Incluye `npm` |
| **Google Chrome** | https://www.google.com/chrome/ | Cualquier versión reciente |

Para comprobar que quedaron instalados, abre una terminal nueva y ejecuta:

```bash
python --version
node --version
npm --version
```

Cada comando debe mostrar un número de versión. En macOS/Linux usa `python3` en lugar de `python`.

> ¿Qué terminal usar? En Windows: **Símbolo del sistema** (tecla Windows → escribir `cmd` → Enter). En macOS: **Terminal**.

---

## 3. Obtener el proyecto

**Opción A: desde el .zip.** Descomprime `automatizacion.zip` y entra a la carpeta:

```bash
cd ruta\donde\descomprimiste\automatizacion
```

**Opción B: desde el repositorio Git.**

```bash
git clone <URL-del-repositorio>
cd automatizacion
```

Estructura del proyecto:

```
automatizacion/
├── ui/                          Pruebas de interfaz (Python + Selenium)
│   ├── pages/                   Page Objects: una clase por pantalla
│   │   ├── base_page.py         Esperas explícitas centralizadas
│   │   ├── login_page.py
│   │   ├── inventory_page.py
│   │   ├── cart_page.py
│   │   └── checkout_page.py
│   ├── tests/
│   │   ├── test_login_invalido.py
│   │   └── test_compra.py
│   ├── conftest.py              Configuración del navegador y opciones
│   ├── pytest.ini
│   └── requirements.txt
├── api/                         Pruebas de API (Node + Jest)
│   ├── tests/booking.test.js
│   ├── package.json
│   └── package-lock.json
├── azure-pipelines.yml
└── README.md
```

---

## 4. Pruebas de interfaz (Selenium)

### 4.1 Instalación (solo la primera vez)

**Windows:**

```bash
cd ui
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**

```bash
cd ui
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

`python -m venv .venv` crea un entorno virtual: una carpeta aislada donde se instalan Selenium y pytest sin afectar el resto del equipo.

### 4.2 Ejecución

Desde la carpeta `ui`. En macOS/Linux cambia `.venv\Scripts\python.exe` por `.venv/bin/python`.

| Para qué | Comando |
|---|---|
| **Ejecutar todas las pruebas** (sin ventana, rápido) | `.venv\Scripts\python.exe -m pytest` |
| **Ver el navegador** mientras se ejecutan | `.venv\Scripts\python.exe -m pytest --headed` |
| **Modo demostración**: resalta cada elemento y pausa entre acciones | `.venv\Scripts\python.exe -m pytest --headed --lento 1.5` |
| Solo el flujo de compra | `.venv\Scripts\python.exe -m pytest tests/test_compra.py --headed` |
| Solo los logins inválidos | `.venv\Scripts\python.exe -m pytest tests/test_login_invalido.py` |
| Generar reporte JUnit | `.venv\Scripts\python.exe -m pytest --junitxml=reports/junit-ui.xml` |

`--lento` recibe los segundos de pausa. Solo existe para presentar la prueba a una persona; sin esa opción las pruebas no tienen ninguna pausa fija.

### 4.3 Resultado esperado

```
tests/test_compra.py::test_login_agregar_checkout_confirmacion PASSED
tests/test_login_invalido.py::test_login_invalido_muestra_mensaje[clave-incorrecta] PASSED
tests/test_login_invalido.py::test_login_invalido_muestra_mensaje[usuario-vacio] PASSED
tests/test_login_invalido.py::test_login_invalido_muestra_mensaje[clave-vacia] PASSED
tests/test_login_invalido.py::test_login_invalido_muestra_mensaje[usuario-bloqueado] PASSED
============================== 5 passed ==============================
```

Si alguna prueba falla, se guarda automáticamente una captura de pantalla en `ui/reports/<nombre-de-la-prueba>.png`.

### 4.4 Qué valida cada prueba

| Prueba | Pasos | Validación |
|---|---|---|
| `clave-incorrecta` | Login con `standard_user` y una contraseña errónea | Mensaje exacto: *"Username and password do not match any user in this service"* |
| `usuario-vacio` | Login sin usuario | Mensaje: *"Username is required"* |
| `clave-vacia` | Login sin contraseña | Mensaje: *"Password is required"* |
| `usuario-bloqueado` | Login con `locked_out_user` | Mensaje: *"Sorry, this user has been locked out."* |
| `test_login_agregar_checkout_confirmacion` | Login → agregar "Sauce Labs Backpack" → carrito → checkout con datos → finalizar | Contador = 1, producto correcto en el carrito, total $32.39 y confirmación *"Thank you for your order!"* |

En todos los casos de login inválido se valida además que el usuario **no** llegue al inventario.

---

## 5. Pruebas de API (Jest)

### 5.1 Instalación (solo la primera vez)

```bash
cd api
npm install
```

### 5.2 Ejecución

```bash
npm test
```

El reporte JUnit se genera automáticamente en `api/reports/junit-api.xml`.

### 5.3 Resultado esperado

```
Ciclo de vida de una reserva
  √ POST /booking crea la reserva y devuelve sus datos
  √ GET /booking/:id devuelve la reserva creada
  √ DELETE /booking/:id con token elimina la reserva
  √ GET /booking/:id de una reserva eliminada responde 404
Casos negativos
  √ DELETE sin token responde 403 Forbidden
  √ GET de una reserva inexistente responde 404
  √ POST /auth con credenciales invalidas no entrega token
Tests: 7 passed, 7 total
```

### 5.4 Qué valida cada prueba

| Prueba | Validación |
|---|---|
| `beforeAll`: POST /auth | Se obtiene el token **una sola vez** para toda la suite (200 y token de tipo texto) |
| POST /booking | 200, `bookingid` entero y el cuerpo devuelto es idéntico al enviado |
| GET /booking/:id | 200 y el cuerpo coincide con la reserva creada |
| DELETE /booking/:id con token | 201 `Created` |
| GET de la reserva eliminada | 404 `Not Found` (confirma que se eliminó) |
| **Negativo:** DELETE sin token | 403 `Forbidden`; al final se elimina la reserva creada para no dejar datos |
| **Negativo:** GET de un id inexistente | 404 `Not Found` |
| **Negativo:** POST /auth con contraseña incorrecta | No entrega token; responde `{"reason":"Bad credentials"}` |

### 5.5 Observaciones sobre la API

Durante las pruebas se encontraron estas diferencias frente al estándar HTTP. Las pruebas validan el comportamiento actual y las dejan documentadas:

- `POST /auth` con credenciales inválidas responde **200** en lugar de **401**.
- `DELETE /booking/:id` responde **201 Created** en lugar de **200** o **204**.
- `POST /booking` con el cuerpo incompleto responde **500** en lugar de **400**.

---

## 6. Pipeline de Azure DevOps

`azure-pipelines.yml` define dos etapas:

1. **Pruebas:** los jobs `API` y `UI` corren en paralelo en un agente `ubuntu-latest`, que ya trae Chrome instalado.
   - Cada job publica su reporte con `PublishTestResults@2` en formato **JUnit**.
   - `condition: succeededOrFailed()` publica el reporte aunque haya fallos, para poder revisarlos.
   - `failTaskOnFailedTests: true` marca la ejecución como fallida si hay pruebas fallidas.
   - Si falla la interfaz, las capturas se publican como artefacto (`capturas-ui`).
2. **Desplegar:** depende de `Pruebas` con `condition: succeeded()`. **Si falla cualquier prueba, el despliegue no se ejecuta.**

**Para usarlo:** en Azure DevOps, **Pipelines → New pipeline**, selecciona el repositorio y elige **Existing Azure Pipelines YAML file** → `/azure-pipelines.yml`. Los resultados aparecen en la pestaña **Tests** de cada ejecución.

---

## 7. Opcional: ejecutar en Sauce Labs

Las pruebas de interfaz también pueden correr en la nube de Sauce Labs:

**Paso 1.** Definir las variables de entorno con las credenciales de Sauce Labs (Windows):

```bash
setx SAUCE_USERNAME "tu_usuario"
setx SAUCE_ACCESS_KEY "tu_access_key"
```

**Paso 2.** Abrir una terminal nueva y ejecutar desde `ui`:

```bash
.venv\Scripts\python.exe -m pytest --remote
```

Los resultados, con video de cada prueba, quedan en el panel de Sauce Labs (Automated → Test Results).

---

## 8. Solución de problemas

| Problema | Solución |
|---|---|
| `'python' no se reconoce como un comando` | Reinstalar Python marcando **"Add python.exe to PATH"**, o usar `py` en lugar de `python` |
| `'npm' no se reconoce como un comando` | Cerrar y volver a abrir la terminal después de instalar Node.js |
| `No module named selenium` / `No module named pytest` | Ejecutar con `.venv\Scripts\python.exe`, no solo `python`, o repetir la instalación de 4.1 |
| `SessionNotCreatedException` o error de driver | Actualizar Google Chrome; Selenium Manager descarga el driver correspondiente (requiere internet) |
| `npm install` muestra avisos (`npm warn ...`) | Son informativos y no afectan la ejecución; solo importa que no aparezca `npm error` |
| La primera prueba de API falla por tiempo | restful-booker puede tardar en responder la primera vez; volver a ejecutar `npm test` |
| El navegador abre y cierra muy rápido | Es normal; usar `--headed --lento 1.5` para verlo con calma |
| En PowerShell no se puede activar el entorno virtual | No es necesario activarlo; los comandos de esta guía usan `.venv\Scripts\python.exe` directamente |

**Requisito de red:** ambas suites prueban sitios públicos, así que necesitan conexión a internet.
