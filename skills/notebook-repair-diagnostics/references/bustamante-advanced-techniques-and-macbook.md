# Técnicas Avanzadas, Método CAF, Trucos de Laboratorio y Diagnóstico MacBook (Daniel Bustamante Sensei)

Compendio técnico extraído de las clases magistrales y reparaciones reales del canal **Daniel Bustamante Sensei**, complementando la metodología de diagnóstico a nivel componente.

---

## 1. Reglas de Seguridad Críticas ("¡No Explotes tu Mother!")

### A. NUNCA energizar la placa si retiraste un IC Controlador Buck dejando los MOSFETs puestos (`a6qZrTbt4oE`)
- **El peligro mortal**: En cualquier fuente Buck con MOSFETs externos (Alta y Baja, ej. controlada por `uP6182`, `TPS51125`, `RT8231`, etc.), los **Gates (pin 4)** de los MOSFETs van conectados directamente al IC controlador sin resistencias pull-down a tierra.
- Si desueldas el IC controlador PWM y conectas los **19V** a la placa para "medir si llegan tensiones a los pads del IC", **los Gates de los MOSFETs quedan flotando en el aire como una antena**.
- En una fracción de segundo, la carga electrostática/parásita dispara el Gate flotante del MOSFET de alta (y/o produce conducción cruzada con el de baja):
  1. **Pasan los 19V directos hacia la línea de salida** (`3.3V`, `5V`, `1.2V RAM` o `1.0V VCORE`), destruyendo instantáneamente el CPU, PCH, EC y haciendo explotar los capacitores de salida.
  2. Ambos MOSFETs (alta y baja) entran en cortocircuito franco.
- **Regla**: Si necesitas retirar un controlador PWM y energizar la placa, **levanta siempre antes un extremo de la bobina de salida (`PL`) o retira el MOSFET de alta**. (Esto no aplica a reguladores lineales LDO sin MOSFETs externos).
- **Truco inverso para probar si un IC Always en una placa de scrap sirve sin desoldarlo**: inyecta 19V en `B+` y en el pin `VIN` del IC en la placa donante y verifica que genere `LDO3` (3.3V) y `LDO5` (5V).

### B. Reglas al Hacer un Puente (Bypass) Temporal en los MOSFETs de Entrada (`irN1hBvdGXg`, `ao-2eHMCIuY`)
- Para probar rápidamente si el resto de la placa enciende cuando no abren los dos MOSFETs de entrada:
  1. **Jamas hagas el puente desde el punto medio (entre el 1er y 2do MOSFET)** hacia la resistencia de sensado (`B+`). Si el 1er MOSFET es Canal P (con su diodo interno en directa), al encender la máquina y consumir `> 1 A`, toda esa corriente pasará por el pequeño diodo interno del 1er MOSFET y lo quemará. **El puente de prueba debe ir siempre desde antes del 1er MOSFET hasta después del 2do MOSFET (resistor shunt)**.
  2. **NUNCA conectes la batería con los MOSFETs de entrada puenteados** ni entregues un equipo así, porque los 19V irían directo hacia la batería sin aislamiento.

### C. Qué Pasa Cuando se Juntan `VIN` (19V) y `BATT+` (14.4V): "En Corto, pero Igual Funciona" (`Mr49RikAjhQ`)
- **Síntoma desconcertante (ej. Lenovo B50-30 `LA-B102P`)**:
  - La laptop funciona perfecto usando **solo el cargador (19V)** (sin batería).
  - Funciona perfecto usando **solo la batería (14.4V)** (sin cargador).
  - Pero al **conectar el cargador con la batería puesta**, la fuente de banco se clava en **cortocircuito total (3.5A – 5A)** y el voltaje cae a ~15V.
- **Causa raíz**: Uno de los 3 MOSFETs de conmutación (`PQ301` entrada 1, `PQ302` entrada 2, o `PQ303` MOSFET separador de batería) está **en cortocircuito entre Drenador y Surtidor** (en este caso `PQ302` `AO4455` Canal P en corto D-S y con fuga de `200 Ω` a Gate). Al enchufar ambos, los 19V del cargador chocan directamente contra los 14.4V de la batería.

### D. Regla de Swap/Scrap de MOSFETs (`yf63LSZhE2s`, `MX_oAE1n1u4`)
- **De Fuente Buck → a Etapa de Entrada (DC-IN)**: **100% VÁLIDO** (respetando que ambos sean Canal N o ambos Canal P). Un MOSFET de una fuente Buck está diseñado para conmutar de **100 kHz a 300 kHz**, mientras que en la entrada DC-IN trabaja como una llave estática (conmuta **1 sola vez** al enchufar el cargador). Por ejemplo, un `AON7410` (30V, 24A) reemplaza perfectamente a un `AON7408` (30V, 23A), o un `AO4435` a un `AO4455`.
- **De Etapa de Entrada → a Fuente Buck**: **NO RECOMENDADO** sin verificar estrictamente el datasheet (`RDS(on)`, capacitancia de Gate y velocidad de conmutación), porque un MOSFET lento en una fuente Buck o de VCORE se recalentará y explotará.

---

## 2. Método "CAF" (Corto, Abierto y con Fugas) en Componentes (`hUxnErWEJGo`)

Todo componente defectuoso cae en uno de tres estados: **Corto** (`0 Ω`), **Abierto** (`OL` / $\infty$) o **Con Fuga** (el componente sufre una degradación química y **"adquiere complejo de resistencia"**, dejando pasar corriente parásita).

### 1. Cómo Detectar Fugas en Capacitores (Por qué Continuidad No Sirve)
- Si un capacitor entra en fuga convirtiéndose en una resistencia de por ejemplo **`1000 Ω` (`1 kΩ`)**, en la escala de **continuidad / buzzer** del multímetro (que solo pita por debajo de `~75 Ω`) marcará **`OL` (aparentemente bueno)** y en la línea de 19.5V casi no hará caer el voltaje.
- **Procedimiento correcto (fuera de placa)**: Medir el capacitor en **escala de Ohmios (resistencia alta)** en ambos sentidos:
  - **Con fuga**: marca un valor resistivo fijo en ambos sentidos (ej. `900 Ω` de un lado y `1100 Ω` invirtiendo las puntas).
  - **Sano**: al tocarlo en Ohmios, el valor sube progresivamente (`50 Ω → 500 Ω → 10 kΩ → 100 kΩ → MΩ → OL`) a medida que se carga con los 3V del multímetro, y repite el ciclo al invertir las puntas. Para verificar desvalorización de capacidad (como el cap de `47 nF` de `ACDET`), usar **capacímetro**.

### 2. Tabla Completa de Caídas de Juntura en Diodos (Escala de Diodo)
- **Diodo Schottky / Rápido**: **`130 mV a 150 mV`** (en directa) / `OL` (en inversa).
- **Diodo de señal común**: **`~450 mV`**.
- **Diodo Zener**: **`~500 mV`**.
- **Diodo rectificador de silicio estándar**: **`580 mV a 650 mV`**.
- **Diodo TVS (supresor en entrada)**: **`600 mV a 700 mV`**.
- **Diodo de protección ESD en puertos HDMI**: caída de juntura **superior a `1000 mV` (`> 1.0 V`)**, por lo que la mayoría de los multímetros los marcan como **`OL` en ambos sentidos** aun estando sanos.
- **Diodo con Fuga**: marca caída de tensión en **ambos sentidos** (ej. `256 mV` en directa y `302 mV` en inversa).
- **Diodo con corto parcial**: si mide `5 Ω` o `10 mV` de un lado y `OL` del otro fuera de placa, **está roto** (ningún diodo de notebook tiene una barrera de 10 mV). *Cuidado en placa*: si el diodo está en paralelo con una bobina, medirá `~10 mV` en ambos sentidos por culpa de la bobina; levantar una pata para medir.

### 3. Bobinas de Potencia (`PL`) vs Bobinas SMD Pequeñas de Paso/Filtro (`L` / `PL`)
- **Cálculo real en Ohmios**: unir primero las puntas del multímetro firmemente (ej. `0.07 Ω`). Medir la bobina (ej. `0.09 Ω`). Restar: `0.09 Ω - 0.07 Ω = 0.02 Ω` reales. *(Nota: el código `4R7` o `4R` impreso sobre una bobina gris indica `4.7 µH` en microhenrios, no ohmios).*
- **Falla típica en bobinas SMD pequeñas negras/grises de paso** (muy común en MacBook y subplacas): por sobreconsumo o sulfatación no siempre se abren del todo, sino que **se desvalorizan convirtiéndose en resistencias de `3 Ω`, `30 Ω`, `100 Ω` o `500 Ω`**. De un lado entran **5V** y del otro lado caen a **3V** cuando la etapa consume corriente.

### 4. Transistores Bipolares BJT (`NPN` y `PNP`) Medidos como Doble Diodo
- En placa también vienen serigrafiados como **`PQ` o `Q`** en encapsulado SOT-23 de 3 patas (**Base, Colector, Emisor**).
- **Mnemotecnia del símbolo**: si la flecha del emisor **P**enetra hacia adentro es **PNP**; si **N**o penetra (sale hacia afuera) es **NPN**.
- **Equivalencia interna para medición en escala de diodo (`~650 mV`)**:
  - **NPN**: equivale a dos diodos con sus ánodos unidos en la **Base**. Punta **ROJA fija en Base** → conduce hacia **Colector (`~650 mV`)** y hacia **Emisor (`~655 mV`, siempre unos mV más que colector)**. Al invertir puntas = `OL`.
  - **PNP**: equivale a dos diodos con sus cátodos unidos en la **Base**. Punta **NEGRA fija en Base** → con punta **ROJA** conduce en **Colector (`~650 mV`)** y **Emisor (`~655 mV`)**.
  - **Entre Colector y Emisor**: **NUNCA debe conducir en ningún sentido (`OL`)** porque los dos diodos internos están en oposición.
- **Condición de saturación (llave cerrada)**: requiere un mínimo de **`0.7 V`** en Base (`+0.7V` en NPN, `-0.7V` respecto a emisor en PNP). Con `0V` o `0.5V` en Base no cierra; con `>0.7V` (ej. `0.9V` a `5V`) cierra Colector-Emisor.
- **BJT con Fuga**: mide `~650 mV` en directa Base-Colector y al invertir las puntas mide p. ej. `350 mV` en lugar de `OL`.

---

## 3. Secretos del Charger `BQ24780S` (`ACDET`), Fuentes Buck (`PEAK`, `VREF`, `BOOT`) y Cargadores

### A. Falla Aleatoria / Falso Inicio en `BQ24780 / BQ24780S`: El Secreto del Capacitor de `ACDET` (`y5z_vx8iiAA`, `yFXH0e1d0uw`)
- **Síntoma**: La laptop cicla de **0 mA a 20 mA → 0 mA → 20 mA** sin arrancar, o bien **enciende solo a veces de forma totalmente aleatoria** (por ejemplo, cuando le tiras alcohol isopropílico o tras enchufar el cargador 10 veces).
- **El engaño del multímetro**: Mides el **Pin 28 (`VCC`) = 20V** y mides el **Pin 6 (`ACDET`) = `2.5V a 2.99V`**. Como el datasheet pide `> 2.4V` (óptimo `~2.6V`), con el multímetro parece estar perfecto e incluso cambias el `BQ24780S` por uno nuevo y sigue fallando igual.
- **Lo que revela el osciloscopio en Pin 6 (`ACDET`)**: Al conectar el osciloscopio en el Pin 6 (`ACDET`), se observan **pequeños pulsos negativos (caídas fugaces de ~10 mV a cientos de mV)** que hacen que el comparador interno del `BQ24780S` crea que se desenchufó el cargador y corte los 25V del Gate (`ACDRV`).
- **Causa raíz y Solución definitiva**:
  - En el divisor resistivo de `ACDET` (ej. `470 kΩ` arriba y `68 kΩ` a GND), el datasheet oficial de Texas Instruments lleva en paralelo hacia tierra un **capacitor cerámico de filtrado de `47 nF` a `100 nF` (`0.1 µF`)**:
    1. **En placas Acer**: muchas veces **no lo montan de fábrica** (dejan los pads vacíos).
    2. **En placas Lenovo (`LA-C292P`) y ASUS**: el capacitor de `47 nF` viene montado pero **se desvaloriza / abre en capacidad** (midiendo con capacímetro apenas `2 nF` o `0.042 nF`, sin marcar corto ni fuga en el multímetro).
  - **Solución**: Soldar o reemplazar ese capacitor en paralelo entre el **Pin 6 (`ACDET`) y GND** por uno cerámico sano de **`100 nF` (`0.1 µF`, `≥ 6.3V`)**. El voltaje de `ACDET` se estabiliza (ej. baja de `2.99V` a `2.76V` limpios sin rizado) y la placa arranca el 100% de las veces.

### B. MOSFET de Entrada "Caprichoso" que Mide Bien en Frío pero Falla Bajo Carga (`ao-2eHMCIuY`)
- **Síntoma (ej. Lenovo 330s)**: El equipo enciende, da imagen (logo Lenovo, ~385 mA) y a los **~30 segundos (cuando sube la exigencia de corriente acercándose a 1A)** se apaga de golpe cayendo a 0 mA.
- **Diagnóstico con osciloscopio de 2 canales**: Canal 1 en consumo de corriente y Canal 2 en el **Gate (25V) del 1er MOSFET de entrada**. Se observa que al subir la corriente, **lo primero que cae a 0V son los 25V del Gate**.
- **Causa**: El 1er MOSFET de entrada Canal N mide perfecto en modo diodo en frío, pero **se degrada bajo carga**, generando una caída entre Drain y Source que activa la protección de sensado (`ACP`/`ACN`) del `BQ24780`. Reemplazar **ambos MOSFETs de entrada** por MOSFETs de etapa de entrada soluciona el apagado.

### C. Condiciones Internas de Referencia (`VREF` y `REGN`) en Chargers y Controladores PWM (`P4Nc0iQvpL4`, `irN1hBvdGXg`)
- **En Charger `BQ24751` (ej. Lenovo G550)**: Si recibe `18V–19V` en **Pin 28 (`VCC`)** y `ACDET` en **Pin 5**, antes de buscar en otro lado mide sus dos fuentes internas (verificando que no tengan corto a tierra):
  - **Pin 10 (`VREF`)**: debe medir **`3.3 V`**.
  - **Pin 24 (`REGN`)**: debe medir **`6.0 V`**.
  - Si tiene `VCC` en Pin 28 pero en Pin 10 y Pin 24 hay `0V` (sin corto a GND), el `BQ24751` está internamente muerto.
- **En Controlador PWM de RAM Richtek `RT8231A` (`24=`) / `RT8231B` (`3T=`) / `4B=4D` (ej. `LA-B801P` clavada en `92 mA` que no apaga del botón)**:
  - Recibe `5V` en **Pin 11 (`VDD`)**, `~0.96V` en **Pin 9 (`TON`**, a través de resistencia de **`470 kΩ` a `620 kΩ`** hacia `19V`), y `3.3V` en **Pin 7 (`S5`)** y **Pin 8 (`S3`)**.
  - Si tiene todo eso y no hay corto en la bobina de `1.2V` ni en `Pin 20 (VTT = 0.6V)`, mide el **Pin 4 (`VREF`)**: debe generar **`~2.0 V`**. Si el Pin 4 está en `0V` sin corto a tierra, el IC controlador está dañado.

### D. Falla de Filtrado (Capacitores Secos/ESR) Detectada sin Osciloscopio con la Función `PEAK` (`NoIFOuM0HJA`)
- **Síntoma**: Placa muerta (ej. `6 mA`), las bobinas de `5V` y `3.3V` miden `0.000V` con el multímetro normal y no tienen corto a tierra.
- **Qué ocurre**: Cuando los capacitores de salida de una fuente Buck pierden capacidad (se secan), al conectar los 19V la fuente intenta arrancar durante **1 milisegundo**, pero el **ripple (rizado)** es tan alto que el IC PWM lo detecta como sobrecarga y se apaga al instante. El multímetro en DC normal es demasiado lento y muestra siempre `0.000V`.
- **Truco con botón `PEAK` (`P-MAX`) del multímetro (ej. Uni-T UT61E / UT161B)**:
  1. Activar la función **`PEAK`** en escala de voltios DC, apoyar la punta en la bobina sospechosa (`5V`) y conectar la fuente de 19V.
  2. Si el multímetro captura un pico de tensión en ese instante (mientras que en otra bobina S0 como `1.8V` marca `0V`), confirma que **el controlador PWM está vivo e intenta arrancar**, y que la falla es por **capacitores de filtrado de salida degradados** (confirmable soldando un capacitor electrolítico en paralelo en la salida: el consumo sube a `15 mA` y aparecen los `5.2V` y `3.3V`).

### E. Línea `BOOT` (Bootstrap) Cortada por Sulfatación (`aXyWVmfAGKk`)
- En todo controlador PWM de fuente Buck existe un pin llamado **`BOOT` / `BST`** conectado mediante una **resistencia en serie de muy bajo valor (0 Ω – 4.7 Ω)** y un **capacitor cerámico (que no va a tierra en ningún extremo)** hacia el nodo de conmutación de la bobina (`PHASE` / `LX`).
- Ese circuito actúa como un "resorte" elevador de tensión para poder disparar el Gate del MOSFET de alta. Si una gota de sulfato corta la pista o abre la resistencia de `BOOT`, la fuente queda en `0V` sin marcar ningún corto.

### F. Cargador Externo: "Hay TENSIÓN (19V) pero NO hay CORRIENTE" (`EoaOQBteS8w`, `fc0Vfmm-bIo`)
- **Síntoma**: Medido sin conectar a la laptop, el cargador entrega **19.2V – 19.8V** en la ficha, pero al enchufarlo a la laptop el voltaje cae y oscila entre **16V y 18V** sin entregar corriente (y en el osciloscopio los 19V en vacío se ven con un **riple "serruchado"** constante).
- **Causa raíz típica tras caída del cargador**: Una de las patas del **transformador switching (chopper)** tiene la pista de cobre circular quebrada alrededor de la soldadura (hace micro-contacto/inducción en alta frecuencia que carga los capacitores en vacío a 19V, pero no puede pasar corriente bajo carga).
- **Solución**: Abrir el cargador en seco aplicando **aire caliente en toda la unión perimetral** (sin acetona ni alcohol para no manchar el plástico), raspar la pista del transformador y soldar un trozo de **cable flexible** de refuerzo, cerrando luego con adhesivo termovariable (tipo B-7000 / cemento de contacto).

---

## 4. Diagnóstico Ultrarrápido de CPU / PCH / SoC Muerto en 2 Minutos (Sin Desoldar Nada)

### A. Prueba de Oro en los Puertos USB 2.0 y USB 3.0 (`ldnlqFaVK5c`, `IVVF16_YKyM`)
- Cuando tengas una placa con corto a tierra (`0 Ω`) en la bobina de **`+3.3V`** (donde el IC de 3V/5V hierve con ~170 mA) o en las bobinas secundarias **`+3VSUS` / `+1.0VSUS`** (donde al inyectar 3A–5A nada parece calentarse porque el puente interno del silicio es de `0.0 Ω`):
- **Antes de levantar bobinas o cambiar el IC de 3V/5V**, mide en escala de continuidad/ohmios los pines de datos **`Datos+` (`D+`) y `Datos-` (`D-`)** de todos los puertos **USB 2.0** (y pares diferenciales de **USB 3.0**):
  1. Mide **`D+` respecto a GND** y **`D-` respecto a GND**.
  2. Mide **`D+` contra `D-` entre sí**.
- Si `D+` y `D-` miden **cortocircuito a tierra (ej. `0 Ω` a `4 Ω`)** y/o **cortocircuito entre sí (`0 Ω` a `8 Ω`)** (habiendo descartado el pequeño chip de 6 patas de diodos de protección ESD `ESD1` si lo hubiera en esa línea), y además la bobina de `1.0V / 1.2V` del SoC mide `~0.1 Ω`: **el PCH / SoC CPU está internamente perforado y muerto**. *(Nota: en algunas placas gamer como la MSI `MS-16J9`, los puertos USB 3.0 llevan un chip redriver/buffer intermedio y no marcan corto, pero el puerto USB 2.0 va directo al PCH y delata el corto de inmediato).*

### B. Cómo Diferenciar Muerte de Sección CPU vs Sección PCH en Procesadores SoC ("2 Mediciones en Frío") (`h94bFZrLwNA`, `4JCHwH_EEnQ`)
En procesadores Intel Todo-en-Uno (SoC con dos pastillas rectangulares en el mismo sustrato: die grande = CPU, die pequeño = PCH):

| Parámetro | Caso 1: Sección **PCH** en Corto | Caso 2: Sección **CPU** en Corto |
| :--- | :--- | :--- |
| **Consumo en fuente** | **2 mA a 6 mA fijos**; al pulsar el botón **no hace absolutamente nada** (muerta total). | **~12 mA en S5**; al pulsar el botón da un **pulso hasta ~64 mA y se apaga a 0 mA**. |
| **Medición 1: Pin 8 (`VCC` 3.3V) de la EEPROM BIOS a GND** | **En corto franco (`0.32 Ω a 0.48 Ω` / `0.000V` en diodo)** y `0V` en S5 (la línea de 3.3V alimenta BIOS, EC y PCH; al abrir el jumper `PJ` e inyectar 2V–3V calienta la pastilla chica del PCH). | **Sano (`~1 MΩ` / alta impedancia)** y tiene sus **3.3V presentes** en Standby. |
| **Medición 2: Bobina de `VCORE` a GND** | **Sana** (ej. `70 Ω` / `97 mV` en arquitecturas de 3ra/4ta gen, o impedancia normal de ese CPU). | **En corto franco (`0.25 Ω` / `0.000V` en diodo**, igual a chocar las puntas del multímetro). |

---

## 5. Trucos Especiales de Memoria RAM, Video, BIOS Loop y "El Dedo Mágico"

### A. Puntos Universales en Slot DDR3 (`Pin 200 SDA` y `Pin 202 SCL`) (`NOTLqQ3thRw`, `ja1jxhUVAdA`)
- Si una placa enciende, sube a **~500 mA** (todas las bobinas incluyendo RAM 1.5V y CPU 1.1V tienen tensión, salvo la última bobina de video `+VGA_CORE`) y **no da video** (o si sube a **114 mA por 4 segundos y cae a 25 mA**):
- Sin necesitar esquemático, mide en el zócalo de memoria RAM **DDR3**:
  - **Pin 199 (`VDDSPD`)**: debe tener **3.3 V**.
  - **Pin 200 (`SDA` - Serial Data)**: debe tener **3.3 V** (y `~687 mV` en escala de diodo).
  - **Pin 202 (`SCL` - Serial Clock)**: debe tener **3.3 V** (y `~654 mV` en escala de diodo).
- **Casos reales**:
  1. **Lenovo G470 (`NOTLqQ3thRw`)**: tenía `3.3V` en el Pin 200 (`SDA`) pero **`0V` en el Pin 202 (`SCL`)** (sin corto a tierra, medía `654 mV` en diodo) por una pista finísima cortada por un rayón/sulfato que venía de la resistencia pull-up. (Si la pista estuviera cortada en una capa interna, se soluciona colocando una resistencia pull-up de **`10 kΩ` hacia `3.3V`**).
  2. **Shuttle `71R-C14CU4-T810` (`ja1jxhUVAdA`)**: los pines 200 y 202 medían apenas **`1.0V a 1.16V`** porque el famoso integrado switch BGA **`U19`** estaba abierto internamente (sin estar en corto ni calentarse, manteniendo 25 mA normales en S5) y no transfería `+3.3VA` a **`+3.3VS`** ni `+5VA` a **`+5VS`**. Solución: retirar `U19` y puentear capacitor **`C460` con `C438` (5V)** y **`C471` con `C464` (3.3V)**.

### B. Cómo Convertir un Módulo RAM DDR3 (1.5V) en DDR3L (1.35V) en 1 Minuto (`jEK8J0q5b_0`)
- Muchos equipos de 4ta a 6ta Gen (ej. Dell, netbooks, Lenovo) rechazan módulos **DDR3 de 1.5V** exigiendo **DDR3L de 1.35V**. La única diferencia lógica reside en el byte de voltaje grabado en la pequeña **EEPROM SPD de 8 pines (`24C02` / `24C04`)** del módulo RAM.
- **Conexión sin desoldar el chip SPD (usando un zócalo DDR3 recortado de scrap hacia el programador `TL866CS` / `CH341A` en modo I2C `24C02`)**:
  - **Pines 1, 2, 3 y 4 del zócalo 24C02** → unidos a **GND** del slot RAM.
  - **Pin 5 (`SDA`) del 24C02** → al **Pin 200 (`SDA`)** del slot RAM DDR3.
  - **Pin 6 (`SCL`) del 24C02** → al **Pin 202 (`SCL`)** del slot RAM DDR3.
  - **Pin 7 (`WP`) del 24C02** → dejar **libre / desconectado**.
  - **Pin 8 (`VCC`) del 24C02** → al **Pin 199 (`VDDSPD`)** del slot RAM DDR3.
- **Edición en HxD**: Leer como `Atmel AT24C02`, ir a la primera fila (`00000000`), columna **`06` (`Offset 0x06`)**: cambiar el valor de `1.5V` (`00` / `02` según lectura comparativa con una DDR3L) al valor de `1.35V` (`02` / `00`) y reprogramar.

### C. Señal `PLT_RST#` en el Pin 22 del Slot Wi-Fi: Diagnóstico de BIOS Loop y "El Dedo Mágico" (`QjCqFkeeG-Q`, `IdBOdL8OLGM`, `Tvm8zKStBaE`)
- **Dónde medir `PLT_RST#` sin esquemático ni boardview**: En el **Pin 22 del conector Mini PCI-Express de la placa Wi-Fi**.
- **Caso 1 — El Truco del "Dedo Mágico" (`QjCqFkeeG-Q`, Banghó Futura 1523)**:
  - La placa enciende sin video clavada en **320 mA** y en el **Pin 22 del slot Wi-Fi (`PLT_RST#`) hay `0V`**.
  - Sin apagar la placa, **ejerce una levísima presión con el dedo sobre el die del FCH/PCH**: si instantáneamente `PLT_RST#` sube a **3.3V**, el consumo se duplica y da video en pantalla, queda 100% confirmado un falso contacto en las esferas BGA del FCH/PCH. **No hacer reflow casero** (quema el chip sano o dura pocos días); realizar **Reballing completo** (preferiblemente con **estaño en pasta con plomo 63/37 y stencil de calor directo** fijado con cinta en los 4 lados, que requiere mucho menos tiempo de calor que las esferas preformadas — `0ZCqf18PQoY`).
- **Caso 2 — Diagnóstico de BIOS Corrupto / BIOS Loop con Osciloscopio (`IdBOdL8OLGM`, `Tvm8zKStBaE`, `InIMFV1Idw8`)**:
  - *Advertencia importante*: En muchas placas (ej. Compaq CQ40 Intel), en estado **Standby (S5)** el EC conversa periódicamente con el **Pin 1 (`CS#`) de la BIOS**, mostrando un tren de pulsos cíclico que es **totalmente normal** tanto con BIOS sana como corrupta.
  - La prueba definitiva se hace **al encender el equipo** midiendo simultáneamente el **Pin 22 del Wi-Fi (`PLT_RST#`)** y el **Pin 2 (`DO`) de la BIOS**:
    - Si `PLT_RST#` sube a `3.3V` y **cae a `0V` cíclicamente cada `2.5 a 5 segundos`** (mientras el consumo da saltos de `650 mA a 720 mA` o reinicia de `700 mA a 185 mA`), o si el Pin 2 de la BIOS queda barriendo datos infinitamente sin parar nunca, el firmware de la **BIOS está corrupto**. Al reprogramar la BIOS, `PLT_RST#` sube a `3.3V` y se mantiene plano y firme.
- **Truco para programar memorias BIOS modernas (`XMC QH128A` / `QH64`) en el programador `TL866CS` antiguo (`cb2YvBqSUJI`)**:
  - Si la marca `XMC` no aparece en el software del `TL866CS`, verifica que sea de **3.3V** y misma capacidad (`128 Mbit = 16 MB`), selecciona manualmente **Winbond `W25Q128BV`** (o `W25Q64` para 8 MB), **desmarca la casilla `Check ID`** y programa normalmente.

### D. Conversión de Video Dedicado a Integrado (Discrete a UMA): "La Bobina de Oro" (`0wnQyau8vMs`)
- En laptops con gráficos híbridos/conmutables (*Switchable Graphics*: Intel HD integrada + GPU dedicada ATI/AMD o NVIDIA, ej. Lenovo Y560 o Asus FX516 con fase DrMOS en corto) donde el GPU dedicado falla:
  1. Antes de desoldar el GPU, las 8 memorias VRAM y decenas de resistencias, localiza y **desuelda únicamente la bobina (`PL`) de alimentación de `GFX` / `VGA_CORE` del GPU dedicado** (o en fuentes multifase de GPU donde un **DrMOS** como el `FDMF5085` entró en corto en una fase, retira ese DrMOS para probar: el equipo encenderá con una fase menos confirmando que la GPU —cuya impedancia normal en frío es de apenas **`0.17 Ω a 0.20 Ω`**— está sana — `MoZ-CZc-7CY`).
  2. **PASO OBLIGATORIO**: **Retirar la pila CMOS (`CR2032`)** para hacer un **Clear CMOS**. Si no quitas la pila CMOS al retirar la bobina del GPU dedicado, el BIOS seguirá intentando iniciar con la GPU dedicada ausente y no dará video. Al quitar la pila, el BIOS se resetea y conmuta automáticamente al video integrado Intel HD.

---

## 6. Guía Especial de Diagnóstico en Apple MacBook (A1278 / A1466: `820-2936`, `820-00165`)

1. **Riel `PP3V42_G3H` (3.42 V) y Charger `ISL6259` (`U7000`) (`CvVoIgR_7qw`)**:
   - Sin `PP3V42_G3H` (3.42V) ni el SMC funcionando, nunca encenderá el LED verde/naranja del MagSafe (`SYS_ONEWIRE`).
   - En el **`ISL6259` (`U7000`)**:
     - **Pin 2 (`DCIN`)**: **16.5V – 18.5V**.
     - **Pin 19 y Pin 20 (`VDD` / `VDDP`)**: **5.0 V**.
     - **Pin 3 (`ACIN`)**: divisor resistivo formado por **`R7010` (`30.1 kΩ`)** y **`R7011` (`9.31 kΩ` a GND)** → con 18.5V debe medir **`~4.37 V a 4.5 V`**.
     - **Pin 14 (`SMC_BC_ACOK`)**: salida abierta que debe estar en **ALTO (`~3.42 V`)** gracias a la resistencia pull-up **`R5087` (`470 kΩ`)** conectada a `PP3V42_G3H`.
     - **Trampa real en `R5087` (`470 kΩ`)**: de un lado tenía `3.42V` y del otro lado caía a `0.63V`. Desoldada y medida en frío con el multímetro marcaba `468 kΩ` (aparentemente perfecta), pero **bajo tensión se abría**. Reemplazarla (nunca puentear con alambre una pull-up de `470 kΩ`) restauró los `3.42V` en `SMC_BC_ACOK` y el MagSafe encendió en verde.
2. **Circuito de Reset del SMC (`U5110`) y la "Resistencia Engañosa" (`RPi8llKl1Gg`)**:
   - Si en una MacBook Air **A1466** tienes `PP3V42_G3H` (3.42V) y los `32.768 kHz` en `U1900`, pero el MagSafe no enciende y consume **12 mA fijos**, mide el IC de reset **`U5110`**:
     - **Pin 1 (`VDD`)**: **3.42 V**.
     - **Pin 3 (alimentación de referencia a través de `R5127` de `0 Ω`)**: debe medir **3.42 V**.
     - **Pin 4 (`SMC_MANUAL_RST_L`)**: debe medir **~2.7 V – 3.4 V**.
     - **Pin 5 (`SMC_RESET_L`)**: salida hacia el SMC, debe medir **3.42 V**. Si está en **`0V`**, el SMC está bloqueado en reset.
     - **Pin 6 (`SMC_TPAD_RST_L`)**: **~3.4 V**.
     - **Pin 7 (`SMC_ONOFF_L`)**: **3.42 V**.
   - **La trampa de `R5127` (`0 Ω`)**: Por sulfatación, la resistencia **`R5127` de `0 Ω`** se desvalorizó subiendo a **`50 kΩ`**. Al medir con el multímetro en el Pin 3 de `U5110` marcaba **`3.12 V`** (parecía alimentado), pero al tener `50 kΩ` en serie no dejaba pasar corriente, haciendo que los pines 4 y 5 (`SMC_RESET_L`) cayeran a **`0V`**.
3. **Cristal de 20 MHz del SMC (`Y5010` en A1278) (`34shLkeoH70`)**:
   - Con osciloscopio: debe mostrar una onda senoidal de **20 MHz** en ambos pines desde S5.
   - **Sin osciloscopio (solo con multímetro)**: debe medir **`1.6 V DC` en ambos extremos** del cristal (y `~800 mV` en escala de diodo en ambos pads). Si un lado mide `1.6V` y el otro `0V` (`OL` en diodo), la pista o el pad debajo del SMC está abierto/arrancado.
4. **Generador de Reloj RTC `U1900` (Pin 12 = `32.768 kHz`) y las Resistencias del PCH (`0vpaZFetMeM`, `CEb0MWeD-cg`)**:
   - A diferencia de las laptops multimarca, las MacBook usan el integrado **`U1900`** (alimentado con 3.3V/3.42V en pines 1, 2, 13 y 14) que saca los **`32.768 kHz` por su Pin 12 (`RTC_CLK32K_RTCX1`)** directo hacia el PCH.
   - **Falla silenciosa mortal del PCH en `820-00165` (`0vpaZFetMeM`)**: La placa queda en **20 mA**, ninguna bobina está en corto (`1.05V` mide `243 Ω`), nada se calienta, pero en el **Pin 12 de `U1900` no hay 32 kHz** porque el **Pin 12 mide `3.4 Ω` en corto a tierra** dentro del propio PCH.
   - **Muerte súbita en `820-2936` por resistencias RTC del PCH (`CEb0MWeD-cg`)**: Si se sulfatan y abren las resistencias pull-up **`R1800` (`330 kΩ` → `PCH_INTVRMEN`)** y **`R1915` (`390 kΩ` → `PCH_DSWVRMEN`)**, los reguladores internos del bloque RTC del PCH se apagan y la placa queda muerta en 24 mA aunque haya 3.42V y luz en el MagSafe. Se pueden reemplazar ambas por resistencias de **`330 kΩ`** de scrap multimarca.

---

## 7. Protocolo de Limpieza Química, Reconstrucción de Pistas/Flex y Sonda "ABox SHUNTpeadora"

1. **Protocolo para Placas Mojadas / Sulfatadas (`MwVcrMmRKJw`, `stxpsQimIhE`, `jBEU4lMx3I8`)**:
   - **Regla #1 antes de cepillar**: **Tomar fotografías macro de alta resolución** de toda la zona sulfatada antes de tocarla con el pincel. Los componentes SMD cuyos pads están comidos por el ácido se desprenderán al pasar el cepillo; si no hay esquemático ni boardview, la foto es la única referencia.
   - **Doble químico**:
     1. Primera limpieza con **Thinner Sello de Oro** (no decapante: disuelve sulfato y resina vieja sin levantar la máscara antisoldante de la placa, aunque la deja opaca).
     2. Segunda limpieza con **Alcohol Isopropílico** (quita la opacidad y devuelve el brillo original; nunca usar alcohol etílico medicinal porque contiene agua y deja residuos blancos).
   - **Paso obligatorio post-lavado**: Aunque la placa luzca limpia, el sulfato degrada la aleación del estaño volviéndola gris, porosa y aislante. Es obligatorio **aplicar flux y repasar con cautín y estaño 60/40 nuevo todos los pines y componentes que estuvieron sulfatados**, y medir continuidad en las pistas finas que cruzan por vías de una cara a la otra (ej. la pista del cristal de 32 kHz al **Pin 2 del EC `IT8502`** en `stxpsQimIhE`, o la pista de 19V al **Pin 16 `VIN` del `TPS51125`** en `jBEU4lMx3I8` que dejaba la placa en `2 mA`).
2. **Cambio de EC de 128 Pines (QFP-128) y Conectores Plásticos (`tjIAjEXGDHw`, `0GH2bo1KBEU`, `4PEoawnPSks`)**:
   - **Cambio de aleación previo**: antes de usar aire caliente para extraer un EC de 128 pines, un Jack Power o un conector FPC, aportar abundante **estaño con plomo 60/40** (o **pasta de soldar de baja fusión a 280 °C desde abajo sin boquilla** para extraer zócalos plásticos de memoria RAM sin derretirlos).
   - Al limpiar los 128 pads del EC con el cautín, mover la punta **siempre en sentido longitudinal al pad (de adentro hacia afuera)** y nunca frotar de costado para no arrancar pistas.
   - Al terminar de soldar un EC o un zócalo de RAM, realizar siempre la **prueba mecánica con la punta de la brucela/aguja bajo el microscopio**, empujando suavemente **pin por pin** para detectar pines que parecen soldados desde arriba pero quedaron sueltos en el aire.
3. **Sonda Activa de Corriente para Osciloscopio ("ABox SHUNTpeadora" — Relación `1V = 1A`) (`5FMK5FXVabM`)**:
   - Intercala una resistencia Shunt con un amplificador operacional alimentado por 2 pilas CR2032 (para no meter ruido de fuente externa) en la línea de 20V y entrega por BNC al osciloscopio **1 Voltio por cada Amperio de consumo (`1V = 1A`)**.
   - **Configuración en el Osciloscopio (ej. Hantek DSO2C15)**:
     - Atenuación de sonda en **`1X`**.
     - Unidad del canal en **Amperes (`A`)** (así `20 mV/div` se lee directamente como `20 mA/div`).
     - Activar **Limitador de Ancho de Banda (`BW Limit = 20 MHz`)** para eliminar el ruido de radiofrecuencia y ver la curva limpia de corriente sincronizada con señales como `ACDET`, `Gate 25V`, `PLT_RST#` o `BIOS Pin 2`.
