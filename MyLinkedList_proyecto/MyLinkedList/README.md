# MyLinkedList

Biblioteca educativa en Python que implementa una lista simplemente ligada usando nodos enlazados por referencias. Incluye una interfaz gráfica de ejemplo hecha con Tkinter.

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido habitualmente en las instalaciones de Python para Windows)

## Ejecutar

Desde la carpeta raíz del proyecto:

```bash
python main.py
```

## Ejecutar pruebas

```bash
python -m unittest discover -s tests -v
```

## Operaciones de la biblioteca

```python
from MyLinkedList import ListaLigada

lista = ListaLigada()
a = lista.insertar("A")
b = lista.insertar("B")
lista.insertar("C", 1)       # Inserta en el índice 1

print(lista.valores())       # ['A', 'C', 'B']
print(lista.buscar("A"))     # Devuelve el nodo que contiene A
print(lista.enlaces_cadena())
lista.agregar_enlace(a.id, b.id)  # Enlace extra para visualización
lista.eliminar(b.id)
```

Los índices empiezan en cero. `insertar(dato)` agrega al final y `insertar(dato, posicion)` inserta en la posición indicada.

## Estructura

- `MyLinkedList/nodo.py`: clase Nodo.
- `MyLinkedList/lista_ligada.py`: implementación de la estructura y operaciones.
- `app/interfaz.py`: interfaz gráfica.
- `main.py`: punto de entrada.
- `tests/test_lista_ligada.py`: pruebas unitarias.

## Integración con una interfaz existente

Si estás migrando una interfaz que usaba `self.lista.nodos`, recorre la lista con `for nodo in self.lista`, usa `len(self.lista)` para el tamaño y `self.lista.obtener_posicion(indice)` para obtener un nodo por posición. Para vaciarla usa `self.lista.limpiar()`.

La interfaz de ejemplo de este paquete es una base funcional. Para conservar exactamente el diseño previo, copia la clase `Aplicacion` original en `app/interfaz.py` y adapta las referencias a `self.lista.nodos` según las indicaciones anteriores.
