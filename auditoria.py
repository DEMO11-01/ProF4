import logging


class AuditoriaSistema:
    """Gestiona el registro de eventos y errores en archivo plano."""

    def __init__(self, archivo_log: str = "sistema_fj.log") -> None:
        self.logger = logging.getLogger("SoftwareFJ")
        self.logger.setLevel(logging.INFO)

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