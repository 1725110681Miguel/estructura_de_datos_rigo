class Nodo:
    def __init__(self, producto):
        self.producto = producto
        self.izquierda = None
        self.derecha = None


class ArbolProductos:
    def __init__(self):
        self.raiz = None

    def buscar(self, codigo):
        actual = self.raiz
        while actual:
            if codigo == actual.producto["codigo"]:
                return actual.producto
            actual = actual.izquierda if codigo < actual.producto["codigo"] else actual.derecha
        return None

    def insertar(self, producto):
        codigo = producto["codigo"]
        if self.buscar(codigo):
            return False
        nuevo = Nodo(producto)
        if self.raiz is None:
            self.raiz = nuevo
            return True
        actual = self.raiz
        while True:
            lado = "izquierda" if codigo < actual.producto["codigo"] else "derecha"
            siguiente = getattr(actual, lado)
            if siguiente is None:
                setattr(actual, lado, nuevo)
                return True
            actual = siguiente

    def eliminar(self, codigo):
        if not self.buscar(codigo):
            return False
        self.raiz = self._eliminar(self.raiz, codigo)
        return True

    def _eliminar(self, nodo, codigo):
        if nodo is None:
            return None
        clave = nodo.producto["codigo"]
        if codigo < clave:
            nodo.izquierda = self._eliminar(nodo.izquierda, codigo)
        elif codigo > clave:
            nodo.derecha = self._eliminar(nodo.derecha, codigo)
        else:
            if nodo.izquierda is None:
                return nodo.derecha
            if nodo.derecha is None:
                return nodo.izquierda
            sucesor = nodo.derecha
            while sucesor.izquierda:
                sucesor = sucesor.izquierda
            nodo.producto = sucesor.producto
            nodo.derecha = self._eliminar(nodo.derecha, sucesor.producto["codigo"])
        return nodo

    def recorrer(self, orden="inorden"):
        productos = []

        def visitar(nodo):
            if nodo is None:
                return
            if orden == "preorden":
                productos.append(nodo.producto)
            visitar(nodo.izquierda)
            if orden == "inorden":
                productos.append(nodo.producto)
            visitar(nodo.derecha)
            if orden == "postorden":
                productos.append(nodo.producto)

        visitar(self.raiz)
        return productos
