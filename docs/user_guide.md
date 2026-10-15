# Manual de Usuario y Demostración — PixelVault

Bienvenido al manual interactivo de **PixelVault**, la tienda digital de videojuegos inspirada visualmente en el equilibrio entre **Steam** (catálogo organizado, ofertas, badges destacados y fichas técnicas) e **itch.io** (personalidad independiente, estética neón oscura y protagonismo para estudios indies).

---

## 1. Puesta en Marcha Rápida

La aplicación está diseñada para ejecutarse fácilmente en cualquier computadora con Python 3.10 o superior y el gestor `uv`:

```powershell
# 1. Clonar o situarse en la carpeta del proyecto
cd "c:\Users\Dark\Desktop\Pagina tipo tienda steam"

# 2. Sincronizar dependencias automáticamente con uv
uv sync

# 3. Iniciar el aplicativo web en el navegador
uv run python main.py
```

Al ejecutarse, la consola mostrará:
```text
==================================================================
[PIXELVAULT] TIENDA DIGITAL DE VIDEOJUEGOS (STEAM + ITCH.IO)
IUT 'Antonio Jose de Sucre' -- Programacion IV
Docente de Referencia: Prof. Yoher Alejandro Vazquez Salinas
Modo: Aplicacion Web en Navegador (http://127.0.0.1:8550)
Persistencia: Archivos JSON locales en data/
Gestion de Entorno: uv (uv run python main.py)
==================================================================
```
Abre tu navegador en `http://127.0.0.1:8550` (o el puerto configurado).

---

## 2. Guía de Navegación y Pantallas

### 2.1. Barra de Navegación Superior
Presente en todas las pantallas:
- **Logotipo PIXELVAULT**: Haz clic en cualquier momento para regresar al inicio de la tienda.
- **Tienda**: Página principal con selecciones editoriales.
- **Catálogo Completo**: Vista de exploración con todos los 18 títulos y filtros interactivos.
- **Zona Indie**: Acceso directo con filtro preactivado a juegos experimentales e independientes.
- **Mis Pedidos**: Historial de todas las compras simuladas guardadas en `data/orders.json`.
- **Buscador Rápido**: Escribe cualquier término (ej. *Cyber*, *RPG*, *Origami*) y presiona Enter para buscar en el catálogo.
- **Botón Carrito**: Muestra una insignia verde con el número actual de videojuegos en el carrito. Al pulsarlo abre la vista del carrito.

---

### 2.2. Portada de la Tienda (Inicio)
Al entrar a la tienda encontrarás:
1. **Banner Promocional Principal (Hero)**: Destaca el juego estelar de la semana (ej. *Cyber Odyssey: Neo-Veridia*) con su descripción, calificación comunitaria, etiqueta de oferta y botones de acción inmediata ("Ver Detalles Completos" y "Añadir al Carrito").
2. **Super Ofertas & Descuentos**: Títulos con descuentos destacados del 20% al 70%, mostrando el precio anterior tachado y el precio rebajado en verde.
3. **Novedades & Tendencias**: Juegos recientemente agregados con insignia dorada `NUEVO`.
4. **Rincón Indie & Experimental (itch.io Spotlight)**: Juegos independientes con mecánicas únicas (ej. *Glitch Runner 404*, *The Botanical Witch*, *Gravity Shift*).
5. **Banner de Llamada a la Acción (CTA)**: Acceso directo al catálogo completo.

---

### 2.3. Catálogo y Filtros Interactivos
En el menú superior pulsa **Catálogo Completo**:
- **Búsqueda por texto**: Escribe en el campo de búsqueda. Los resultados se actualizan en vivo sin recargar la página.
- **Filtro por Género**: Despliega el menú y selecciona un género específico (*Acción, Aventura, Rol / RPG, Estrategia, Terror, Simulación, Plataformas*).
- **Solo Ofertas 🔥**: Activa el switch para ver únicamente juegos con descuento promocional activo.
- **Solo Indies 👾**: Activa el switch para filtrar únicamente títulos de desarrolladores independientes.
- **Ordenamiento**: Elige cómo ordenar la lista (*Destacados, Precio: Menor a Mayor, Precio: Mayor a Menor, Mejor Valorados, Alfabético A-Z*).
- **Restablecer**: Si aplicas una combinación sin coincidencias o deseas reiniciar los filtros, pulsa el botón *"Restablecer"* para volver a ver los 18 títulos.

---

### 2.4. Ficha Técnica y Detalle del Videojuego
Al hacer clic en **"Detalles"** en cualquier tarjeta de juego o en el banner:
- Podrás ver la portada en alta resolución o arte conceptual.
- Etiquetas de género y tags descriptivos.
- Resumen cualitativo de reseñas (*"Extremadamente positivas"*, *"Muy positivas"*).
- Ficha técnica: Desarrollador, Editor, Fecha de lanzamiento y Licencia.
- Sinopsis y lista de características jugables.
- Tabla de **Requisitos del Sistema para PC** (Sistema Operativo, Procesador, Memoria RAM, Gráficos y Almacenamiento).
- Caja de compra con precio, descuento, ahorro obtenido y botones:
  - **"Añadir al Carrito"**: Agrega el juego al carrito.
  - **"Comprar Ahora"**: Agrega el juego y salta directamente a la pantalla de compra.

---

### 2.5. Carrito de Compras
Al hacer clic en **"Carrito"** en la barra superior:
- Se muestra la lista de juegos seleccionados.
- **Regla de No Duplicación**: Como en una tienda real de licencias digitales de software, un mismo juego no se duplica. Si intentas añadirlo de nuevo, el sistema te notificará mediante un mensaje informativo y mantendrá una única copia.
- **Eliminar ítem**: Haz clic en el ícono de papelera roja junto a cualquier título para removerlo.
- **Vaciar Carrito**: Permite limpiar todos los productos de una vez.
- **Desglose Económico**:
  - **Precio Base (Subtotal)**.
  - **Ahorro por Ofertas** (suma de todos los descuentos en verde).
  - **Total Estimado a Pagar**.
- **Continuar a la Compra**: Pulsa el botón verde para proceder a la confirmación de la orden.

---

### 2.6. Proceso de Compra Simulada (Checkout)
Al proceder al pago:
- Verás el resumen con los títulos que estás a punto de adquirir.
- Formulario de demostración:
  - **Nombre Completo**: Mínimo 3 caracteres (ej. *Alejandro Morales*).
  - **Correo Electrónico**: Correo con formato válido (ej. *estudiante@universidad.edu*).
  - **Método de Pago Simulado**: Selecciona una opción de prueba (ej. *Saldo PixelVault*).
- **Aviso Académico**: Claramente señalizado indicando que no se maneja dinero real ni se solicitan datos financieros privados.
- Pulsa **"Confirmar Compra Simulada"**.

---

### 2.7. Claves de Activación Digital (Confirmación)
Tras completar la compra:
- El carrito se vacía automáticamente.
- Se genera un **Identificador de Pedido** único (ej. `PV-2026-F91A2B`).
- Se genera una **Clave Digital de Activación** para cada videojuego adquirido (ej. `PIXEL-9F41-8A10-BC23-01D5`).
- La orden queda guardada en el archivo local `data/orders.json`.
- Puedes hacer clic en **"Ver Historial de Pedidos"** para comprobar que el archivo se actualizó correctamente en el disco.

---

### 2.8. Historial de Pedidos (`Mis Pedidos`)
En cualquier momento, puedes pulsar **"Mis Pedidos"** en el encabezado:
- Lee directamente el archivo `data/orders.json`.
- Muestra el listado de todas las órdenes emitidas, el comprador, la fecha/hora UTC, el monto pagado y los códigos de clave digital entregados.
- Esto permite al docente evaluar la persistencia real de extremo a extremo sin requerir bases de datos pesadas.
