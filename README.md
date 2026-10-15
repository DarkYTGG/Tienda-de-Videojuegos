# 🎮 PixelVault — Tienda Digital de Videojuegos

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/GUI-Flet%201.0.4-8B5CF6.svg?logo=flutter&logoColor=white)](https://flet.dev/)
[![uv](https://img.shields.io/badge/Package%20Manager-uv-06B6D4.svg)](https://github.com/astral-sh/uv)
[![Architecture](https://img.shields.io/badge/Architecture-Hexagonal%20%2F%20Layered-emerald.svg)](#-arquitectura-del-software)
[![Tests](https://img.shields.io/badge/Tests-30%20Passed%20(100%25)-brightgreen.svg)](#-ejecuci%C3%B3n-de-pruebas-automatizadas)

> **Evaluación Práctica — Programación IV**  
> **Instituto Universitario de Tecnología "Antonio José de Sucre"**  
> **Docente de Referencia:** Prof. Yoher Alejandro Vázquez Salinas ([Repositorio de Referencia](https://github.com/yohervz/progra-iv-web))

---

## 📖 1. Propósito del Proyecto y Objetivo Académico
**PixelVault** es una aplicación web interactiva que simula una tienda digital de videojuegos de última generación. Su dirección artística combina la solidez organizativa de **Steam** (catálogo extenso, banners promocionales, precios tachados, porcentajes de descuento y fichas técnicas) con el espíritu independiente y creativo de **itch.io** (estética oscura con neones violeta y cian, badges distintivos y protagonismo de títulos experimentales).

El objetivo principal es demostrar en un nivel académico profesional:
1. **Programación Orientada a Objetos (POO)**: Encapsulamiento, abstracción, herencia, polimorfismo e inyección de dependencias.
2. **Arquitectura en Capas Limpia**: Separación verificable entre Dominio, Casos de Uso (Aplicación), Adaptadores de Persistencia (Infraestructura) e Interfaz Gráfica Reactiva (Presentación).
3. **Flujo de Desarrollo Moderno**: Gestión reproducible de dependencias con `uv` (`pyproject.toml` y `uv.lock`), pruebas unitarias automatizadas (`unittest`) y persistencia local sin bases de datos externas mediante archivos JSON thread-safe.

---

## 🛠️ 2. Tecnologías Utilizadas
- **Lenguaje:** Python (>= 3.10, probado y verificado en Python 3.12 y 3.14).
- **Interfaz Gráfica / Web:** [Flet](https://flet.dev/) 1.0.4 (Flutter binding para Python, modo navegador web).
- **Gestor de Paquetes y Entornos:** [uv](https://github.com/astral-sh/uv) (Astral Software).
- **Persistencia:** Archivos locales en formato JSON (`data/games.json` y `data/orders.json`).
- **Pruebas Automatizadas:** `unittest` nativo de Python con cobertura de dominio, casos de uso, repositorios y estructura OOP de vistas.
- **Control de Versiones:** Git y GitHub.

---

## 🌟 3. Funcionalidades Implementadas
| Sección / Funcionalidad | Descripción |
|---|---|
| **Página Principal (StoreView)** | Banner hero promocional para juego destacado, sección de Super Ofertas, sección de Novedades 2026, sección Indie Spotlight (itch.io) y llamada al catálogo completo. |
| **Catálogo Interactivo (CatalogView)** | Exploración de 18 videojuegos con búsqueda en vivo, filtro por género, interruptor "Solo Ofertas", interruptor "Solo Indies", ordenamiento múltiple y estado vacío amigable con botón de restablecimiento. |
| **Ficha de Videojuego (GameDetailView)** | Portada de alta definición, sinopsis, etiquetas de género, resumen cualitativo de reseñas (*Extremadamente positivas*), requisitos del sistema para PC, precio, descuento y compra rápida. |
| **Carrito de Compras (CartView)** | Gestión de productos con **prevención estricta de duplicados** (restricción intrínseca de licencias digitales de software), cálculo en vivo de subtotal, descuento acumulado y total neto. Opciones de eliminación individual y vaciado. |
| **Compra Simulada (CheckoutView)** | Formulario de datos mínimos con validación semántica, aviso académico de no cobro real y cálculo de importes coordinado por la lógica de negocio. |
| **Claves Digitales (OrderConfirmationView)** | Pantalla de confirmación con generación de identificador de pedido (`PV-2026-XXXX`) y claves criptográficas de activación digital (`PIXEL-XXXX-XXXX-XXXX`) para cada título. |
| **Historial Persistido (OrdersHistoryView)** | Lectura directa de `data/orders.json` para comprobar pedidos completados y sus claves asignadas. |

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
│   └── gui/                     # CAPA DE PRESENTACIÓN (Interfaz Flet Web)
│       ├── __init__.py
│       ├── app.py               # PixelVaultApp (Ciclo de vida, DI, Router)
│       ├── theme.py             # Tokens de diseño, colores Steam + itch.io
│       ├── components/          # Componentes reutilizables
│       │   ├── header.py        # StoreHeaderComponent (Logo, nav links, cart badge)
│       │   ├── game_card.py     # GameCardComponent (Portada, tags, precios, botones)
│       │   ├── hero_banner.py   # FeaturedHeroBannerComponent (Banner principal)
│       │   ├── filter_bar.py    # FilterBarComponent (Buscador, combos, switches)
│       │   └── footer.py        # StoreFooterComponent (Créditos académicos)
│       └── views/               # Vistas polimórficas (Heredan de BaseView)
│           ├── base_view.py     # BaseView (Clase abstracta)
│           ├── store_view.py    # StoreView (Inicio)
│           ├── catalog_view.py  # CatalogView (Catálogo interactivo)
│           ├── detail_view.py   # GameDetailView (Detalle del producto)
│           ├── cart_view.py     # CartView (Carrito)
│           ├── checkout_view.py # CheckoutView (Pago simulado)
│           ├── confirmation_view.py # OrderConfirmationView (Recibo y claves)
│           └── orders_view.py   # OrdersHistoryView (Historial JSON)
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
│   └── test_gui_oop.py          # Herencia, polimorfismo y ensamblado de vistas
│
├── docs/                        # DOCUMENTACIÓN TÉCNICA
│   ├── architecture.md          # Diagramas Mermaid y justificación de POO
│   └── user_guide.md            # Manual de uso paso a paso
│
├── main.py                      # Punto de entrada de la aplicación
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

Para iniciar la tienda web en tu navegador:
```powershell
uv run python main.py
```
O especificando un puerto personalizado (por ejemplo, el 8550):
```powershell
uv run python main.py 8550
```

Se abrirá automáticamente tu navegador web predeterminado en:
`http://127.0.0.1:8550`

---

## 🧪 7. Ejecución de Pruebas Automatizadas

El proyecto incluye una suite completa de **30 pruebas unitarias e integrales** que validan la lógica de negocio, cálculos de ofertas, carrito de compras, persistencia en JSON y la arquitectura orientada a objetos de la GUI sin necesidad de abrir una ventana gráfica:

```powershell
# Ejecutar todas las pruebas del proyecto
uv run python -m unittest discover tests
```

Salida esperada:
```text
Ran 30 tests in 0.284s

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
