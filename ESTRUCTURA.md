# Estructura del proyecto

Este archivo explica como esta organizado el codigo para que cada uno del grupo
pueda trabajar en su clase sin pisarse con los demas.

## Layout

```
tp-optimizacion-logistica-urbana/
├── main.py                    # punto de entrada del programa
├── README.md                  # enunciado y documentacion del TP
├── LICENSE
├── ESTRUCTURA.md              # este archivo
│
├── modelado/                  # todas las clases del dominio, una por archivo
│   ├── __init__.py            # re-exporta todo (NO tocar salvo agregar clases nuevas)
│   ├── excepciones.py         # ErrorLogistica + hijas
│   ├── enums.py               # EstadoViaje, TipoIncidente, ResultadoParada
│   ├── ubicacion.py
│   ├── deposito.py
│   ├── articulo.py
│   ├── ventana.py
│   ├── solicitud.py
│   ├── transporte.py          # clase abstracta
│   ├── motocicleta.py
│   ├── furgoneta.py
│   ├── camion.py
│   ├── parada.py
│   ├── comprobante.py
│   ├── incidente.py
│   ├── matriz_distancias.py
│   ├── itinerario.py
│   ├── viaje.py
│   ├── politica.py            # PoliticaDeOrdenamiento + subclases
│   └── empresa.py
│
└── tests/                     # un test file por clase (o por grupo logico)
    ├── __init__.py            # (vacio, marca a tests/ como paquete)
    ├── helpers.py             # funciones auxiliares compartidas
    ├── test_excepciones.py
    ├── test_ubicacion.py
    ├── test_deposito.py
    ├── test_articulo.py
    ├── test_ventana.py
    ├── test_solicitud.py
    ├── test_transporte.py     # incluye polimorfismo y validaciones
    ├── test_parada.py
    ├── test_incidente.py
    ├── test_viaje.py          # incluye enum, maquina de estados y composicion
    └── test_empresa.py
```

## Como importar cosas

Gracias al `__init__.py`, TODOS los imports en el codigo de tests o en `main.py`
usan la forma corta:

```python
from modelado import Viaje, Empresa, Furgoneta, EstadoViaje, DatosInvalidos
```

NO uses la forma larga (`from modelado.viaje import Viaje`) salvo que estes DENTRO
de otro archivo de `modelado/` que necesita importar de un archivo hermano.

### Ejemplo dentro del paquete modelado

`modelado/empresa.py` necesita importar `Viaje`. Como esta dentro del paquete,
usa el path completo:

```python
from modelado.viaje import Viaje
```

## Como correr los tests

Desde la raiz del proyecto:

```bash
# Correr TODA la suite (74 tests, tarda 0.1s)
python3 -m pytest -v

# Correr solo los tests de una clase (mientras trabajas en ella)
python3 -m pytest tests/test_viaje.py -v

# Correr un test especifico si algo esta fallando
python3 -m pytest tests/test_viaje.py::TestEstadoViaje_Maquina::test_iniciar_pasa_a_en_curso -v
```

## Reglas del equipo

1. **Cada clase vive en un archivo**. Si agregas una nueva, creala en su propio archivo
   dentro de `modelado/` y agregala al `__init__.py`.

2. **Cada clase tiene su test file**. Si creas `modelado/nueva_clase.py`, creas tambien
   `tests/test_nueva_clase.py`.

3. **Antes de commitear, correr la suite entera**. Si alguna otra clase se rompio por
   lo que tocaste, los tests te avisan al toque.

4. **Los helpers compartidos van a `tests/helpers.py`**. No los dupliques en cada
   test file.

5. **Si necesitas modificar mas de una clase para un cambio**, avisa al grupo. Es una
   senal de que el cambio afecta a varias personas.

## Como identificar rapido de donde viene un error

Cuando un test falla, pytest te muestra la ruta exacta:

```
tests/test_viaje.py::TestEstadoViaje_Maquina::test_iniciar_pasa_a_en_curso FAILED
```

De ahi sabes:
- Se rompio algo en `Viaje` o en algo que Viaje usa (probablemente `Itinerario`).
- El responsable de Viaje mira primero `modelado/viaje.py`.
- Si el test rompio y nadie toco Viaje, algo cambio en una dependencia (Itinerario,
  EstadoViaje, TransicionIlegal). Se busca en git log quien toco esas.
