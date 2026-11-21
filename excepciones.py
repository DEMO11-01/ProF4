class SoftwareFJError(Exception):
    """Excepción base para todos los errores controlados de Software FJ."""
    pass


class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando un atributo (correo, documento, nombre, etc.) no cumple las reglas."""
    pass


class ParametroFaltanteError(SoftwareFJError):
    """Se lanza cuando falta un dato obligatorio para crear un cliente, servicio o reserva."""
    pass


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta reservar un servicio inactivo o sin cupo/stock."""
    pass


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza al intentar transiciones de estado inválidas (ej. cancelar una reserva ya procesada)."""
    pass


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza ante tarifas negativas, duraciones en cero o descuentos mayores al 100%."""
    pass

import logging
import traceback


class AuditoriaSistema:
    """Gestiona el registro de eventos y errores en archivo plano."""

    def __init__(self, archivo_log: str = "sistema_fj.log") -> None:
        self.logger = logging.getLogger("SoftwareFJ")
        self.logger.setLevel(logging.INFO)

        # Evitar duplicar manejadores si se instancia varias veces
        if not self.logger.handlers:
            file_handler = logging.FileHandler(archivo_log, mode="w", encoding="utf-8")
            formato = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(formato)
            self.logger.addHandler(file_handler)

    def registrar_evento(self, mensaje: str) -> None:
        self.logger.info(mensaje)

    def registrar_error(self, contexto: str, error: Exception) -> None:
        detalle = f"{contexto} -> [{type(error).__name__}]: {error}"
        if error.__cause__:
            detalle += f" | Causa original -> [{type(error.__cause__).__name__}]: {error.__cause__}"
        self.logger.error(detalle)