import web
from collections import deque
from pathlib import Path
from threading import Lock

from jinja2 import Environment, FileSystemLoader, select_autoescape


urls = (
    "/", "Inicio",
    "/agregar", "Agregar",
    "/atender", "Atender",
)

app = web.application(urls, globals())

fila = deque()
turno = Lock()

carpeta = Path(__file__).resolve().parent
plantillas = Environment(
    loader=FileSystemLoader(str(carpeta / "templates")),
    autoescape=select_autoescape(["html"]),
)

# Estas rutas corresponden a los enlaces y formularios de index.html.
def url_for(nombre, filename=None):
    if nombre == "static":
        return f"/static/{filename}"

    rutas = {
        "inicio": "/",
        "agregar": "/agregar",
        "atender": "/atender",
    }
    return rutas[nombre]


plantillas.globals["url_for"] = url_for


def volver_al_inicio(mensaje):
    web.setcookie("aviso", mensaje, path="/")
    raise web.seeother("/")


class Inicio:
    def GET(self):
        avisos = {
            "agregado": "Estudiante agregado al final de la fila.",
            "atendido": "Se atendió al primer estudiante de la fila.",
            "vacia": "La fila está vacía. No hay estudiantes por atender.",
            "faltan_datos": "Completa los cuatro campos del estudiante.",
        }

        codigo = web.cookies(aviso="").aviso
        mensaje = avisos.get(codigo)

        if codigo:
            web.setcookie("aviso", "", expires=-1, path="/")

        with turno:
            estudiantes = list(fila)

        web.header("Content-Type", "text/html; charset=utf-8")
        return plantillas.get_template("index.html").render(
            estudiantes=estudiantes,
            mensajes=[mensaje] if mensaje else [],
        )


class Agregar:
    def POST(self):
        datos = web.input(matricula="", nombre="", carrera="", tramite="")

        estudiante = {
            "matricula": datos.matricula.strip(),
            "nombre": datos.nombre.strip(),
            "carrera": datos.carrera.strip(),
            "tramite": datos.tramite.strip(),
        }

        if not all(estudiante.values()):
            volver_al_inicio("faltan_datos")

        with turno:
            fila.append(estudiante)  

        volver_al_inicio("agregado")


class Atender:
    def POST(self):
        with turno:
            if fila:
                fila.popleft()  
                resultado = "atendido"
            else:
                resultado = "vacia"

        volver_al_inicio(resultado)


if __name__ == "__main__":
    app.run()