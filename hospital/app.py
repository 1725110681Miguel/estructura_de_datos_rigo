import web
from time import monotonic
from threading import Lock
from pathlib import Path

web.config.debug = False
carpeta = Path(__file__).resolve().parent
render = web.template.render(str(carpeta / "templates"))

fila_general = []
fila_prioritaria = []
atendidos = []
paciente_actual = None
siguiente_turno = 1
control = Lock()

urls = (
    "/", "Inicio",
    "/registrar", "Registrar",
    "/atender", "Atender",
    "/finalizar", "Finalizar",
)


class Inicio:
    def GET(self):
        with control:
            total = siguiente_turno - 1
            cantidad = len(atendidos)
            prioritarios = sum(p["tipo"] == "Prioritaria" for p in atendidos)
            promedio = 0
            if cantidad > 0:
                promedio = round(sum(p["duracion"] for p in atendidos) / cantidad, 2)
            return render.index(
                fila_general, fila_prioritaria, paciente_actual,
                atendidos, total, prioritarios, promedio
            )


class Registrar:
    def POST(self):
        global siguiente_turno
        datos = web.input(nombre="", edad="", motivo="", tipo="", tiempo="")
        nombre = datos.nombre.strip()
        motivo = datos.motivo.strip()
        try:
            edad = int(datos.edad)
            tiempo = int(datos.tiempo)
        except ValueError:
            raise web.badrequest("Edad y tiempo deben ser numeros enteros.")

        if not nombre or not motivo or len(nombre) > 100 or len(motivo) > 300:
            raise web.badrequest("Escribe nombre (hasta 100) y motivo (hasta 300 caracteres).")
        if not 0 <= edad <= 120 or not 1 <= tiempo <= 240:
            raise web.badrequest("Edad permitida: 0 a 120. Tiempo: 1 a 240 minutos.")
        if datos.tipo not in ("General", "Prioritaria"):
            raise web.badrequest("Selecciona un tipo de atencion valido.")

        with control:
            paciente = {
                "turno": siguiente_turno,
                "nombre": nombre,
                "edad": edad,
                "motivo": motivo,
                "tipo": datos.tipo,
                "tiempo": tiempo,
            }
            siguiente_turno += 1
            if paciente["tipo"] == "Prioritaria":
                fila_prioritaria.append(paciente)
            else:
                fila_general.append(paciente)
        raise web.seeother("/")


class Atender:
    def POST(self):
        global paciente_actual
        with control:
            if paciente_actual is None:
                if fila_prioritaria:
                    paciente_actual = fila_prioritaria.pop(0)
                elif fila_general:
                    paciente_actual = fila_general.pop(0)
                if paciente_actual is not None:
                    paciente_actual["inicio"] = monotonic()
        raise web.seeother("/")


class Finalizar:
    def POST(self):
        global paciente_actual
        with control:
            if paciente_actual is not None:
                paciente_actual["duracion"] = (
                    monotonic() - paciente_actual["inicio"]
                ) / 60
                atendidos.append(paciente_actual)
                paciente_actual = None
        raise web.seeother("/")


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
