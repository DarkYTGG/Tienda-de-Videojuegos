<div align="center">

  # 🎮 PixelVault — Digital Videogame Store
  ### Tienda Digital de Videojuegos · Arquitectura Hexagonal Desacoplada · Doble Capa de Presentación (Flask Web + Flet GUI)
  ### Next-Gen Digital Game Store · Hexagonal Clean Architecture · Dual Presentation (Flask Web + Flet GUI)

  <p align="center">
    <a href="#-versión-en-español"><b>🇪🇸 Versión en Español</b></a>
    &nbsp;•&nbsp;
    <a href="#-english-version"><b>🇬🇧 English Version</b></a>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Tipo-Proyecto_Acad%C3%A9mico-blueviolet?style=for-the-badge&logo=google-classroom&logoColor=white" alt="Proyecto Académico">
    <img src="https://img.shields.io/badge/Type-Academic_Project-blueviolet?style=for-the-badge&logo=google-classroom&logoColor=white" alt="Academic Project">
    <img src="https://img.shields.io/badge/Autor-%40DarkYTGG-2563EB?style=for-the-badge&logo=github&logoColor=white" alt="Autor DarkYTGG">
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Web-Flask%203.1-black?style=flat-square&logo=flask&logoColor=white" alt="Flask">
    <img src="https://img.shields.io/badge/GUI-Flet%201.0.4-8B5CF6?style=flat-square&logo=flutter&logoColor=white" alt="Flet">
    <img src="https://img.shields.io/badge/Package_Manager-uv-06B6D4?style=flat-square" alt="uv">
    <img src="https://img.shields.io/badge/Architecture-Hexagonal%20%2F%20Layered-emerald?style=flat-square" alt="Hexagonal Architecture">
    <img src="https://img.shields.io/badge/Tests-Passed%20(100%25)-brightgreen?style=flat-square" alt="Tests 100%">
  </p>

</div>

> **Evaluación Práctica / Practical Evaluation — Programación IV**  
> **Instituto Universitario de Tecnología "Antonio José de Sucre"**  
> **Docente de Referencia:** Prof. Yoher Alejandro Vázquez Salinas

---

<a id="-versión-en-español"></a>
## 🇪🇸 Versión en Español

### 📖 1. Propósito del Proyecto y Objetivo Académico
**PixelVault** es una plataforma de comercio digital de videojuegos que fusiona la solidez organizativa de **Steam** (catálogo exhaustivo, banners promocionales, precios tachados, porcentajes de descuento y fichas técnicas) con el espíritu independiente y creativo de **itch.io** (estética oscura con neones violeta y cian, badges distintivos y protagonismo de títulos indie).

El sistema implementa una **Arquitectura en Capas Hexagonal** donde el núcleo de Dominio, Casos de Uso y Persistencia alimenta **dos clientes de presentación independientes**:
1. **Cliente Web Interactivo (Flask + HTML5 / CSS3 / JavaScript):** Interfaz web completa con diseño cyberpunk, offcanvas drawer para el carrito reactivo, animaciones CSS y filtrado instantáneo.
2. **Cliente GUI (Flet / Flutter Web):** Interfaz gráfica reactiva basada en componentes orientados a objetos.

### 🛠️ 2. Tecnologías Utilizadas
- **Lenguaje:** Python (>= 3.10, compatible con 3.12 y 3.14).
- **Capa Web (Flask):** Flask 3.1+, Jinja2, Bootstrap 5.3, Bootstrap Icons y CSS3 personalizado.
- **Capa GUI (Flet):** Flet 1.0.4 (Flutter binding para Python, modo navegador web).
- **Gestor de Paquetes y Entornos:** `uv` (Astral Software).
- **Persistencia:** Archivos locales en formato JSON (`data/games.json` y `data/orders.json`).
- **Pruebas Automatizadas:** `unittest` nativo con suite completa cubriendo Dominio, Aplicación, Persistencia, GUI y Rutas Flask.

### 🌟 3. Funcionalidades Implementadas
- **Página Principal (StoreView / Flask Index):** Banner hero promocional, sección de Super Ofertas, Novedades y sección Indie Spotlight.
- **Catálogo Interactivo (CatalogView):** Exploración de 18 videojuegos con búsqueda en vivo, filtro por género, interruptor "Solo Ofertas", "Solo Indies" y ordenamiento múltiple.
- **Ficha Técnica de Videojuego (GameDetailView):** Portada HD, galería de capturas, sinopsis, requisitos de hardware para PC y compra rápida.
- **Carrito de Compras (CartView / Offcanvas Drawer):** Gestión reactiva con **prevención estricta de duplicados** (restricción de licencias digitales de software), cálculo de subtotales y descuentos acumulados.
- **Checkout y Claves Digitales:** Simulación de compra con generación criptográfica de claves de activación digital (`PV-2026-XXXX`).
- **Historial Persistido & Inspector de Órdenes:** Consulta en tiempo real de pedidos almacenados en JSON.

### 🏛️ 4. Estructura y Arquitectura Hexagonal
```text
pixelvault/
├── src/
│   ├── domain/                  # Entidades puras y reglas de negocio
│   ├── application/             # Casos de uso y DTOs
│   ├── infrastructure/          # Repositorios JSON y clientes API
│   ├── web/                     # Presentación 1: Flask Web (Templates, Controllers)
│   └── gui/                     # Presentación 2: Flet GUI (Flutter Web)
├── data/                        # Persistencia en JSON (games.json, orders.json)
└── tests/                       # Suite de pruebas automatizadas con unittest
```

### 🚀 5. Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/DarkYTGG/Tienda-de-Videojuegos.git
cd Tienda-de-Videojuegos

# 2. Sincronizar dependencias con uv
uv sync

# 3. Opción A: Ejecutar Servidor Web Flask (Recomendado)
uv run python run.py
# Accede en: http://127.0.0.1:5000

# 4. Opción B: Ejecutar Interfaz GUI Flet
uv run python main.py
# Accede en: http://127.0.0.1:8555

# 5. Ejecutar Pruebas Automatizadas
uv run python -m unittest discover tests
```

---

<a id="-english-version"></a>
## 🇬🇧 English Version

### 📖 1. Project Purpose & Academic Overview
**PixelVault** is a next-generation digital videogame storefront fusing the organizational clarity of **Steam** (exhaustive catalog, hero banners, strikethrough pricing, discount badges, and PC hardware requirements) with the independent spirit of **itch.io** (cyberpunk dark aesthetic, neon violet/cyan accents, and indie highlights).

Built around an **Hexagonal Layered Architecture**, the pure domain core and JSON persistence layer cleanly drive **two independent presentation clients**:
1. **Interactive Web Client (Flask + HTML5 / CSS3 / Vanilla JS):** Full-featured cyberpunk web store featuring an offcanvas shopping cart drawer, CSS animations, and instant catalog filtering.
2. **GUI Client (Flet / Flutter Web):** Reactive object-oriented component interface running on Flutter engine via Python.

### 🛠️ 2. Tech Stack
- **Language:** Python (>= 3.10, tested on 3.12 and 3.14).
- **Web Layer:** Flask 3.1+, Jinja2, Bootstrap 5.3, Bootstrap Icons, custom CSS3.
- **GUI Layer:** Flet 1.0.4 (Flutter binding for Python, browser web mode).
- **Environment & Package Manager:** `uv` by Astral Software.
- **Persistence:** Local JSON data stores (`data/games.json` and `data/orders.json`).
- **Testing:** Comprehensive test suite with native `unittest` covering Domain, Application, JSON storage, and web controllers.

### 🌟 3. Core Features
- **Storefront (StoreView / Flask Index):** Hero spotlight carousel, Super Deals, New Releases, and Indie Showcase.
- **Interactive Catalog (CatalogView):** 18 curated videogames with real-time text search, genre filtering, "Deals Only" toggle, "Indies Only" toggle, and multi-criteria sorting.
- **Game Details Page (GameDetailView):** HD cover art, screenshots gallery, plot synopsis, hardware requirements table, and instant purchase.
- **Shopping Cart (CartView / Offcanvas Drawer):** Real-time cart state with **strict duplicate item prevention** (digital software license constraint), automatic subtotal, and discount calculation.
- **Simulated Checkout & Key Generation:** Academic order processing that generates cryptographically unique activation keys (`PV-2026-XXXX`) with 1-click clipboard copy.
- **Order History & JSON Inspector:** Live inspector to review generated orders and verify local JSON state.

### 🏛️ 4. Hexagonal Folder Structure
```text
pixelvault/
├── src/
│   ├── domain/                  # Pure entities, domain exceptions & repository ports
│   ├── application/             # Use cases & DTOs
│   ├── infrastructure/          # Thread-safe JSON repositories & API integrations
│   ├── web/                     # Presentation 1: Flask Web (Jinja2, routes, static)
│   └── gui/                     # Presentation 2: Flet GUI (OOP components, views)
├── data/                        # JSON storage (games.json, orders.json)
└── tests/                       # Automated unit & integration tests
```

### 🚀 5. Quickstart & Execution

```bash
# 1. Clone repository
git clone https://github.com/DarkYTGG/Tienda-de-Videojuegos.git
cd Tienda-de-Videojuegos

# 2. Sync dependencies using uv
uv sync

# 3. Option A: Run Flask Web Server (Recommended)
uv run python run.py
# Open: http://127.0.0.1:5000

# 4. Option B: Run Flet GUI Client
uv run python main.py
# Open: http://127.0.0.1:8555

# 5. Run Automated Tests
uv run python -m unittest discover tests
```

---

## 👨‍💻 Autor / Author

Desarrollado por / Built by **DarkYTGG** — Estudiante de TSU en Informática / Computer Science Student.
- 🌐 GitHub: [@DarkYTGG](https://github.com/DarkYTGG)
