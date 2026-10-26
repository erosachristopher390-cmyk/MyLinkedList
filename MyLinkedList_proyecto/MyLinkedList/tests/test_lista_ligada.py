import unittest

from MyLinkedList import ListaLigada


class TestListaLigada(unittest.TestCase):
    def setUp(self):
        self.lista = ListaLigada()

    def test_insertar_al_final(self):
        self.lista.insertar("A")
        self.lista.insertar("B")
        self.assertEqual(self.lista.valores(), ["A", "B"])
        self.assertEqual(len(self.lista), 2)

    def test_insertar_en_posicion(self):
        self.lista.insertar("A")
        self.lista.insertar("C")
        self.lista.insertar("B", 1)
        self.assertEqual(self.lista.valores(), ["A", "B", "C"])

    def test_eliminar_cabeza_y_cola(self):
        a = self.lista.insertar("A")
        b = self.lista.insertar("B")
        self.assertTrue(self.lista.eliminar(a.id))
        self.assertTrue(self.lista.eliminar(b.id))
        self.assertTrue(self.lista.esta_vacia())
        self.assertIsNone(self.lista.cola)

    def test_buscar_sin_distinguir_mayusculas(self):
        self.lista.insertar("Hola")
        resultado = self.lista.buscar("HOLA")
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.dato, "Hola")

    def test_enlaces_personalizados_separados(self):
        a = self.lista.insertar("A")
        b = self.lista.insertar("B")
        c = self.lista.insertar("C")
        self.lista.agregar_enlace(a.id, c.id)
        self.assertEqual(self.lista.enlaces_cadena(), {(a.id, b.id), (b.id, c.id)})
        self.assertIn((a.id, c.id), self.lista.todos_los_enlaces())

    def test_eliminar_nodo_limpia_enlaces_personalizados(self):
        a = self.lista.insertar("A")
        b = self.lista.insertar("B")
        self.lista.agregar_enlace(a.id, b.id)
        self.lista.eliminar(a.id)
        self.assertNotIn((a.id, b.id), self.lista.enlaces_extra)


if __name__ == "__main__":
    unittest.main()
