# Etapa de Entrada (19V/20V), MOSFETs de Entrada, Charger IC y USB-C PD

Referencia técnica extraída de los casos reales y clases de **Xtreme PC RGB** sobre el circuito de entrada principal, detección de cargador y arquitectura USB-C.

---

## 1. Localización de la Resistencia de Sensado Principal (`PR_SENSE`)

Toda placa de laptop posee una resistencia de sensado de corriente principal por donde pasa toda la energía del cargador hacia el sistema (`B+`, `VIN`, `PWR_SRC`, `DCBATOUT`, `+19V_DCBAOUT`).
- **Cómo ubicarla sin esquemático**:
  1. Buscar cerca del conector de carga (DC-IN) por ambas caras de la placa: suele ser una resistencia de mayor tamaño físico (a veces de color verde, blanco o negro con letras como `R010` / `R020`) acompañada siempre de **dos MOSFETs de entrada** (`PQ`).
  2. Si no está junto al DC-IN, buscarla cerca del **conector de la batería** o de la **bobina de batería**.
  3. **Atajo rápido para medir la línea de la resistencia de sensado**: medir los capacitores cerámicos grandes ubicados junto a las bobinas de VCORE del CPU (alimentación de los MOSFETs de alta del CPU). Un extremo es GND y el otro extremo está conectado directamente a la salida de la resistencia de sensado (`B+` / `PWR_SRC`).
- **Valor normal en escala de diodo (punta roja a GND)**: **400 mV a 550 mV** (típicamente ~450–480 mV).

---

## 2. Los Dos Escenarios de MOSFETs de Entrada: Canal N vs Canal P

Uno de los errores más frecuentes entre técnicos es asumir que el Gate (pin 4) de los MOSFETs de entrada **siempre** debe tener ~25V. Eso depende exclusivamente de si los MOSFETs de entrada son **Canal N** o **Canal P**:

### Caso 1: MOSFETs de Entrada Canal N (La flecha interna apunta hacia AFUERA / hacia el Drenador)
- **Condición de conducción**: Necesita en el Gate (pin 4) un voltaje **superior** al voltaje entre Drenador y Surtidor (`VGS > 0`).
- **Voltaje esperado en Gate**: Si entran **19V–20V**, el Gate debe recibir **~24V a 28V (típicamente 25V)**.
- **¿Quién genera los 25V?**: El **Charger IC** (controlador de carga de batería) a través de su pin **`ACDRV`** (AC Drive, ej. pin 4 en `BQ24780S` / `BQ24800`) mediante una bomba de carga interna (charge pump).
- **Por qué faltan los 25V en `ACDRV`**:
  1. Corto después de la resistencia de sensado o en uno de los dos MOSFETs de entrada (el Charger IC detecta el problema y bloquea `ACDRV` por protección).
  2. El Charger IC no recibe su alimentación principal **`VCC` / `VIN` / `DCIN`** (ej. pin 28 en `BQ24780S`/`BQ24800`, pin 17 en `ISL9538H`). Revisar el **diodo doble OR (`PD`)** y la resistencia fusible de entrada al pin VCC (ej. `PR314`).
  3. El Charger IC no tiene el voltaje correcto en el pin **`ACDET`** (AC Detect).

### Caso 2: MOSFETs de Entrada Canal P (La flecha interna apunta hacia ADENTRO / hacia el Surtidor)
- **Condición de conducción**: Necesita en el Gate (pin 4) un voltaje **bastante inferior (más negativo)** al voltaje de 20V presente en el Surtidor (`VGS < 0`).
- **Error típico**: Medir **18.2V a 20V** en el Gate de un MOSFET Canal P y creer que faltan 25V. Con 18.2V en el Gate y 20V en el Surtidor, la diferencia (`VGS = -1.8V`) no es suficiente para abrir el MOSFET y pasan `0V` al Drenador.
- **Voltaje esperado en Gate (Canal P)**: **~8V a 10V** (por ejemplo, **9.65V – 9.75V** cuando entran 19.5V–20V).
- **¿Cómo se generan los ~9.7V en un MOSFET Canal P?**:
  - El Gate de un MOSFET Canal P **casi nunca va conectado al Charger IC**; se controla mediante un **divisor de tensión** formado por dos resistencias (por ejemplo, dos resistencias de `499 kΩ` en serie desde los 20V).
  - Para que el divisor de tensión funcione, el extremo inferior de la segunda resistencia debe conectarse a **Tierra (GND)** a través de un pequeño **MOSFET Canal N de 3 patas** (ej. `PQ6`).
  - Ese pequeño MOSFET Canal N necesita recibir **3.3V en su Gate (pin 2)** para conducir y enviar la tierra al divisor.
  - **Cadena típica de habilitación en placas con Canal P**:
    1. **Divisor de tensión desde `DCIN` (20V)** (ej. `240 kΩ` arriba y `23.2 kΩ` abajo → debe generar **1.76V**).
    2. **Comparador de voltaje** (símbolo triangular con entradas `+` no inversora en pin 3 y `-` inversora en pin 2, alimentado con 3.3V en pin 8):
       - Si `V(+) > V(-)` (ej. pin 3 tiene `1.76V` > pin 2 que tiene `1.49V` fijos por otro divisor desde 3.3V), el comparador conduce de `P` hacia la salida `O` (pin 1), entregando **3.3V** (`AC_IN_NB`).
       - Si la resistencia superior de `240 kΩ` se desvaloriza (sube a MΩ), el pin 3 cae a `0.4V` (`< 1.49V`), y el comparador conecta su salida a **GND (0V)**.
    3. **Compuerta lógica AND** (ej. `PU1`): recibe sus dos entradas `A` y `B` en 3.3V + alimentación `P` (3.3V) y saca **3.3V** hacia el Gate del MOSFET pequeño Canal N (`PQ6`), cerrando el divisor de tensión y bajando el Gate del MOSFET principal Canal P de `18.2V` a **`9.65V`**.

---

## 3. El Controlador de Carga de Batería (Charger IC)

### Modelos más comunes (cubren >90% del mercado)
- **Texas Instruments (Serie BQ)**: `BQ24780S`, `BQ24800`
- **Intersil / Renesas (Serie ISL)**: `ISL88739A`, `ISL9241H`, `ISL9538H`, `ISL9552H`
  - *Precaución*: Intersil también fabrica controladores PWM de fuentes buck. Para confirmar sin esquemático cuál IC es el Charger, medir **continuidad (con placa sin energía)** entre el **pin 4 (Gate) de los MOSFETs de entrada** y los pines del IC sospechoso: el Charger IC siempre tendrá continuidad directa con el Gate de los MOSFETs de entrada (o a través de una resistencia de bajo valor).

### Arquitecturas NVDC (Narrow Voltage DC) vs Convencionales
- En cargadores tradicionales (`BQ24780S`), la línea principal después de la resistencia de sensado (`B+`) mantiene los **19V–20V** del cargador.
- En cargadores **NVDC** (como el **`ISL9538H`** o arquitecturas Dell), el Charger IC convierte los 19V–20V de entrada a un voltaje más bajo en la línea principal del sistema (`PWR_SRC` / `19V_DCBAOUT`): típicamente **8.5V** o **12.5V – 13.5V**.
- **Regla de diagnóstico**: Si mides **8.36V – 8.5V** o **12.5V – 13.5V** en los capacitores grandes junto al CPU o en el pin `VIN` de la fuente de 3V/5V, **consulta el datasheet del Charger IC**. Si el datasheet dice **NVDC**, ese voltaje de 8.5V o 13V es **100% normal** y no es una caída de tensión ni un corto.

### Secuencia Interna Crítica del Charger IC (Ejemplo `BQ24780S`)
1. **Alimentación `VCC` (Pin 28 en BQ24780S / Pin 17 en ISL9538H)**:
   - Recibe ~19V–20V a través de una resistencia de bajo valor (ej. `PR314`) conectada a la salida de un **diodo doble OR (`PD302`)**.
   - **Función del Diodo OR ("O cargador O batería")**: recibe por un pin los 20V del cargador y por el otro pin el voltaje de la batería, dejando pasar únicamente el voltaje mayor. Si falta el diodo o está abierto en el lado del cargador, `VCC` tendrá 0V con el cargador conectado.
2. **Regulador interno `REGN` / `VDD` (ej. Pin 18 en ISL9538H)**:
   - Una vez alimentado, el Charger genera un LDO interno de **5V o 6V** (`REGN` / `VDD`).
3. **Detección de Cargador `ACDET` (Pin 6 en BQ24780S)**:
   - Recibe un voltaje proveniente de un **divisor de tensión** conectado a los 20V de entrada (`VIN`).
   - Ejemplo real: `VIN` (20V) → `PR313` (`43 kΩ`) y `PR315` (`7.15 kΩ` a GND) → genera **~2.8V** en el pin 6 (`ACDET`).
   - **Requisito según datasheet**: `ACDET` **debe ser mayor a 2.4V** (`> 2.4V`) para que el Charger reconozca el adaptador como válido.
   - **Falla típica**: La resistencia inferior a tierra (`7.15 kΩ`) se altera hacia abajo (ej. cae a `3 kΩ`), filtrando más tensión a tierra y bajando `ACDET` a `1.29V`. Como `1.29V < 2.4V`, el Charger no libera `ACOK` ni los `25V` de `ACDRV`.
4. **Salida `ACOK` (AC Good / Adapter Present) → hacia el EC como `ACIN`**:
   - Cuando `VCC` y `ACDET` (`> 2.4V`) están correctos, el Charger activa su salida `ACOK` para avisarle al EC que hay un cargador válido conectado.
   - **¡CUIDADO CON LA LÓGICA DE `ACIN` (`ACIN` vs `ACIN#`)!**:
     - Si en el esquemático del EC el pin se llama **`ACIN`** o **`AC_PRESENT` (sin el símbolo `#`)**: es **Active High** → debe medir **3.3V** con el cargador conectado. (Falla típica: resistencia pull-up de `100 kΩ` abierta o faltante hacia los 3.3V, dejando el pin en `0.17V`).
     - Si en el esquemático del EC el pin se llama **`ACIN#`** o **`AC_IN_KBC#` (terminado con el símbolo `#`)**: es **Active Low** → debe medir **0V** con el cargador conectado.
     - **Cómo funciona el circuito inversor cuando `ACIN#` es Active Low**: Un riel de `3.3V_AUX_S5` alimenta la línea `PWR_ACIN#` mediante una resistencia pull-up (`PR4480`), y esa línea va conectada al Drenador de un pequeño MOSFET Canal N (`PQ4415`, con Surtidor a GND). Cuando el cargador se conecta, el pin `VDD` (5V) del Charger pasa por un divisor de tensión (`100 kΩ` / `196 kΩ`) aplicando **3.3V** al Gate de `PQ4415`. El MOSFET conduce, tira los 3.3V a tierra y deja `ACIN#` en **0V** hacia el EC. Si `PQ4415` se daña o no recibe los 3.3V en su Gate, al EC le llegan `3.3V` en `ACIN#` e interpreta que **NO hay cargador conectado** (causando que los enables de 3V y 5V suban y caigan en bucle).

---

## 4. Diagnóstico de Laptops con Carga Exclusiva por USB-C (Power Delivery)

Para diagnosticar placas alimentadas por USB-C es imprescindible un tester USB-C (**Power-Z** o **2UUL Power Mac PW08**) conectado en serie:
- El cargador USB-C entrega inicialmente **5V** por defecto; el **Controlador PD (Power Delivery)** de la placa (ej. **`TPS65994`**) debe comunicarse por las líneas **CC (Communication Channel)** con el cargador para negociar **20V** (o 15V/19V).
- **Nota sobre el `TPS65994`**: requiere programación de firmware; al reemplazarlo conviene extraerlo de una placa donante del mismo modelo o contar con programador compatible.

### Interpretación rápida con el Tester USB-C:
1. **El tester muestra 5V CON sobreconsumo (amperaje alto)**:
   - En la gran mayoría de los casos indica que el **Controlador PD está en corto o defectuoso** (o un corto en su LDO de alimentación de 3.3V/5V).
2. **El tester muestra 5V SIN sobreconsumo (0.00A – 0.02A) y no sube a 20V**:
   - Apunta a **puerto USB-C físicamente dañado**, líneas `CC1`/`CC2` abiertas, fusible/diodos de protección iniciales abiertos, o falta de alimentación al controlador PD. (Usar tester de puerto USB-C para medir caída de tensión en `VBUS` y `CC`).
3. **El tester negocia 9V, 15V, 19V o 20V correctamente**:
   - Toda la etapa USB-C y el controlador PD están funcionando al 100%. A partir de aquí, el diagnóstico continúa exactamente igual que en una laptop de conector convencional (medir resistencia de sensado, Charger IC, 3V/5V ALW, EC, etc.).
