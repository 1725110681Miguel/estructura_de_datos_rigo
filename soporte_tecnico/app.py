import web
from collections import deque
from itertools import count
from pathlib import Path
from threading import Lock

from jinja2 import Environment, FileSystemLoader, select_autoescape


urls = (
    "/", "Inicio",
    "/registrar", "Registrar",
    "/atender", "Atender",
)

fila_normal = deque()
fila_prioritaria = deque()

numeros = count(1)
total_atendidos = 0
bloqueo = Lock()

carpeta = Path(__file__).resolve().parent
plantillas = Environment(
    loader=FileSystemLoader(str(carpeta / "templates")),
    autoescape=select_autoescape(["html"]),
)


def fila_con_turno():
    """Devuelve la fila de la que corresponde tomar el siguiente ticket."""
    if fila_prioritaria:
        return fila_prioritaria
    return fila_normal


def volver(mensaje):
    # Cada navegador recibe el aviso de la acción que acaba de realizar.
    web.setcookie("aviso", mensaje, path="/")
    raise web.seeother("/")


class Inicio:
    def GET(self):
        aviso = web.cookies(aviso="").aviso
        if aviso:
            web.setcookie("aviso", "", expires=-1, path="/")

        with bloqueo:
            normales = list(fila_normal)
            prioritarios = list(fila_prioritaria)
            atendidos = total_atendidos
            fila = fila_con_turno()
            siguiente = fila[0] if fila else None

        pendientes = normales + prioritarios
        minutos = sum(ticket["tiempo"] for ticket in pendientes)

        web.header("Content-Type", "text/html; charset=utf-8")
        return plantillas.get_template("index.html").render(
            normales=normales,
            prioritarios=prioritarios,
            siguiente=siguiente,
            atendidos=atendidos,
            cantidad_pendiente=len(pendientes),
            minutos_pendientes=minutos,
            aviso=aviso,
        )


class Registrar:
    def POST(self):
        datos = web.input(cliente="", problema="", prioridad="", tiempo="")
        cliente = datos.cliente.strip()
        problema = datos.problema.strip()
        prioridad = datos.prioridad

        if not cliente or not problema:
            volver("Escribe el nombre del cliente y el problema.")

        if prioridad not in ("Normal", "Prioritaria"):
            volver("Selecciona una prioridad válida.")

        try:
            tiempo = int(datos.tiempo)
        except ValueError:
            volver("El tiempo debe ser un número entero de minutos.")

        if tiempo < 1:
            volver("El tiempo estimado debe ser de al menos un minuto.")

        with bloqueo:
            numero = f"T-{next(numeros):03d}"
            ticket = {
                "numero": numero,
                "cliente": cliente,
                "problema": problema,
                "prioridad": prioridad,
                "tiempo": tiempo,
            }

            if prioridad == "Prioritaria":
                fila_prioritaria.append(ticket)
            else:
                fila_normal.append(ticket)

        volver(f"Ticket {numero} registrado en la fila {prioridad.lower()}.")


class Atender:
    def POST(self):
        global total_atendidos

        with bloqueo:
            fila = fila_con_turno()
            if fila:
                ticket = fila.popleft()
                total_atendidos += 1
            else:
                ticket = None

        if ticket is None:
            volver("Las dos filas están vacías.")

        volver(f"Se atendió el ticket {ticket['numero']}.")


if __name__ == "__main__":
    app = web.application(urls, globals(), autoreload=False)
    app.run()