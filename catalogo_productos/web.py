import html
import json
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from arbol import ArbolProductos


CARPETA = Path(__file__).parent
ARCHIVO = CARPETA / "productos.json"
ARBOL = ArbolProductos()


def guardar():
    ARCHIVO.write_text(json.dumps(ARBOL.recorrer(), ensure_ascii=False, indent=2), encoding="utf-8")


def cargar():
    if ARCHIVO.exists():
        for producto in json.loads(ARCHIVO.read_text(encoding="utf-8")):
            ARBOL.insertar(producto)


def escapar(valor):
    return html.escape(str(valor), quote=True)


class Pagina(BaseHTTPRequestHandler):
    def responder(self, contenido, tipo="text/html; charset=utf-8"):
        datos = contenido.encode("utf-8") if isinstance(contenido, str) else contenido
        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def redirigir(self, mensaje):
        self.send_response(303)
        self.send_header("Location", "/?" + urlencode({"mensaje": mensaje}))
        self.end_headers()

    def do_GET(self):
        ruta = urlparse(self.path)
        if ruta.path == "/estilo.css":
            return self.responder((CARPETA / "estilo.css").read_bytes(), "text/css; charset=utf-8")
        if ruta.path != "/":
            self.send_error(404)
            return
        datos = parse_qs(ruta.query)
        codigo = datos.get("buscar", [""])[0].strip()
        orden = datos.get("orden", ["inorden"])[0]
        if orden not in ("inorden", "preorden", "postorden"):
            orden = "inorden"
        productos = ARBOL.recorrer(orden)
        if codigo:
            encontrado = ARBOL.buscar(codigo)
            productos = [encontrado] if encontrado else []
        filas = "".join(
            f'<tr><td>{escapar(p["codigo"])}</td><td>{escapar(p["nombre"])}</td>'
            f'<td>{escapar(p["categoria"])}</td><td>${escapar(p["precio"])}</td>'
            f'<td>{escapar(p["cantidad"])}</td><td><form method="post" action="/eliminar">'
            f'<input type="hidden" name="codigo" value="{escapar(p["codigo"])}">'
            '<button class="borrar" type="submit" onclick="return confirm(\'¿Eliminar producto?\')">Eliminar</button></form></td></tr>'
            for p in productos
        ) or '<tr><td colspan="6" class="vacio">No hay productos para mostrar.</td></tr>'
        pagina = (CARPETA / "index.html").read_text(encoding="utf-8")
        pagina = pagina.replace("{{FILAS}}", filas).replace("{{TOTAL}}", str(len(ARBOL.recorrer())))
        pagina = pagina.replace("{{BUSCAR}}", escapar(codigo)).replace("{{MENSAJE}}", escapar(datos.get("mensaje", [""])[0]))
        for opcion in ("inorden", "preorden", "postorden"):
            pagina = pagina.replace("{{" + opcion.upper() + "}}", "selected" if orden == opcion else "")
        self.responder(pagina)

    def do_POST(self):
        ruta = urlparse(self.path).path
        if ruta not in ("/agregar", "/eliminar"):
            self.send_error(404)
            return
        longitud = int(self.headers.get("Content-Length", "0"))
        if longitud > 10000:
            self.send_error(413)
            return
        datos = parse_qs(self.rfile.read(longitud).decode("utf-8"))
        valor = lambda campo: datos.get(campo, [""])[0].strip()
        codigo = valor("codigo")
        if ruta == "/eliminar":
            mensaje = "Producto eliminado." if ARBOL.eliminar(codigo) else "No existe ese código."
            if mensaje == "Producto eliminado.":
                guardar()
            return self.redirigir(mensaje)
        try:
            precio = Decimal(valor("precio"))
            cantidad = int(valor("cantidad"))
            if not codigo or not valor("nombre") or not valor("categoria") or precio < 0 or cantidad < 0 or not precio.is_finite():
                raise ValueError
        except (InvalidOperation, ValueError):
            return self.redirigir("Revisa los datos del producto.")
        producto = {"codigo": codigo, "nombre": valor("nombre"), "categoria": valor("categoria"),
                    "precio": str(precio.quantize(Decimal("0.01"))), "cantidad": cantidad}
        if not ARBOL.insertar(producto):
            return self.redirigir("Ese código ya existe.")
        guardar()
        self.redirigir("Producto agregado.")


def iniciar():
    cargar()
    servidor = HTTPServer(("localhost", 8000), Pagina)
    print("Abre http://localhost:8000 en tu navegador")
    servidor.serve_forever()
