# ⚡ Casos Rápidos — Enrutador de Síntomas a Diagnóstico

Tabla de síntoma → causa probable → archivo de referencia a consultar. Úsala como punto de entrada cuando un equipo llega al taller.

---

## Síntoma → Causa Probable → Archivo a Consultar

| Síntoma | Consumo | Causa Probable | Archivo a Consultar |
| :--- | :--- | :--- | :--- |
| **No enciende, 0 mA, no hace nada** | 0 mA | MOSFET de entrada en corto, o falta voltaje principal (B+) | `power-input-and-charger.md` |
| **No enciende, 0 mA, no hay pico inicial** | 0 mA | Corto en línea principal (capacitor o MOSFET) | `power-input-and-charger.md` + `electrosotox-errors-and-techniques.md` |
| **Fuente se protege (OCP) al conectar** | Pico alto | Corto directo en 19V/20V (antes o después de resistencia de sensado) | `power-input-and-charger.md` |
| **Corto simultáneo en 19V, 3V y 5V** | Pico alto | Load Switch en corto uniendo 5V con 3.3V (peligro para PCH) | `power-input-and-charger.md` + `buck-converters-and-ldo.md` |
| **Tiene 20V pero no pasa a la resistencia de sensado** | 0 mA | MOSFET de entrada bloqueado (Canal N: falta 25V en Gate; Canal P: Gate no baja de 18V) | `power-input-and-charger.md` |
| **Tiene 20V en sensado pero no hay 3V/5V** | ~15-30 mA | Falla en IC de fuente 3V/5V (VIN, EN, LDO, FB, PGOOD) | `buck-converters-and-ldo.md` |
| **Tiene 3V y 5V pero no enciende** | ~15-30 mA | Falla en EC (KBC): no libera `RSMRST#`, `S5_ON`, o `PBTN_OUT#` | `power-sequence-ec-pch-ram.md` |
| **Al pulsar encendido sube a ~100 mA y cae** | 100→0 mA | Fuente secundaria no logra sostenerse (corto en salida, falla FB/TON) | `buck-converters-and-ldo.md` |
| **Al pulsar encendido sube a ~250 mA y se apaga a los 4 seg** | 250→25 mA | Falla en fuente de RAM (Enable del PCH OK, pero fuente no sostiene) | `buck-converters-and-ldo.md` + `power-sequence-ec-pch-ram.md` |
| **Enciende, sube a ~500 mA y queda fijo sin video** | 500 mA | Falta señal `DRAM_RST#` (Pin 108 DDR4) o fuente de video no activa | `power-sequence-ec-pch-ram.md` |
| **Enciende, sube a ~700 mA y se reinicia en bucle** | 700→185 mA→700 mA | BIOS Loop (corrupción de firmware, `PLT_RST#` cayendo cada 3-5 seg) | `components-shorts-and-bios.md` + `metadataVE-advanced-bios-and-diagnostics.md` |
| **Enciende, ~400-600 mA, sin video, sin reinicio** | 400-600 mA | Corrupción de BIOS (sin actividad SPI en Pin 2) o falta de comunicación CPU-RAM | `components-shorts-and-bios.md` + `metadataVE-advanced-bios-and-diagnostics.md` |
| **No carga batería** | Normal | MOSFET de carga, `BQ24780 ACDET`, o batería con celdas dañadas/bloqueadas | `power-input-and-charger.md` + `metadataVE-advanced-bios-and-diagnostics.md` |
| **No carga batería, LED parpadea** | Normal | Señal `PS_ID` (Dell) o `AD_ID` (HP) incorrecta/ausente | `metadataVE-advanced-bios-and-diagnostics.md` |
| **USB-C: 5V con sobreconsumo** | 5V + 1.5A | Controlador PD en corto | `power-input-and-charger.md` |
| **USB-C: 5V sin consumo** | 5V + 0A | Puerto USB-C dañado, líneas CC abiertas, o PD sin alimentación | `power-input-and-charger.md` |
| **USB-C: 20V negociados pero no enciende** | Normal | El PD está bien, diagnostico como laptop normal (ver casos anteriores) | `power-input-and-charger.md` |
| **Pantalla negra pero hay actividad (LED teclado)** | Normal | Problema de video: chip de GPU, backlight, o conector LVDS/eDP | `metadataVE-advanced-bios-and-diagnostics.md` (señal EDID) |
| **Pantalla blanca** | Normal | Falta `+LCDVDD` (3.3V al panel T-CON) | `metadataVE-advanced-bios-and-diagnostics.md` |
| **Video opaco (se ve con linterna)** | Normal | Backlight: falta `DISPOFF#`/`BL_EN` o señal `PWM` | `metadataVE-advanced-bios-and-diagnostics.md` |
| **Se apaga a los ~30 segundos** | Normal | Falla térmica o BIOS corrupta con watchdog | `components-shorts-and-bios.md` |
| **Se apaga al conectar batería + cargador** | Corto | MOSFET de entrada en corto (choque 19V vs 14.4V) | `power-input-and-charger.md` |
| **Funciona con cargador pero no con batería** | 0 mA | Batería descargada/bloqueada, o MOSFET de carga en corto | `power-input-and-charger.md` + `metadataVE-advanced-bios-and-diagnostics.md` |
| **Lenta con cargador (throttling)** | Normal | Señal `CH_PROHOT` o `ACDET` fuera de rango | `metadataVE-advanced-bios-and-diagnostics.md` |
| **Error "connected AC adapter has lower wattage"** | Normal | MOSFET de entrada dañado (caída anormal) o `AD_ID` incorrecto | `power-input-and-charger.md` + `metadataVE-advanced-bios-and-diagnostics.md` |
| **No apaga desde el botón** | Fijo | EC/PCH colgado esperando PowerGood de una fuente que falla | `buck-converters-and-ldo.md` + `power-sequence-ec-pch-ram.md` |
| **5 pitidos (beeps) al encender** | Normal | Error de RTC/pila CMOS o falta de pantalla | `metadataVE-advanced-bios-and-diagnostics.md` |
| **Error MPM (Manufacture Programming Mode)** | Normal | BIOS necesita limpieza de padding DMI | `metadataVE-advanced-bios-and-diagnostics.md` |
| **RAM onboard dañada (pantallazos azules)** | Normal | Chips RAM soldados defectuosos | `components-shorts-and-bios.md` (Memory Down Strap) |
| **GPU dedicada muerta (pantalla negra)** | Normal | Conversión Discrete a UMA | `bustamante-advanced-techniques-and-macbook.md` (La Bobina de Oro) |

---

## Cómo Usar Esta Tabla en el Taller

1. **El equipo llega** → Observa el síntoma principal (¿no enciende? ¿no carga? ¿pantalla negra?)
2. **Mide el consumo** en la fuente de laboratorio (¿0 mA? ¿500 mA? ¿se reinicia?)
3. **Busca en la tabla** → Obtén la causa probable y el archivo de referencia a consultar
4. **Carga el archivo de referencia** con `read` para obtener la metodología detallada de diagnóstico
5. **Sigue el flujo paso a paso** del archivo para confirmar la causa raíz
6. **Si el síntoma no está en la tabla** → Carga el `SKILL.md` principal y sigue el flujo maestro desde el Paso 0

---

## Archivos de Referencia Cruzados

### `power-input-and-charger.md`
- **Ver también**: `metadataVE-advanced-bios-and-diagnostics.md` (señal AD_ID, PS_ID, cálculo de divisores ACDET), `electrosotox-errors-and-techniques.md` (inyección segura, MOSFETs de entrada)

### `buck-converters-and-ldo.md`
- **Ver también**: `power-sequence-ec-pch-ram.md` (señales de habilitación SLP_S4#, SLP_S3#), `metadataVE-advanced-bios-and-diagnostics.md` (OPAMPS, Load Switches, fuentes buck)

### `power-sequence-ec-pch-ram.md`
- **Ver también**: `buck-converters-and-ldo.md` (fuentes secundarias), `metadataVE-advanced-bios-and-diagnostics.md` (edición BIOS, señales SUSON#, ACOFF)

### `components-shorts-and-bios.md`
- **Ver también**: `metadataVE-advanced-bios-and-diagnostics.md` (edición BIOS Dell/HP/Lenovo, limpieza ME), `bustamante-advanced-techniques-and-macbook.md` (método CAF, medición de MOSFETs)

### `bustamante-advanced-techniques-and-macbook.md`
- **Ver también**: `power-input-and-charger.md` (reglas de seguridad al desoldar ICs), `electrosotox-errors-and-techniques.md` (errores comunes), `metadataVE-advanced-bios-and-diagnostics.md` (señales de encendido por arquitectura)

### `metadataVE-advanced-bios-and-diagnostics.md`
- **Ver también**: `components-shorts-and-bios.md` (limpieza ME, programación BIOS), `bustamante-advanced-techniques-and-macbook.md` (método CAF, diagnóstico de CPU/PCH), `electrosotox-errors-and-techniques.md` (errores comunes, inyección de voltaje)

### `electrosotox-errors-and-techniques.md`
- **Ver también**: `power-input-and-charger.md` (MOSFETs de entrada, seguridad), `bustamante-advanced-techniques-and-macbook.md` (método CAF, diagnóstico de CPU/PCH), `metadataVE-advanced-bios-and-diagnostics.md` (edición BIOS, señales de encendido)
