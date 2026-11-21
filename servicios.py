from abc import abstractmethod
from entidades import EntidadSistema
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
)


class Servicio(EntidadSistema):
    """Clase abstracta que modela cualquier servicio ofrecido por Software FJ."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, disponible: bool = True) -> None:
        super().__init__(id_servicio)
        if not nombre or not str(nombre).strip():
            raise ParametroFaltanteError("El nombre del servicio es obligatorio.")
        if tarifa_base is None or float(tarifa_base) <= 0:
            raise CalculoInconsistenteError(f"La tarifa base debe ser mayor a 0 (recibido: {tarifa_base}).")

        self.__nombre = str(nombre).strip()
        self.__tarifa_base = float(tarifa_base)
        self.__disponible = bool(disponible)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, estado: bool) -> None:
        self.__disponible = bool(estado)

    def _aplicar_impuestos_y_descuentos(self, subtotal: float, tasa_iva: float = 0.0, descuento: float = 0.0) -> float:
        """Método auxiliar que implementa la lógica sobrecargada de impuestos y descuentos."""
        if tasa_iva < 0 or tasa_iva > 1:
            raise CalculoInconsistenteError(f"Tasa de IVA inválida ({tasa_iva}). Debe estar entre 0.0 y 1.0.")
        if descuento < 0 or descuento >= 1:
            raise CalculoInconsistenteError(f"Descuento inválido ({descuento}). Debe ser >= 0.0 y menor a 1.0.")

        monto_con_descuento = subtotal * (1 - descuento)
        total = monto_con_descuento * (1 + tasa_iva)
        return round(total, 2)

    @abstractmethod
    def validar_parametros(self, duracion: int) -> None:
        """Valida que el servicio esté disponible y cumpla reglas específicas antes de reservar."""
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' ({self.id}) no se encuentra disponible.")
        if not isinstance(duracion, int) or duracion <= 0:
            raise CalculoInconsistenteError(f"La duración debe ser un entero positivo (recibido: {duracion}).")

    @abstractmethod
    def calcular_costo(self, duracion: int, tasa_iva: float = 0.0, descuento: float = 0.0) -> float:
        """Método polimórfico y sobrecargado para calcular el costo final del servicio."""
        pass

    @abstractmethod
    def describir_servicio(self) -> str:
        """Devuelve una ficha técnica detallada del servicio especializado."""
        pass

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return f"[{self.id}] {self.nombre} (${self.tarifa_base:,.2f}/h) - {estado}"


class ReservaSala(Servicio):
    """Servicio especializado para alquiler de salas de reuniones y capacitación."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, capacidad: int, tiene_proyector: bool = True, disponible: bool = True) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise DatosInvalidosError(f"La capacidad de la sala debe ser mayor a 0 (recibido: {capacidad}).")
        self.__capacidad = capacidad
        self.__tiene_proyector = bool(tiene_proyector)

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    def validar_parametros(self, duracion: int) -> None:
        super().validar_parametros(duracion)
        if duracion > 12:
            raise DatosInvalidosError("Una sala no puede reservarse por más de 12 horas continuas.")

    def calcular_costo(self, duracion: int, tasa_iva: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        # Recargo fijo por uso de equipo audiovisual integrado
        if self.__tiene_proyector:
            subtotal += 15000.0
        return self._aplicar_impuestos_y_descuentos(subtotal, tasa_iva, descuento)

    def describir_servicio(self) -> str:
        equipo = "con proyector HD" if self.__tiene_proyector else "sin equipo audiovisual"
        return f"Sala '{self.nombre}' | Capacidad: {self.capacidad} personas | {equipo}."


class AlquilerEquipo(Servicio):
    """Servicio especializado para préstamo de hardware y estaciones de trabajo."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, stock_disponible: int, gama_alta: bool = False, disponible: bool = True) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not isinstance(stock_disponible, int) or stock_disponible < 0:
            raise DatosInvalidosError(f"El stock no puede ser negativo (recibido: {stock_disponible}).")
        self.__stock = stock_disponible
        self.__gama_alta = bool(gama_alta)

    @property
    def stock(self) -> int:
        return self.__stock

    def descontar_stock(self) -> None:
        if self.__stock <= 0:
            raise ServicioNoDisponibleError(f"Sin unidades en inventario para '{self.nombre}'.")
        self.__stock -= 1
        if self.__stock == 0:
            self.disponible = False

    def restaurar_stock(self) -> None:
        self.__stock += 1
        self.disponible = True

    def validar_parametros(self, duracion: int) -> None:
        super().validar_parametros(duracion)
        if self.__stock <= 0:
            raise ServicioNoDisponibleError(f"No hay unidades disponibles del equipo '{self.nombre}'.")

    def calcular_costo(self, duracion: int, tasa_iva: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        # Seguro obligatorio del 10% sobre el subtotal para equipos de gama alta
        if self.__gama_alta:
            subtotal *= 1.10
        return self._aplicar_impuestos_y_descuentos(subtotal, tasa_iva, descuento)

    def describir_servicio(self) -> str:
        nivel = "Gama Alta (incluye seguro)" if self.__gama_alta else "Estándar"
        return f"Equipo '{self.nombre}' | Nivel: {nivel} | Unidades en stock: {self.__stock}."


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de consultoría técnica con ingenieros senior."""

    def __init__(self, id_servicio: str, nombre: str, tarifa_base: float, especialidad: str, horas_minimas: int = 2, disponible: bool = True) -> None:
        super().__init__(id_servicio, nombre, tarifa_base, disponible)
        if not especialidad or not str(especialidad).strip():
            raise ParametroFaltanteError("Debe especificar el área de especialidad de la asesoría.")
        if horas_minimas < 1:
            raise DatosInvalidosError("Las horas mínimas de asesoría deben ser al menos 1.")
        self.__especialidad = str(especialidad).strip()
        self.__horas_minimas = horas_minimas

    def validar_parametros(self, duracion: int) -> None:
        super().validar_parametros(duracion)
        if duracion < self.__horas_minimas:
            raise DatosInvalidosError(
                f"La asesoría '{self.nombre}' requiere un mínimo de {self.__horas_minimas} horas (solicitadas: {duracion})."
            )

    def calcular_costo(self, duracion: int, tasa_iva: float = 0.0, descuento: float = 0.0) -> float:
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        return self._aplicar_impuestos_y_descuentos(subtotal, tasa_iva, descuento)

    def describir_servicio(self) -> str:
        return f"Asesoría en {self.__especialidad} ('{self.nombre}') | Mínimo: {self.__horas_minimas}h."