from entidades import Cliente, EntidadSistema
from excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
)
from servicios import AlquilerEquipo, Servicio


class Reserva(EntidadSistema):
    """Integra un Cliente, un Servicio, la duración y el ciclo de vida de la reserva."""

    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_CONFIRMADA = "CONFIRMADA"
    ESTADO_PROCESADA = "PROCESADA"
    ESTADO_CANCELADA = "CANCELADA"

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        tasa_iva: float = 0.19,
        descuento: float = 0.0,
    ) -> None:
        super().__init__(id_reserva)

        if not isinstance(cliente, Cliente):
            raise ParametroFaltanteError("La reserva requiere un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ParametroFaltanteError("La reserva requiere un objeto Servicio válido.")

        # Valida disponibilidad y reglas específicas del servicio (polimorfismo)
        servicio.validar_parametros(duracion)

        self.__cliente = cliente
        self.__servicio = servicio
        self.__duracion = duracion
        self.__estado = self.ESTADO_PENDIENTE
        self.__tasa_iva = tasa_iva
        self.__descuento = descuento
        # Calcula el costo inicial invocando el método sobrecargado del servicio
        self.__costo_total = self.recalcular_costo(tasa_iva, descuento)

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion(self) -> int:
        return self.__duracion

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def costo_total(self) -> float:
        return self.__costo_total

    def recalcular_costo(self, tasa_iva: float = 0.19, descuento: float = 0.0) -> float:
        """Método sobrecargado (parámetros opcionales) para liquidar la reserva con impuestos o descuentos."""
        try:
            self.__tasa_iva = tasa_iva
            self.__descuento = descuento
            self.__costo_total = self.__servicio.calcular_costo(
                self.__duracion, tasa_iva=tasa_iva, descuento=descuento
            )
            return self.__costo_total
        except Exception as error_origen:
            raise CalculoInconsistenteError(
                f"No se pudo liquidar el costo de la reserva '{self.id}'."
            ) from error_origen

    def confirmar(self) -> None:
        """Cambia el estado de PENDIENTE a CONFIRMADA y aparta recursos si aplica."""
        if self.__estado != self.ESTADO_PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar la reserva '{self.id}' porque su estado actual es '{self.__estado}'."
            )

        # Revalida disponibilidad en el momento exacto de confirmar
        self.__servicio.validar_parametros(self.__duracion)

        if isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.descontar_stock()

        self.__estado = self.ESTADO_CONFIRMADA

    def procesar(self) -> None:
        """Ejecuta y cierra la prestación del servicio (requiere estado CONFIRMADA)."""
        if self.__estado != self.ESTADO_CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"No se puede procesar la reserva '{self.id}': debe estar CONFIRMADA (actual: '{self.__estado}')."
            )
        self.__estado = self.ESTADO_PROCESADA

    def cancelar(self) -> None:
        """Cancela una reserva PENDIENTE o CONFIRMADA y libera inventario si fue descontado."""
        if self.__estado in (self.ESTADO_PROCESADA, self.ESTADO_CANCELADA):
            raise OperacionNoPermitidaError(
                f"Operación denegada: la reserva '{self.id}' ya se encuentra '{self.__estado}' y no puede cancelarse."
            )

        # Si estaba confirmada y era un equipo físico, devolvemos la unidad al stock
        if self.__estado == self.ESTADO_CONFIRMADA and isinstance(self.__servicio, AlquilerEquipo):
            self.__servicio.restaurar_stock()

        self.__estado = self.ESTADO_CANCELADA

    def obtener_resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Estado: {self.__estado} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} ({self.__duracion}h) | Total: ${self.__costo_total:,.2f}"
        )