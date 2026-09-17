from biblioteca import Biblioteca, Estudiante, Libro, LibroDigital, Profesor


def leer_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Debes ingresar un número válido.")


def leer_float(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Debes ingresar un número válido.")


def imprimir_menu(titulo, opciones):
    print(f"\n--- {titulo} ---")
    for numero, texto in opciones.items():
        print(f"{numero}. {texto}")


def listar_libros(biblioteca):
    if not biblioteca.libros:
        print("No hay libros registrados.")
        return
    print("\nLibros registrados:")
    for libro in biblioteca.libros.values():
        estado = "Disponible" if libro.disponible else "Prestado"
        print(f"- {libro.codigo_barras} | {libro.titulo} | {libro.autor} | {libro.tipo} | {estado}")


def listar_usuarios(biblioteca):
    if not biblioteca.usuarios:
        print("No hay usuarios registrados.")
        return
    print("\nUsuarios registrados:")
    for usuario in biblioteca.usuarios.values():
        if usuario.tipo == "estudiante":
            print(f"- {usuario.identificacion} | Estudiante | {usuario.nombre} | {usuario.edad} años | Grado {usuario.grado} - Sección {usuario.seccion} | Vetado: {usuario.vetado} | Deuda: {usuario.deuda}")
        else:
            print(f"- {usuario.identificacion} | Profesor | {usuario.nombre} | {usuario.edad} años | Grados: {', '.join(usuario.grados) if usuario.grados else 'Ninguno'} | Secciones: {', '.join(usuario.secciones_asignadas) if usuario.secciones_asignadas else 'Ninguna'} | Vetado: {usuario.vetado} | Deuda: {usuario.deuda}")


def registrar_estudiante(biblioteca):
    nombre = input("Nombre del estudiante: ")
    identificacion = input("Identificación: ").strip()
    edad = leer_entero("Edad (6-14): ")
    grado = input("Grado: ")
    seccion = input("Sección: ")
    try:
        usuario = Estudiante(nombre, identificacion, edad, grado, seccion)
        biblioteca.registrar_usuario(usuario)
        print("Estudiante registrado correctamente.")
    except ValueError as exc:
        print(f"Error: {exc}")


def registrar_profesor(biblioteca):
    nombre = input("Nombre del profesor: ")
    identificacion = input("Identificación: ").strip()
    edad = leer_entero("Edad: ")
    grados = input("Grados asignados (separados por coma): ")
    secciones = input("Secciones asignadas (separadas por coma): ")
    try:
        usuario = Profesor(
            nombre,
            identificacion,
            edad,
            grados=[g.strip() for g in grados.split(",") if g.strip()],
            secciones_asignadas=[s.strip() for s in secciones.split(",") if s.strip()],
        )
        biblioteca.registrar_usuario(usuario)
        print("Profesor registrado correctamente.")
    except ValueError as exc:
        print(f"Error: {exc}")


def registrar_libro_fisico(biblioteca):
    titulo = input("Título: ")
    autor = input("Autor: ")
    isbn = input("ISBN: ")
    codigo = input("Código de barras: ").strip()
    precio = leer_float("Precio: ")
    try:
        libro = Libro(titulo, autor, isbn, codigo, precio)
        biblioteca.registrar_libro(libro)
        print("Libro físico registrado.")
    except ValueError as exc:
        print(f"Error: {exc}")


def registrar_libro_digital(biblioteca):
    titulo = input("Título del e-book: ")
    autor = input("Autor: ")
    isbn = input("ISBN: ")
    codigo = input("Código de barras: ").strip()
    precio = leer_float("Precio: ")
    try:
        libro = LibroDigital(titulo, autor, isbn, codigo, precio)
        biblioteca.registrar_libro(libro)
        print("Libro digital registrado.")
    except ValueError as exc:
        print(f"Error: {exc}")


def prestar_libro(biblioteca):
    usuario_id = input("Identificación del usuario: ").strip()
    codigo = input("Código de barras del libro: ").strip()
    try:
        biblioteca.prestar_libro(usuario_id, codigo)
        print("Préstamo realizado correctamente.")
    except Exception as exc:
        print(f"Error: {exc}")


def leer_respuesta_si_no(mensaje):
    while True:
        respuesta = input(mensaje).strip().lower()
        if respuesta in {"si", "sí", "s"}:
            return True
        if respuesta in {"no", "n"}:
            return False
        print("Respuesta inválida. Responde con 'si' o 'no'.")


def devolver_libro(biblioteca):
    codigo = input("Código de barras del libro a devolver: ").strip()
    esta_bueno = leer_respuesta_si_no("¿El libro está en buena condición? (si/no): ")
    condicion = "bueno" if esta_bueno else "daniado"
    try:
        biblioteca.devolver_libro(codigo, condicion)
        print("Devolución registrada.")
    except Exception as exc:
        print(f"Error: {exc}")


def registrar_pago(biblioteca):
    usuario_id = input("Identificación del usuario: ").strip()
    monto = leer_float("Monto del pago: ")
    try:
        biblioteca.registrar_pago(usuario_id, monto)
        print("Pago registrado.")
    except Exception as exc:
        print(f"Error: {exc}")


def eliminar_libro(biblioteca):
    codigo = input("Código de barras del libro: ").strip()
    nombre = input("Nombre del libro: ").strip()
    try:
        biblioteca.eliminar_libro(codigo, nombre)
        print("Libro eliminado correctamente.")
    except Exception as exc:
        print(f"Error: {exc}")


def eliminar_usuario(biblioteca):
    nombre = input("Nombre del usuario: ").strip()
    identificacion = input("Número de identificación: ").strip()
    try:
        biblioteca.eliminar_usuario(nombre, identificacion)
        print("Usuario eliminado correctamente.")
    except Exception as exc:
        print(f"Error: {exc}")


def generar_enlace_cli(biblioteca):
    codigo = input("Código de barras del libro digital: ").strip()
    dias = None
    while dias is None:
        try:
            dias = int(input("Duración en días del acceso (por defecto 7): ") or "7")
        except ValueError:
            print("Ingresa un número válido para días.")
    try:
        enlace = biblioteca.generar_enlace_acceso(codigo, duracion_dias=dias)
        libro = biblioteca.libros.get(codigo)
        fecha = getattr(libro, "fecha_vencimiento_acceso", None)
        fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S") if fecha else "(sin fecha)"
        print(f"Enlace generado: {enlace}")
        print(f"Expira el: {fecha_str}")
    except Exception as exc:
        print(f"Error: {exc}")





def generar_reporte(biblioteca):
    biblioteca.generar_reporte_csv()
    print("Reporte generado en data/reporte_prestamos.csv")


def main():
    biblioteca = Biblioteca()
    while True:
        imprimir_menu(
            "Sistema de biblioteca escolar",
            {
                1: "Registrar estudiante",
                2: "Registrar profesor",
                3: "Registrar libro físico",
                4: "Registrar libro digital",
                5: "Listar libros",
                6: "Listar usuarios",
                7: "Prestar libro",
                8: "Devolver libro",
                9: "Registrar pago",
                10: "Generar reporte",
                11: "Eliminar libro",
                12: "Eliminar usuario",
                13: "Generar enlace libro digital",
                0: "Salir",
            },
        )
        opcion = leer_entero("Selecciona una opción: ")

        if opcion == 1:
            registrar_estudiante(biblioteca)
        elif opcion == 2:
            registrar_profesor(biblioteca)
        elif opcion == 3:
            registrar_libro_fisico(biblioteca)
        elif opcion == 4:
            registrar_libro_digital(biblioteca)
        elif opcion == 5:
            listar_libros(biblioteca)
        elif opcion == 6:
            listar_usuarios(biblioteca)
        elif opcion == 7:
            prestar_libro(biblioteca)
        elif opcion == 8:
            devolver_libro(biblioteca)
        elif opcion == 9:
            registrar_pago(biblioteca)
        elif opcion == 10:
            generar_reporte(biblioteca)
        elif opcion == 11:
            eliminar_libro(biblioteca)
        elif opcion == 12:
            eliminar_usuario(biblioteca)
        elif opcion == 13:
            generar_enlace_cli(biblioteca)
        elif opcion == 0:
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    main()
