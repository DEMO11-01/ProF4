from abc import ABC, abstractmethod
from datetime import datetime
import re
from excepciones import DatosInvalidosError, ParametroFaltanteError


class EntidadSistema(ABC):
    """Clase abstracta base que representa cualquier entidad principal de Software FJ."""

    def __init__(self, id_entidad: str) -> None:
        if not id_entidad or not str(id_entidad).strip():
            raise ParametroFaltanteError("El identificador de la entidad no puede estar vacío.")
        self.__id = str(id_entidad).strip()
        self.__fecha_creacion = datetime.now()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def fecha_creacion(self) -> datetime:
        return self.__fecha_creacion

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Método polimórfico obligatorio para describir la entidad."""
        pass


class Cliente(EntidadSistema):
    """Representa un cliente del sistema con encapsulación y validaciones estrictas."""

    def __init__(self, id_cliente: str, documento: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(id_cliente)
        # Al asignar mediante self.atributo, se ejecutan automáticamente las validaciones de los setters
        self.documento = documento
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def documento(self) -> str:
        return self.__documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El documento de identidad es obligatorio.")
        limpio = str(valor).strip()
        if not limpio.isdigit() or len(limpio) < 6:
            raise DatosInvalidosError(f"Documento inválido ('{valor}'): debe ser numérico y tener al menos 6 dígitos.")
        self.__documento = limpio

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        limpio = str(valor).strip()
        if len(limpio) < 3:
            raise DatosInvalidosError(f"Nombre inválido ('{valor}'): debe tener al menos 3 caracteres.")
        self.__nombre = limpio

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        limpio = str(valor).strip()
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron, limpio):
            raise DatosInvalidosError(f"Correo electrónico con formato inválido: '{valor}'.")
        self.__correo = limpio

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ParametroFaltanteError("El teléfono de contacto es obligatorio.")
        limpio = str(valor).strip()
        if not limpio.isdigit() or len(limpio) < 7:
            raise DatosInvalidosError(f"Teléfono inválido ('{valor}'): debe contener solo números y mínimo 7 dígitos.")
        self.__telefono = limpio

    def obtener_resumen(self) -> str:
        return f"Cliente [{self.id}] {self.nombre} | Doc: {self.documento} | Email: {self.correo}"