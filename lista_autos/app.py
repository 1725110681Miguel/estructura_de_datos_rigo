import os
import web


urls = (
    "/", "Index",
    "/agregar", "Agregar",
    "/eliminar/(.+)", "Eliminar",
)

app = web.application(urls, globals())

render = web.template.render("templates/", base="layout")

DB_PATH = os.path.join(os.path.dirname(__file__), "autos.db")
db = web.database(dbn="sqlite", db=DB_PATH)

db.query("""
CREATE TABLE IF NOT EXISTS autos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT,
    modelo TEXT,
    traccion TEXT,
    color TEXT,
    anio INTEGER,
    num_serie TEXT UNIQUE,
    tipo_motor TEXT,
    tipo_combustible TEXT
)
""")

# Autos de ejemplo, solo si la tabla está vacía (para que la demo
# no arranque en blanco).
if len(list(db.select("autos"))) == 0:
    autos_ejemplo = [
        dict(marca="Nissan", modelo="Versa", traccion="Delantera",
             color="Blanco", anio=2022, num_serie="NS-0001",
             tipo_motor="4 cilindros", tipo_combustible="Gasolina"),
        dict(marca="Toyota", modelo="Hilux", traccion="4x4",
             color="Gris", anio=2023, num_serie="TY-0002",
             tipo_motor="V6", tipo_combustible="Diésel"),
        dict(marca="Chevrolet", modelo="Onix", traccion="Delantera",
             color="Rojo", anio=2021, num_serie="CH-0003",
             tipo_motor="3 cilindros", tipo_combustible="Gasolina"),
    ]
    for auto in autos_ejemplo:
        db.insert("autos", **auto)



class Index:
    def GET(self):
        parametros = web.input(buscar="")
        buscar = parametros.buscar.strip()

        if buscar:
            like = "%" + buscar + "%"
            autos = db.select(
                "autos",
                where=(
                    "marca LIKE $like OR modelo LIKE $like "
                    "OR color LIKE $like"
                ),
                vars={"like": like},
                order="marca",
            )
        else:
            autos = db.select("autos", order="marca")

        # Importante: convertir el resultado de la consulta a una lista
        # normal antes de pasarlo al template. El objeto que regresa
        # db.select() es un iterador "perezoso" ligado al cursor de la
        # base de datos; si el template lo recorre más de una vez (o
        # llama len() sobre él) el programa se queda colgado.
        return render.index(list(autos), buscar)


class Agregar:
    def GET(self):
        return render.agregar(None)

    def POST(self):
        datos = web.input(
            marca="", modelo="", traccion="", color="",
            anio="", num_serie="", tipo_motor="", tipo_combustible="",
        )

        if not datos.marca or not datos.modelo or not datos.num_serie:
            return render.agregar("Marca, modelo y número de serie son obligatorios.")

        try:
            db.insert(
                "autos",
                marca=datos.marca,
                modelo=datos.modelo,
                traccion=datos.traccion,
                color=datos.color,
                anio=int(datos.anio) if datos.anio.isdigit() else None,
                num_serie=datos.num_serie,
                tipo_motor=datos.tipo_motor,
                tipo_combustible=datos.tipo_combustible,
            )
        except Exception:
            return render.agregar("Ya existe un auto con ese número de serie.")

        raise web.seeother("/")


class Eliminar:
    def POST(self, num_serie):
        db.delete("autos", where="num_serie = $num_serie", vars={"num_serie": num_serie})
        raise web.seeother("/")


if __name__ == "__main__":
    app.run()