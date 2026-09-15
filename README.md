<<<<<<< HEAD
# Sistema de biblioteca

Aplicación de consola en Python para gestionar libros, usuarios, préstamos y reportes.

## Reglas de negocio

- Cada ejemplar físico tiene un código de barras único.
- Cada obra tiene un ISBN.
- Los préstamos físicos duran 7 días.
- Se permite una prórroga automática de 2 días.
- Si se supera la prórroga, el usuario queda vetado y debe pagar el precio del libro.
- Un libro dañado genera deuda por el precio y se bloquea hasta reactivación administrativa.
- `LibroDigital` solo permite lectura y no participa en préstamos ni en el límite de 5.
- El administrador actúa desde el menú, sin autenticación.
- La persistencia principal está en JSON y el CSV es un reporte generado.

## Estructura

- `biblioteca.py`: lógica de negocio y persistencia.
- `main.py`: menú interactivo.
- `data/`: almacenamiento JSON y CSV.
- `tests/`: pruebas unitarias.

## Ejecución

```bash
python main.py
```

## Verificación

```bash
python -m py_compile main.py biblioteca.py
python -m unittest discover -s tests -v
```
=======
# mini_proyecto_SDL
prueba biblioteca escolar
>>>>>>> 6db483d5caaa3751b29afe60d9c685c6cdcec45a
