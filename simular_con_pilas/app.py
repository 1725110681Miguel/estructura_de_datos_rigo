import web


class Pila:
    def __init__(self):
        self.items = []

    def apilar(self, elemento):
        self.items.append(elemento)

    def desapilar(self):
        return self.items.pop()

    def cima(self):
        return self.items[-1]

    def esta_vacia(self):
        return len(self.items) == 0

    def tamano(self):
        return len(self.items)

    def vaciar(self):
        self.items = []

    def eliminar(self, identificador):
        self.items = [item for item in self.items if item.id != identificador]


urls = (
    "/", "Inicio",
)

render = web.template.render("templates/")
pila = Pila()
visitadas = []
estado = {"mensaje": "Elige una opción del menú.", "vista": "mensaje", "salio": False, "contador": 0}


def mostrar():
    paginas = list(reversed(visitadas))
    if pila.esta_vacia():
        actual_id = None
    else:
        actual_id = pila.cima().id
    return render.index(estado["mensaje"], estado["vista"], paginas, actual_id, estado["salio"])


class Inicio:
    def GET(self):
        return mostrar()

    def POST(self):
        datos = web.input(accion="", url="")
        accion = datos.accion
        pagina = datos.url.strip()
        estado["vista"] = "mensaje"

        if accion == "visitar":
            if pagina == "":
                estado["mensaje"] = "Escribe el nombre de una página para visitarla."
            else:
                estado["contador"] += 1
                visita = web.storage(id=estado["contador"], url=pagina)
                pila.apilar(visita)
                visitadas.append(visita)
                estado["mensaje"] = "Visitaste: " + pagina

        elif accion == "regresar":
            if pila.tamano() <= 1:
                estado["mensaje"] = "No hay una página anterior a la cual regresar."
            else:
                pila.desapilar()
                estado["mensaje"] = "Regresaste a: " + pila.cima().url

        elif accion == "actual":
            if pila.esta_vacia():
                estado["mensaje"] = "No hay página actual. El historial está vacío."
            else:
                estado["mensaje"] = "Página actual: " + pila.cima().url

        elif accion == "historial":
            if len(visitadas) == 0:
                estado["mensaje"] = "El historial está vacío."
            else:
                estado["mensaje"] = "Historial completo (de la más reciente a la más antigua):"
                estado["vista"] = "historial"

        elif accion == "vacio":
            if len(visitadas) == 0:
                estado["mensaje"] = "El historial está vacío."
            else:
                estado["mensaje"] = "Tu historial tiene " + str(len(visitadas)) + " página(s). Presiona ✕ para borrar una."
                estado["vista"] = "gestionar"

        elif accion.startswith("borrar_"):
            identificador = int(accion.split("_")[1])
            borrada = None
            for visita in visitadas:
                if visita.id == identificador:
                    borrada = visita
            if borrada is None:
                estado["mensaje"] = "Esa página ya no está en el historial."
            else:
                visitadas.remove(borrada)
                pila.eliminar(identificador)
                estado["mensaje"] = "Se eliminó: " + borrada.url
            if len(visitadas) > 0:
                estado["vista"] = "gestionar"
            else:
                estado["mensaje"] = estado["mensaje"] + ". El historial quedó vacío."

        elif accion == "eliminar_todo":
            pila.vaciar()
            visitadas.clear()
            estado["mensaje"] = "El historial fue eliminado."

        elif accion == "salir":
            estado["mensaje"] = "Programa finalizado."
            estado["salio"] = True

        elif accion == "reiniciar":
            pila.vaciar()
            visitadas.clear()
            estado["mensaje"] = " Elige una opción del menú."
            estado["salio"] = False

        return mostrar()


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()