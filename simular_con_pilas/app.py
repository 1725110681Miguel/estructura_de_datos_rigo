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


urls = (
    "/", "Inicio",
    "/reiniciar", "Reiniciar"
)

render = web.template.render("templates/")
pila = Pila()
estado = {"mensaje": "Bienvenido. Elige una opción del menú.", "confirmar": False, "salio": False}


class Inicio:
    def GET(self):
        return render.index(estado["mensaje"], estado["confirmar"], estado["salio"])

    def POST(self):
        datos = web.input(accion="", url="")
        accion = datos.accion
        pagina = datos.url.strip()
        estado["confirmar"] = False

        if accion == "visitar":
            if pagina == "":
                estado["mensaje"] = "Escribe el nombre de una página para visitarla."
            else:
                pila.apilar(pagina)
                estado["mensaje"] = "Visitaste: " + pagina

        elif accion == "regresar":
            if pila.tamano() <= 1:
                estado["mensaje"] = "No hay una página anterior a la cual regresar."
            else:
                pila.desapilar()
                estado["mensaje"] = "Regresaste a: " + pila.cima()

        elif accion == "actual":
            if pila.esta_vacia():
                estado["mensaje"] = "No hay página actual. El historial está vacío."
            else:
                estado["mensaje"] = "Página actual: " + pila.cima()

        elif accion == "historial":
            if pila.esta_vacia():
                estado["mensaje"] = "El historial está vacío."
            else:
                texto = "Historial (de la más reciente a la más antigua):\n"
                posicion = 1
                for item in reversed(pila.items):
                    texto += str(posicion) + ". " + item + "\n"
                    posicion += 1
                estado["mensaje"] = texto

        elif accion == "vacio":
            if pila.esta_vacia():
                estado["mensaje"] = "El historial está vacío."
            else:
                estado["mensaje"] = "El historial tiene " + str(pila.tamano()) + " página(s). ¿Deseas eliminarlo?"
                estado["confirmar"] = True

        elif accion == "eliminar":
            pila.vaciar()
            estado["mensaje"] = "El historial fue eliminado."

        elif accion == "salir":
            estado["mensaje"] = "Programa finalizado."
            estado["salio"] = True

        raise web.seeother("/")


class Reiniciar:
    def GET(self):
        pila.vaciar()
        estado["mensaje"] = "Bienvenido. Elige una opción del menú."
        estado["confirmar"] = False
        estado["salio"] = False
        raise web.seeother("/")


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()