# Trabajo Práctico: Optimización de Flota Logística Urbana

## Situación Hipotética

Ustedes han sido contratados como consultores juniors de software para "Logística Inteligente S.A." (LISASA), una empresa en pleno crecimiento que se especializa en la distribución de paquetería y mercadería en grandes centros urbanos. LISASA opera con un modelo de múltiples depósitos distribuidos estratégicamente y posee una flota diversa de transportes, que incluye desde motocicletas para entregas rápidas y livianas, hasta furgonetas y camiones para cargas más voluminosas y pesadas.

El sistema actual de LISASA es rudimentario, basado en hojas de cálculo y comunicación manual, lo que provoca ineficiencias significativas: rutas subóptimas, transportes que exceden sus capacidades, incumplimiento de ventanas horarias de entrega y una gestión deficiente de las incidencias. La empresa está perdiendo dinero y reputación debido a estos problemas operativos.

## Requerimientos Técnicos Obligatorios

Su tarea es diseñar e implementar un sistema inicial que permita a LISASA gestionar de manera más eficiente sus operaciones diarias de entrega. Este sistema debe ser capaz de:

-   Mantener un registro de los distintos tipos de transporte que LISASA utiliza, considerando sus capacidades de carga (peso y volumen) y sus características operativas.
-   Administrar las solicitudes de entrega, las cuales incluyen los artículos a enviar (con su peso y volumen específicos), la ubicación de destino del cliente y, un aspecto crucial, una franja horaria estricta para la entrega.
-   Organizar viajes de entrega que asignen las solicitudes a los transportes adecuados, agrupándolas en secuencias lógicas que partan de un almacén, visiten múltiples puntos y regresen.
-   Asegurar que cada transporte no exceda sus límites de peso y volumen al momento de cargar las solicitudes asignadas para un viaje.
-   Garantizar que las entregas planificadas se realicen dentro de las franjas horarias acordadas con los clientes.
-   Generar comprobantes de recepción una vez que una solicitud ha sido entregada exitosamente.
-   Registrar cualquier problema o eventualidad que surja durante el proceso de entrega (por ejemplo, retrasos inesperados, paquetes dañados, clientes ausentes en el momento de la entrega).

El diseño debe ser robusto y, a la vez, suficientemente flexible para permitir futuras extensiones, como la optimización dinámica de rutas, la integración con sistemas de rastreo GPS en tiempo real o la adición de nuevos tipos de transportes y servicios. Piensen en un modelo que pueda evolucionar junto con las necesidades de LISASA.

La solución que propongan debe estructurarse utilizando el paradigma de Programación Orientada a Objetos. Esto implica que deberán modelar los distintos elementos que componen el sistema de LISASA como unidades distintas, cada una con sus propias características y los comportamientos que pueden realizar.

Cuando existan categorías de elementos similares pero con particularidades, como los diferentes tipos de transporte (motocicletas, furgonetas, camiones), se espera que el diseño refleje esta relación general-específica para promover la reutilización de conceptos y la claridad del modelo. Para acciones comunes que pueden manifestarse de distintas maneras según el tipo de elemento involucrado (por ejemplo, la manera en que diferentes transportes calculan su impacto ambiental o su costo operativo), el sistema debe ser capaz de manejar estas variaciones de forma unificada.

El sistema debe ser capaz de reaccionar ante situaciones inesperadas o datos incorrectos mediante mecanismos que permitan gestionar errores de manera controlada y específica. Por ejemplo, al intentar cargar un transporte más allá de su capacidad, o al recibir una solicitud con una ventana horaria imposible de cumplir, el sistema debe señalar la falla claramente.

Además, la solución debe ser diseñada pensando en su verificabilidad. Esto significa que la estructura que propongan debe facilitar la creación de pruebas automatizadas para asegurar que las lógicas de negocio más importantes funcionen según lo esperado y que el sistema se comporte correctamente bajo diversas condiciones.

## Reglas de Negocio

1.  LISASA requiere que todo medio de transporte que opere tenga claramente definidas sus capacidades máximas de carga, tanto en peso (en kilogramos) como en volumen (en metros cúbicos). Estos valores son fundamentales y deben ser siempre estrictamente positivos al ser registrados.
2.  La empresa dispone de diversos tipos de transporte, como motocicletas, furgonetas y camiones. Cada tipo posee características predeterminadas en cuanto a su capacidad y un costo operativo base por distancia recorrida. Por ejemplo, una motocicleta, por su naturaleza, no podría cargar más de 100 kg o 0.5 m³. El sistema debe ser capaz de distinguir y gestionar estas especializaciones.
3.  Cada solicitud de entrega debe detallar los artículos a despachar (donde cada artículo tiene un peso y un volumen individual), la ubicación final para el cliente y, críticamente, una franja horaria de entrega precisa, definida por una hora de inicio y una hora de fin (ej. "10:00", "12:00"). El sistema debe ser capaz de determinar automáticamente el peso y volumen total de una solicitud a partir de sus artículos.
4.  Al registrar nuevos elementos en el sistema (sean transportes, solicitudes de entrega, datos de clientes o almacenes), es esencial validar que la información inicial sea coherente y completa. Si se intentan ingresar datos inconsistentes (ej. identificadores vacíos, capacidades negativas, o ventanas horarias ilógicas), el sistema debe señalar el error de manera específica.
5.  Al momento de agregar una solicitud a un viaje de entrega planificado, el sistema debe verificar meticulosamente que el peso y volumen acumulado de todas las solicitudes ya planificadas para ese viaje, junto con la nueva adición, no excedan los límites máximos del transporte asignado para dicho viaje. Si una solicitud no puede ser incorporada a un viaje porque su carga superaría la capacidad del transporte, el sistema debe registrar esta situación de forma explícita y detener la operación, informando el motivo.
6.  Una solicitud se considera apta para ser entregada por un transporte en un viaje solo si la hora prevista de llegada al destino del cliente (considerando el itinerario y la secuencia de paradas ya definidas en el viaje) se ajusta perfectamente a la franja horaria establecida para esa entrega. Para simplificar esta lógica, pueden asumir un tiempo de viaje fijo entre paradas o utilizar una matriz de distancias predefinida entre ubicaciones clave. Si al intentar asignar una solicitud a un viaje, se detecta que no es posible cumplir con su ventana horaria, el sistema debe indicar esta inviabilidad de forma clara.
7.  El sistema debe poder estimar el costo total de cada viaje. Este se calculará en función de la distancia total del recorrido (simplificada por un cálculo por número de paradas o utilizando distancias fijas entre ubicaciones) multiplicada por el costo base operativo del tipo de transporte, y sumando un costo fijo por cada parada realizada en el viaje.
8.  Una vez que una solicitud ha sido confirmada como entregada durante un viaje, el sistema debe generar un documento de respaldo que contenga una referencia a la solicitud entregada, la fecha y hora real de la entrega, y un identificador del receptor (puede ser un simple texto en esta etapa).
9.  Si durante la ejecución de un viaje surge algún problema (ej. un retraso por tráfico, un paquete se daña, el cliente no está presente en la dirección), el sistema debe permitir registrar estas eventualidades. Cada problema registrado debe asociarse a la solicitud específica y/o al transporte involucrado, incluyendo una descripción detallada y un tipo de problema (ej. 'DAÑO', 'AUSENTE', 'RETRASO').
10. Finalmente, LISASA se preocupa por el medio ambiente. Por ello, el sistema debe ser capaz de evaluar el impacto ambiental de cada tipo de transporte, aunque sea de forma simplificada. Esta evaluación variará según el tipo de vehículo (motocicleta, furgoneta, camión), demostrando que el sistema puede manejar acciones similares de manera diferente según el elemento que las realice.

## Notas
- Se prohíbe el uso de la librería pandas; el objetivo es evaluar el manejo de estructuras nativas (listas, diccionarios) y la lógica de algoritmos manuales.
- Es requisito obligatorio presentar un diagrama de flujo previo a la codificación para organizar la arquitectura lógica y prevenir fallos de diseño.
- Cada implementación debe estar debidamente sustentada; el alumno debe ser capaz de explicar y justificar técnicamente las decisiones tomadas en el código.
- Se recomienda el uso de la librería estándar de Python (como datetime o math) para optimizar tareas específicas y evitar la redacción innecesaria de funciones ya existentes.
