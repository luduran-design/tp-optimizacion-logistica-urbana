from datetime import date, datetime

from modelado import (
    Articulo, Ubicacion, Deposito, Ventana, Solicitud,
    Transporte, Motocicleta, Furgoneta, Camion,
    MatrizDistancias, Incidente, Viaje, Empresa,
    VecinoMasCercano, MenorVentanaPrimero, TipoIncidente,
    ErrorLogistica, DatosInvalidos, CapacidadExcedida, RutaIncompleta,
    TransicionIlegal,
)

# Todo el escenario ocurre el mismo dia.
FECHA = date(2026, 9, 30)


def hora(h: int, m: int = 0) -> datetime:
    """datetime de FECHA a las h:m."""
    return datetime(FECHA.year, FECHA.month, FECHA.day, h, m)


def ids(solicitudes: list) -> list:
    """Lista de ids, para imprimir ordenes de forma compacta."""
    return [s.id for s in solicitudes]


def mostrar_paradas(viaje: Viaje) -> None:
    """Imprime orden, solicitud, destino y llegada prevista de cada parada."""
    for p in viaje.paradas:
        print(f"  {p.orden}. {p.solicitud.id} -> {p.solicitud.destino.nombre}, "
              f"llegada prevista {p.llegada_prevista:%H:%M}")


def paso_0_escenario() -> tuple:
    """Arma deposito, ubicaciones, matriz dirigida y la Empresa."""
    print("===== PASO 0: El escenario =====")

    deposito = Deposito("D1", "Deposito Central", "Barracas")
    palermo = Ubicacion("U1", "Palermo", "Destino del pedido S1")
    belgrano = Ubicacion("U2", "Belgrano", "Destino de la solicitud secundaria S2")

    matriz = MatrizDistancias([deposito, palermo, belgrano])
    matriz.agregar_tramo(deposito, palermo, 9.5)
    matriz.agregar_tramo(palermo, deposito, 10.2)   # la vuelta mide distinto: es dirigida

    empresa = Empresa(deposito, matriz)

    print("Deposito de la empresa:", empresa.deposito)
    print("Es deposito?", empresa.deposito.es_deposito())
    print("Ida    D1 -> Palermo:", matriz.distancia(deposito, palermo), "km")
    print("Vuelta Palermo -> D1:", matriz.distancia(palermo, deposito), "km")
    print("D1 -> D1:", matriz.distancia(deposito, deposito), "km (no hace falta cargarla)")

    # Belgrano es conocida por la matriz, pero todavia no tiene tramos.
    try:
        matriz.distancia(deposito, belgrano)
    except RutaIncompleta as e:
        print("RutaIncompleta ->", e)

    try:
        matriz.agregar_tramo(deposito, Ubicacion("U9", "Tigre", ""), 30)
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    # Ahora si cargamos los tramos de Belgrano, en ambos sentidos.
    matriz.agregar_tramo(deposito, belgrano, 14.0)
    matriz.agregar_tramo(belgrano, deposito, 13.0)
    matriz.agregar_tramo(palermo, belgrano, 5.0)
    matriz.agregar_tramo(belgrano, palermo, 5.5)
    print("Tramos de Belgrano cargados. D1 -> Belgrano:",
          matriz.distancia(deposito, belgrano), "km")

    return empresa, palermo, belgrano


def paso_1_nace_el_pedido(empresa: Empresa, palermo: Ubicacion,
                          belgrano: Ubicacion) -> tuple:
    """Crea S1 a mano y S2 con la fabrica de Empresa."""
    print()
    print("===== PASO 1: Nace el pedido =====")

    # S1 se arma de abajo hacia arriba: Ventana + Articulos -> Solicitud.
    ventana = Ventana(hora(10), hora(12))
    articulos = [
        Articulo("A1", "televisor", 18.0, 0.3),
        Articulo("A2", "microondas", 12.0, 0.1),
    ]
    s1 = Solicitud("S1", palermo, ventana, articulos)
    empresa.registrar_solicitud(s1)

    print(f"{s1.id}: destino {s1.destino.nombre}, "
          f"ventana {s1.ventana.inicio:%H:%M}-{s1.ventana.fin:%H:%M}")
    print("Peso total:", s1.peso_total(), "kg")
    print("Volumen total:", round(s1.volumen_total(), 2), "m3")
    print("Esta asignada?", s1.esta_asignada())

    # Identidad por id: otro objeto con el mismo id es "la misma" solicitud.
    copia = Solicitud("S1", palermo, Ventana(hora(8), hora(9)),
                      [Articulo("A9", "otro", 1.0, 0.1)])
    print("Otra Solicitud con id S1 == s1?", copia == s1)

    # El __init__ valida: una ventana no puede terminar antes de empezar.
    try:
        Ventana(hora(12), hora(10))
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    # S2 con la fabrica de Empresa. **articulos recibe cada articulo como
    # nombre=(peso, volumen); Empresa arma los Articulo y la Ventana por nosotros.
    s2 = empresa.crear_solicitud("S2", belgrano, hora(9), hora(10, 30),
                                 silla=(7.0, 0.4), lampara=(3.0, 0.2))
    print(f"{s2.id} creada con kwargs: articulos {[a.nombre for a in s2.articulos]}, "
          f"ventana {s2.ventana.inicio:%H:%M}-{s2.ventana.fin:%H:%M}")

    # Empresa guarda las solicitudes en un dict por id: no admite repetidos.
    try:
        empresa.registrar_solicitud(copia)
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    return s1, s2


def paso_2_quien_lo_lleva(empresa: Empresa) -> Furgoneta:
    """Registra la flota y muestra el polimorfismo de calcular_impacto."""
    print()
    print("===== PASO 2: Quien lo lleva =====")

    # (id, cap_peso, cap_volumen, velocidad, costo_km, costo_parada, factor_ambiental)
    # Mismo factor ambiental para los tres: la diferencia viene SOLO de la subclase.
    empresa.registrar_transporte(Motocicleta("M1", 20, 0.2, 40, 150, 200, 0.27))
    empresa.registrar_transporte(Furgoneta("F1", 800, 8.0, 30, 250, 500, 0.27))
    empresa.registrar_transporte(Camion("C1", 5000, 30.0, 25, 600, 800, 0.27))

    # Polimorfismo: mismo mensaje, mismos datos, cada uno responde a su manera.
    km, carga = 20, 1000
    print(f"Impacto para {km} km y {carga} kg de carga:")
    for t in empresa.flota:
        print(f"  {t}: {round(t.calcular_impacto(km, carga), 2)} kg CO2")

    # Transporte es abstracta: no se puede instanciar directamente.
    try:
        Transporte("X1", 100, 1.0, 30, 100, 100, 0.27)
    except TypeError as e:
        print("TypeError ->", e)

    try:
        empresa.registrar_transporte(Furgoneta("F1", 500, 5.0, 30, 200, 400, 0.27))
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    # La furgoneta lleva el viaje: le entran S1 + S2 (40 kg, 1.0 m3) de sobra.
    furgoneta = empresa.buscar_transporte("F1")
    print("Transporte elegido:", furgoneta,
          f"(capacidad {furgoneta.capacidad_peso} kg, {furgoneta.capacidad_volumen} m3)")
    return furgoneta


def paso_3_politica(empresa: Empresa) -> list:
    """Consulta dos politicas intercambiables sobre las solicitudes pendientes."""
    print()
    print("===== PASO 3: PoliticaDeOrdenamiento =====")

    pendientes = empresa.solicitudes_pendientes()
    print("Pendientes:", ids(pendientes))

    # Strategy: Empresa no sabe que politica recibe, solo le pide sugerir_orden.
    vecino = empresa.consultar_politica(VecinoMasCercano(), pendientes)
    urgencia = empresa.consultar_politica(MenorVentanaPrimero(), pendientes)
    print("VecinoMasCercano   sugiere:", ids(vecino), "(Palermo esta mas cerca de D1)")
    print("MenorVentanaPrimero sugiere:", ids(urgencia), "(la ventana de S2 cierra 10:30)")

    # La politica solo sugiere: no toca la lista ni asigna nada.
    print("Lista original sin cambios:", ids(pendientes))
    print("Alguna quedo asignada?", any(s.esta_asignada() for s in pendientes))

    return urgencia


def paso_4_se_arma_el_viaje(empresa: Empresa, furgoneta: Furgoneta, s1: Solicitud,
                            s2: Solicitud, palermo: Ubicacion,
                            orden_sugerido: list) -> Viaje:
    """Crea el viaje, agrega paradas y muestra la revalidacion atomica."""
    print()
    print("===== PASO 4: Se arma el viaje =====")

    # Factory: el viaje se crea desde Empresa, que le pasa deposito y matriz.
    viaje = empresa.crear_viaje("V1", FECHA, furgoneta, hora(8, 30))
    print(f"Viaje {viaje.id} creado, estado:", viaje.estado.value)

    viaje.agregar_solicitud(s1)
    viaje.agregar_solicitud(s2)
    # Si llega antes de la ventana, espera la apertura y despues atiende 10 min.
    print("Paradas (salida 08:30, si llega temprano espera la ventana):")
    mostrar_paradas(viaje)
    print("Distancia total:", round(viaje.distancia_total(), 2), "km")
    print("Carga:", viaje.carga_peso(), "kg")
    print("Es factible?", viaje.es_factible())
    print("S1 esta asignada?", s1.esta_asignada())

    # Regla 7: si agregar falla, el viaje queda exactamente como estaba.
    s3 = empresa.crear_solicitud("S3", palermo, hora(9), hora(18),
                                 heladera_industrial=(900.0, 2.5))
    antes = (len(viaje.paradas), viaje.distancia_total())
    print(f"Antes : {antes[0]} paradas, {round(antes[1], 2)} km")
    try:
        viaje.agregar_solicitud(s3)
    except CapacidadExcedida as e:
        print("CapacidadExcedida ->", e)
    despues = (len(viaje.paradas), viaje.distancia_total())
    print(f"Despues: {despues[0]} paradas, {round(despues[1], 2)} km")
    print("Viaje intacto?", antes == despues, "| S3 asignada?", s3.esta_asignada())

    # Regla 5: una solicitud no puede estar dos veces.
    try:
        viaje.agregar_solicitud(s1)
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    # Con este orden S2 llega 10:20 y su ventana cierra 10:30: poco margen.
    # Aplicamos el orden de MenorVentanaPrimero: mas km, pero S2 llega holgada.
    viaje.reordenar(orden_sugerido)
    print("Reordenado segun MenorVentanaPrimero:", ids(orden_sugerido))
    mostrar_paradas(viaje)
    print("Distancia total:", round(viaje.distancia_total(), 2), "km",
          "| Es factible?", viaje.es_factible())

    # Itinerario calcula, Viaje opera.
    return viaje


def paso_5_se_ejecuta(empresa: Empresa, viaje: Viaje, furgoneta: Furgoneta,
                      s1: Solicitud, s2: Solicitud) -> None:
    """Inicia el viaje y resuelve cada parada: Incidente o Comprobante."""
    print()
    print("===== PASO 5: Se ejecuta =====")

    # Un viaje sin paradas no puede salir.
    v0 = empresa.crear_viaje("V0", FECHA, furgoneta, hora(8))
    try:
        v0.iniciar()
    except TransicionIlegal as e:
        print("TransicionIlegal ->", e)

    viaje.iniciar()
    print(f"Viaje {viaje.id} iniciado, estado:", viaje.estado.value)

    # En curso ya no se planifica.
    try:
        viaje.agregar_solicitud(empresa.buscar_solicitud("S3"))
    except TransicionIlegal as e:
        print("TransicionIlegal ->", e)

    # Regla 11: las paradas se resuelven en orden. La actual es S2, no S1.
    print("Parada actual:", viaje.parada_actual().solicitud.id)
    try:
        viaje.registrar_entrega(s1, "Juan Perez", hora(9, 0))
    except TransicionIlegal as e:
        print("TransicionIlegal ->", e)

    # S2 falla: nadie atiende en Belgrano. Queda un Incidente, no un Comprobante.
    incidente = Incidente("I1", TipoIncidente.AUSENTE, hora(9, 5),
                          "Nadie atendio en el domicilio", s2)
    viaje.registrar_fallo(s2, incidente)
    print(f"Fallo en {s2.id}: incidente {incidente.id} ({incidente.tipo.value})")
    print("Comprobantes emitidos:", len(viaje.comprobantes),
          "| Incidentes:", len(viaje.incidentes))

    # Con S1 todavia pendiente, el viaje no se puede cerrar.
    try:
        viaje.finalizar()
    except TransicionIlegal as e:
        print("TransicionIlegal ->", e)

    # S1 se entrega: se genera el Comprobante.
    viaje.registrar_entrega(s1, "Juan Perez", hora(10, 5))
    comprobante = viaje.comprobantes[0]
    print(f"Comprobante nro {comprobante.nro}: {comprobante.solicitud.id} "
          f"recibido por {comprobante.receptor} a las {comprobante.fecha_hora_real:%H:%M}")
    print("Comprobantes emitidos:", len(viaje.comprobantes),
          "| Incidentes:", len(viaje.incidentes))

    print("Resultado de cada parada:")
    for p in viaje.paradas:
        print(f"  {p.orden}. {p.solicitud.id}: {p.resultado.value}")


def paso_6_cierre(viaje: Viaje) -> None:
    """Finaliza el viaje y muestra costo, impacto y resumen."""
    print()
    print("===== PASO 6: Cierre =====")

    # Solo se finaliza EN_CURSO y sin paradas pendientes (lo vimos en el Paso 5).
    viaje.finalizar()
    print(f"Viaje {viaje.id} estado:", viaje.estado.value)

    print("Costo:", round(viaje.costo(), 2))
    # El impacto vuelve a delegar en el transporte: se cierra el circulo del polimorfismo.
    print("Impacto ambiental:", round(viaje.impacto_ambiental(), 2), "kg CO2")
    print("Distancia total:", round(viaje.distancia_total(), 2), "km")

    print("Resumen del viaje:")
    for clave, valor in viaje.resumen().items():
        print(f"  {clave}: {valor}")

    print()
    print("El pedido nace en Solicitud, lo lleva un Transporte polimorfico, "
          "el Itinerario valida que sea factible sin romper nada, el Viaje lo "
          "ejecuta, y termina en un Comprobante o un Incidente. Todo coordinado "
          "por Empresa.")


def main() -> None:
    """Recorre el pedido S1 de punta a punta, un paso por funcion."""
    try:
        empresa, palermo, belgrano = paso_0_escenario()
        s1, s2 = paso_1_nace_el_pedido(empresa, palermo, belgrano)
        furgoneta = paso_2_quien_lo_lleva(empresa)
        orden_sugerido = paso_3_politica(empresa)
        viaje = paso_4_se_arma_el_viaje(empresa, furgoneta, s1, s2, palermo, orden_sugerido)
        paso_5_se_ejecuta(empresa, viaje, furgoneta, s1, s2)
        paso_6_cierre(viaje)
    except ErrorLogistica as e:
        # Red de seguridad: ningun error del dominio corta la demo sin explicacion.
        print(f"Error inesperado: {type(e).__name__} -> {e}")


# No cambiar a partir de aqui
if __name__ == "__main__":
    main()
