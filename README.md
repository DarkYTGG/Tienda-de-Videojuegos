# 🎮 PixelVault — Tienda Digital de Videojuegos

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Web-Flask%203.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Flet](https://img.shields.io/badge/GUI-Flet%201.0.4-8B5CF6.svg?logo=flutter&logoColor=white)](https://flet.dev/)
[![uv](https://img.shields.io/badge/Package%20Manager-uv-06B6D4.svg)](https://github.com/astral-sh/uv)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal%20%2F%20Layered-emerald.svg)](#-arquitectura-del-software)
[![Tests](https://img.shields.io/badge/Tests-36%20Passed%20(100%25)-brightgreen.svg)](#-ejecuci%C3%B3n-de-pruebas-automatizadas)

> **Evaluación Práctica — Programación IV**  
> **Instituto Universitario de Tecnología "Antonio José de Sucre"**  
> **Docente de Referencia:** Prof. Yoher Alejandro Vázquez Salinas ([Repositorio de Referencia](https://github.com/yohervz/progra-iv-web))

---

## 📖 1. Propósito del Proyecto y Objetivo Académico
**PixelVault** es una plataforma de comercio digital de videojuegos de última generación. Su dirección artística fusiona la solidez organizativa de **Steam** (catálogo exhaustivo, banners promocionales, precios tachados, porcentajes de descuento y fichas técnicas de hardware) con el espíritu independiente y creativo de **itch.io** (estética oscura con neones violeta y cian, badges distintivos y protagonismo de títulos indie).

Siguiendo el patrón arquitectónico del repositorio de referencia de la cátedra (`yoher-tech-courses`), el sistema implementa una **Arquitectura en Capas Hexagonal** donde el núcleo de Dominio, Casos de Uso y Persistencia JSON alimenta **dos clientes de presentación independientes**:
1. **Cliente Web Interactivo (Flask + HTML5 / CSS3 / JavaScript):** Interfaz web completa con diseño cyberpunk, offcanvas drawer para el carrito reactivo, animaciones CSS y filtrado instantáneo.
2. **Cliente GUI (Flet / Flutter Web):** Interfaz gráfica reactiva basada en componentes orientados a objetos.

---

## 🛠️ 2. Tecnologías Utilizadas
- **Lenguaje:** Python (>= 3.10, probado y verificado en Python 3.12 y 3.14).
- **Capa Web (Flask):** [Flask](https://flask.palletsprojects.com/) 3.1+, Jinja2, Bootstrap 5.3, Bootstrap Icons y CSS3 personalizado.
- **Capa GUI (Flet):** [Flet](https://flet.dev/) 1.0.4 (Flutter binding para Python, modo navegador web).
- **Gestor de Paquetes y Entornos:** [uv](https://github.com/astral-sh/uv) (Astral Software).
- **Persistencia:** Archivos locales en formato JSON (`data/games.json` y `data/orders.json`).
- **Pruebas Automatizadas:** `unittest` nativo con 36 pruebas que cubren Dominio, Aplicación, Persistencia, GUI en Flet y Rutas/APIs en Flask.
- **Control de Versiones:** Git y GitHub.

---

## 🌟 3. Funcionalidades Implementadas
| Sección / Funcionalidad | Descripción |
|---|---|
| **Página Principal (StoreView / Flask Index)** | Banner hero promocional para juego destacado, sección de Super Ofertas, sección de Novedades 2026, sección Indie Spotlight (itch.io) y llamada al catálogo completo. |
| **Catálogo Interactivo (CatalogView / Flask Catalog)** | Exploración de 18 videojuegos con búsqueda en vivo, filtro por género, interruptor "Solo Ofertas", interruptor "Solo Indies", ordenamiento múltiple y estado vacío amigable con botón de restablecimiento. |
| **Ficha de Videojuego (GameDetailView / Flask Detail)** | Portada de alta definición, galería de capturas, sinopsis, etiquetas de género, resumen cualitativo de reseñas (*Extremadamente positivas*), requisitos del sistema para PC, precio, descuento y compra rápida. |
| **Carrito de Compras (CartView / Drawer Offcanvas)** | Gestión de productos con **prevención estricta de duplicados** (restricción intrínseca de licencias digitales de software), cálculo en vivo de subtotal, descuento acumulado y total neto. Opciones de eliminación individual y vaciado. |
| **Compra Simulada (CheckoutView / Flask Checkout)** | Formulario de datos mínimos con validación semántica, aviso académico de no cobro real y cálculo de importes coordinado por la lógica de negocio. |
| **Claves Digitales (OrderConfirmationView / Flask Confirmation)** | Pantalla de confirmación con generación de identificador de pedido (`PV-2026-XXXX`) y claves criptográficas de activación digital (`XXXXX-XXXXX-XXXXX`) para cada título con botón de 1-clic para copiar. |
| **Historial Persistido & Inspector (OrdersHistoryView / Flask Orders)** | Lectura directa de `data/orders.json` para comprobar pedidos completados y sus claves asignadas, incluyendo inspector en vivo del archivo JSON crudo. |

---

## 🏛️ 4. Arquitectura del Software y Organización de Carpetas

El proyecto sigue una arquitectura en capas hexagonal desacoplada:

```text
pixelvault/
├── src/
│   ├── domain/                  # CAPA DE DOMINIO (Reglas de negocio puras)
│   │   ├── __init__.py
│   │   ├── entities.py          # Game, CartItem, ShoppingCart, Order, OrderItem
│   │   ├── exceptions.py        # Jerarquía de excepciones semánticas
│   │   └── ports.py             # Interfaces abstractas ABC (GameRepository, OrderRepository)
│   │
│   ├── application/             # CAPA DE APLICACIÓN (Casos de uso y DTOs)
│   │   ├── __init__.py
│   │   ├── dtos.py              # GameFilterDTO, CheckoutRequestDTO, CheckoutResponseDTO
│   │   └── use_cases.py         # ListGamesUseCase, SearchAndFilterGamesUseCase, CheckoutUseCase, etc.
│   │
│   ├── infrastructure/          # CAPA DE INFRAESTRUCTURA (Persistencia técnica)
│   │   ├── __init__.py
│   │   ├── repositories.py      # JsonGameRepository, JsonOrderRepository (Thread-safe)
│   │   └── seed_data.py         # Catálogo inicial de 18 títulos diversos
│   │
│   ├── web/                     # CAPA DE PRESENTACIÓN 1: FLASK WEB
│   │   ├── __init__.py
│   │   ├── app.py               # create_app() factory e inyección de dependencias
│   │   ├── routes.py            # StoreWebController (OOP) y Blueprint
│   │   ├── static/              # Estilos CSS cyberpunk, JS interactivo
│   │   └── templates/           # Plantillas Jinja2 (base, index, catalog, detail, cart, etc.)
│   │
│   └── gui/                     # CAPA DE PRESENTACIÓN 2: FLET GUI
│       ├── __init__.py
│       ├── app.py               # PixelVaultApp (Ciclo de vida, DI, Router Flet)
│       ├── theme.py             # Tokens de diseño, safe_icon() para Flutter Web
│       ├── components/          # Componentes reutilizables (Header, Cards, Banner, Filter, Footer)
│       └── views/               # Vistas polimórficas (BaseView, StoreView, CatalogView, etc.)
│
├── data/                        # PERSISTENCIA LOCAL EN JSON
│   ├── games.json               # Catálogo de videojuegos
│   └── orders.json              # Registro persistente de compras simuladas
│
├── tests/                       # PRUEBAS AUTOMATIZADAS (unittest)
│   ├── __init__.py
│   ├── test_domain.py           # Reglas de negocio e invariantes
│   ├── test_use_cases.py        # Casos de uso y DTOs
│   ├── test_repositories.py     # Lectura, escritura y resiliencia de JSON
│   ├── test_gui_oop.py          # Herencia, polimorfismo y ensamblado de vistas Flet
│   └── test_web_flask.py        # Rutas, templates, API y carrito en Flask
│
├── docs/                        # DOCUMENTACIÓN TÉCNICA
│   ├── architecture.md          # Diagramas Mermaid y justificación de POO
│   └── user_guide.md            # Manual de uso paso a paso
│
├── run.py                       # Punto de entrada para la aplicación Web Flask (Puerto 5000)
├── main.py                      # Punto de entrada para la aplicación GUI Flet (Puerto 8555)
├── pyproject.toml               # Configuración de dependencias uv
├── uv.lock                      # Bloqueo reproducible de versiones
├── .gitignore                   # Exclusión de .venv, __pycache__, etc.
└── README.md                    # Documentación principal
```

Para una explicación exhaustiva con diagramas Mermaid de clases y secuencias, consulta [docs/architecture.md](docs/architecture.md).

---

## ⚙️ 5. Requisitos Previos e Instalación

### 5.1. Requisitos Previos
- **Sistema Operativo:** Windows 10/11, macOS o Linux.
- **Python:** Versión 3.10 o superior instalada.
- **uv:** Gestor de paquetes ultrarrápido recomendado por la cátedra.

### 5.2. Instalación de uv (si aún no lo tienes instalado)
En Windows (PowerShell):
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
En macOS / Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 5.3. Preparación del Entorno
Clona o descarga el repositorio y abre una terminal en la carpeta raíz:
```powershell
cd "c:\Users\Dark\Desktop\Pagina tipo tienda steam"

# Sincroniza e instala las dependencias del proyecto de forma reproducible
uv sync
```

---

## 🚀 6. Ejecución de la Aplicación

El proyecto cuenta con dos clientes de presentación para máxima versatilidad:

### Opción A: Cliente Web Interactivo en Flask (Recomendado — Estilo Steam + itch.io)
Proporciona la experiencia visual más avanzada, con diseño cyberpunk, animaciones fluidas, offcanvas drawer para el carrito y respuesta instantánea:
```powershell
uv run python run.py
```
Abre en tu navegador: **`http://127.0.0.1:5000`**

### Opción B: Cliente GUI en Flet (Flutter Web)
Permite evaluar la implementación con componentes orientados a objetos en Flet:
```powershell
uv run python main.py
```
Abre en tu navegador: **`http://127.0.0.1:8555`**

---

## 🧪 7. Ejecución de Pruebas Automatizadas

El proyecto incluye una suite completa de **36 pruebas unitarias e integrales** que validan la lógica de negocio, cálculos de ofertas, carrito de compras, persistencia en JSON, la arquitectura OOP de Flet y las rutas/APIs de Flask:

```powershell
# Ejecutar todas las pruebas del proyecto
uv run python -m unittest discover tests
```

Salida esperada:
```text
Ran 36 tests in 0.581s

OK
```

---

## 💾 8. Ubicación y Propósito de los Archivos JSON
- **`data/games.json`**: Contiene el catálogo de los 18 videojuegos con su esquema unificado (título, género, desarrollador, precio base, descuento, valoración, requisitos del sistema, imágenes). Si este archivo no existe al iniciar la aplicación, `JsonGameRepository` lo inicializa automáticamente de forma segura.
- **`data/orders.json`**: Guarda de forma persistente cada simulación académica de compra con su identificador de orden, fecha/hora, comprador, total pagado y claves de activación generadas.

---

## ⚠️ 9. Limitaciones de la Simulación Académica
1. **Pasarelas de Pago:** No se procesa dinero real ni se solicitan números de tarjetas bancarias. Los métodos de pago son exclusivamente simulados para fines pedagógicos.
2. **Descarga de Juegos:** No se descargan binarios de videojuegos pesados. Al completar una compra se entregan códigos alfanuméricos simulados de activación (`PIXEL-XXXX-XXXX-XXXX`).
3. **Persistencia Local:** Los datos se almacenan localmente en archivos JSON, lo cual es ideal para demostraciones estudiantiles sin requerir la configuración de servidores de bases de datos remotos.

---

## 🚀 10. Procedimiento para Subir el Proyecto a GitHub

Si deseas publicar este repositorio en tu cuenta personal de GitHub:

```powershell
# 1. Asegúrate de estar en la raíz del proyecto
cd "c:\Users\Dark\Desktop\Pagina tipo tienda steam"

# 2. Comprobar estado de Git
git status

# 3. Agregar los archivos al área de preparación (el .gitignore excluye .venv)
git add .

# 4. Crear el commit inicial estructurado
git commit -m "feat: implementacion inicial de PixelVault con Flet, POO y uv"

# 5. Renombrar la rama principal a main
git branch -M main

# 6. Vincular con tu repositorio remoto de GitHub (reemplaza TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/pixelvault-store.git

# 7. Subir el proyecto
git push -u origin main
```

---

## 🎯 11. Aspectos Clave para la Defensa ante el Profesor
Al defender el proyecto ante el docente evaluador, se sugiere resaltar:
1. **Separación de Capas:** Mostrar cómo la capa de dominio (`src/domain/entities.py`) no importa nada de Flet ni de archivos, protegiendo las reglas del negocio (cálculo de precios, descuentos y unicidad en el carrito).
2. **Puertos e Inversión de Dependencias:** Explicar cómo `src/domain/ports.py` define contratos abstractos (`GameRepository` y `OrderRepository`) que `src/infrastructure/repositories.py` implementa, permitiendo cambiar el motor de persistencia sin tocar la lógica de negocio.
3. **Polimorfismo en Vistas:** Explicar cómo `PixelVaultApp.navigate()` utiliza el método abstracto `build()` de `BaseView` para montar cualquier vista dinámicamente.
4. **Resiliencia:** Destacar que los repositorios manejan concurrencia con cerrojos (`threading.Lock`) y se recuperan automáticamente de archivos inexistentes o JSON corruptos.
5. **Cobertura de Pruebas:** Ejecutar `uv run python -m unittest discover tests` en vivo para evidenciar que las 30 pruebas automatizadas pasan en fracciones de segundo.
