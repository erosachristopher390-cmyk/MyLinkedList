from .nodo import Nodo


class ListaLigada:
    """
    Implementación propia de una lista simplemente ligada.

    La cadena principal se administra mediante referencias entre nodos
    (cabeza -> siguiente -> siguiente), sin usar una lista de Python para
    almacenar los nodos.

    Los enlaces personalizados se guardan aparte como pares (id_origen,
    id_destino), para que la interfaz pueda dibujarlos sin alterar la cadena.
    """

    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.longitud = 0
        self.siguiente_id = 1
        self.enlaces_extra = set()

    def __len__(self):
        return self.longitud

    def __iter__(self):
        actual = self.cabeza
        while actual is not None:
            yield actual
            actual = actual.siguiente

    def __getitem__(self, indice):
        if isinstance(indice, slice):
            return [nodo for nodo in self][indice]
        nodo = self.obtener_posicion(indice)
        if nodo is None:
            raise IndexError("Índice fuera de rango.")
        return nodo

    def __contains__(self, item):
        if isinstance(item, Nodo):
            return self.obtener(item.id) is not None
        if isinstance(item, int):
            return self.obtener(item) is not None
        return any(str(nodo.dato).casefold() == str(item).casefold() for nodo in self)

    def __eq__(self, other):
        if isinstance(other, (list, tuple)):
            return self.valores() == list(other)
        return NotImplemented

    def __str__(self):
        return str(self.valores())

    def __repr__(self):
        return f"ListaLigada({self.valores()!r})"

    @property
    def nodos(self):
        """Compatibilidad con interfases antiguas que esperaban una lista de nodos."""
        return list(self)

    def esta_vacia(self):
        return self.cabeza is None

    def insertar(self, dato, posicion=None):
        """
        Inserta un nodo en la posición indicada (índice desde cero).
        Si posicion es None, lo agrega al final.
        Devuelve el nodo creado.
        """
        if posicion is None:
            posicion = self.longitud

        if not isinstance(posicion, int):
            raise TypeError("La posición debe ser un número entero.")
        if posicion < 0:
            posicion += self.longitud
        if posicion < 0:
            posicion = 0
        if posicion > self.longitud:
            posicion = self.longitud

        nuevo = Nodo(self.siguiente_id, dato)
        self.siguiente_id += 1

        if self.cabeza is None:
            self.cabeza = self.cola = nuevo
        elif posicion == 0:
            nuevo.siguiente = self.cabeza
            self.cabeza = nuevo
        elif posicion == self.longitud:
            self.cola.siguiente = nuevo
            self.cola = nuevo
        else:
            anterior = self._obtener_nodo(posicion - 1)
            nuevo.siguiente = anterior.siguiente
            anterior.siguiente = nuevo

        self.longitud += 1
        return nuevo

    def eliminar(self, nodo_o_id):
        """
        Elimina un nodo por referencia Nodo o por identificador.
        Devuelve True si se eliminó; False si no se encontró.
        """
        identificador = nodo_o_id.id if isinstance(nodo_o_id, Nodo) else nodo_o_id

        anterior = None
        actual = self.cabeza

        while actual is not None:
            if actual.id == identificador:
                if anterior is None:
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente

                if self.cola is actual:
                    self.cola = anterior

                actual.siguiente = None
                self.longitud -= 1

                self.enlaces_extra = {
                    (origen, destino)
                    for origen, destino in self.enlaces_extra
                    if origen != identificador and destino != identificador
                }

                if self.cabeza is None:
                    self.cola = None

                return True

            anterior = actual
            actual = actual.siguiente

        return False

    def obtener(self, identificador):
        """Busca y devuelve un nodo por su ID, o None si no existe."""
        for nodo in self:
            if nodo.id == identificador:
                return nodo
        return None

    def obtener_posicion(self, posicion):
        """Devuelve el nodo en un índice desde cero, o None si no existe."""
        if not isinstance(posicion, int):
            return None
        if posicion < 0:
            posicion += self.longitud
        if posicion < 0 or posicion >= self.longitud:
            return None
        return self._obtener_nodo(posicion)

    def _obtener_nodo(self, posicion):
        actual = self.cabeza
        indice = 0
        while actual is not None and indice < posicion:
            actual = actual.siguiente
            indice += 1
        return actual

    def buscar(self, dato):
        """Busca por igualdad de texto ignorando mayúsculas/minúsculas."""
        objetivo = str(dato).casefold()
        for nodo in self:
            if str(nodo.dato).casefold() == objetivo:
                return nodo
        return None

    def enlaces_cadena(self):
        """Devuelve los enlaces consecutivos de la lista principal."""
        enlaces = set()
        actual = self.cabeza
        while actual is not None and actual.siguiente is not None:
            enlaces.add((actual.id, actual.siguiente.id))
            actual = actual.siguiente
        return enlaces

    def todos_los_enlaces(self):
        """Devuelve los enlaces principales y los enlaces personalizados."""
        return self.enlaces_cadena() | set(self.enlaces_extra)

    def agregar_enlace(self, origen_id, destino_id):
        """Agrega un enlace personalizado si ambos nodos existen."""
        if origen_id == destino_id:
            raise ValueError("No se permite enlazar un nodo consigo mismo.")
        if self.obtener(origen_id) is None or self.obtener(destino_id) is None:
            raise ValueError("Los dos nodos deben existir en la lista.")
        self.enlaces_extra.add((origen_id, destino_id))

    def eliminar_enlace(self, origen_id, destino_id):
        """Elimina un enlace personalizado. Devuelve True si existía."""
        enlace = (origen_id, destino_id)
        if enlace in self.enlaces_extra:
            self.enlaces_extra.remove(enlace)
            return True
        return False

    def recorrer(self, inicio=None):
        """
        Recorre la cadena principal desde el primer nodo o desde un nodo/ID.
        Devuelve una lista Python con los nodos visitados, no almacena la lista
        ligada internamente en una lista Python.
        """
        if inicio is None:
            actual = self.cabeza
        elif isinstance(inicio, Nodo):
            actual = self.obtener(inicio.id)
        else:
            actual = self.obtener(inicio)

        resultado = []
        visitados = set()
        while actual is not None and actual.id not in visitados:
            resultado.append(actual)
            visitados.add(actual.id)
            actual = actual.siguiente
        return resultado

    def valores(self):
        """Devuelve los datos en orden como una lista de Python."""
        return [nodo.dato for nodo in self]

    def append(self, dato):
        """Agrega un dato al final y devuelve el nodo creado."""
        return self.insertar(dato)

    def insert(self, posicion, dato):
        """Inserta un dato en la posición indicada."""
        return self.insertar(dato, posicion)

    def remove(self, dato):
        """Elimina el primer nodo cuyo dato coincide con `dato`."""
        nodo = self.buscar(dato)
        if nodo is None:
            raise ValueError(f"{dato!r} no está en la lista.")
        if not self.eliminar(nodo.id):
            raise ValueError(f"{dato!r} no está en la lista.")

    def pop(self, posicion=-1):
        """Elimina y devuelve el nodo de la posición indicada."""
        if self.esta_vacia():
            raise IndexError("pop from empty list")
        if posicion < 0:
            posicion += self.longitud
        if posicion < 0 or posicion >= self.longitud:
            raise IndexError("Índice fuera de rango.")
        nodo = self.obtener_posicion(posicion)
        self.eliminar(nodo.id)
        return nodo

    def count(self, valor):
        """Cuenta cuántas veces aparece `valor` en la lista."""
        return sum(1 for nodo in self if str(nodo.dato).casefold() == str(valor).casefold())

    def index(self, valor):
        """Devuelve la posición del primer elemento que coincide con `valor`."""
        for indice, nodo in enumerate(self):
            if str(nodo.dato).casefold() == str(valor).casefold():
                return indice
        raise ValueError(f"{valor!r} no está en la lista.")

    def clear(self):
        """Elimina todos los nodos y enlaces personalizados."""
        self.limpiar()

    def limpiar(self):
        """Elimina todos los nodos y enlaces personalizados."""
        actual = self.cabeza
        while actual is not None:
            siguiente = actual.siguiente
            actual.siguiente = None
            actual = siguiente
        self.cabeza = None
        self.cola = None
        self.longitud = 0
        self.siguiente_id = 1
        self.enlaces_extra.clear()
