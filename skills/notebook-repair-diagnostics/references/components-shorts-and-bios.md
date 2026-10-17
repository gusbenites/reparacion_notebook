# Medición de Componentes SMD, Inyección de Voltaje, RAM Onboard y BIOS / Región ME

Referencia práctica basada en las guías paso a paso de **Xtreme PC RGB** sobre comprobación de componentes SMD, localización de cortocircuitos, desactivación por hardware de memoria RAM soldada y programación de BIOS / limpieza de Región ME Intel.

---

## 1.Cómo Medir Cualquier MOSFET como Profesional (y Evitar la Trampa del Gate)

Siempre que un MOSFET marque valores dudosos en la placa, **desóldalo** para medirlo fuera del circuito en **escala de diodo**.

### A. MOSFET de 3 Patas (SOT-23) y de 8 Patas (SOIC-8 / DFN 5x6 / 3x3)
- En un MOSFET de 8 patas:
  - **Pines 1, 2 y 3 (unidos internamente)**: **Surtidor (Source - S)** (el pin 1 se identifica por el punto/hendidura en el cuerpo o marca blanca en placa).
  - **Pin 4 (individual)**: **Puerta (Gate - G)**.
  - **Pines 5, 6, 7 y 8 (unidos internamente)**: **Drenador (Drain - D)**.
- **Cómo distinguir Canal N de Canal P en el esquemático**:
  - Mirar la flecha interna conectada al Gate/Sustrato:
    - Si apunta **hacia afuera** del cuerpo (o el diodo interno apunta de Surtidor a Drenador): **Canal N**.
    - Si apunta **hacia adentro** del cuerpo (o el diodo interno apunta de Drenador a Surtidor): **Canal P**.
- **No confundir encapsulados SOT-23 de 3 patas**:
  - Físicamente un **MOSFET (`PQ` / `Q`)**, un **Transistor BJT NPN/PNP (`Q`, pines 1=Base/Colector, Emisor con flecha)** y un **Diodo Doble (`D` / `PD`)** son idénticos. Verificar siempre en el esquemático o por el código serigrafiado encima del componente.
- **Medición correcta (Drenador ↔ Surtidor)**:
  - En un sentido debe conducir mostrando la caída de tensión del diodo interno: **400 mV a 700 mV** (o ~270–550 mV).
  - Al invertir las puntas debe marcar **`OL` (Open Line / no conduce)**.
  - Entre **Gate y Surtidor** y entre **Gate y Drenador**: debe marcar **`OL`** en ambos sentidos (cuando se mide fuera de la placa; *en placa a veces conduce en un sentido entre Gate y Source por componentes conectados al circuito*).
- **⚠️ LA TRAMPA DE CARGAR EL GATE CON EL MULTÍMETRO (Error muy común)**:
  - En escala de diodo, la punta roja del multímetro inyecta **~3V**.
  - Si primero tocas **Gate y Surtidor** (punta roja en Gate y negra en Surtidor en un Canal N), esos 3V del multímetro **cargan internamente la capacitancia del Gate y dejan el MOSFET activado (abierto)**.
  - Cuando inmediatamente después mides entre **Drenador y Surtidor**, el MOSFET pitará marcando **`0.000V` (cortocircuito) en ambos sentidos**, haciéndote creer que está quemado.
  - **Cómo descargarlo (y a la vez probar que su Gate conmuta bien)**: invierte las puntas entre Gate y Surtidor (punta negra en Gate y punta roja en Surtidor por un par de segundos). Al volver a medir Drenador y Surtidor, el falso corto desaparece y vuelve a conducir en un solo sentido (`~460 mV` / `OL`).
  - **Regla**: Mide **siempre primero entre Drenador y Surtidor** antes de tocar el Gate.

### B. Dual MOSFET (MOSFET Doble: Alta + Baja en el mismo encapsulado)
- Contiene dos MOSFETs internos: **MOSFET 1 (Alta)** y **MOSFET 2 (Baja)**. Sus pines solo son accesibles desoldándolo y midiéndolo por la parte inferior:
  - **Drenador 1 (`D1`)**: alimentación de alta.
  - **Surtidor 1 (`S1`) + Drenador 2 (`D2`)**: comparten un mismo pad grande central llamado **Fase (`PHASE` / `LX`)**.
  - **Surtidor 2 (`S2`)**: conectado a GND.
  - **Gate 1 (`G1`)** y **Gate 2 (`G2`)**: pines pequeños individuales.
- **Detalle clave del MOSFET de Baja (`S2` ↔ `D2`)**:
  - Mientras que el MOSFET 1 (Alta) da una caída de tensión normal de **~550 mV**, el MOSFET 2 (Baja) integra un **diodo Schottky**, por lo que su caída de tensión normal es de **~150 mV a 170 mV** (`OL` al invertir puntas).
  - Por esta razón, al medir en placa la bobina de `5V` o `3.3V` en muchos equipos, una bobina marca `~350 mV` y la otra marca **`~159 mV`**. **159 mV en esa bobina NO es corto ni baja resistencia; es el diodo Schottky interno del MOSFET de baja.**

---

## 2. Diodos, Fusibles, Resistencias y Capacitores SMD

### Fusibles (`F` / `PF`, ej. `PF1`, `PF101`)
- Se ubican en la entrada de carga, puertos USB, HDMI y conector de pantalla eDP (backlight).
- *Curiosidad física*: Algunos fusibles llevan impresa la letra **`L`** encima y parecen una bobina o resistencia, pero en la serigrafía de la placa dicen **`PF`**. Si lleva `F` en la primera o segunda letra, es un fusible.
- **Medición**: Continuidad directa (debe pitar = `0 Ω`). Al reemplazarlo, respetar sus dos parámetros del esquemático: **Amperaje máximo y Voltaje máximo** (ej. `7A / 24V`, o en gráficas `10A` en encapsulado `1206` o `1808`).

###Los 4 Tipos de Diodos en Placas de Laptop (`D` / `PD`)
1. **Diodo Rectificador**: conduce de Ánodo a Cátodo (la flecha del símbolo y la rayita impresa en el cuerpo marcan el **Cátodo**). Caída de tensión: **~0.7 V**. Bloquea en sentido inverso (`OL`).
2. **Diodo Schottky**: símbolo con puntas dobladas en el cátodo. Caída de tensión mucho menor: **~0.2 V a 0.3 V** (`200–300 mV` en escala de diodo; `OL` al invertir).
3. **Diodo Zener**: en polarización directa cae `0.7V`, pero **en polarización inversa (voltaje entrando por el Cátodo)** deja pasar corriente restando su **Voltaje Zener (`Vz`)**:
   - Ejemplo: si entran **19V** por el cátodo de un Zener de **5V**, al otro lado pasan **`14V` (`19V - 5V`)**.
   - Si entran **3V** por el cátodo de un Zener de **5V**, como `3V < 5V`, no vence la barrera y al otro lado pasan **`0V`**.
4. **Diodo Supresor TVS (Transient Voltage Suppressor)**:
   - Se coloca en paralelo entre la entrada del cargador (`19V`) y **Tierra (GND)** (por ejemplo, un TVS de `20V`).
   - Con 19V no conduce. Si el usuario conecta por error un cargador de 24V, el TVS supera su umbral de 20V y **se pone en cortocircuito internamente a propósito**, enviando los 24V a tierra para salvar el resto de la placa.

### Capacitores (`C` / `PC`) y el Caso de los Capacitores de Acoplamiento / Bootstrap
- **Encapsulado**: cuerpo marrón claro/café (a diferencia de las resistencias que son negras con bordes plateados y las bobinas que son gris oscuro/negro).
- **Capacitor de desacoplo normal**: un extremo pita a **GND** y el otro va a la línea de voltaje. Entre sus dos extremos siempre debe marcar **`OL`** en continuidad.
- **Capacitor que NO pita a tierra en ninguno de sus dos extremos (Bootstrap / Acoplamiento AC)**:
  - Ubicados siempre junto a los ICs controladores PWM (conectados al pin `BOOT` / `BST` y `LX`).
  - **Ninguno de sus dos lados va a tierra** y cuando la placa está energizada **tienen voltajes distintos en cada extremo** (ej. `20V` de un lado y `13V` del otro). Eso es **100% normal**; no es caída de tensión ni falla. Igual que cualquier capacitor, entre sus dos extremos sin energía debe medir `OL`.

### Resistencias (`R` / `PR` / `RC`)
- Encapsulados esenciales para stock de taller: **`0201`, `0402`, `0603`, `0805`, `1206`**.
- **Unidades en el esquemático**: Si dice `100K` = `100 kΩ`. Si solo dice `100` (sin letra) = **`100 Ω`** (Ohmios).
- **Tolerancia**: `5%` en líneas generales; `1%` en líneas críticas digitales o divisores de tensión de precisión (`ACDET`, `FB`, comparadores).
- **Símbolo `@` (Arroba) o `NO STUFF` / `*` delante del componente en el esquemático**: significa que **ese componente NO viene instalado de fábrica en la placa** (solo verás los dos pads de soldadura vacíos). No pierdas tiempo buscándolo ni creas que alguien lo arrancó.

---

## 3. Método Seguro para Localizar Cortocircuitos e Inyectar Voltaje

1. **Aislar la bobina (`PL`) antes de inyectar**:
   - Cuando una fuente (ej. 3V o 5V) marca `0 mV` en escala de diodo, levanta **un solo extremo de la bobina** con aire caliente.
   - Mide en diodo ambos pads:
     - **Lado de los MOSFETs / IC PWM**: si el corto está aquí, desuelda y mide los MOSFETs de alta y baja y el IC PWM. (Si el MOSFET de alta estaba en corto, al retirarlo también desaparecerá el corto que se reflejaba en la resistencia de sensado de 19V).
     - **Lado del Sistema (Carga)**: el corto está en un componente alimentado por esa línea.
2. **Regla de Oro de Inyección de Voltaje**:
   - **Comienza siempre con `1.0 V` y `500 mA` a `1.0 A`** en la fuente de laboratorio (y **NUNCA superes el voltaje nominal de esa línea**, especialmente en la línea de 3.3V donde el PCH está conectado directo).
   - Soldar un cable en el pad de salida de la bobina levantada o apoyar la punta del multímetro unida al caimán positivo de la fuente (y caimán negro a GND).
3. **Cómo encontrar el componente sin Cámara Térmica**:
   - Si el consumo al inyectar 1V supera los **2A – 3.6A**, suele ser un componente grande (MOSFET, capacitor cerámico en corto franco, o el propio PCH/CPU).
   - Aplicar **alcohol isopropílico** o humo de **rosín (colofonia)** sobre los componentes sospechosos:
     - **Truco crucial en el PCH/CPU**: Cuando un PCH está sano pero consume algo de corriente, se entibia de manera uniforme. Si al aplicar alcohol isopropílico sobre el cristal (die) del PCH ves que **se evapora instantáneamente en una sola esquina o punto específico del die** (y además los pequeños capacitores encima del sustrato del PCH marcan corto en ambos extremos), el **PCH está internamente en corto y dañado**.

---

## 4. Cómo Desactivar la RAM Onboard (Soldada) Paso a Paso Vía Hardware

Cuando una laptop con **RAM soldada (Onboard)** presenta pantalla negra fija, reinicios, pantallazos azules, artefactos de líneas de colores o `DRAM_RST#` en 0V, y cuenta con un slot SO-DIMM libre (ej. Lenovo V330-15IKB, IdeaPad, ASUS VivoBook):
- *Por qué no hacerlo modificando la BIOS*: si el usuario o Windows actualiza la BIOS en el futuro, la RAM soldada dañada se vuelve a habilitar y el equipo vuelve a fallar. La solución definitiva es por **Hardware (Straps)**.

### Método A: Tabla `Memory Down Strap` (`MD_ID0`, `MD_ID1`, `MD_ID2`, `MD_ID3`)
1. Abrir el esquemático en PDF y buscar el término **`Memory Down`** o **`Strap`**.
2. Localizar la tabla de configuración que lista las combinaciones de módulos (Samsung, Micron, Hynix, 4GB, 8GB) y buscar la fila **`Only DIMM`**, **`Memory Onboard Disable`** o **`UMA / Disable`**.
3. Anotar los 4 valores binarios (`0` o `1`) de las columnas **`MD_ID0`, `MD_ID1`, `MD_ID2`, `MD_ID3`**:
   - **`1` (Estado Alto / High)**: la resistencia de esa línea debe ir colocada en la posición conectada a **`+3.3V`** (pull-up).
   - **`0` (Estado Bajo / Low)**: la resistencia de esa línea debe ir colocada en la posición conectada a **`GND` (Tierra)** (pull-down).
4. En el BoardView, localizar cada par de resistencias (nunca están las dos puestas a la vez en la misma línea; un pad tiene la resistencia y el otro está vacío) y mover las resistencias necesarias para formar el código binario de `Only DIMM`.

### Método B: Señal `ONBOARD_RAM_CFG` (Cuando la tabla `Memory Down` no incluye `Only DIMM`)
1. Si el fabricante ocultó la fila `Only DIMM` en la tabla de RAM, ir a las páginas de configuración (**CFG / GPIO**) del **CPU / PCH** en el esquemático.
2. Buscar una señal llamada **`ONBOARD_RAM_CFG`** (o similar).
3. Seguir esa señal hasta su circuito de dos resistencias entre `+3.3V` y `GND`:
   - Una posición dirá **`Onboard RAM Stuff`** (ej. `R2010` → RAM soldada habilitada).
   - La otra posición dirá **`Onboard RAM Unstuff / Disable`** (ej. `R2009` → RAM soldada deshabilitada).
4. Buscar `R2010` y `R2009` en el BoardView (suelen estar muy cerca del CPU y del cristal oscilador), desoldar la pequeña resistencia de `R2010` y soldarla en los pads vacíos de `R2009`. La placa ignorará por completo los chips de RAM soldados y arrancará usando únicamente el slot SO-DIMM externo.

---

## 5. Diagnóstico de BIOS con Osciloscopio, Reprogramación y Región ME Intel

### ¿Cuándo SÍ y cuándo NO reprogramar la BIOS?
- **NUNCA hacer BIOS** si: hay un corto en 19V/3V/5V, falta algún voltaje primario o secundario de la secuencia, o el pin 8 de la BIOS no recibe su alimentación (**3.3V** o **1.8V**).
- **SÍ sospechar de BIOS** cuando: todas las fuentes hasta `+1.0VS_VCCIO` / `VCORE` se activan, la BIOS tiene su alimentación en el pin 8, no hay cortos, pero el equipo queda en pantalla negra (~400 mA) o se apaga y reinicia en bucle.

### Comprobación en Pin 2 de la BIOS con Osciloscopio
- Conectar la punta del osciloscopio al **Pin 2 de la BIOS SPI (`DO` / `IO1` / Data Out)** y tierra a GND.
- Presionar el botón de encendido:
  - **Equipo con BIOS corrupta**: se observa un primer pulso corto de datos (lo cual confirma que el PCH está vivo e intenta leer la BIOS), seguido de silencio o trenes muy pobres antes de caer el consumo.
  - **Equipo con BIOS sana**: tras el primer tren inicial, se suceden **múltiples trenes largos y densos de paquetes de datos** mientras sube el consumo y da video. *(Nota: tras reprogramar una BIOS, es totalmente normal que la primera vez que se alimenta la placa demore más tiempo y se apague/reinicie 1 o 2 veces sola mientras configura el hardware antes de dar imagen).*

### Cómo Calcular el Tamaño del Archivo BIOS según el Código del Chip
- Los chips de BIOS SPI siempre comienzan con el número **`25`** (ej. GigaDevice `GD25Q64`, `GD25Q128`, Winbond `W25Q256`).
- **Fórmula**: Dividir el número final entre **8**:
  - `25Q32` → `32 / 8` = **4 MB**
  - `25Q64` → `64 / 8` = **8 MB** (`8,192 KB`)
  - `25Q128` → `128 / 8` = **16 MB** (`16,384 KB`)
  - `25Q256` → `256 / 8` = **32 MB**

### Reglas Seguras con Programador `CH341A` / `T48 Pro` (Sin Desoldar con Pinza SOIC8 / WSON-8)
1. En el `CH341A`, usar siempre la mitad de 8 pines marcada como **`25XX`** (no `24XX`).
2. **Verificar el voltaje del Pin 8 con el multímetro antes de conectar a la placa**:
   - Si la BIOS es de **3.3V**, conectar la pinza al adaptador normal y medir con el multímetro que entre el pin 8 de la pinza y GND haya **3.3V**.
   - Si la BIOS es de **1.8V**, intercalar obligatoriamente el **adaptador de 1.8V** y medir en el pin 8 de la pinza que haya exactamente **1.8V**.
3. **Orden de conexión para no dañar nada**: Conectar **primero la pinza al chip BIOS en la placa (con la placa desconectada de toda fuente)** haciendo coincidir el cable rojo con el **Pin 1** (marcado con un punto en el chip o marca blanca en la placa), y **después** conectar el programador al puerto USB de la PC.
4. **SIEMPRE leer y guardar un backup (`salva.bin`) de la BIOS original** antes de borrar o escribir nada.

### Limpieza de Región ME Intel (Management Engine)
- **Síntomas típicos de Región ME corrupta o sucia**:
  - La laptop enciende pero **tarda 15 a 40 segundos en mostrar imagen**.
  - La laptop **se apaga exactamente a los 30 minutos** de uso.
  - Los **ventiladores giran al 100%** constantemente.
  - Pantallazos azules o fallas aleatorias tras cambiar el PCH o programar un dump descargado de otro equipo (porque la Región ME de otro equipo ya viene en estado **`Initialized`**, casada con el PCH de aquella otra máquina).
- **Procedimiento con `ME Analyzer` y `ME Injector`**:
  1. Leer la BIOS original del equipo con el programador y guardarla como `bios_sucia.bin`.
  2. Arrastrar `bios_sucia.bin` dentro de **`ME Analyzer`** y anotar 3 datos:
     - **Versión exacta de ME** (ej. `11.8.50.3426`).
     - **Tipo de Chipset / SKU** (ej. `LP C` vs `H DA`).
     - Observar que dirá `Type: Extracted` y `File System State: Initialized`.
  3. Abrir **`ME Injector`**, cargar la base de datos del repositorio de regiones ME Intel (`Change ME`), abrir `bios_sucia.bin` y seleccionar el archivo de la misma versión y SKU que termine en **`rgn.bin`** (Región Stock limpia; **nunca usar `extr.bin`** que es extraída).
  4. Guardar como `bios_limpia.bin` y verificarla en una nueva ventana de `ME Analyzer`: ahora debe decir **`Type: Stock`** y **`File System State: Unconfigured`** (lista para autoconfigurarse con el hardware en el primer arranque).
  5. Reprogramar `bios_limpia.bin` en la placa.
