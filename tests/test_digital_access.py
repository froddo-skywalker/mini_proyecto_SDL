import tempfile
import unittest
from datetime import datetime, timedelta

from biblioteca import Biblioteca, LibroDigital


class DigitalAccessTests(unittest.TestCase):
    def test_generar_y_acceder_enlace_valido(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Biblioteca(ruta_base=tmpdir)
            libro = LibroDigital("Ebook", "AutorX", "ISBN-D1", "DX01", 3.0)
            b.registrar_libro(libro)

            enlace = b.generar_enlace_acceso(libro.codigo_barras, duracion_dias=2)
            self.assertIsInstance(enlace, str)

            resultado = b.acceder_libro_digital(libro.codigo_barras, enlace)
            self.assertIn("lectura", resultado.lower())

    def test_acceso_con_enlace_invalido(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Biblioteca(ruta_base=tmpdir)
            libro = LibroDigital("Ebook2", "AutorY", "ISBN-D2", "DX02", 4.0)
            b.registrar_libro(libro)

            enlace = b.generar_enlace_acceso(libro.codigo_barras, duracion_dias=2)
            with self.assertRaises(ValueError):
                b.acceder_libro_digital(libro.codigo_barras, enlace + "-wrong")

    def test_acceso_digital_sobrevive_a_la_recarga(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = Biblioteca(ruta_base=tmpdir)
            libro = LibroDigital("Ebook persistente", "Autor", "ISBN-D4", "DX04", 6.0)
            b.registrar_libro(libro)
            enlace = b.generar_enlace_acceso(libro.codigo_barras, duracion_dias=2)
            b.cerrar()

            recargada = Biblioteca(ruta_base=tmpdir)

            resultado = recargada.acceder_libro_digital(libro.codigo_barras, enlace)
            self.assertIn("lectura", resultado.lower())

    def test_acceso_expirado(self):
        # controlamos el tiempo con Biblioteca.ahora
        base_time = datetime(2020, 1, 1, 12, 0, 0)
        b = Biblioteca(ruta_base=tempfile.mkdtemp(), ahora=lambda: base_time)
        libro = LibroDigital("Ebook3", "AutorZ", "ISBN-D3", "DX03", 5.0)
        b.registrar_libro(libro)

        enlace = b.generar_enlace_acceso(libro.codigo_barras, duracion_dias=1)

        # avanzar el tiempo más allá de la expiración
        b.ahora = lambda: base_time + timedelta(days=2)

        with self.assertRaises(ValueError) as cm:
            b.acceder_libro_digital(libro.codigo_barras, enlace)
        self.assertIn("expir", str(cm.exception).lower())


if __name__ == "__main__":
    unittest.main()
