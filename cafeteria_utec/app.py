import web
from urllib.parse import urlencode

urls = (
    "/", "Inicio",
    "/registrar", "Registrar",
    "/preparar", "Preparar",
    "/siguiente", "Siguiente",
    "/estadisticas", "Estadisticas",
    "/cancelar", "Cancelar"
)

render = web.template.render("templates/")

normales = []
prioritarios = []

numero = 1
preparados = 0
cancelados = 0


# Regresa al inicio sin cambiar la dirección de Codespaces.
def volver(mensaje):
    direccion = "/?" + urlencode({"mensaje": mensaje})

    raise web.HTTPError(
        "303 See Other",
        {"Location": direccion},
        ""
    )


# Selecciona la fila que tiene preferencia.
def elegir_fila():
    if prioritarios:
        return prioritarios

    return normales


class Inicio:
    def GET(self):
        datos = web.input(mensaje="")

        return render.index(
            normales,
            prioritarios,
            datos.mensaje
        )


class Registrar:
    def POST(self):
        global numero

        datos = web.input(
            cliente="",
            producto="",
            cantidad="",
            tipo="",
            tiempo=""
        )

        cliente = datos.cliente.strip()
        producto = datos.producto.strip()

        if not cliente or not producto:
            volver("Completa el nombre y el producto.")

        try:
            cantidad = int(datos.cantidad)
            tiempo = int(datos.tiempo)
        except ValueError:
            volver("Cantidad y tiempo deben ser números enteros.")

        if cantidad <= 0 or tiempo <= 0:
            volver("Cantidad y tiempo deben ser mayores a cero.")

        if datos.tipo not in ["Normal", "Prioritario"]:
            volver("Selecciona un tipo de pedido válido.")

        pedido = {
            "numero": numero,
            "cliente": cliente,
            "producto": producto,
            "cantidad": cantidad,
            "tipo": datos.tipo,
            "tiempo": tiempo
        }

        if datos.tipo == "Prioritario":
            prioritarios.append(pedido)
        else:
            normales.append(pedido)

        numero += 1

        volver(
            "Pedido "
            + str(pedido["numero"])
            + " registrado correctamente."
        )


class Preparar:
    def POST(self):
        global preparados

        fila = elegir_fila()

        if not fila:
            volver("No hay pedidos pendientes.")

        # Retira el primer pedido de la fila.
        pedido = fila.pop(0)
        preparados += 1

        volver(
            "Se preparó el pedido "
            + str(pedido["numero"])
            + " de "
            + pedido["cliente"]
            + "."
        )


class Siguiente:
    def GET(self):
        fila = elegir_fila()

        if not fila:
            volver("No hay pedidos pendientes.")

        # Consulta el primero sin retirarlo.
        pedido = fila[0]

        volver(
            "Siguiente pedido: "
            + str(pedido["numero"])
            + " | Cliente: "
            + pedido["cliente"]
            + " | Producto: "
            + pedido["producto"]
            + " | Cantidad: "
            + str(pedido["cantidad"])
            + " | Tipo: "
            + pedido["tipo"]
            + " | Tiempo: "
            + str(pedido["tiempo"])
            + " minutos."
        )


class Estadisticas:
    def GET(self):
        minutos = 0

        for pedido in normales + prioritarios:
            minutos += pedido["tiempo"]

        pendientes = len(normales) + len(prioritarios)

        volver(
            "Registrados: " + str(numero - 1)
            + " | Preparados: " + str(preparados)
            + " | Cancelados: " + str(cancelados)
            + " | Pendientes: " + str(pendientes)
            + " | Normales: " + str(len(normales))
            + " | Prioritarios: " + str(len(prioritarios))
            + " | Minutos pendientes: " + str(minutos)
        )


class Cancelar:
    def POST(self):
        global cancelados

        datos = web.input(numero="")

        try:
            buscado = int(datos.numero)
        except ValueError:
            volver("Escribe un número de pedido válido.")

        for fila in [prioritarios, normales]:
            for pedido in fila:
                if pedido["numero"] == buscado:
                    fila.remove(pedido)
                    cancelados += 1

                    volver(
                        "Pedido "
                        + str(buscado)
                        + " cancelado."
                    )

        volver("No existe ese pedido entre los pendientes.")


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()