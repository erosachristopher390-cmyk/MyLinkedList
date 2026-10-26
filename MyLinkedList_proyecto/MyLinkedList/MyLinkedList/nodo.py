class Nodo:
    """Nodo de una lista simplemente ligada."""

    def __init__(self, identificador, dato):
        self.id = identificador
        self.dato = dato
        self.siguiente = None

    def __repr__(self):
        return f"Nodo(id={self.id!r}, dato={self.dato!r})"
