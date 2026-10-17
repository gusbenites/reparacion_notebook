---
name: notebook-repair-diagnostics
description: Diagnóstico experto y reparación a nivel componente de placas madre de notebooks (laptops) basado en la metodología de Xtreme PC RGB. Úsese cuando el usuario consulte sobre fallas de encendido, pantalla negra, cortos a tierra, secuencia de encendido (S5 a S0, EC, PCH, RSMRST#, SLP_S4#, PLT_RST#), medición de MOSFETs/componentes SMD, falla de carga o entrada de 19V/20V/USB-C (Charger IC, ACDET, ACOK, 25V Gate vs Canal P), fuentes buck/PWM (3V/5V ALW, LDO, Feedback, TON, PowerGood), lectura de esquemáticos y boardview, desactivación de RAM onboard (Memory Down Strap) o reprogramación de BIOS y limpieza de Región ME Intel.
---

# Diagnóstico y Reparación de Placas Madre de Notebook (Metodología Xtreme PC RGB)

Guía operativa paso a paso para diagnosticar y reparar placas madre de laptops a nivel componente, integrando el flujo de trabajo sistemático del canal **Xtreme PC RGB** y las herramientas de laboratorio disponibles.

## Archivos de Referencia Detallados

Cargue estos archivos con `read` según la etapa donde se encuentre la falla:

- `references/power-input-and-charger.md` — Etapa de entrada 19V/20V, MOSFETs de entrada Canal N (25V en Gate) vs Canal P (~9V por divisor de tensión + comparador + compuerta lógica), Charger ICs (`BQ24780S`, `BQ24800`, `ISL9538H`, `ISL88739`, arquitecturas NVDC de 8.5V/13.5V), diodo OR, `ACDET` (>2.4V), `ACOK`/`ACIN` y diagnóstico USB-C Power Delivery (PD).
- `references/buck-converters-and-ldo.md` — El ABC de 6 pasos para cualquier IC de fuente PWM (`VIN`, `EN`, `VREG/LDO`, `LX/SW` + MOSFETs Alta/Baja/DrMOS, `FB` divisor de tensión, `PGOOD` y resistencia `TON`), Load Switches (`TPS22966`) y **Método de Aislamiento de Micro-Cortos en LDOs** (cuando la fuente de banco marca ~18mA y la cámara térmica no detecta nada).
- `references/power-sequence-ec-pch-ram.md` — Lectura de tablas `PM Table` y `Power Plane` (estados S5 vs S0), requisitos del EC/KBC (`+3V_ALW_EC`, `LID_SW#`, `ACIN`, `PWR_SW#`, `S5_ON`), comunicación EC ↔ PCH (`EC_RSMRST#`, compuerta AND `ALW_PWRGD_3V_5V`, `PCH_RSMRST#`, `SIO_PWRBTN#`, `SLP_S4#`, `SLP_S3#`, `PLT_RST#`), subsistema DDR4 (`VDD` 1.2V, `VPP` 2.5V, `VTT` 0.6V, `VDDSPD` 3.3V, `DRAM_RST#` 1.2V) y pin ID de cargadores Gamer.
- `references/components-shorts-and-bios.md` — Medición profesional de MOSFETs (3 pines, SOIC-8 y Dual MOSFET, trampa de carga del Gate con el multímetro), diodos (Rectificador, Schottky, Zener, TVS), capacitores (acoplamiento AC/bootstrap con distinto voltaje en cada lado vs desacoplo a GND), tabla de caídas de tensión en escala de diodo por bobina, inyección segura de voltaje (1V), desactivación de RAM soldada (`Memory Down Strap` / `ONBOARD_RAM_CFG`), reprogramación de BIOS (1.8V/3.3V, WSON-8) y limpieza de Región ME Intel (`ME Analyzer` + `ME Injector`).
- `references/video-catalog-cases.md` — Catálogo indexado de casos reales de reparación de Xtreme PC RGB y Daniel Bustamante Sensei (Síntoma → Mediciones → Causa Raíz → Solución) y stock recomendado de componentes SMD e ICs.
- `references/bustamante-advanced-techniques-and-macbook.md` — Técnicas avanzadas de **Daniel Bustamante Sensei**: Reglas críticas ("¡No explotes tu mother!" al retirar un IC Buck, puentes en entrada, conflicto 19V vs Batería), **Método CAF (Corto, Abierto y con Fugas)** en capacitores/diodos/bobinas/BJT, secreto del capacitor de `ACDET` (47nF/100nF) en `BQ24780S`, detección de fallas de filtrado con botón `PEAK`, diagnóstico de **CPU/PCH/SoC muerto en 2 minutos** (por líneas USB `D+`/`D-` y Pin 8 BIOS vs VCORE), conversión de **RAM DDR3 1.5V a DDR3L 1.35V** (Offset `06`), conversión Discrete a UMA (**"La Bobina de Oro"** + Clear CMOS), truco del **"Dedo Mágico"** en Pin 22 Wi-Fi (`PLT_RST#`), diagnóstico de **MacBook (A1278/A1466: `ISL6259`, `U5110`, `U1900`, `SMC`)** y protocolo químico para placas mojadas (`Thinner Oro` + `Isopropílico`).
- `references/metadataVE-advanced-bios-and-diagnostics.md` — Técnicas de **Leonardo García (MetadataVE)**: Edición de BIOS Dell/HP/Lenovo (extracción de DMI/Service Tag/Windows Key, limpieza ME con Intel FIT, transferencia con `Ctrl+B`), diagnóstico de EC autoprogramable vs externo, señales `SUSON#`/`SYSON`/`ACOFF`/`PACIN`/`D/C#`/`VA_OFF`/`AD_ID`/`PS_ID`/`BATT_EN#`/`EDID`/`CPU_DRAMRST#`, OPAMPS y comparadores (`LM393`), Load Switches, protocolo de reballing con estaño en pasta, reset de ciclos de batería con NLBA, y distribución de corriente (por qué inyectar 1V y no 19V).
- `references/electrosotox-errors-and-techniques.md` — **ElectroSotox**: Los 10 errores más comunes al reparar laptops (OCP, PSID, "no todo lo que calienta está malo", medición con punta conectada primero, rango manual vs autorango, etc.), mecanismo de carga de firmware del KBC desde la BIOS principal, diagnóstico de MCP/PCH por patrón térmico, técnicas de inyección progresiva (1V→2V→3V), levantar bobinas para aislar fases, y valores de referencia rápidos.
- `references/quick-cases-routing.md` — **⚡ ENRAPIDOR DE CASOS**: Tabla de síntoma → causa probable → archivo de referencia a consultar. Úsala como punto de entrada cuando un equipo llega al taller.

---

## Flujo Maestro de Diagnóstico (Paso a Paso)

### Paso 0: Regla de Oro Antes de Energizar
1. **Desconectar siempre la batería** y todos los flex (teclado, pantalla eDP, Wi-Fi, disco) antes de manipular o medir la placa.
2. **NUNCA conectar el cargador ni la fuente de laboratorio sin antes medir caída de tensión en todas las bobinas (escala de diodo, punta ROJA a GND)**:
   - Si un MOSFET de alta (High-Side) de VCORE/VCCGT está en corto entre Drenador y Surtidor, al conectar 19V/20V pasarán directamente los 20V al CPU/GPU/PCH destruyéndolo de forma irreversible.
   - **¡PELIGRO MORTAL AL DESOLDAR UN IC CONTROLADOR BUCK! ("¡No explotes tu mother!")**: **NUNCA** alimentes la placa con 19V si retiraste el IC controlador PWM de una fuente Buck dejando soldados en la placa sus MOSFETs externos de alta y baja. Al quitar el IC, los **Gates quedan flotantes como una antena**, se autodisparan instantáneamente y dejan pasar los **19V directos** hacia la línea de salida (`3.3V`, `5V`, `1.2V RAM` o `VCORE`), quemando el CPU/PCH/EC y ambos MOSFETs. Si quitas un IC PWM y necesitas energizar, **levanta siempre antes la bobina de salida (`PL`) o retira el MOSFET de alta**.
   - **Descarte en 2 minutos de CPU/PCH/SoC muerto antes de trabajar en vano**: Si la bobina de `3.3V` o `1.0V/1.2V` está en corto a tierra (`0 Ω`), mide en los puertos **USB 2.0 y 3.0** las líneas de datos **`D+` y `D-` respecto a GND y entre sí**. Si `D+` y `D-` están en corto a tierra o entre sí (descartando el diodo ESD), el SoC/PCH está internamente perforado. En procesadores SoC (CPU+PCH), medir **Pin 8 de la BIOS a GND** (`0.4 Ω` = PCH en corto; placa muerta en ~2–6 mA) vs **Bobina VCORE a GND** (`0.25 Ω` = CPU en corto; placa da pulso a ~64 mA y corta).
3. **Valores de referencia en escala de diodo (Punta ROJA a GND, placa sin energía)**:
   - **Resistencia de sensado principal (`PR_SENSE` / `B+` / `PWR_SRC`)**: **400 mV – 550 mV**.
   - **Bobina de carga de batería** (la bobina gris más grande, cerca del conector de batería): **450 mV – 600 mV**.
   - **Bobinas de 3.3V y 5V Always (`+3VALW`, `+5VALW`)**: **300 mV – 450 mV** *(Nota: si el MOSFET de baja o Dual MOSFET integra un diodo Schottky, la bobina de 5V o 3V puede medir **150 mV – 180 mV** siendo totalmente normal)*.
   - **Bobina de Memoria RAM (`1.2V DDR4` / `1.35V DDR3L`)**: **100 mV – 280 mV** (o hasta ~37 mV con módulos instalados; al retirar la RAM sube el valor: truco rápido para identificar la bobina de RAM).
   - **Bobina de PCH / `+1.05V` / `+1.8V`**: **30 mV – 200 mV** (verificar en los capacitores superiores del PCH si comparten la misma caída de tensión).
   - **Bobinas de CPU (`VCORE`, `VCCGT`, `VCCSA`) y GPU (`NVVDD`)**: **Valores muy bajos (2 mV – 50 mV, p. ej. `0.008 V` a `0.022 V`), pero NUNCA `0.000 V` absoluto**. En GPUs modernas (RTX 30/40) y CPUs de baja impedancia, cambiar a **escala de Ohmios (Ω)** y restar la resistencia de las puntas: valores de **0.2 Ω – 0.5 Ω netos** son normales en GPU moderna; `0.0 Ω` neto es corto.
   - **Bobina de VRAM (`FBVDDQ`)**: **~50 mV – 90 mV** (50 Ω – 90 Ω).

---

### Paso 1: Clasificación por Comportamiento y Consumo en Fuente de Banco

Conectar a la fuente regulable (19V–20V; en equipos USB-C usar tester tipo Power-Z) con batería desconectada:
- **Consumo normal en Standby (S5, equipo apagado)**: **8 mA a 30 mA** (típicamente `< 20 mA`).
- **Caso A — La fuente se protege (OCP) o cae el voltaje a 0V al conectar**:
  - Corto directo en la línea de 19V/20V. Verificar si el corto está **antes** o **después** de la resistencia de sensado midiendo en escala de diodo un capacitor cerámico grande de entrada junto a las bobinas de CPU (`VIN` de alta). Si da ~400 mV, el corto está **antes** de la resistencia de sensado (jack, bobina de entrada, diodo TVS de 20V o capacitor antes del primer MOSFET). Si da `0 mV`, el corto está en la línea principal `B+`.
  - **Regla crítica si hay corto simultáneo en 19V, 3V y 5V**: **NUNCA empieces inyectando en 19V**. Diagnostica primero las salidas de 3V y 5V levantando un lado de sus bobinas (`PL`). Si un Load Switch (que recibe 5V y 3V) o un MOSFET de alta se puso en corto y unió los 5V con la línea de 3.3V, pudo haber enviado 5V al PCH (que soporta máx. 3.3V) matándolo. Si el PCH está en corto en 3.3V, no pierdas horas reparando la línea de 19V primero.
- **Caso B — Consumo 0.000 A (0 mA) y no enciende**:
  - Medir voltaje en el conector DC-IN (20V) y luego en la **resistencia de sensado principal**.
  - **Si NO hay 20V en la resistencia de sensado**: el bloqueo está en los dos MOSFETs de entrada o en el Charger IC (`ACDET`, `VCC`, `ACDRV`/Gate de 25V en Canal N, o divisor de tensión de ~9V en Canal P). Ver `references/power-input-and-charger.md`.
  - **Si SÍ hay 20V en la resistencia de sensado (o 8.5V/13.5V en arquitecturas NVDC)**: falta un voltaje primario en estado S5 (`+3VALW`, `+5VALW`, `+3V_RTC_LDO`) o una señal básica del EC (`ACIN`, `LID_SW#`, `S5_ON`). Ver `references/buck-converters-and-ldo.md`.
- **Caso C — Consumo Standby normal (15–30 mA), tiene 3V y 5V, pero al presionar el botón no hace nada**:
  - 1. Descartar **botón de encendido / encendido en teclado** (muy común en Lenovo/ASUS): verificar 3.3V en el pin `PWR_SW#` / `ON/OFFBTN#` y que caiga a 0V al pulsar, o puentear los pads de bronce junto al conector del teclado / usar el Novo Button lateral.
  - 2. Revisar la tabla **PM Table / Power Plane** en estado **S5 (AC ON)**: no basta con tener 3V y 5V; verificar **todos** los voltajes marcados como `ON` en S5 (ej. `+1.0V_PRIM`, `+1.8V_PRIM`, `+3.3V_ALW_PCH`, `+1.05V_M`), empezando por el **último voltaje de la lista S5** (ya que depende de los anteriores).
  - 3. Si todos los voltajes S5 están presentes, medir en el **EC (KBC)** y **PCH**: alimentación `+3V_ALW_EC`, `ACIN` (atento a si lleva `#` active-low = 0V o sin `#` active-high = 3.3V), `LID_SW#` (3.3V), `EC_RSMRST#` (3.3V), compuerta lógica AND intermedia (ej. `UZ6` que exige `EC_RSMRST#` + `ALW_PWRGD_3V_5V` + su propio pin 5 de VCC) hacia `PCH_RSMRST#` y `SIO_PWRBTN#`. Ver `references/power-sequence-ec-pch-ram.md`.
- **Caso D — Al pulsar encendido sube a ~100 mA – 250 mA y cae a 0 / se apaga**:
  - El EC y el PCH despertaron (`SLP_S4#` y/o `SLP_S3#` se activan por un instante), pero una fuente secundaria no logra sostenerse (por corto a la salida, falla de `Feedback` / resistencia `TON`, o ausencia de `PowerGood`).
  - Medir en qué bobina el voltaje intenta subir (ej. llega a 0.7V en vez de 1.2V en RAM y cae) o medir cuál es la última fuente de la secuencia S0 (ej. `+1.0VS_VCCIO`).
  - Si **todas** las fuentes hasta `+1.0VS_VCCIO` / `VCORE` suben correctamente por unos segundos y no hay cortos, sospechar de corrupción de **BIOS** (verificar tráfico en Pin 2 de la BIOS con osciloscopio).
- **Caso E — Enciende, se mantiene en ~400 mA – 800 mA, pantalla negra sin video (o reinicia en bucle)**:
  - 1. Verificar **subsistema de RAM DDR4**: además de `1.2V VDD` en la bobina, medir `VPP` (2.5V), `VTT` (0.6V), `VDDSPD` (3.3V) y sobre todo la señal **`DRAM_RST#` (`RAM_RESET#` = 1.2V)**. Si hay 1.2V en la bobina pero `DRAM_RST#` está en 0V, hay falla de comunicación con la RAM (módulo RAM onboard dañado → desactivar por hardware con `Memory Down Strap`).
  - 2. Verificar lectura de datos en **Pin 2 de la BIOS** con el osciloscopio al encender: si solo da un pulso corto pobre y queda plano en ~400 mA, reprogramar BIOS (haciendo backup previo siempre).
  - 3. Si demora 20–30 seg en dar video, se apaga exactamente a los 30 minutos, ventiladores al 100% o pantallazos azules aleatorios: **Región ME Intel sucia/corrupta** → limpiar con `ME Analyzer` + `ME Injector` usando imagen `rgn.bin` (Stock / Unconfigured).

---

## Equipo Disponible en el Laboratorio del Usuario

Al guiar al usuario en mediciones prácticas, aprovecha sus herramientas específicas:
- **Osciloscopio**: Hantek DSO2C15 (100 MHz, 2 canales) — ideal para medir el cristal de 32.768 kHz del EC/PCH, trenes de datos en el Pin 2 de la BIOS, switcheo PWM en bobinas (`LX`) y caída/subida de `RSMRST#`, `PLT_RST#` y `PWROK`.
- **Programador SPI**: CH341A (con zócalo y pinza SOIC8; recordar verificar con multímetro 3.3V o usar adaptador de 1.8V en el pin 8 antes de conectar la pinza; conectar primero la pinza al chip sin energía y luego el USB).
- **Programador universal**: TL866CS — lectura/escritura rápida de BIOS SPI, EEPROM, NAND, ATMEL.
- **Analizador lógico**: 24 MHz, 8 canales — decodificación de tramas I2C/SMBus (SPD de RAM, comunicación Charger-EC-Batería), SPI y UART.
- **Tarjeta POST** con chip Xilinx — códigos POST de diagnóstico LPC/eSPI.
- **Arduino Uno / Nano y NodeMCU ESP32-S3** — puente serie, inyección/lectura I2C/SPI.
- **Skill `boardview-analysis`** (`~/.agents/skills/boardview-analysis/scripts/gencad.py`) — úselo siempre que exista un archivo `.cad` disponible para localizar componentes (`comp`, `find`), trazar nets (`net`) o buscar componentes cercanos (`near`).
