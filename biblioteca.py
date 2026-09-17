from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass, field
from uuid import uuid4
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


def _date_to_str(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None


def _str_to_date(value: Optional[str]) -> Optional[datetime]:
    if value is None or value == "":
        return None
    return datetime.fromisoformat(value)


class BibliotecaError(Exception):
    pass


class UsuarioNoEncontrado(ValueError, BibliotecaError):
    pass


class LibroNoEncontrado(ValueError, BibliotecaError):
    pass


class LibroNoDisponible(ValueError, BibliotecaError):
    pass


class UsuarioVetado(ValueError, BibliotecaError):
    pass


class UsuarioConDeuda(ValueError, BibliotecaError):
    pass


class PrestamoInvalido(ValueError, BibliotecaError):
    pass


@dataclass
class Libro:
    titulo: str
    autor: str
    isbn: str
    codigo_barras: str
    precio: float
    disponible: bool = True
    tipo: str = "fisico"

    def __post_init__(self):
        if not self.titulo or not self.autor:
            raise ValueError("Título y autor son obligatorios")
        if not self.isbn or not self.codigo_barras:
            raise ValueError("ISBN y código de barras son obligatorios")
        if self.precio < 0:
            raise ValueError("El precio no puede ser negativo")

    def abrir(self):
        if self.tipo == "digital":
            return f"Abriendo libro digital: {self.titulo} ({self.autor}) en modo lectura"
        return f"El libro físico {self.titulo} se usa en la biblioteca"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "titulo": self.titulo,
            "autor": self.autor,
            "isbn": self.isbn,
            "codigo_barras": self.codigo_barras,
            "precio": self.precio,
            "disponible": self.disponible,
            "tipo": self.tipo,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Libro":
        tipo = data.get("tipo", "fisico")
        if tipo == "digital":
            # construct LibroDigital with digital-specific fields
            return LibroDigital(
                titulo=data["titulo"],
                autor=data["autor"],
                isbn=data["isbn"],
                codigo_barras=data["codigo_barras"],
                precio=float(data.get("precio", 0)),
                disponible=data.get("disponible", True),
                acceso_enlace=data.get("acceso_enlace"),
                fecha_vencimiento_acceso=_str_to_date(data.get("fecha_vencimiento_acceso")),
            )

        return cls(
            titulo=data["titulo"],
            autor=data["autor"],
            isbn=data["isbn"],
            codigo_barras=data["codigo_barras"],
            precio=float(data.get("precio", 0)),
            disponible=data.get("disponible", True),
            tipo=tipo,
        )


@dataclass
class LibroDigital(Libro):
    tipo: str = "digital"
    acceso_enlace: Optional[str] = None
    fecha_vencimiento_acceso: Optional[datetime] = None

    def abrir(self):
        return f"Abriendo libro digital para lectura: {self.titulo} ({self.autor})"

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "acceso_enlace": self.acceso_enlace,
            "fecha_vencimiento_acceso": _date_to_str(self.fecha_vencimiento_acceso),
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LibroDigital":
        return cls(
            titulo=data["titulo"],
            autor=data["autor"],
            isbn=data["isbn"],
            codigo_barras=data["codigo_barras"],
            precio=float(data.get("precio", 0)),
            disponible=data.get("disponible", True),
            acceso_enlace=data.get("acceso_enlace"),
            fecha_vencimiento_acceso=_str_to_date(data.get("fecha_vencimiento_acceso")),
        )


@dataclass
class Usuario:
    nombre: str
    identificacion: str
    edad: int
    tipo: str = "usuario"
    vetado: bool = False
    deuda: float = 0.0
    _prestamos_activos: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.identificacion or not self.nombre:
            raise ValueError("Identificación y nombre son obligatorios")
        self.tipo = (self.tipo or "usuario").lower()
        if self.tipo not in {"usuario", "profesor", "estudiante"}:
            raise ValueError("Tipo debe ser usuario, profesor o estudiante")
        if self.edad <= 0:
            raise ValueError("Edad debe ser positiva")

    @property
    def prestamos_activos(self) -> List[str]:
        return list(self._prestamos_activos)

    @prestamos_activos.setter
    def prestamos_activos(self, value: List[str]):
        self._prestamos_activos = list(value)

    def prestar_libro(self, codigo_barras: str):
        if codigo_barras not in self._prestamos_activos:
            self._prestamos_activos.append(codigo_barras)

    def devolver_libro(self, codigo_barras: str):
        if codigo_barras in self._prestamos_activos:
            self._prestamos_activos.remove(codigo_barras)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "identificacion": self.identificacion,
            "edad": self.edad,
            "tipo": self.tipo,
            "vetado": self.vetado,
            "deuda": self.deuda,
            "prestamos_activos": self._prestamos_activos,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Usuario":
        tipo = (data.get("tipo") or "usuario").lower()
        if tipo == "estudiante":
            return Estudiante.from_dict(data)
        if tipo == "profesor":
            return Profesor.from_dict(data)
        return cls(
            nombre=data["nombre"],
            identificacion=data["identificacion"],
            edad=int(data.get("edad", 0)),
            tipo=tipo,
            vetado=data.get("vetado", False),
            deuda=float(data.get("deuda", 0.0)),
            _prestamos_activos=data.get("prestamos_activos", []),
        )


@dataclass
class Estudiante(Usuario):
    grado: str = ""
    seccion: str = ""

    def __init__(self, nombre: str, identificacion: str, edad: int, grado: str, seccion: str,
                 vetado: bool = False, deuda: float = 0.0, prestamos_activos: Optional[List[str]] = None):
        super().__init__(
            nombre=nombre,
            identificacion=identificacion,
            edad=edad,
            tipo="estudiante",
            vetado=vetado,
            deuda=deuda,
            _prestamos_activos=prestamos_activos or [],
        )
        self.grado = grado
        self.seccion = seccion
        if not (6 <= self.edad <= 14):
            raise ValueError("Los estudiantes deben tener entre 6 y 14 años")
        if not self.grado or not self.seccion:
            raise ValueError("Grado y sección son obligatorios para los estudiantes")

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "grado": self.grado,
            "seccion": self.seccion,
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Estudiante":
        legacy_grado = data.get("grado", "")
        legacy_seccion = data.get("seccion", "")
        if isinstance(legacy_grado, str) and legacy_grado and not legacy_seccion and any(ch.isalpha() for ch in legacy_grado):
            digits = "".join(ch for ch in legacy_grado if ch.isdigit())
            letters = "".join(ch for ch in legacy_grado if ch.isalpha())
            legacy_grado = digits or legacy_grado
            legacy_seccion = letters or legacy_seccion
        return cls(
            nombre=data["nombre"],
            identificacion=data["identificacion"],
            edad=int(data.get("edad", 0)),
            grado=str(legacy_grado),
            seccion=str(legacy_seccion),
            vetado=data.get("vetado", False),
            deuda=float(data.get("deuda", 0.0)),
            prestamos_activos=data.get("prestamos_activos", []),
        )


@dataclass
class Profesor(Usuario):
    grados: List[str] = field(default_factory=list)
    secciones_asignadas: List[str] = field(default_factory=list)

    def __init__(self, nombre: str, identificacion: str, edad: int, grados: Optional[List[str]] = None,
                 secciones_asignadas: Optional[List[str]] = None, vetado: bool = False,
                 deuda: float = 0.0, prestamos_activos: Optional[List[str]] = None):
        super().__init__(
            nombre=nombre,
            identificacion=identificacion,
            edad=edad,
            tipo="profesor",
            vetado=vetado,
            deuda=deuda,
            _prestamos_activos=prestamos_activos or [],
        )
        self.grados = list(grados or [])
        self.secciones_asignadas = list(secciones_asignadas or [])

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "grados": self.grados,
            "secciones_asignadas": self.secciones_asignadas,
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Profesor":
        legacy_grados = data.get("grados") or []
        if "grado" in data and not legacy_grados:
            legacy = data["grado"]
            if isinstance(legacy, str):
                legacy_grados = [legacy]
            elif isinstance(legacy, list):
                legacy_grados = legacy

        legacy_secciones = data.get("secciones_asignadas") or data.get("seccion") or []
        if isinstance(legacy_secciones, str):
            legacy_secciones = [legacy_secciones]

        return cls(
            nombre=data["nombre"],
            identificacion=data["identificacion"],
            edad=int(data.get("edad", 0)),
            grados=list(legacy_grados),
            secciones_asignadas=list(legacy_secciones),
            vetado=data.get("vetado", False),
            deuda=float(data.get("deuda", 0.0)),
            prestamos_activos=data.get("prestamos_activos", []),
        )


@dataclass
class Prestamo:
    usuario_id: str
    libro_codigo: str
    fecha_inicio: datetime
    fecha_vencimiento: datetime
    estado: str = "activo"
    prorroga_aplicada: bool = False
    fecha_devolucion: Optional[datetime] = None
    condicion: Optional[str] = None
    deuda_generada: float = 0.0
    pagado: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "usuario_id": self.usuario_id,
            "libro_codigo": self.libro_codigo,
            "fecha_inicio": _date_to_str(self.fecha_inicio),
            "fecha_vencimiento": _date_to_str(self.fecha_vencimiento),
            "estado": self.estado,
            "prorroga_aplicada": self.prorroga_aplicada,
            "fecha_devolucion": _date_to_str(self.fecha_devolucion),
            "condicion": self.condicion,
            "deuda_generada": self.deuda_generada,
            "pagado": self.pagado,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Prestamo":
        return cls(
            usuario_id=data["usuario_id"],
            libro_codigo=data["libro_codigo"],
            fecha_inicio=_str_to_date(data["fecha_inicio"]),
            fecha_vencimiento=_str_to_date(data["fecha_vencimiento"]),
            estado=data.get("estado", "activo"),
            prorroga_aplicada=data.get("prorroga_aplicada", False),
            fecha_devolucion=_str_to_date(data.get("fecha_devolucion")),
            condicion=data.get("condicion"),
            deuda_generada=float(data.get("deuda_generada", 0.0)),
            pagado=float(data.get("pagado", 0.0)),
        )


class Biblioteca:
    def __init__(self, ruta_base: str = None, ahora: Optional[callable] = None):
        self.ruta_base = ruta_base or os.path.join(os.getcwd(), "data")
        self.ahora = ahora or (lambda: datetime.now())
        self.libros: Dict[str, Libro] = {}
        self.usuarios: Dict[str, Usuario] = {}
        self.prestamos: List[Prestamo] = []
        os.makedirs(self.ruta_base, exist_ok=True)
        self._cargar_datos()

    def _ruta_json(self, nombre: str) -> str:
        return os.path.join(self.ruta_base, nombre)

    def _cargar_datos(self):
        for nombre, tipo in [("libros.json", self.libros), ("usuarios.json", self.usuarios)]:
            ruta = self._ruta_json(nombre)
            if not os.path.exists(ruta):
                self._guardar_json(ruta, [])
                continue
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            if tipo is self.libros:
                self.libros = {item["codigo_barras"]: Libro.from_dict(item) for item in data}
            else:
                self.usuarios = {item["identificacion"]: Usuario.from_dict(item) for item in data}

        ruta_prestamos = self._ruta_json("prestamos.json")
        if not os.path.exists(ruta_prestamos):
            self._guardar_json(ruta_prestamos, [])
        else:
            with open(ruta_prestamos, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.prestamos = [Prestamo.from_dict(item) for item in datos]

    def _guardar_json(self, ruta: str, datos: Any):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def _guardar_todos(self):
        self._guardar_json(self._ruta_json("libros.json"), [libro.to_dict() for libro in self.libros.values()])
        self._guardar_json(self._ruta_json("usuarios.json"), [usuario.to_dict() for usuario in self.usuarios.values()])
        self._guardar_json(self._ruta_json("prestamos.json"), [prestamo.to_dict() for prestamo in self.prestamos])

    def registrar_libro(self, libro: Libro):
        libro.codigo_barras = libro.codigo_barras.strip()
        if not libro.codigo_barras:
            raise ValueError("El código de barras es obligatorio")
        if libro.codigo_barras in self.libros:
            raise ValueError("Ya existe un libro con ese código de barras")
        self.libros[libro.codigo_barras] = libro
        self._guardar_todos()

    def generar_enlace_acceso(self, codigo_barras: str, duracion_dias: int = 7) -> str:
        """Genera un enlace único para un libro digital con una fecha de expiración."""
        codigo_barras = codigo_barras.strip()
        libro = self.libros.get(codigo_barras)
        if libro is None:
            raise LibroNoEncontrado(f"Libro {codigo_barras} no existe")
        if libro.tipo != "digital":
            raise ValueError("Solo se pueden generar enlaces para libros digitales")

        # libro should be LibroDigital (from_dict creates LibroDigital for tipo digital)
        ahora = self.ahora()
        enlace = f"https://biblioteca.local/access/{uuid4().hex}"
        # set attributes; works if instance is LibroDigital
        setattr(libro, "acceso_enlace", enlace)
        setattr(libro, "fecha_vencimiento_acceso", ahora + timedelta(days=duracion_dias))
        self._guardar_todos()
        return enlace

    def acceder_libro_digital(self, codigo_barras: str, enlace: str) -> str:
        """Valida el enlace y la fecha de expiración, devuelve el contenido si está permitido."""
        codigo_barras = codigo_barras.strip()
        libro = self.libros.get(codigo_barras)
        if libro is None:
            raise LibroNoEncontrado(f"Libro {codigo_barras} no existe")
        if libro.tipo != "digital":
            raise ValueError("No es un libro digital")

        acceso_enlace = getattr(libro, "acceso_enlace", None)
        fecha_venc = getattr(libro, "fecha_vencimiento_acceso", None)
        if acceso_enlace is None or acceso_enlace != enlace:
            raise ValueError("Enlace inválido")
        ahora = self.ahora()
        if fecha_venc is None or ahora > fecha_venc:
            raise ValueError("Acceso expirado")
        return libro.abrir()

    def registrar_usuario(self, usuario: Usuario):
        usuario.identificacion = usuario.identificacion.strip()
        if not usuario.identificacion:
            raise ValueError("La identificación es obligatoria")
        if usuario.identificacion in self.usuarios:
            raise ValueError("Ya existe un usuario con esa identificación")
        self.usuarios[usuario.identificacion] = usuario
        self._guardar_todos()

    def eliminar_libro(self, codigo_barras: str, nombre: str):
        codigo_barras = codigo_barras.strip()
        nombre = nombre.strip()
        libro = self.libros.get(codigo_barras)
        if libro is None or libro.titulo.casefold() != nombre.casefold():
            raise LibroNoEncontrado("No existe un libro con ese código de barras y nombre")
        if any(
            prestamo.libro_codigo == codigo_barras and prestamo.estado in {"activo", "vencido"}
            for prestamo in self.prestamos
        ):
            raise LibroNoDisponible("No se puede eliminar un libro con un préstamo activo")
        del self.libros[codigo_barras]
        self._guardar_todos()

    def eliminar_usuario(self, nombre: str, identificacion: str):
        nombre = nombre.strip()
        identificacion = identificacion.strip()
        usuario = self.usuarios.get(identificacion)
        if usuario is None or usuario.nombre.casefold() != nombre.casefold():
            raise UsuarioNoEncontrado("No existe un usuario con ese nombre y número de identificación")
        if usuario.deuda > 0:
            raise UsuarioConDeuda("No se puede eliminar un usuario con deuda pendiente")
        if usuario.prestamos_activos or any(
            prestamo.usuario_id == identificacion and prestamo.estado in {"activo", "vencido"}
            for prestamo in self.prestamos
        ):
            raise ValueError("No se puede eliminar un usuario con préstamos activos")
        del self.usuarios[identificacion]
        self._guardar_todos()

    def prestar_libro(self, usuario_id: str, codigo_barras: str):
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(f"Usuario {usuario_id} no existe")
        if usuario.vetado:
            raise UsuarioVetado("Usuario vetado")
        if usuario.deuda > 0:
            raise UsuarioConDeuda("Usuario con deuda pendiente")

        libro = self.libros.get(codigo_barras)
        if libro is None:
            raise LibroNoEncontrado(f"Libro {codigo_barras} no existe")
        if libro.tipo == "digital":
            raise ValueError("No se prestan libros digitales")
        if not libro.disponible:
            raise LibroNoDisponible("Libro no disponible")
        if len(usuario.prestamos_activos) >= 5:
            raise ValueError("El usuario ya tiene 5 libros físicos activos")

        ahora = self.ahora()
        prestamo = Prestamo(
            usuario_id=usuario_id,
            libro_codigo=codigo_barras,
            fecha_inicio=ahora,
            fecha_vencimiento=ahora + timedelta(days=7),
        )
        self.prestamos.append(prestamo)
        usuario.prestar_libro(codigo_barras)
        libro.disponible = False
        self._guardar_todos()

    def devolver_libro(self, codigo_barras: str, condicion: str = "bueno"):
        libro = self.libros.get(codigo_barras)
        if libro is None:
            raise LibroNoEncontrado(f"Libro {codigo_barras} no existe")
        prestamo = next(
            (
                p
                for p in reversed(self.prestamos)
                if p.libro_codigo == codigo_barras and p.estado in {"activo", "vencido"}
            ),
            None,
        )
        if prestamo is None:
            raise PrestamoInvalido("No hay préstamo pendiente para ese libro")

        usuario = self.usuarios.get(prestamo.usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(f"Usuario {prestamo.usuario_id} no existe")

        prestamo.fecha_devolucion = self.ahora()
        prestamo.condicion = condicion
        prestamo.estado = "devuelto"
        usuario.devolver_libro(codigo_barras)
        if condicion == "daniado":
            libro.disponible = False
            prestamo.deuda_generada = libro.precio
            usuario.deuda += libro.precio
            usuario.vetado = True
        else:
            libro.disponible = True
        self._guardar_todos()

    def registrar_pago(self, usuario_id: str, monto: float):
        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(f"Usuario {usuario_id} no existe")
        if monto <= 0:
            raise ValueError("El monto debe ser positivo")

        usuario.deuda = max(0.0, usuario.deuda - monto)
        if usuario.deuda == 0.0:
            usuario.vetado = False

        for prestamo in self.prestamos:
            if prestamo.usuario_id == usuario_id and prestamo.estado == "devuelto" and prestamo.condicion == "daniado":
                libro = self.libros.get(prestamo.libro_codigo)
                if libro is not None and not libro.disponible and prestamo.deuda_generada > 0 and usuario.deuda == 0:
                    libro.disponible = True
                    prestamo.condicion = "daniado_pagado"

        self._guardar_todos()

    def _marcar_libro_disponible(self, codigo_barras: str):
        libro = self.libros.get(codigo_barras)
        if libro is None:
            raise LibroNoEncontrado(f"Libro {codigo_barras} no existe")
        libro.disponible = True

    def actualizar_prestamos(self, fecha: Optional[datetime] = None):
        fecha_actual = fecha or self.ahora()
        for prestamo in self.prestamos:
            if prestamo.estado != "activo":
                continue
            usuario = self.usuarios.get(prestamo.usuario_id)
            libro = self.libros.get(prestamo.libro_codigo)
            if usuario is None or libro is None:
                continue

            if fecha_actual > prestamo.fecha_vencimiento and not prestamo.prorroga_aplicada:
                prestamo.prorroga_aplicada = True
                prestamo.fecha_vencimiento += timedelta(days=2)

            if fecha_actual > prestamo.fecha_vencimiento and prestamo.prorroga_aplicada:
                if prestamo.deuda_generada == 0:
                    prestamo.deuda_generada = libro.precio
                    usuario.deuda += libro.precio
                    usuario.vetado = True
                prestamo.estado = "vencido"
                libro.disponible = False

        self._guardar_todos()

    def generar_reporte_csv(self):
        ruta = self._ruta_json("reporte_prestamos.csv")
        rows = [
            [
                "usuario_id",
                "libro_codigo",
                "titulo",
                "fecha_inicio",
                "fecha_vencimiento",
                "estado",
                "prorroga_aplicada",
                "condicion",
                "deuda_generada",
                "pagado",
            ]
        ]

        for prestamo in self.prestamos:
            libro = self.libros.get(prestamo.libro_codigo)
            rows.append([
                prestamo.usuario_id,
                prestamo.libro_codigo,
                libro.titulo if libro else "",
                _date_to_str(prestamo.fecha_inicio),
                _date_to_str(prestamo.fecha_vencimiento),
                prestamo.estado,
                prestamo.prorroga_aplicada,
                prestamo.condicion or "",
                prestamo.deuda_generada,
                prestamo.pagado,
            ])

        with open(ruta, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        output = []
        for row in rows:
            output.append(",".join(str(value) for value in row))
        return "\n".join(output)

    def cerrar(self):
        self._guardar_todos()
