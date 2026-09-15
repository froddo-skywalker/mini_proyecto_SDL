import os
import tempfile
import unittest
from datetime import timedelta

from biblioteca import Biblioteca, Estudiante, Libro, LibroDigital, Profesor


class BibliotecaTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.biblioteca = Biblioteca(ruta_base=self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_encapsulamiento_y_disponibilidad(self):
        libro = Libro("Dune", "Frank Herbert", "978-1-234", "B001", 25.0)
        self.assertTrue(libro.disponible)
        libro.disponible = False
        self.assertFalse(libro.disponible)

    def test_polimorfismo_abrir(self):
        digital = LibroDigital("Python", "Guido", "978-2-345", "D001", 15.0)
        self.assertIn("lectura", digital.abrir().lower())

    def test_limite_de_5_libros(self):
        usuario = Estudiante("Ana", "U-1", 12, "3", "A")
        self.biblioteca.registrar_usuario(usuario)
        for i in range(5):
            libro = Libro(f"Libro {i}", "Autor", f"ISBN-{i}", f"B{i:03d}", 10.0)
            self.biblioteca.registrar_libro(libro)
            self.biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)
        self.assertEqual(len(usuario.prestamos_activos), 5)
        extra = Libro("Otro", "Autor", "ISBN-EXTRA", "B999", 10.0)
        self.biblioteca.registrar_libro(extra)
        with self.assertRaises(ValueError):
            self.biblioteca.prestar_libro(usuario.identificacion, extra.codigo_barras)

    def test_libro_ocupado(self):
        usuario1 = Profesor("Luis", "U-2", 40, ["Primero"], ["A"])
        usuario2 = Estudiante("Marta", "U-3", 8, "2", "B")
        self.biblioteca.registrar_usuario(usuario1)
        self.biblioteca.registrar_usuario(usuario2)
        libro = Libro("El Quijote", "Cervantes", "978-9-999", "B010", 30.0)
        self.biblioteca.registrar_libro(libro)
        self.biblioteca.prestar_libro(usuario1.identificacion, libro.codigo_barras)
        with self.assertRaises(ValueError):
            self.biblioteca.prestar_libro(usuario2.identificacion, libro.codigo_barras)

    def test_rechazo_de_libros_digitales_en_prestamos(self):
        usuario = Estudiante("Diego", "U-4", 7, "1", "A")
        self.biblioteca.registrar_usuario(usuario)
        digital = LibroDigital("Manual digital", "Autor", "978-3-456", "D100", 5.0)
        self.biblioteca.registrar_libro(digital)
        with self.assertRaises(ValueError):
            self.biblioteca.prestar_libro(usuario.identificacion, digital.codigo_barras)

    def test_prorroga_y_vencimiento(self):
        usuario = Estudiante("Sofia", "U-5", 9, "4", "C")
        self.biblioteca.registrar_usuario(usuario)
        libro = Libro("Ficciones", "Borges", "978-4-567", "B020", 18.0)
        self.biblioteca.registrar_libro(libro)
        self.biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)

        fecha_despues_prorroga = self.biblioteca.prestamos[0].fecha_vencimiento + timedelta(days=3)
        self.biblioteca.actualizar_prestamos(fecha_despues_prorroga)

        self.assertTrue(usuario.vetado)
        self.assertGreaterEqual(usuario.deuda, libro.precio)

    def test_veto_y_pagos(self):
        usuario = Profesor("Pablo", "U-6", 35, ["Primaria"], ["A"])
        self.biblioteca.registrar_usuario(usuario)
        libro = Libro("1984", "Orwell", "978-5-678", "B030", 20.0)
        self.biblioteca.registrar_libro(libro)
        self.biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)

        self.biblioteca.actualizar_prestamos(self.biblioteca.prestamos[0].fecha_vencimiento + timedelta(days=3))
        self.assertTrue(usuario.vetado)

        self.biblioteca.registrar_pago(usuario.identificacion, 20.0)
        self.assertFalse(usuario.vetado)
        self.assertEqual(usuario.deuda, 0.0)

    def test_devoluciones_daniadas(self):
        usuario = Estudiante("Elena", "U-7", 10, "5", "D")
        self.biblioteca.registrar_usuario(usuario)
        libro = Libro("La metamorfosis", "Kafka", "978-6-789", "B040", 22.0)
        self.biblioteca.registrar_libro(libro)
        self.biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)

        self.biblioteca.devolver_libro(libro.codigo_barras, condicion="daniado")
        self.assertTrue(usuario.vetado)
        self.assertEqual(usuario.deuda, 22.0)
        self.assertFalse(libro.disponible)

    def test_persistencia_y_generacion_reporte(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            biblioteca = Biblioteca(ruta_base=tmpdir)
            usuario = Profesor("Nora", "U-8", 45, ["Primaria"], ["B"])
            biblioteca.registrar_usuario(usuario)
            libro = Libro("Moby Dick", "Melville", "978-7-890", "B050", 28.0)
            biblioteca.registrar_libro(libro)
            biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)
            biblioteca.generar_reporte_csv()

            self.assertTrue(os.path.exists(os.path.join(tmpdir, "reporte_prestamos.csv")))

            nueva = Biblioteca(ruta_base=tmpdir)
            self.assertEqual(len(nueva.usuarios), 1)
            self.assertEqual(len(nueva.libros), 1)
            self.assertEqual(len(nueva.prestamos), 1)

    def test_pago_reactiva_libro_daniado(self):
        usuario = Estudiante("Ana", "U-9", 11, "3", "B")
        self.biblioteca.registrar_usuario(usuario)
        libro = Libro("Libro dañado", "Autor", "978-8-901", "B060", 12.0)
        self.biblioteca.registrar_libro(libro)
        self.biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)
        self.biblioteca.devolver_libro(libro.codigo_barras, condicion="daniado")

        self.assertFalse(libro.disponible)
        self.assertEqual(usuario.deuda, 12.0)

        self.biblioteca.registrar_pago(usuario.identificacion, 12.0)
        self.assertEqual(usuario.deuda, 0.0)
        self.assertTrue(libro.disponible)

    def test_visualizar_reporte_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            biblioteca = Biblioteca(ruta_base=tmpdir)
            usuario = Profesor("Nora", "U-8", 45, ["Primaria"], ["B"])
            biblioteca.registrar_usuario(usuario)
            libro = Libro("Moby Dick", "Melville", "978-7-890", "B050", 28.0)
            biblioteca.registrar_libro(libro)
            biblioteca.prestar_libro(usuario.identificacion, libro.codigo_barras)
            contenido = biblioteca.generar_reporte_csv()

            self.assertIn("usuario_id", contenido)
            self.assertIn("Moby Dick", contenido)

    def test_edad_estudiante_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            Estudiante("Pepe", "E-ERR", 5, "1", "A")
        with self.assertRaises(ValueError):
            Estudiante("Pepe", "E-ERR-2", 15, "1", "A")


if __name__ == "__main__":
    unittest.main()
