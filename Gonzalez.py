"""
Universidad Nacional Abierta y a Distancia (UNAD)
Escuela de Ciencias Básicas, Tecnología e Ingeniería (ECBTI)
Programa: Ingeniería de Sistemas
Curso: Programación (Código: 213023) - Fase 4: Componente Práctico
Proyecto: Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Autor: Ronal Stiben Gonzalez Medina
Descripción:
    Aplicación orientada a objetos sin base de datos que gestiona clientes,
    servicios y reservas en memoria mediante listas y diccionarios, aplicando
    abstracción, herencia, polimorfismo, encapsulación, sobrecarga de métodos
    y manejo avanzado de excepciones con registro en archivo de logs.
"""

from abc import ABC, abstractmethod
from functools import singledispatchmethod
import logging
import re
from typing import Dict, List


# ==============================================================================
# 1. CONFIGURACIÓN DEL ARCHIVO DE LOGS (ÚNICA PERSISTENCIA PERMITIDA)
# ==============================================================================
def configurar_logger(nombre_archivo: str = "software_fj.log") -> logging.Logger:
    """Configura el registro de eventos y errores en archivo .log y consola."""
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    # Evita duplicar manejadores si la función es llamada más de una vez
    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Manejador para guardar todos los eventos y errores en archivo de texto
        archivo_handler = logging.FileHandler(
            nombre_archivo, mode="a", encoding="utf-8"
        )
        archivo_handler.setLevel(logging.INFO)
        archivo_handler.setFormatter(formato)

        # Manejador para visualizar la ejecución en la terminal de VS Code
        consola_handler = logging.StreamHandler()
        consola_handler.setLevel(logging.INFO)
        consola_handler.setFormatter(formato)

        logger.addHandler(archivo_handler)
        logger.addHandler(consola_handler)

    return logger


# ==============================================================================
# 2. EXCEPCIONES PERSONALIZADAS DEL SISTEMA
# ==============================================================================
class ErrorSistemaSoftwareFJ(Exception):
    """Excepción base para cualquier error controlado en Software FJ."""


class ValidacionDatosError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando un dato o parámetro incumple las reglas de negocio."""


class ServicioNoDisponibleError(ErrorSistemaSoftwareFJ):
    """Se lanza al intentar reservar un servicio inactivo o no disponible."""


class EstadoReservaError(ErrorSistemaSoftwareFJ):
    """Se lanza cuando se intenta una transición de estado no permitida."""


class CalculoCostoError(ErrorSistemaSoftwareFJ):
    """Se lanza ante inconsistencias o fallos en el cálculo de tarifas."""


# ==============================================================================
# 3. ARQUITECTURA ORIENTADA A OBJETOS (ABSTRACCIÓN, ENCAPSULACIÓN Y HERENCIA)
# ==============================================================================
class EntidadBase(ABC):
    """Clase abstracta que representa cualquier entidad identificable del sistema."""

    def __init__(self, id_entidad: str) -> None:
        # Valida que el identificador sea una cadena válida y no vacía
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValidacionDatosError(
                "El identificador de la entidad debe ser un texto no vacío."
            )
        self._id: str = id_entidad.strip().upper()

    @property
    def id(self) -> str:
        """Retorna el identificador único encapsulado."""
        return self._id

    @abstractmethod
    def resumen(self) -> str:
        """Método abstracto obligatorio para describir resumidamente la entidad."""


class Cliente(EntidadBase):
    """Representa un cliente de Software FJ con atributos privados y validaciones."""

    def __init__(
        self, id_cliente: str, nombre: str, correo: str, telefono: str
    ) -> None:
        super().__init__(id_cliente)
        # Se usan los setters para garantizar validación desde la instanciación
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionDatosError(
                "El nombre del cliente debe contener al menos 3 caracteres."
            )
        self._nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not isinstance(valor, str) or not re.match(patron_correo, valor.strip()):
            raise ValidacionDatosError(
                f"El correo electrónico '{valor}' no tiene un formato válido."
            )
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        # Extrae únicamente los dígitos numéricos del teléfono
        solo_digitos = re.sub(r"\D", "", str(valor))
        if len(solo_digitos) < 7 or len(solo_digitos) > 15:
            raise ValidacionDatosError(
                "El teléfono debe tener entre 7 y 15 dígitos numéricos."
            )
        self._telefono = solo_digitos

    def resumen(self) -> str:
        return f"Cliente [{self.id}] {self._nombre} | Correo: {self._correo} | Tel: {self._telefono}"


class Servicio(EntidadBase, ABC):
    """Clase abstracta base para todos los servicios ofrecidos por Software FJ."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio)
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValidacionDatosError("El nombre del servicio no puede estar vacío.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ValidacionDatosError(
                "La tarifa base del servicio debe ser un valor numérico mayor a cero."
            )

        self._nombre: str = nombre.strip()
        self._tarifa_base: float = float(tarifa_base)
        self._disponible: bool = bool(disponible)

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion_horas: int) -> None:
        """Valida las reglas específicas de duración según el tipo de servicio."""

    @abstractmethod
    def describir(self) -> str:
        """Retorna la descripción detallada y polimórfica del servicio."""

    def calcular_costo(
        self,
        duracion_horas: int,
        descuento_porcentaje: float = 0.0,
        impuesto_porcentaje: float = 0.0,
        recargo_fijo: float = 0.0,
    ) -> float:
        """
        Método sobrecargado mediante parámetros opcionales para calcular costos:
        - Variante 1: solo duración (tarifa base * horas)
        - Variante 2: duración + descuento
        - Variante 3: duración + descuento + impuesto + recargo fijo
        Incluye encadenamiento de excepciones ante fallos matemáticos o de tipo.
        """
        try:
            # Ejecuta la validación polimórfica de cada subclase
            self.validar_parametros(duracion_horas)

            if not isinstance(descuento_porcentaje, (int, float)) or not (
                0 <= descuento_porcentaje < 100
            ):
                raise ValidacionDatosError(
                    "El porcentaje de descuento debe estar entre 0 y 99.9."
                )
            if not isinstance(impuesto_porcentaje, (int, float)) or impuesto_porcentaje < 0:
                raise ValidacionDatosError(
                    "El porcentaje de impuesto no puede ser negativo."
                )
            if not isinstance(recargo_fijo, (int, float)) or recargo_fijo < 0:
                raise ValidacionDatosError("El recargo fijo no puede ser negativo.")

            subtotal = self._tarifa_base * duracion_horas
            valor_con_descuento = subtotal * (1.0 - (descuento_porcentaje / 100.0))
            valor_con_impuesto = valor_con_descuento * (
                1.0 + (impuesto_porcentaje / 100.0)
            )
            total = valor_con_impuesto + recargo_fijo

            if total <= 0:
                raise CalculoCostoError(
                    "Inconsistencia financiera: el costo total debe ser mayor a cero."
                )

            return round(total, 2)

        except ErrorSistemaSoftwareFJ:
            # Propaga directamente nuestras excepciones de negocio ya clasificadas
            raise
        except Exception as causa:
            # Encadenamiento explícito de excepciones (raise ... from ...)
            raise CalculoCostoError(
                f"Fallo inesperado calculando el costo del servicio '{self._nombre}'."
            ) from causa

    def resumen(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return (
            f"Servicio [{self.id}] {self._nombre} | "
            f"Tarifa: ${self._tarifa_base:,.2f}/h | Estado: {estado}"
        )


class ReservaSala(Servicio):
    """Servicio especializado 1: Reserva de salas físicas o virtuales."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        capacidad_personas: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise ValidacionDatosError(
                "La capacidad de la sala debe ser un número entero positivo."
            )
        self._capacidad_personas = capacidad_personas

    def validar_parametros(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or not (1 <= duracion_horas <= 12):
            raise ValidacionDatosError(
                "Las salas solo pueden reservarse entre 1 y 12 horas continuas."
            )

    def describir(self) -> str:
        return (
            f"Reserva de Sala '{self._nombre}' "
            f"(Capacidad máxima: {self._capacidad_personas} personas)."
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado 2: Alquiler de hardware y equipos de cómputo."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        especificacion_equipo: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(especificacion_equipo, str) or not especificacion_equipo.strip():
            raise ValidacionDatosError(
                "La especificación del equipo es obligatoria."
            )
        self._especificacion_equipo = especificacion_equipo.strip()

    def validar_parametros(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or not (2 <= duracion_horas <= 72):
            raise ValidacionDatosError(
                "El alquiler de equipos requiere entre 2 y 72 horas."
            )

    def describir(self) -> str:
        return (
            f"Alquiler de Equipo '{self._nombre}' "
            f"(Ficha técnica: {self._especificacion_equipo})."
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado 3: Consultoría y asesoría en ingeniería de software."""

    def __init__(
        self,
        id_servicio: str,
        nombre: str,
        tarifa_base: float,
        area_especialidad: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(area_especialidad, str) or not area_especialidad.strip():
            raise ValidacionDatosError(
                "El área de especialidad de la asesoría es obligatoria."
            )
        self._area_especialidad = area_especialidad.strip()

    def validar_parametros(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or not (1 <= duracion_horas <= 8):
            raise ValidacionDatosError(
                "Las asesorías especializadas tienen una duración válida de 1 a 8 horas."
            )

    def describir(self) -> str:
        return (
            f"Asesoría Especializada '{self._nombre}' "
            f"(Área: {self._area_especialidad})."
        )


class Reserva(EntidadBase):
    """Integra Cliente, Servicio, duración y estado con control transaccional."""

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        descuento: float = 0.0,
        impuesto: float = 0.0,
        recargo: float = 0.0,
    ) -> None:
        super().__init__(id_reserva)

        if not isinstance(cliente, Cliente):
            raise ValidacionDatosError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ValidacionDatosError("La reserva requiere un objeto Servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' [{servicio.id}] no se encuentra disponible."
            )

        self._cliente: Cliente = cliente
        self._servicio: Servicio = servicio
        self._duracion_horas: int = duracion_horas
        self._estado: str = "PENDIENTE"

        # Calcula el costo aplicando las reglas del servicio y posibles recargos/descuentos
        self._costo_total: float = servicio.calcular_costo(
            duracion_horas=duracion_horas,
            descuento_porcentaje=descuento,
            impuesto_porcentaje=impuesto,
            recargo_fijo=recargo,
        )

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def confirmar(self) -> None:
        """Cambia el estado de PENDIENTE a CONFIRMADA validando reglas de negocio."""
        if self._estado == "CANCELADA":
            raise EstadoReservaError(
                f"Operación no permitida: la reserva [{self.id}] ya fue cancelada."
            )
        if self._estado == "CONFIRMADA":
            raise EstadoReservaError(
                f"Operación redundante: la reserva [{self.id}] ya está confirmada."
            )
        self._estado = "CONFIRMADA"

    def cancelar(self) -> None:
        """Cancela la reserva siempre que no haya sido cancelada anteriormente."""
        if self._estado == "CANCELADA":
            raise EstadoReservaError(
                f"Operación no permitida: la reserva [{self.id}] ya estaba cancelada."
            )
        self._estado = "CANCELADA"

    def resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} ({self._duracion_horas}h) | "
            f"Total: ${self._costo_total:,.2f} | Estado: {self._estado}"
        )


# ==============================================================================
# 4. GESTOR INTEGRAL EN MEMORIA (LISTAS Y SOBRECARGA POR TIPO DE DATO)
# ==============================================================================
class SistemaGestionSoftwareFJ:
    """Administra clientes, servicios y reservas en memoria sin base de datos."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._clientes: List[Cliente] = []
        self._servicios: List[Servicio] = []
        self._reservas: List[Reserva] = []
        self._mapa_clientes: Dict[str, Cliente] = {}
        self._mapa_servicios: Dict[str, Servicio] = {}

    def registrar_cliente(self, cliente: Cliente) -> str:
        if cliente.id in self._mapa_clientes:
            raise ValidacionDatosError(
                f"El cliente con ID '{cliente.id}' ya se encuentra registrado."
            )
        self._clientes.append(cliente)
        self._mapa_clientes[cliente.id] = cliente
        self._logger.info(f"REGISTRO CLIENTE EXITOSO -> {cliente.resumen()}")
        return cliente.resumen()

    def registrar_servicio(self, servicio: Servicio) -> str:
        if servicio.id in self._mapa_servicios:
            raise ValidacionDatosError(
                f"El servicio con ID '{servicio.id}' ya se encuentra registrado."
            )
        self._servicios.append(servicio)
        self._mapa_servicios[servicio.id] = servicio
        self._logger.info(f"REGISTRO SERVICIO EXITOSO -> {servicio.resumen()}")
        return servicio.resumen()

    def procesar_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion_horas: int,
        descuento: float = 0.0,
        impuesto: float = 0.0,
        recargo: float = 0.0,
        confirmar_automaticamente: bool = False,
    ) -> Reserva:
        """Crea y opcionalmente confirma una reserva encadenando errores de búsqueda."""
        try:
            cliente = self._mapa_clientes[id_cliente.strip().upper()]
        except KeyError as causa:
            raise ValidacionDatosError(
                f"No existe ningún cliente registrado con el ID '{id_cliente}'."
            ) from causa

        try:
            servicio = self._mapa_servicios[id_servicio.strip().upper()]
        except KeyError as causa:
            raise ValidacionDatosError(
                f"No existe ningún servicio registrado con el ID '{id_servicio}'."
            ) from causa

        reserva = Reserva(
            id_reserva=id_reserva,
            cliente=cliente,
            servicio=servicio,
            duracion_horas=duracion_horas,
            descuento=descuento,
            impuesto=impuesto,
            recargo=recargo,
        )

        if confirmar_automaticamente:
            reserva.confirmar()

        self._reservas.append(reserva)
        self._logger.info(f"RESERVA PROCESADA -> {reserva.resumen()}")
        return reserva

    @singledispatchmethod
    def obtener_detalle_entidad(self, entidad) -> str:
        """Método sobrecargado por tipo de argumento para inspeccionar entidades."""
        raise ValidacionDatosError(
            f"Tipo de entidad no soportado para consulta: {type(entidad).__name__}"
        )

    @obtener_detalle_entidad.register
    def _(self, entidad: Cliente) -> str:
        return f"[FICHA CLIENTE] {entidad.resumen()}"

    @obtener_detalle_entidad.register
    def _(self, entidad: Servicio) -> str:
        return f"[FICHA SERVICIO] {entidad.resumen()} -> {entidad.describir()}"

    @obtener_detalle_entidad.register
    def _(self, entidad: Reserva) -> str:
        return f"[FICHA RESERVA] {entidad.resumen()}"

    def generar_reporte_memoria(self) -> None:
        """Muestra el estado final de todas las listas internas tras la simulación."""
        print("\n" + "=" * 75)
        print("REPORTE FINAL EN MEMORIA - SOFTWARE FJ (SIN BASE DE DATOS)")
        print("=" * 75)
        print(f"Total Clientes activos : {len(self._clientes)}")
        for c in self._clientes:
            print("  •", self.obtener_detalle_entidad(c))

        print(f"\nTotal Servicios activos: {len(self._servicios)}")
        for s in self._servicios:
            print("  •", self.obtener_detalle_entidad(s))

        print(f"\nTotal Reservas creadas : {len(self._reservas)}")
        for r in self._reservas:
            print("  •", self.obtener_detalle_entidad(r))
        print("=" * 75)


# ==============================================================================
# 5. SIMULACIÓN DE OPERACIONES (MÍNIMO 10 ESCENARIOS VÁLIDOS E INVÁLIDOS)
# ==============================================================================
def ejecutar_operacion_segura(
    numero: int, titulo: str, funcion_operacion, logger: logging.Logger
) -> None:
    """
    Ejecuta cada caso de prueba empleando try / except / else / finally
    para asegurar que la aplicación continúe funcionando ante cualquier error.
    """
    print(f"\n>>> OPERACIÓN {numero:02d}: {titulo}")
    try:
        resultado = funcion_operacion()
    except ErrorSistemaSoftwareFJ as err_negocio:
        # Registra el error de negocio y su causa encadenada si existe
        detalle_causa = (
            f" | Causa raíz: {type(err_negocio.__cause__).__name__}: {err_negocio.__cause__}"
            if err_negocio.__cause__
            else ""
        )
        logger.error(
            f"[OP-{numero:02d}] {titulo} -> {type(err_negocio).__name__}: {err_negocio}{detalle_causa}"
        )
        print(f"    [ERROR CONTROLADO] {err_negocio}")
    except Exception as err_inesperado:
        logger.exception(f"[OP-{numero:02d}] Error crítico inesperado: {err_inesperado}")
        print(f"    [ERROR CRÍTICO REGISTRADO] {err_inesperado}")
    else:
        logger.info(f"[OP-{numero:02d}] Completada sin errores.")
        if resultado is not None:
            print(f"    [ÉXITO] {resultado}")
    finally:
        # Garantiza trazabilidad del ciclo de ejecución en cada operación
        print(f"    [FIN OP-{numero:02d}] Sistema estable y listo para continuar.")


def main() -> None:
    logger = configurar_logger("software_fj.log")
    logger.info("=== INICIO DE EJECUCIÓN DEL SISTEMA SOFTWARE FJ ===")
    sistema = SistemaGestionSoftwareFJ(logger)

    # OP 01: Registro de cliente válido 1
    ejecutar_operacion_segura(
        1,
        "Registro de cliente válido (Ronal Gonzalez)",
        lambda: sistema.registrar_cliente(
            Cliente("CLI-001", "Ronal Stiben Gonzalez", "ronal.gonzalez@unad.edu.co", "3104567890")
        ),
        logger,
    )

    # OP 02: Registro de cliente inválido (correo sin dominio válido)
    ejecutar_operacion_segura(
        2,
        "Registro de cliente inválido (correo electrónico mal formado)",
        lambda: sistema.registrar_cliente(
            Cliente("CLI-002", "Juan Pérez", "juan.perez_correo_invalido", "3001234567")
        ),
        logger,
    )

    # OP 03: Registro de cliente inválido (teléfono muy corto)
    ejecutar_operacion_segura(
        3,
        "Registro de cliente inválido (teléfono con menos de 7 dígitos)",
        lambda: sistema.registrar_cliente(
            Cliente("CLI-003", "María López", "maria.lopez@empresa.com", "123")
        ),
        logger,
    )

    # OP 04: Registro de cliente válido 2
    ejecutar_operacion_segura(
        4,
        "Registro de segundo cliente válido (Camila Torres)",
        lambda: sistema.registrar_cliente(
            Cliente("CLI-004", "Camila Torres", "camila.torres@tech.co", "3209876543")
        ),
        logger,
    )

    # OP 05: Creación correcta de servicio 1 (Reserva de Sala)
    ejecutar_operacion_segura(
        5,
        "Creación válida de servicio: Reserva de Sala",
        lambda: sistema.registrar_servicio(
            ReservaSala("SRV-001", "Sala Innovación FJ", 95000.0, capacidad_personas=20)
        ),
        logger,
    )

    # OP 06: Creación correcta de servicio 2 (Alquiler de Equipo)
    ejecutar_operacion_segura(
        6,
        "Creación válida de servicio: Alquiler de Equipo",
        lambda: sistema.registrar_servicio(
            AlquilerEquipo(
                "SRV-002",
                "Workstation Render Pro",
                45000.0,
                especificacion_equipo="Intel i9, 64GB RAM, RTX 4080",
            )
        ),
        logger,
    )

    # OP 07: Creación correcta de servicio 3 (Asesoría Especializada no disponible)
    ejecutar_operacion_segura(
        7,
        "Creación válida de servicio: Asesoría Especializada (No disponible)",
        lambda: sistema.registrar_servicio(
            AsesoriaEspecializada(
                "SRV-003",
                "Arquitectura Cloud & DevOps",
                150000.0,
                area_especialidad="Sistemas Distribuidos",
                disponible=False,
            )
        ),
        logger,
    )

    # OP 08: Creación incorrecta de servicio (tarifa base negativa)
    ejecutar_operacion_segura(
        8,
        "Creación inválida de servicio (tarifa negativa)",
        lambda: sistema.registrar_servicio(
            ReservaSala("SRV-999", "Sala Fantasma", -25000.0, capacidad_personas=5)
        ),
        logger,
    )

    # OP 09: Reserva exitosa con sobrecarga de cálculo (descuento + IVA + confirmación)
    def operacion_09():
        reserva = sistema.procesar_reserva(
            id_reserva="RES-001",
            id_cliente="CLI-001",
            id_servicio="SRV-001",
            duracion_horas=4,
            descuento=10.0,
            impuesto=19.0,
            confirmar_automaticamente=True,
        )
        return reserva.resumen()

    ejecutar_operacion_segura(
        9,
        "Reserva exitosa y confirmada (con descuento 10% e IVA 19%)",
        operacion_09,
        logger,
    )

    # OP 10: Reserva fallida por duración fuera del rango del servicio (1h en equipo)
    ejecutar_operacion_segura(
        10,
        "Reserva fallida por duración inválida (1 hora en Alquiler de Equipo)",
        lambda: sistema.procesar_reserva(
            id_reserva="RES-002",
            id_cliente="CLI-004",
            id_servicio="SRV-002",
            duracion_horas=1,
        ),
        logger,
    )

    # OP 11: Reserva fallida por servicio no disponible
    ejecutar_operacion_segura(
        11,
        "Reserva fallida por servicio no disponible (SRV-003)",
        lambda: sistema.procesar_reserva(
            id_reserva="RES-003",
            id_cliente="CLI-001",
            id_servicio="SRV-003",
            duracion_horas=2,
        ),
        logger,
    )

    # OP 12: Reserva exitosa, cancelación e intento inválido de re-confirmar
    def operacion_12():
        reserva = sistema.procesar_reserva(
            id_reserva="RES-004",
            id_cliente="CLI-004",
            id_servicio="SRV-002",
            duracion_horas=5,
            recargo=15000.0,
        )
        reserva.cancelar()
        logger.info(f"Reserva [{reserva.id}] cancelada correctamente antes de prueba de error.")
        # Esta línea provoca EstadoReservaError controlado
        reserva.confirmar()

    ejecutar_operacion_segura(
        12,
        "Reserva cancelada e intento no permitido de confirmarla",
        operacion_12,
        logger,
    )

    # Muestra el reporte final y confirma la generación del archivo de logs
    sistema.generar_reporte_memoria()
    logger.info("=== FIN DE EJECUCIÓN DEL SISTEMA SOFTWARE FJ ===")
    print("\nArchivo de auditoría generado correctamente: 'software_fj.log'")


if __name__ == "__main__":
    main()