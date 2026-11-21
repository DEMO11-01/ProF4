from entidades import Cliente
from excepciones import SoftwareFJError
from gestor import SistemaSoftwareFJ
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def ejecutar_simulacion() -> None:
    sistema = SistemaSoftwareFJ("sistema_fj.log")
    print("\n================ INICIANDO SIMULACIÓN SOFTWARE FJ ================\n")

    # --- BLOQUE 1: GESTIÓN DE CLIENTES (Válidos e Inválidos) ---
    print("--- 1. Registro de Clientes ---")
    # Operación 1 (Válida): Cliente 1
    c1 = Cliente("CLI-01", "1144098765", "Laura Gómez", "laura.gomez@correo.com", "3104567890")
    sistema.registrar_cliente(c1)

    # Operación 2 (Válida): Cliente 2
    c2 = Cliente("CLI-02", "1005894321", "Carlos Mendoza", "cmendoza@empresa.co", "3159876543")
    sistema.registrar_cliente(c2)

    # Operación 3 (Inválida): Correo sin @ y documento corto (capturado al instanciar)
    try:
        c_invalido = Cliente("CLI-03", "123", "Ana", "correo_invalido.com", "300")
        sistema.registrar_cliente(c_invalido)
    except SoftwareFJError as err:
        sistema._SistemaSoftwareFJ__auditor.registrar_error("Instanciación de cliente inválido", err)
        print(f"[ERROR CAPTURADO EN MAIN] {err}")

    # Operación 4 (Inválida): Cliente duplicado (documento repetido de Laura Gómez)
    c_duplicado = Cliente("CLI-04", "1144098765", "Laura Duplicada", "otra@correo.com", "3112223344")
    sistema.registrar_cliente(c_duplicado)

    # --- BLOQUE 2: GESTIÓN DE SERVICIOS POLIMÓRFICOS (Válidos e Inválidos) ---
    print("\n--- 2. Registro de Servicios ---")
    # Operación 5 (Válida): Sala con proyector
    s1 = ReservaSala("SRV-01", "Sala Ejecutiva Norte", 80000.0, capacidad=15, tiene_proyector=True)
    sistema.registrar_servicio(s1)

    # Operación 6 (Válida): Equipo de gama alta con stock de 1 unidad
    s2 = AlquilerEquipo("SRV-02", "Workstation Dell Precision", 45000.0, stock_disponible=1, gama_alta=True)
    sistema.registrar_servicio(s2)

    # Operación 7 (Válida): Asesoría especializada (mínimo 2 horas)
    s3 = AsesoriaEspecializada("SRV-03", "Auditoría Ciberseguridad", 150000.0, especialidad="Seguridad Informática", horas_minimas=2)
    sistema.registrar_servicio(s3)

    # Operación 8 (Inválida): Servicio con tarifa negativa
    try:
        s_invalido = ReservaSala("SRV-04", "Sala Fantasma", -50000.0, capacidad=10)
        sistema.registrar_servicio(s_invalido)
    except SoftwareFJError as err:
        sistema._SistemaSoftwareFJ__auditor.registrar_error("Instanciación de servicio inválido", err)
        print(f"[ERROR CAPTURADO EN MAIN] {err}")

    # --- BLOQUE 3: RESERVAS, SOBRECARGA DE COSTOS Y ESTADOS ---
    print("\n--- 3. Operaciones de Reserva y Estados ---")
    # Operación 9 (Válida): Reserva de sala por 3 horas con IVA 19% y 10% de descuento (sobrecarga)
    sistema.crear_reserva("RES-01", "CLI-01", "SRV-01", duracion=3, tasa_iva=0.19, descuento=0.10)
    sistema.gestionar_estado_reserva("RES-01", "CONFIRMAR")
    sistema.gestionar_estado_reserva("RES-01", "PROCESAR")

    # Operación 10 (Inválida): Intentar cancelar una reserva que ya fue PROCESADA
    sistema.gestionar_estado_reserva("RES-01", "CANCELAR")

    # Operación 11 (Válida + Agotamiento de Stock): Reservar la única Workstation disponible
    sistema.crear_reserva("RES-02", "CLI-02", "SRV-02", duracion=4, tasa_iva=0.19, descuento=0.0)
    sistema.gestionar_estado_reserva("RES-02", "CONFIRMAR")  # Deja el stock en 0 y disponible=False

    # Operación 12 (Inválida): Intentar reservar la misma Workstation cuando ya no hay stock
    sistema.crear_reserva("RES-03", "CLI-01", "SRV-02", duracion=2)

    # Operación 13 (Inválida): Asesoría por 1 hora (incumple mínimo de 2 horas)
    sistema.crear_reserva("RES-04", "CLI-02", "SRV-03", duracion=1)

    # Operación 14 (Inválida con Encadenamiento): Reserva con cliente inexistente (LookupError -> OperacionNoPermitidaError)
    sistema.crear_reserva("RES-99", "CLI-INEXISTENTE", "SRV-01", duracion=2)

    # --- RESUMEN FINAL EN MEMORIA ---
    print("\n================ RESUMEN FINAL DEL SISTEMA (EN MEMORIA) ================")
    print(f"Total Clientes válidos:  {len(sistema.clientes)}")
    print(f"Total Servicios activos: {len(sistema.servicios)}")
    print(f"Total Reservas creadas:  {len(sistema.reservas)}")
    print("Simulación finalizada con éxito. Revisa 'sistema_fj.log' para la auditoría completa.\n")


if __name__ == "__main__":
    ejecutar_simulacion()