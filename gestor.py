from auditoria import AuditoriaSistema
from entidades import Cliente
from excepciones import (
    DatosInvalidosError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    SoftwareFJError,
)
from reservas import Reserva
from servicios import Servicio


class SistemaSoftwareFJ:
    """Controlador principal que administra listas en memoria, transacciones y auditoría."""

    def __init__(self, archivo_log: str = "sistema_fj.log") -> None:
        self.__clientes: list[Cliente] = []
        self.__servicios: list[Servicio] = []
        self.__reservas: list[Reserva] = []
        self.__auditor = AuditoriaSistema(archivo_log)
        self.__auditor.registrar_evento("=== INICIO DE SESIÓN EN SISTEMA SOFTWARE FJ ===")

    @property
    def clientes(self) -> list[Cliente]:
        return list(self.__clientes)

    @property
    def servicios(self) -> list[Servicio]:
        return list(self.__servicios)

    @property
    def reservas(self) -> list[Reserva]:
        return list(self.__reservas)

    def auditar_error_externo(self, contexto: str, error: Exception) -> None:
        """Registra fallos ocurridos durante la instanciación previa al ingreso al gestor."""
        self.__auditor.registrar_error(contexto, error)

    def _buscar_cliente(self, id_cliente: str) -> Cliente:
        for cliente in self.__clientes:
            if cliente.id == id_cliente:
                return cliente
        raise LookupError(f"No existe ningún cliente con ID '{id_cliente}'.")

    def _buscar_servicio(self, id_servicio: str) -> Servicio:
        for servicio in self.__servicios:
            if servicio.id == id_servicio:
                return servicio
        raise LookupError(f"No existe ningún servicio con ID '{id_servicio}'.")

    def _buscar_reserva(self, id_reserva: str) -> Reserva:
        for reserva in self.__reservas:
            if reserva.id == id_reserva:
                return reserva
        raise LookupError(f"No existe ninguna reserva con ID '{id_reserva}'.")

    def registrar_cliente(self, cliente: Cliente) -> bool:
        """Registra un cliente usando try/except/else/finally sin detener el sistema ante errores."""
        exito = False
        try:
            if not isinstance(cliente, Cliente):
                raise ParametroFaltanteError("Se esperaba una instancia válida de Cliente.")
            if any(c.id == cliente.id or c.documento == cliente.documento for c in self.__clientes):
                raise DatosInvalidosError(
                    f"Cliente duplicado: ID '{cliente.id}' o documento '{cliente.documento}' ya registrado."
                )
        except SoftwareFJError as err:
            self.__auditor.registrar_error(f"Registro de cliente fallido", err)
            print(f"[ERROR CONTROLADO] {err}")
        else:
            self.__clientes.append(cliente)
            self.__auditor.registrar_evento(f"Cliente registrado: {cliente.obtener_resumen()}")
            print(f"[OK] {cliente.obtener_resumen()}")
            exito = True
        finally:
            self.__auditor.registrar_evento("Auditoría cerrada para intento de registro de cliente.")
        return exito

    def registrar_servicio(self, servicio: Servicio) -> bool:
        """Registra un servicio especializado en el catálogo en memoria."""
        exito = False
        try:
            if not isinstance(servicio, Servicio):
                raise ParametroFaltanteError("Se esperaba una instancia válida de Servicio.")
            if any(s.id == servicio.id for s in self.__servicios):
                raise DatosInvalidosError(f"El servicio con ID '{servicio.id}' ya existe en el catálogo.")
        except SoftwareFJError as err:
            self.__auditor.registrar_error("Registro de servicio fallido", err)
            print(f"[ERROR CONTROLADO] {err}")
        else:
            self.__servicios.append(servicio)
            self.__auditor.registrar_evento(f"Servicio registrado: {servicio.obtener_resumen()}")
            print(f"[OK] {servicio.obtener_resumen()} | {servicio.describir_servicio()}")
            exito = True
        finally:
            self.__auditor.registrar_evento("Auditoría cerrada para intento de registro de servicio.")
        return exito

    def crear_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        id_servicio: str,
        duracion: int,
        tasa_iva: float = 0.19,
        descuento: float = 0.0,
    ) -> Reserva | None:
        """Crea una reserva vinculando IDs en memoria y encadenando excepciones si falla la búsqueda."""
        nueva_reserva = None
        try:
            try:
                if any(r.id == id_reserva for r in self.__reservas):
                    raise DatosInvalidosError(f"Ya existe una reserva con ID '{id_reserva}'.")
                cliente = self._buscar_cliente(id_cliente)
                servicio = self._buscar_servicio(id_servicio)
            except LookupError as err_busqueda:
                # Encadenamiento de excepción técnica (LookupError) a excepción de negocio
                raise OperacionNoPermitidaError(
                    f"Imposible crear reserva '{id_reserva}': entidad referenciada no encontrada."
                ) from err_busqueda

            nueva_reserva = Reserva(id_reserva, cliente, servicio, duracion, tasa_iva, descuento)
        except SoftwareFJError as err_negocio:
            self.__auditor.registrar_error(f"Creación de reserva '{id_reserva}'", err_negocio)
            print(f"[ERROR CONTROLADO] {err_negocio}")
            nueva_reserva = None
        else:
            self.__reservas.append(nueva_reserva)
            self.__auditor.registrar_evento(f"Reserva creada: {nueva_reserva.obtener_resumen()}")
            print(f"[OK] {nueva_reserva.obtener_resumen()}")
        finally:
            self.__auditor.registrar_evento(f"Ciclo transaccional finalizado para reserva '{id_reserva}'.")
        return nueva_reserva

    def gestionar_estado_reserva(self, id_reserva: str, accion: str, nuevo_descuento: float | None = None) -> None:
        """Permite confirmar, procesar, cancelar o recalcular costo de una reserva existente."""
        try:
            try:
                reserva = self._buscar_reserva(id_reserva)
            except LookupError as err_busqueda:
                raise OperacionNoPermitidaError(f"No se puede operar sobre '{id_reserva}'.") from err_busqueda

            accion_norm = accion.strip().upper()
            if accion_norm == "CONFIRMAR":
                reserva.confirmar()
            elif accion_norm == "PROCESAR":
                reserva.procesar()
            elif accion_norm == "CANCELAR":
                reserva.cancelar()
            elif accion_norm == "RECALCULAR":
                desc = 0.0 if nuevo_descuento is None else nuevo_descuento
                reserva.recalcular_costo(tasa_iva=0.19, descuento=desc)
            else:
                raise OperacionNoPermitidaError(f"Acción desconocida: '{accion}'.")
        except SoftwareFJError as err:
            self.__auditor.registrar_error(f"Gestión de reserva '{id_reserva}' ({accion})", err)
            print(f"[ERROR CONTROLADO] {err}")
        else:
            self.__auditor.registrar_evento(f"Acción '{accion}' exitosa -> {reserva.obtener_resumen()}")
            print(f"[OK] Acción '{accion}' -> {reserva.obtener_resumen()}")
        finally:
            self.__auditor.registrar_evento(f"Fin de gestión sobre reserva '{id_reserva}'.")