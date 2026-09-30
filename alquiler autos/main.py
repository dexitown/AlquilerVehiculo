from datetime import date
import calendar

from clases import (
    Cliente,
    Auto,
    Camioneta,
    Moto,
    Sucursal,
    Reserva,
    ServicioNotificaciones,
    EstadoReserva,
    EstadoVehiculo,
    AlquilerError,
    TarifaInvalidaError,
    FechasInvalidasError,
    TransicionInvalidaError,
    VehiculoNoDisponibleError,
    SuperposicionReservaError,
)


def titulo(texto):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


def demo():
    titulo("1. Crear cliente")
    cliente = Cliente("Juan", "Pérez", "40123456", "2996123456", "juan.perez@mail.com")
    print(cliente)

    titulo("2. Crear vehículos de distintos tipos")
    auto = Auto("AA123BB", "Toyota", "Etios", 10000)
    camioneta = Camioneta("AC456DD", "Ford", "Ranger", 10000)
    moto = Moto("A123XYZ", "Honda", "XR150", 10000)
    for v in (auto, camioneta, moto):
        print(v)

    titulo("3. Agrupar vehículos en sucursales")
    sucursal_neuquen = Sucursal("NQN01", "Neuquén", "Av. Argentina 1234")
    sucursal_cutral = Sucursal("CUT01", "Cutral Co", "San Martín 567")
    sucursal_neuquen.agregar_vehiculo(auto)
    sucursal_neuquen.agregar_vehiculo(camioneta)
    sucursal_neuquen.agregar_vehiculo(moto)
    print(sucursal_neuquen)
    for v in sucursal_neuquen.vehiculos:
        print("  -", v)

    print("\nTrasladamos la moto a Cutral Co:")
    sucursal_neuquen.trasladar_vehiculo(moto, sucursal_cutral)
    print(f"  {sucursal_neuquen.codigo}: {len(sucursal_neuquen.vehiculos)} vehículos")
    print(f"  {sucursal_cutral.codigo}: {len(sucursal_cutral.vehiculos)} vehículos")

    titulo("4. Polimorfismo (5 días)")
    for v in (auto, camioneta, moto):
        print(f"{v.__class__.__name__:10} tarifa base ${v.tarifa_base} -> costo: ${v.calcular_costo(5):.2f}")

    titulo("5. Reserva válida y costo")
    notificaciones = ServicioNotificaciones()
    reservas = []

    reserva1 = Reserva(1, cliente, camioneta, date(2026, 10, 10), date(2026, 10, 15),
                       servicio_notificaciones=notificaciones, reservas_existentes=reservas)
    reservas.append(reserva1)
    print(reserva1)
    print(f"Días: {reserva1.dias()} | Costo total: ${reserva1.calcular_costo():.2f}")

    titulo("6. Cambios de estado e historial")
    reserva1.cambiar_estado(EstadoReserva.CONFIRMADA, "Pago recibido")
    print("Reserva:", reserva1.estado.value, "| Vehículo:", camioneta.estado.value)
    reserva1.cambiar_estado(EstadoReserva.EN_CURSO, "Cliente retiró el vehículo")
    print("Reserva:", reserva1.estado.value, "| Vehículo:", camioneta.estado.value)

    print("\nHistorial:")
    for registro in reserva1.historial:
        print("  -", registro)

    titulo("7. Operaciones inválidas")

    print("\n[1] Tarifa 0:")
    try:
        Auto("ZZ999ZZ", "Fiat", "Cronos", 0)
    except TarifaInvalidaError as e:
        print("  ERROR:", e)

    print("\n[2] Fecha de fin anterior al inicio:")
    try:
        Reserva(2, cliente, auto, date(2026, 11, 10), date(2026, 11, 5))
    except FechasInvalidasError as e:
        print("  ERROR:", e)

    print("\n[3] SOLICITADA -> FINALIZADA:")
    reserva2 = Reserva(3, cliente, auto, date(2026, 11, 1), date(2026, 11, 4),
                       servicio_notificaciones=notificaciones, reservas_existentes=reservas)
    reservas.append(reserva2)
    try:
        reserva2.cambiar_estado(EstadoReserva.FINALIZADA)
    except TransicionInvalidaError as e:
        print("  ERROR:", e)

    print("\n[4] Mismo vehículo en período superpuesto:")
    try:
        Reserva(4, cliente, auto, date(2026, 11, 2), date(2026, 11, 6),
                reservas_existentes=reservas)
    except SuperposicionReservaError as e:
        print("  ERROR:", e)

    print("\n[5] Confirmar con vehículo fuera de servicio:")
    moto.estado = EstadoVehiculo.FUERA_DE_SERVICIO
    reserva3 = Reserva(5, cliente, moto, date(2026, 12, 1), date(2026, 12, 3))
    try:
        reserva3.cambiar_estado(EstadoReserva.CONFIRMADA)
    except VehiculoNoDisponibleError as e:
        print("  ERROR:", e)

    titulo("8. Reservas del cliente")
    for r in cliente.reservas:
        print(" ", r)


def pedir_fecha(mensaje):
    # pide una fecha AAAA-MM-DD, si esta mal devuelve None
    texto = input(mensaje)
    partes = texto.split("-")
    if len(partes) != 3:
        return None
    if not (partes[0].isdigit() and partes[1].isdigit() and partes[2].isdigit()):
        return None
    anio = int(partes[0])
    mes = int(partes[1])
    dia = int(partes[2])
    if mes < 1 or mes > 12:
        return None
    if dia < 1 or dia > calendar.monthrange(anio, mes)[1]:
        return None
    return date(anio, mes, dia)


def menu():
    print("\n--- ALQUILER DE VEHICULOS ---")
    print("Primero registrate:")
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    dni = input("DNI: ")
    telefono = input("Telefono: ")
    email = input("Email: ")
    cliente = Cliente(nombre, apellido, dni, telefono, email)

    # cargamos la sucursal con algunos vehiculos
    sucursal = Sucursal("NQN01", "Neuquén", "Av. Argentina 1234")
    sucursal.agregar_vehiculo(Auto("AA123BB", "Toyota", "Etios", 10000))
    sucursal.agregar_vehiculo(Auto("AB222CD", "Fiat", "Cronos", 11000))
    sucursal.agregar_vehiculo(Camioneta("AC456DD", "Ford", "Ranger", 15000))
    sucursal.agregar_vehiculo(Moto("A123XYZ", "Honda", "XR150", 6000))

    notificaciones = ServicioNotificaciones()
    reservas = []
    numero = 1
    opcion = ""

    while opcion != "0":
        print("\n1. Ver vehiculos")
        print("2. Reservar un vehiculo")
        print("3. Ver mis reservas")
        print("4. Cambiar estado de una reserva")
        print("5. Ver historial de una reserva")
        print("0. Salir")
        opcion = input("Opcion: ")

        if opcion == "1":
            for i, v in enumerate(sucursal.vehiculos):
                print(f"{i + 1}. {v} - ${v.tarifa_base}/dia")

        elif opcion == "2":
            vehiculos = sucursal.vehiculos
            for i, v in enumerate(vehiculos):
                print(f"{i + 1}. {v} - ${v.tarifa_base}/dia")
            eleccion = input("Que vehiculo queres? (numero): ")
            if not eleccion.isdigit() or int(eleccion) < 1 or int(eleccion) > len(vehiculos):
                print("Ese vehiculo no existe")
                continue
            vehiculo = vehiculos[int(eleccion) - 1]

            inicio = pedir_fecha("Fecha de inicio (AAAA-MM-DD): ")
            fin = pedir_fecha("Fecha de fin (AAAA-MM-DD): ")
            if inicio is None or fin is None:
                print("Fecha mal escrita, usa el formato AAAA-MM-DD")
                continue

            # si algo no cumple las reglas, Reserva tira un AlquilerError
            try:
                reserva = Reserva(numero, cliente, vehiculo, inicio, fin,
                                  servicio_notificaciones=notificaciones,
                                  reservas_existentes=reservas)
            except AlquilerError as e:
                print("No se pudo reservar:", e)
                continue

            reservas.append(reserva)
            numero += 1
            print("Reserva creada!")
            print(reserva)
            print(f"Costo total: ${reserva.calcular_costo():.2f}")

        elif opcion == "3":
            if len(reservas) == 0:
                print("Todavia no tenes reservas")
            for r in reservas:
                print(r)

        elif opcion == "4":
            if len(reservas) == 0:
                print("No hay reservas")
                continue
            for r in reservas:
                print(r)
            num = input("Numero de reserva: ")
            reserva = None
            for r in reservas:
                if str(r.numero) == num:
                    reserva = r
            if reserva is None:
                print("No existe esa reserva")
                continue

            print("1. Confirmar")
            print("2. En curso")
            print("3. Finalizar")
            print("4. Cancelar")
            nuevo = input("Nuevo estado: ")
            estados = {
                "1": EstadoReserva.CONFIRMADA,
                "2": EstadoReserva.EN_CURSO,
                "3": EstadoReserva.FINALIZADA,
                "4": EstadoReserva.CANCELADA,
            }
            if nuevo not in estados:
                print("Opcion invalida")
                continue

            try:
                reserva.cambiar_estado(estados[nuevo])
                print("Listo, ahora esta", reserva.estado.value)
            except AlquilerError as e:
                print("No se pudo cambiar el estado:", e)

        elif opcion == "5":
            num = input("Numero de reserva: ")
            for r in reservas:
                if str(r.numero) == num:
                    for registro in r.historial:
                        print(" -", registro)

        elif opcion == "0":
            print("Chau!")

        else:
            print("Opcion invalida")


if __name__ == "__main__":
    respuesta = input("Correr la demostracion automatica? (s/n): ")
    if respuesta.lower() == "s":
        demo()
    menu()