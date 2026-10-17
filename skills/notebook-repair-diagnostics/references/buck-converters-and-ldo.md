# Diagnóstico de Fuentes Buck (PWM), Reguladores LDO y Aislamiento de Micro-Cortos

Referencia técnica basada en la metodología de **Xtreme PC RGB** para revisar cualquier fuente de alimentación conmutada (Step-Down / Buck Converter) de una laptop y localizar cortos ocultos en reguladores lineales (LDO).

---

## 1. El ABC de los 6 Terminales en Cualquier IC Controlador de Fuente (PWM)

Siempre que falte el voltaje en una bobina (`PL`), realiza primero la medición en **escala de diodo (punta roja a GND, sin energía)** para descartar un corto a la salida. Si **NO hay corto**, localiza en el esquemático el IC controlador de esa fuente (`PU`) y verifica en orden estricto estos **6 terminales**:

| Orden | Nombre del Pin en Esquemático | Función | Qué Medir y Valor Esperado |
| :--- | :--- | :--- | :--- |
| **1. Alimentación** | `VIN`, `IN`, `VCC`, `V5IN`, `VDD` | Alimentación principal del IC | Normalmente **19V–20V** (o **8.5V–13.5V** en NVDC) desde `PWR_SRC`/`B+`. En fuentes secundarias (ej. `TPS51212` de 1.05V o `PM01` de 1.2V RAM) suele venir de **`+5VALW` (5V)**. |
| **2. Habilitación** | `EN`, `EN1`, `EN2`, `ENABLE`, `EN_LDO` | Orden para que el IC comience a trabajar | **~3.3V** (enviado en el 90% de los casos por el EC como `S5_ON`/`ALW_ON` o por el PCH como `SLP_S4#`/`SLP_S3#`). Para `EN_LDO` suele venir de un divisor de tensión desde `VIN` (ej. ~6V). |
| **3. Reguladores LDO** | `VREG3`, `VREG5`, `LDO`, `VL`, `REG` | Reguladores lineales internos de baja corriente | **3.3V** (`+3V_RTC_LDO` / `+3VALW_LDO`) y **5V** (`+5VALW_LDO`). **Se generan ANTES que las bobinas de potencia** para alimentar en Standby al EC, botón de encendido y RTC. |
| **4. Salida a Bobina** | `LX`, `LL`, `SW`, `SW1`, `SW2`, `PHASE` | Nodo de conmutación hacia la bobina `PL` | Debe medir el voltaje nominal de esa fuente (ej. 3.3V, 5V, 1.2V, 1.05V). Depende del switcheo de los MOSFETs de Alta y Baja controlados por los pines `UGATE`/`DRVH` y `LGATE`/`DRVL`. |
| **5. Comprobación** | `FB`, `VFB`, `VFB1`, `VFB2`, `SNS` | Feedback (monitoreo de la salida) | Conectado a la salida de la bobina mediante un **divisor de tensión** (dos resistencias, una hacia la salida de voltaje y otra a GND). Si una resistencia se altera o abre, la fuente da un voltaje erróneo o se apaga enseguida. |
| **6. Confirmación** | `PGOOD`, `PG`, `POK`, `PWRGD` | Power Good (confirmación de fuente OK) | **3.3V** cuando los 5 puntos anteriores están perfectos. Si hay falla en la fuente, el IC pone este pin a **GND (0V)**, bloqueando al EC o a las compuertas lógicas de la secuencia. |

### Terminal Extra Crítico: Pin `TON` (Time-On)
- En muchos controladores PWM (como el IC de la fuente de 1.2V de RAM o 3V/5V), existe un pin llamado **`TON`** conectado a una resistencia de alto valor (ej. **`453 kΩ`** o `470 kΩ`).
- **Función**: regula el tiempo de encendido del MOSFET de alta.
- **Síntoma cuando falla `TON` o `FB`**: La fuente recibe `VIN` y `EN`, intenta generar voltaje por una fracción de segundo (ej. sube a `0.7V–0.8V` en vez de `1.2V`), incluso llega a dar un pulso en `PGOOD`, y se cae inmediatamente. Medir siempre en escala de Ohmios (sin energía) la resistencia de `TON` y las dos resistencias del divisor de `FB` (ej. `100 kΩ` a GND).

---

## 2. Funcionamiento de los MOSFETs de una Fuente Step-Down (Alta y Baja)

En toda fuente conmutada con MOSFETs externos (o Dual MOSFET):
- **MOSFET de Alta (High-Side)**:
  - Su **Drenador (pines 5, 6, 7, 8)** recibe la línea principal de alimentación (`PWR_SRC` / 13V–20V).
  - Su **Gate (pin 4)** recibe pulsos del controlador PWM.
  - Su **Surtidor (pines 1, 2, 3)** va conectado a la entrada de la bobina (`LX`/`PHASE`) y al Drenador del MOSFET de baja.
- **MOSFET de Baja (Low-Side)**:
  - Su **Surtidor (pines 1, 2, 3)** está conectado directamente a **Tierra (GND)** (fácil de identificar midiendo continuidad a tierra en los pines 1–3).
  - Su **Gate (pin 4)** recibe pulsos sincronizados del controlador PWM cuando el MOSFET de alta se apaga.
- **Caso real de diagnóstico (Dell Latitude `+1.05V_M` con `TPS51212` / `PU300`)**:
  - La placa tenía 20V, 3.3V ALW, 5V ALW, `+3.3V_ALW_PCH`, `+3.3V_RTC_LDO` y `+3.3V_M`, pero faltaba `+1.05V_M` en estado S5.
  - El IC `PU300` tenía su alimentación `V5IN` (5V en pin 7) y su `EN` (3.3V en pin 3).
  - El MOSFET de alta (`PQ300`) tenía `13V` en su Drenador.
  - Al medir los Gates (pin 4): el MOSFET de baja tenía `5V` en su Gate (quedando fijo en conducción a tierra), mientras que el Gate del MOSFET de alta tenía **`0V`**.
  - Tras comprobar que la bobina `PL300` no tenía corto (`190 mV` en diodo) y que el MOSFET de alta no estaba en corto ni abierto, se concluye que el controlador PWM `PU300` está dañado por no enviar el pulso al Gate de alta.

---

## 3. Load Switches (Interruptores de Carga, ej. `TPS22966`)

En muchas placas modernas, voltajes derivados (como `+3.3V_ALW_PCH`, `+3.3V_M`, `+5VS`, `+3VS`) no nacen de otra bobina, sino de un **Load Switch** (ej. `TPS22966`, encapsulado pequeño de 14 pines):
- Recibe en sus pines de entrada los **3.3V y/o 5V** desde las bobinas principales.
- Recibe una señal **`ON` / `EN`** (normalmente desde el EC o PCH).
- Cuando llega el `EN`, cierra el interruptor interno y entrega el voltaje en sus pines de salida hacia el PCH, Wi-Fi, SSD, etc.
- **Peligro grave en Load Switches duales (que reciben tanto 5V como 3.3V)**:
  - Si el Load Switch entra en corto interno, puede **unir internamente la línea de 5V con la línea de 3.3V**.
  - Si un técnico inyecta 5V en la bobina de 5V sin antes aislar ese Load Switch, **los 5V pasarán directamente a la línea de 3.3V alimentando al PCH**, quemando el PCH instantáneamente (el PCH tolera máximo 3.3V).

---

## 4. Método de Aislamiento para Micro-Cortos en LDOs (Cuando el Multímetro y la Cámara Térmica No Ven Nada)

### El Problema Trampa
Tienes una placa que no enciende (consumo ~18 mA en la fuente de banco). No hay 3.3V en la bobina `PL100`. Vas al controlador de 3V/5V (`PU100`):
- Tiene su alimentación `VIN` (12.5V–20V).
- Tiene su habilitación `EN_LDO_3V5V` (~6V por divisor de tensión).
- Pero **en la salida `LDO_3V` (pin 17) hay `0V`**.
- Mides en escala de diodo el pin `LDO_3V` y te da **`496 mV` (NO marca corto directo)**.
- **¿Por qué cae a 0V el LDO si marca 496 mV y la cámara térmica no muestra nada calentando?**
  - Porque el regulador lineal LDO interno del IC es de **muy baja corriente** (pocos miliamperios) y tiene protección interna inmediata. Si cualquier componente conectado a la línea LDO tiene una fuga o micro-sobreconsumo, el IC apaga el LDO al instante. Como la corriente es minúscula, no genera calor detectable en cámara térmica y en escala de diodo aún mide ~496 mV.
  - **Error clásico**: Cambiar el IC `PU100` creyendo que está dañado, y que el nuevo IC siga dando 0V en el LDO.

### Procedimiento de Aislamiento Paso a Paso (Sin Inyectar a Ciegas)
1. En el BoardView / Esquemático, selecciona el nodo de salida del **`LDO_3V`** (ej. pin 17 de `PU100`).
2. Identifica los **puntos de paso en serie** (resistencias de `0 Ω` o diodos) por donde el LDO se reparte al resto de la placa:
   - **Rama 1**: Resistencia en serie (ej. `PR104` / `RE57`) que lleva la alimentación al **EC**.
   - **Rama 2**: Resistencia hacia el **Diodo Dual RTC (`D` / `BAT54C`)** de 3 patas (donde el pin 3 recibe los 3.3V del LDO, el pin 2 recibe los 3V de la pila CR2032 `+RTC_CELL`, y el pin 1 saca `+RTC_VCC` hacia el circuito RTC del PCH y del EC).
3. **Desconecta la Rama 1** (retira con aire caliente la resistencia en serie hacia el EC) y alimenta la placa:
   - Si el voltaje `LDO_3V` reaparece (3.3V), el sobreconsumo está en el **EC** (99% EC dañado).
   - Si sigue en `0V`, esa rama está sana.
4. **Desconecta la Rama 2** (retira el **Diodo Dual RTC** de 3 patas) y alimenta la placa:
   - Si ahora **SÍ aparecen los 3.3V en `LDO_3V`**, el problema está en el propio diodo o **después del pin 1 de salida del diodo RTC**.
5. Mide el diodo RTC fuera de placa (debe conducir de pin 3 → pin 1 y de pin 2 → pin 1 con ~318 mV, OL al invertir, y OL entre pin 2 y pin 3). Si está bueno, vuelve a soldarlo y busca en el BoardView los **capacitores cerámicos** conectados a la salida del diodo RTC (ej. cerca del PCH en la línea `INTRUDER#` / `SRTC_RST#` / `RTC_VCC`).
6. Retira los capacitores sospechosos de esa línea RTC y mídelos fuera de la placa en continuidad: encontrarás el pequeño capacitor SMD con fuga/corto que bloqueaba todo el LDO de la placa.
