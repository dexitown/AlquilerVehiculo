from enum import Enum
from datetime import date, datetime
class AlquilerError(Exception):
    """Error base del sistema de alquiler."""


class TarifaInvalidaError(AlquilerError):
    pass


class FechasInvalidasError(AlquilerError):
    pass


class VehiculoNoDisponibleError(AlquilerError):
    pass


class TransicionInvalidaError(AlquilerError):
    pass


class SuperposicionReservaError(AlquilerError):
    pass
class EstadoVehiculo(Enum):
    DISPONIBLE = "DISPONIBLE"
    RESERVADO = "RESERVADO"
    EN_ALQUILER = "EN_ALQUILER"
    FUERA_DE_SERVICIO = "FUERA_DE_SERVICIO"
 
 
class EstadoReserva(Enum):
    SOLICITADA = "SOLICITADA"
    CONFIRMADA = "CONFIRMADA"
    EN_CURSO = "EN_CURSO"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"
class Cliente:
    def __init__(self, nombre, apellido, dni, telefono, email):
        self.__nombre = nombre
        self.__apellido = apellido
        self.__dni = dni
        self.telefono = telefono
        self.email = email
        self.__reservas = [] 
 
    @property
    def nombre(self):
        return self.__nombre
 
    @property
    def apellido(self):
        return self.__apellido
 
    @property
    def dni(self):
        return self.__dni
 
    @property
    def reservas(self):
        return list(self.__reservas)  
 
    def agregar_reserva(self, reserva):
        self.__reservas.append(reserva)
 
    def __str__(self):
        return f"{self.__nombre} {self.__apellido} (DNI {self.__dni})"

class Vehiculo:
    """Clase base. Calcula el costo con la tarifa base; las hijas lo sobrescriben."""
 
    def __init__(self, patente, marca, modelo, tarifa_base):
        self.__patente = patente
        self.marca = marca
        self.modelo = modelo
        self.__tarifa_base = None
        self.tarifa_base = tarifa_base  
        self.__estado = EstadoVehiculo.DISPONIBLE
 
    # --- encapsulamiento ---
    @property
    def patente(self):
        return self.__patente
 
    @property
    def tarifa_base(self):
        return self.__tarifa_base
 
    @tarifa_base.setter
    def tarifa_base(self, valor):
        if valor <= 0:
            raise TarifaInvalidaError("La tarifa base por día debe ser mayor que cero")
        self.__tarifa_base = valor
 
    @property
    def estado(self):
        return self.__estado
 
    @estado.setter
    def estado(self, nuevo_estado):
        if not isinstance(nuevo_estado, EstadoVehiculo):
            raise TypeError("El estado debe ser un EstadoVehiculo")
        self.__estado = nuevo_estado
 
    # --- polimorfismo: las hijas sobrescriben este método ---
    def calcular_costo(self, dias):
        if dias <= 0:
            raise FechasInvalidasError("La cantidad de días debe ser mayor que cero")
        return self.tarifa_base * dias
 
    def esta_disponible(self):
        return self.__estado == EstadoVehiculo.DISPONIBLE
 
    def __str__(self):
        return f"{self.__class__.__name__} {self.marca} {self.modelo} [{self.__patente}] - {self.__estado.value}"
 
 
class Auto(Vehiculo):
    """Usa la tarifa base por día (sin recargo ni descuento)."""
 
    def calcular_costo(self, dias):
        return super().calcular_costo(dias)
 
 
class Camioneta(Vehiculo):
    """Recargo del 20 % sobre la tarifa base."""
 
    RECARGO = 0.20
 
    def calcular_costo(self, dias):
        costo = super().calcular_costo(dias) * (1 + self.RECARGO)
        return max(costo, 0)
 
 
class Moto(Vehiculo):
    """Descuento del 15 % sobre la tarifa base."""
 
    DESCUENTO = 0.15
 
    def calcular_costo(self, dias):
        costo = super().calcular_costo(dias) * (1 - self.DESCUENTO)
        return max(costo, 0)

class Sucursal:
    def __init__(self, codigo, ciudad, direccion):
        self.__codigo = codigo
        self.ciudad = ciudad
        self.direccion = direccion
        self.__vehiculos = []
 
    @property
    def codigo(self):
        return self.__codigo
 
    @property
    def vehiculos(self):
        return list(self.__vehiculos)
 
    def agregar_vehiculo(self, vehiculo):
        if vehiculo not in self.__vehiculos:
            self.__vehiculos.append(vehiculo)
 
    def quitar_vehiculo(self, vehiculo):
        if vehiculo in self.__vehiculos:
            self.__vehiculos.remove(vehiculo)
 
    def trasladar_vehiculo(self, vehiculo, sucursal_destino):
        """El vehículo se mueve de sucursal sin dejar de existir."""
        if vehiculo not in self.__vehiculos:
            raise AlquilerError(f"El vehículo {vehiculo.patente} no está en la sucursal {self.__codigo}")
        self.quitar_vehiculo(vehiculo)
        sucursal_destino.agregar_vehiculo(vehiculo)
 
    def vehiculos_disponibles(self):
        return [v for v in self.__vehiculos if v.esta_disponible()]
 
    def __str__(self):
        return f"Sucursal {self.__codigo} - {self.ciudad}, {self.direccion}"

class ServicioNotificaciones:
    def notificar(self, cliente, mensaje):
        print(f"[NOTIFICACIÓN a {cliente.email}] {mensaje}")
 
 
class RegistroHistorial:
    def __init__(self, estado, descripcion):
        ahora = datetime.now()
        self.__fecha = ahora.date()
        self.__hora = ahora.time().replace(microsecond=0)
        self.__estado = estado
        self.__descripcion = descripcion
 
    @property
    def fecha(self):
        return self.__fecha
 
    @property
    def hora(self):
        return self.__hora
 
    @property
    def estado(self):
        return self.__estado
 
    @property
    def descripcion(self):
        return self.__descripcion
 
    def __str__(self):
        return f"{self.__fecha} {self.__hora} | {self.__estado.value} | {self.__descripcion}"
 

class Reserva:
    # Transiciones permitidas entre estados
    TRANSICIONES = {
        EstadoReserva.SOLICITADA: [EstadoReserva.CONFIRMADA, EstadoReserva.CANCELADA],
        EstadoReserva.CONFIRMADA: [EstadoReserva.EN_CURSO, EstadoReserva.CANCELADA],
        EstadoReserva.EN_CURSO: [EstadoReserva.FINALIZADA],
        EstadoReserva.FINALIZADA: [],
        EstadoReserva.CANCELADA: [],
    }
 
    ESTADOS_ACTIVOS = [EstadoReserva.SOLICITADA, EstadoReserva.CONFIRMADA, EstadoReserva.EN_CURSO]
 
    def __init__(self, numero, cliente, vehiculo, fecha_inicio, fecha_fin,
                 servicio_notificaciones=None, reservas_existentes=None):
        if fecha_fin <= fecha_inicio:
            raise FechasInvalidasError("La fecha de finalización debe ser posterior a la de inicio")
 
        # Regla: un vehículo no puede estar en dos reservas activas en el mismo período
        for otra in (reservas_existentes or []):
            if otra.vehiculo is vehiculo and otra.esta_activa() and otra.se_superpone(fecha_inicio, fecha_fin):
                raise SuperposicionReservaError(
                    f"El vehículo {vehiculo.patente} ya tiene la reserva {otra.numero} en ese período"
                )
 
        self.__numero = numero
        self.__cliente = cliente
        self.__vehiculo = vehiculo
        self.__fecha_inicio = fecha_inicio
        self.__fecha_fin = fecha_fin
        self.__estado = EstadoReserva.SOLICITADA
        self.__historial = []  # composición
        self.__notificaciones = servicio_notificaciones  # dependencia
 
        self.__registrar_cambio("Reserva solicitada")
        cliente.agregar_reserva(self)
 
    # --- encapsulamiento ---
    @property
    def numero(self):
        return self.__numero
 
    @property
    def cliente(self):
        return self.__cliente
 
    @property
    def vehiculo(self):
        return self.__vehiculo
 
    @property
    def fecha_inicio(self):
        return self.__fecha_inicio
 
    @property
    def fecha_fin(self):
        return self.__fecha_fin
 
    @property
    def estado(self):
        return self.__estado
 
    @property
    def historial(self):
        return list(self.__historial)

    def dias(self):
        return (self.__fecha_fin - self.__fecha_inicio).days
 
    def calcular_costo(self):
        costo = self.__vehiculo.calcular_costo(self.dias())
        if costo < 0:
            raise AlquilerError("El costo total no puede ser negativo")
        return costo
 
    def esta_activa(self):
        return self.__estado in self.ESTADOS_ACTIVOS
 
    def se_superpone(self, inicio, fin):
        return inicio < self.__fecha_fin and fin > self.__fecha_inicio
 
    def cambiar_estado(self, nuevo_estado, descripcion=""):
        if nuevo_estado not in self.TRANSICIONES[self.__estado]:
            raise TransicionInvalidaError(
                f"No se puede pasar de {self.__estado.value} a {nuevo_estado.value}"
            )
 
        if nuevo_estado == EstadoReserva.CONFIRMADA:
            if not self.__vehiculo.esta_disponible():
                raise VehiculoNoDisponibleError(
                    f"El vehículo {self.__vehiculo.patente} no está disponible"
                )
            self.__vehiculo.estado = EstadoVehiculo.RESERVADO
        elif nuevo_estado == EstadoReserva.EN_CURSO:
            self.__vehiculo.estado = EstadoVehiculo.EN_ALQUILER
        elif nuevo_estado in (EstadoReserva.FINALIZADA, EstadoReserva.CANCELADA):
            self.__vehiculo.estado = EstadoVehiculo.DISPONIBLE
 
        self.__estado = nuevo_estado
        self.__registrar_cambio(descripcion or f"Cambio a {nuevo_estado.value}")
 
        if self.__notificaciones is not None:
            self.__notificaciones.notificar(
                self.__cliente,
                f"Tu reserva {self.__numero} ahora está {nuevo_estado.value}"
            )
 
    def __registrar_cambio(self, descripcion):
        self.__historial.append(RegistroHistorial(self.__estado, descripcion))
 
    def __str__(self):
        return (f"Reserva #{self.__numero} | {self.__cliente} | {self.__vehiculo.patente} | "
                f"{self.__fecha_inicio} -> {self.__fecha_fin} | {self.__estado.value}")
 
