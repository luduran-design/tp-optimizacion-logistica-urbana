import json
from pathlib import Path
from datetime import date, datetime, time

from modelado import (
    Articulo, Ubicacion, Deposito, Ventana, Solicitud,
    Transporte, Motocicleta, Furgoneta, Camion,
    MatrizDistancias, Incidente, Viaje, Empresa,
    VecinoMasCercano, MenorVentanaPrimero, TipoIncidente,
    ErrorLogistica, DatosInvalidos, CapacidadExcedida, RutaIncompleta,
    TransicionIlegal,
)

# Todo el escenario ocurre el mismo dia.
FECHA = None  # Se establece al leer la fecha de datos.json.


def hora(h: int, m: int = 0) -> datetime:
    """datetime de FECHA a las h:m."""
    return datetime(FECHA.year, FECHA.month, FECHA.day, h, m)


def cargar_datos() -> dict:
    """Lee datos.json junto a main.py, independientemente de donde se ejecute."""
    ruta = Path(__file__).resolve().parent / "datos.json"
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def horario(texto: str) -> datetime:
    """Convierte un horario del JSON (HH:MM) a datetime de la fecha del escenario."""
    return datetime.combine(FECHA, time.fromisoformat(texto))


def crear_solicitud_desde_datos(empresa: Empresa, datos: dict,
                                destino: Ubicacion) -> Solicitud:
    """Reconstruye una solicitud usando los constructores y validaciones existentes."""
    inicio = horario(datos["inicio"])
    fin = horario(datos["fin"])
    if "articulos_kwargs" in datos:
        # # JSON convierte los pares en listas; crear_solicitud espera tuplas.
        articulos = {}
        for nombre, medidas in datos["articulos_kwargs"].items():
            articulos[nombre] = tuple(medidas)
        return empresa.crear_solicitud(datos["id"], destino, inicio, fin, **articulos)
    articulos = []
    for articulo in datos["articulos"]:
        articulos.append(Articulo(**articulo))
    solicitud = Solicitud(datos["id"], destino, Ventana(inicio, fin), articulos)
    empresa.registrar_solicitud(solicitud)
    return solicitud


def ids(solicitudes: list) -> list:
    """Devuelve solo los ids, para mostrar el orden de las solicitudes sin imprimir cada objeto."""
    return [s.id for s in solicitudes]


def mostrar_paradas(viaje: Viaje) -> None:
    """Imprime orden, solicitud, destino y llegada prevista de cada parada."""
    for p in viaje.paradas:
        print(f"  {p.orden}. {p.solicitud.id} -> {p.solicitud.destino.nombre}, "
              f"llegada prevista {p.llegada_prevista:%H:%M}")


def paso_0_escenario(datos: dict) -> tuple:
    """Arma deposito, ubicaciones, matriz dirigida y la Empresa."""
    print("===== PASO 0: El escenario =====")

    deposito = Deposito(**datos["deposito"])
    ubicaciones = {deposito.id: deposito}
    for dato in datos["ubicaciones"]:
        ubicacion = Ubicacion(**dato)
        if ubicacion.id in ubicaciones:
            raise DatosInvalidos("Id de ubicacion repetido en datos.json.")
        ubicaciones[ubicacion.id] = ubicacion
    # La demostracion sigue los pedidos S1 y S2.
    solicitudes = {s["id"]: s for s in datos["solicitudes"]}
    palermo = ubicaciones[solicitudes["S1"]["destino"]]
    belgrano = ubicaciones[solicitudes["S2"]["destino"]]
    matriz = MatrizDistancias(list(ubicaciones.values()))
    for tramo in datos["tramos_iniciales"]:
        matriz.agregar_tramo(ubicaciones[tramo["origen"]],
                             ubicaciones[tramo["destino"]], tramo["distancia"])

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
        matriz.agregar_tramo(deposito, Ubicacion("U_NO_REGISTRADA", "Tigre", ""), 30)
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    # Ahora si cargamos los tramos de Belgrano, en ambos sentidos.
    for tramo in datos["tramos_adicionales"]:
        matriz.agregar_tramo(ubicaciones[tramo["origen"]],
                             ubicaciones[tramo["destino"]], tramo["distancia"])
    print("Tramos de Belgrano cargados. D1 -> Belgrano:",
          matriz.distancia(deposito, belgrano), "km")

    return empresa, palermo, belgrano


def paso_1_nace_el_pedido(empresa: Empresa, palermo: Ubicacion,
                          belgrano: Ubicacion, datos: dict) -> tuple:
    """Crea S1 a mano y S2 con empresa.crear_solicitud."""
    print()
    print("===== PASO 1: Nace el pedido =====")

    # S1 se arma de abajo hacia arriba: Ventana + Articulos -> Solicitud.
    solicitudes = {s["id"]: s for s in datos["solicitudes"]}
    s1 = crear_solicitud_desde_datos(empresa, solicitudes["S1"], palermo)

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

    # S2 con empresa.crear_solicitud. **articulos recibe cada articulo como
    # nombre=(peso, volumen); Empresa arma los Articulo y la Ventana por nosotros.
    s2 = crear_solicitud_desde_datos(empresa, solicitudes["S2"], belgrano)
    print(f"{s2.id} creada con kwargs: articulos {[a.nombre for a in s2.articulos]}, "
          f"ventana {s2.ventana.inicio:%H:%M}-{s2.ventana.fin:%H:%M}")

    # Empresa guarda las solicitudes en un dict por id: no admite repetidos.
    try:
        empresa.registrar_solicitud(copia)
    except DatosInvalidos as e:
        print("DatosInvalidos ->", e)

    # Cargamos tambien las solicitudes extra para que esten disponibles en Empresa.
    ubicaciones = {u["id"]: Ubicacion(**u) for u in datos["ubicaciones"]}
    for dato in datos["solicitudes"]:
        if dato["id"] not in ("S1", "S2", "S3"):
            crear_solicitud_desde_datos(empresa, dato, ubicaciones[dato["destino"]])
    print("Solicitudes registradas (S3 se carga en el paso 4):", len(empresa.solicitudes))

    return s1, s2


def paso_2_quien_lo_lleva(empresa: Empresa, datos: dict) -> Furgoneta:
    """Registra la flota y muestra el polimorfismo de calcular_impacto."""
    print()
    print("===== PASO 2: Quien lo lleva =====")

    # (id, cap_peso, cap_volumen, velocidad, costo_km, costo_parada, factor_ambiental)
    # Mismo factor ambiental para los tres: la diferencia viene SOLO de la subclase.
    clases = {"Motocicleta": Motocicleta, "Furgoneta": Furgoneta, "Camion": Camion}
    for dato in datos["flota"]:
        atributos = dato.copy()
        tipo = atributos.pop("tipo")
        if tipo not in clases:
            raise DatosInvalidos(f"Tipo de transporte desconocido: {tipo}")
        empresa.registrar_transporte(clases[tipo](**atributos))

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

    # El viaje didactico sigue usando S1 y S2; las demas quedan disponibles.
    pendientes = [s for s in empresa.solicitudes_pendientes() if s.id in ("S1", "S2")]
    print("Pendientes:", ids(pendientes))

    # Empresa recibe cualquier politica y solo le pide sugerir_orden.
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
                            orden_sugerido: list, datos: dict) -> Viaje:
    """Crea el viaje, agrega paradas y muestra la revalidacion atomica: si algo falla, el viaje queda como estaba"""
    print()
    print("===== PASO 4: Se arma el viaje =====")

    # El viaje se crea desde Empresa, que le pasa deposito y matriz.
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
    solicitudes = {s["id"]: s for s in datos["solicitudes"]}
    s3 = crear_solicitud_desde_datos(empresa, solicitudes["S3"], palermo)
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

    # PILA: el orden que habia quedo apilado. Deshacer lo desapila (el ultimo
    # que entro es el primero que sale) y lo vuelve a aplicar.
    viaje.deshacer_reordenar()
    print("Deshacer -> vuelve el orden anterior:", ids([p.solicitud for p in viaje.paradas]))
    try:
        viaje.deshacer_reordenar()
    except TransicionIlegal as e:
        print("TransicionIlegal ->", e)
    viaje.reordenar(orden_sugerido)
    print("Se vuelve a aplicar MenorVentanaPrimero:", ids([p.solicitud for p in viaje.paradas]))

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
    # COLA: al iniciar, las paradas se encolan en el orden planificado.
    print("Cola de paradas por visitar:", ids([p.solicitud for p in viaje.paradas_por_visitar]))

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
    print("Sale S2 por adelante. Cola:", ids([p.solicitud for p in viaje.paradas_por_visitar]))
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
    print("Cola vacia?", viaje.paradas_por_visitar == [])
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
    global FECHA
    try:
        datos = cargar_datos()
        FECHA = date.fromisoformat(datos["fecha"])
        empresa, palermo, belgrano = paso_0_escenario(datos)
        s1, s2 = paso_1_nace_el_pedido(empresa, palermo, belgrano, datos)
        furgoneta = paso_2_quien_lo_lleva(empresa, datos)
        orden_sugerido = paso_3_politica(empresa)
        viaje = paso_4_se_arma_el_viaje(empresa, furgoneta, s1, s2, palermo, orden_sugerido, datos)
        paso_5_se_ejecuta(empresa, viaje, furgoneta, s1, s2)
        paso_6_cierre(viaje)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"No se pudo cargar o interpretar datos.json: {e}")
        raise
    except ErrorLogistica as e:
        # Red de seguridad: ningun error del dominio corta la demo sin explicacion.
        print(f"Error inesperado: {type(e).__name__} -> {e}")


# No cambiar a partir de aqui
if __name__ == "__main__":
    main()