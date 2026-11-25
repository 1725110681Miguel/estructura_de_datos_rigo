# Catálogo tecnológico

Sistema sencillo para administrar productos con un árbol binario de búsqueda. Cada producto está en un nodo y se compara por su código.

## Ejecutar

1. Instala Python 3.
2. Abre una terminal dentro de esta carpeta.
3. Ejecuta `python app.py` (o `python3 app.py` en macOS).
4. Abre `http://localhost:8000`.

No necesitas instalar paquetes. Los productos se guardan automáticamente en `productos.json` al agregar o eliminar. Ese archivo aparece al usar el sistema.

## Funciones

- Agregar productos con código único, nombre, categoría, precio y cantidad.
- Buscar un producto por código.
- Eliminar productos, incluso si el nodo tiene dos hijos.
- Mostrar recorridos inorden, preorden y postorden.

`app.py` inicia el servidor, `web.py` recibe las solicitudes, y `arbol.py` contiene los nodos y las operaciones del árbol. `index.html` y `estilo.css` forman la interfaz.
