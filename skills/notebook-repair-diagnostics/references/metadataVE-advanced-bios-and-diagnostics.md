# Técnicas Avanzadas de Leonardo García (MetadataVE) — Diagnóstico Laptop

Compendio técnico extraído de los videos y cursos de **Leonardo García (MetadataVE)**, especialista en reparación de laptops a nivel electrónico, edición de BIOS y herramientas de laboratorio.

---

## 1. Edición de BIOS Dell / HP / Lenovo — Extracción de DMI, Service Tag y Windows Key

### A. Estructura del BIOS Dell (Descriptor + ME Region + BIOS Region)
- En Dell modernas (Inspiron 3593, Vostro 3400, etc.), el BIOS puede estar dividido en **2 chips SPI** (ej. 8 MB + 16 MB = 24 MB total) o en **1 solo chip de 16 MB**.
- El **Descriptor** y la **Región ME (Management Engine)** están en el primer chip (8 MB). La **BIOS Region** está en el segundo chip (16 MB).
- **Problema**: Si se abre solo el chip de 16 MB en UEFITool o ME Analyzer, no aparece el Descriptor ni el ME. Hay que **unir ambos binarios en uno solo**:
  1. En HxD: Abrir `UC5` (8 MB) y `UC6` (16 MB). Copiar todo el contenido de `UC6` (`Ctrl + A`, `Ctrl + C`), ir al final exacto de `UC5` (offset `0x800000`, justo después de `0x7FFFFF`) y pegar insertando (`Ctrl + V`).
  2. Guardar como `UC5+UC6.bin` y verificar que pese exactamente **24 MB (24,576 KB)**.

### B. Extracción de la Información del Cliente (DBAR / Service Tag / Windows Key)
- **Buscar en UEFITool**: `Search` (`Ctrl + F`) → pestaña `Text`, desmarcar `Unicode`, buscar **`DBAR`** (en Dell) o `$BVDT$` (en Lenovo).
- El resultado apunta al primer `Padding` (no vacío) dentro de la región BIOS. Contiene:
  - **Service Tag / Serial**: En el offset relativo `0x2000` dentro del Padding.
  - **Windows Key**: En el offset relativo `0x9000` dentro del Padding.
  - **MPM Lock**: Estado de bloqueo de Manufacturing Programming Mode.
  - **Datos DMI**: Modelo, SKU, Feature Byte, Board ID, Flash Lock.

### C. Transferencia al BIOS Nuevo (Pegar Escribiendo — NO Pegar Insertando)
1. Extraer el Padding con `Extract as is...` en UEFITool.
2. En HxD: Abrir el BIOS nuevo descargado de la web → ir al offset donde comienza la región BIOS (ej. `0x400000` en Dell Vostro, `0x210000` en Lenovo V330) → `Ctrl + A`, `Ctrl + C` en el Padding extraído → `Ctrl + B` (**Pegar escribiendo / Replace**, NO `Ctrl + V` que inserta bytes y altera el tamaño).
3. Verificar que el tamaño final sea exactamente el correcto (ej. `16,384 KB` para 16 MB).

### D. Limpieza de Región ME con Intel FIT (Flash Image Tool)
1. Arrastrar el BIOS unido al `fit.exe` para que cree la carpeta `Decomp`.
2. `Build` → `Build Settings...` → `Generate Intermediate Files` → **`No`** → `OK`. Guardar configuración como `.xml` y **cerrar FIT**.
3. En la carpeta `Decomp`: Reemplazar `BIOS Region.bin` por el nuevo (con la info del cliente inyectada) y `ME SubPartition.bin` por el archivo de ME limpio extraído del instalador oficial.
4. Volver a abrir `fit.exe`, cargar el proyecto `.xml` y darle a **`Build Image` (F5)**.
5. FIT genera automáticamente `outimage.bin` (completo) y también los archivos cortados listos para grabar (`outimage_1.bin` para el chip 8 MB, `outimage_2.bin` para el chip 16 MB).

### E. Específico HP — Eliminar error MPM (Manufacture Programming Mode)
1. Descargar el `.exe` de HP → Ejecutar → `Siguiente` → `Acepto` → elegir **`Copy`** (Copiar archivos) → guardar en carpeta de trabajo.
2. En UEFITool, extraer el **primer Padding al inicio del archivo** (contiene MPM Lock + Windows Key + DMI).
3. Inyectar en el BIOS nuevo con HxD (`Ctrl + B`).
4. **Trasplante opcional de NVRAM**: Extraer los dos bloques de 256 KB de NVRAM (offsets `0x76A000` y `0x7AA000`) y pegarlos en el BIOS nuevo para evitar problemas con BitLocker.

### F. Específico Lenovo — Editar archivo `.CAP` desde la web
1. Descargar el `.exe` de Lenovo → Abrir con **InnoExtractor** → extraer el archivo `.CAP` (más grande que la BIOS Region).
2. En HxD: Cortar el encabezado Capsule (buscar texto `Lenovo`, ir al inicio del bloque BIOS y borrar desde ahí hasta el principio).
3. Cortar la cola sobrante (copiar la última fila de bytes del original y buscarla en el `.CAP` para borrar todo lo que sobra por debajo).
4. Inyectar en el BIOS original del cliente en el offset correcto con `Ctrl + B`.

### G. Específico HP — Extraer `.bin` encriptados del `.exe`
1. Descomprimir el `.exe` con WinRAR/7-Zip.
2. Buscar el archivo con el **BID (Board ID)** correcto (buscar texto `BID` en el dump original del cliente, ej. `BID0831E`).
3. **Truco**: Si el instalador de HP no deja extraer, renombrar **otro** archivo `.bin` de la carpeta como `FV.bin` y ejecutar el extractor. Esto habilita la opción `Copy`.
4. Extraer y verificar que el archivo desencriptado mida exactamente `8,192 KB` (8 MB).

### H. Programar EC en notebooks Gamers modernas (ITE IT8226E)
- **Peligro**: En notebooks Gamers modernas con EC **ITE IT8226E**, el conector del teclado va a un **segundo microcontrolador** (teclado RGB), NO al EC principal. Conectar el programador al conector del teclado **quema el controlador de teclado y/o el bloque USB del PCH**.
- **Solución**: Usar un **adaptador ZIF de programación fuera de placa (Socket QFP128/LQFP128)** conectado al programador SVOD.
- **Truco indispensable**: Hay que **soldarle un chip BIOS SPI (ej. 1 MB)** en la placa del adaptador ZIF para que el software del SVOD detecte el adaptador correctamente (bug/requisito del hardware).
- Colocar el EC nuevo en el zócalo con el Pin 1 hacia abajo, seleccionar el zócalo inferior ITE en SVOD, dar `Read ID`, cargar el binario `.bin` y `Write + Verify`.

---

## 2. Técnicas de Diagnóstico Avanzadas

### A. Cómo Saber si un EC se Autoprograma o Necesita Firmware Externo
- Si la placa tiene dos chips BIOS (ej. 16 MB + 8 MB = 24 MB):
  - Leer el chip de 16 MB en el programador y buscar texto en hexadecimal.
  - Si aparece la cadena **`ITE`** o el modelo del EC (ej. `IT5571`), significa que el bloque del firmware del EC está **dentro del chip SPI externo** y el EC **se autoprograma** al alimentarse.
  - Al soldar un EC nuevo virgen y conectar el cargador, este se autoprograma solo desde el BIOS principal.

### B. Señal `SUSON#` / `SYSON` y Fallas de EC (HP 240 G6)
- En HP con EC **ITE IT8887HE**, la señal `SUSON` sale del **Pin 35 del EC** y habilita la fuente de RAM (1.2V/1.35V).
- Si el BIOS está corrupto en la sección que gestiona la transición de encendido, el EC no libera `SUSON` al presionar el botón, dejando la fuente de RAM en 0V y el equipo en un bucle de prender/apagar.
- **Diagnóstico**: Medir el Pin 35 del EC con osciloscopio al presionar el botón. Si se queda clavado en 154 mV (nivel bajo), la falla está en el firmware del EC/BIOS.
- **Solución**: Reprogramar el chip BIOS con un dump limpio.

### C. Señal `ACOFF` en Lenovo G50 (`NM-A311` con `BQ24737`)
- La señal **`ACOFF`** viene del EC y **se activa en nivel alto (3.3V)** cuando el EC quiere cortar el cargador.
- **En estado normal**: `ACOFF` debe estar en **0V** (Tierra).
- Si el firmware del EC está corrupto, puede levantar `ACOFF` a 3.3V durante la secuencia de encendido, tirando `PACIN` a tierra y cortando los 20V de la placa a los ~2 segundos.
- **Diagnóstico**: Medir `ACOFF` con osciloscopio. Si está en 0V y de pronto pega un pulso a 3.3V a los 2 segundos de encender, la falla es corrupción de firmware del EC.
- **Solución**: Reprogramar el EC mediante el conector de teclado con SVOD (no usar modo I2C porque tarda >15 min; si da error *ITE Busy*, presionar el botón de encendido al conectar).

### D. Señal `PACIN` en Lenovo G480 AMD (`BQ24737` con MOSFETs Canal P)
- Los MOSFETs de entrada son **Canal P** (necesitan `V_Gate` < `V_Source` para conducir).
- El divisor resistivo de los Gates de `PQ301` y `PQ302` se activa con la señal **`PACIN`** (que proviene del Charger IC y del EC).
- **Escenario Normal (`PACIN = 3V`)**:
  - Los 3V de `PACIN` saturan un MOSFET Canal N que pone a tierra el divisor de Gates, fijando los Gates en **~8V–8.8V** (muy inferior a los 19V del Source) → Ambos MOSFETs conducen y pasan los 19V a la resistencia de sensado → Se genera **`B+`**.
- **Escenario de Falla (`PACIN = 0V`)**:
  - El MOSFET Canal N no conduce. Un transistor PNP intermedio une el Surtidor (18.4V) con el Gate → Ambos MOSFETs quedan cerrados → **0V en `B+`**.
- **Señal `D/C#` (Pin 32 del KBC)**: Cuando el KBC activa `D/C#` a nivel alto (3.3V) para desconectar el adaptador, un transistor PNP interno envía los 19V directamente al Gate del MOSFET Canal P `PQ1`, abriéndolo y bloqueando el paso del cargador, permitiendo que la batería (11V) pase sin caída de diodo.

### E. Señal `CPU_DRAMRST#` en DDR4 (Pin 108 del Slot DDR4)
- En memoria RAM DDR4, el reset se mide en el **Pin 108** del slot (NO en el Pin 202 como en DDR3).
- Si `PLT_RST#` está presente (3.3V) pero `CPU_DRAMRST#` solo sube a 1.2V y hace un pequeño pulso de reset sin los pulsos posteriores de entrenamiento de memoria, apunta a **corrupción de BIOS**.
- **Osciloscopio**: Medir Pin 108 del slot DDR4 al encender. Si solo hay un tren de pulsos corto y luego la placa se apaga en bucle, el BIOS está corrupto.

### F. Señal `EDID` — Diagnóstico de Video por Conector LVDS/eDP
- El **EDID** es el bus I2C por donde la placa lee la información de identificación de la pantalla antes de habilitar el video.
- **Pines típicos**: `+EDID_VDD` (3.3V), `EDID_CLK` (Pin 5), `EDID_DATA` (Pin 6) del conector LVDS.
- **Diagnóstico**: Si al encender no hay tren de pulsos en `EDID_CLK`/`EDID_DATA`, la placa no detecta la pantalla → No habilita `+LCDVCC` ni el backlight → Pantalla muerta (ni siquiera se ilumina con linterna).
- **Simulación de fallas**:
  - Sin señal EDID → La pantalla queda totalmente muerta (ni backlight ni iluminación).
  - Sin canal `TXOUT0` → Imagen distorsionada teñida de color ROJO.
  - Sin canal `TXOUT1` → Imagen alterada con predominancia de VERDE.
  - Sin canal `TXOUT2` o sin reloj `TXCLK` → Backlight encendido pero sin imagen.
  - Sin alimentación `+LCDVCC` (pero con EDID presente) → Pantalla completamente BLANCA (todos los píxeles abiertos dejan pasar la luz).

### G. Señal `PS_ID` en Dell — Solo Afecta Carga, NO Encendido
- El pin central de los cargadores Dell usa un protocolo **1-Wire** (EEPROM `DS2501`/`DS2502` dentro del cargador).
- El pin central tiene **~3.3V de pull-up desde la placa madre** (NO desde el cargador).
- **Diagnóstico**: Al enchufar el cargador original, el osciloscopio muestra una **trama digital 1-Wire** en el pin central.
- **Sin `PS_ID`**: El equipo **enciende y da video perfectamente**, pero **no carga la batería** (y en algunos modelos limita la frecuencia del CPU).
- **Regla**: Si una Dell no enciende con la fuente de laboratorio, la falla NO es por falta del pin central.

### H. Señal `VA_OFF` en Sony Vaio — Circuito de Protección Enclavado
- En Sony Vaio, existe un circuito de protección llamado **`VA_OFF`** que puede bloquear completamente el paso de corriente a la placa.
- **Tiradores de `VA_OFF` a Tierra**:
  1. **Detector de subtensión en `VIN`**: Si `VIN` está en 0V.
  2. **Detector de sobretensión (OVP > 22V)**: Un comparador activa la protección si el cargador supera los 22V–23V.
  3. **Circuito de enclavamiento con `3V_RTC`**: Una cadena de inversores alimentados por la pila CMOS puede mantener `VA_OFF` clavado a tierra.
- **Solución (Truco de oro para Sony Vaio)**: Desconectar el cargador → **Retirar la pila de BIOS (RTC) y puentear con una pinza los contactos positivo y negativo del portapila** (o el jumper de reset RTC) para descargar el circuito lógico → Al volver a conectar el cargador, el consumo vuelve a la normalidad.

### I. Señal `AD_ID` en HP Omen — Diferencias entre `AD_TYPE` y `AD_SELECT`
- **HP Omen** utiliza una **resistencia interna dentro del cargador** entre los 19V y el pin central (`AD_ID`):
  - 65W: ~400 kΩ → Genera 0.4V–0.5V en `AD_ID`.
  - 90W: ~309–320 kΩ → Genera ~0.5V.
  - 150W: ~139 kΩ → Genera 1.10V–1.13V.
  - 200W: ~110 kΩ → Genera 1.42V–1.46V.
  - 230W: ~86 kΩ → Genera ~1.80V–2.13V.
- El pin `AD_ID` cuenta con un **diodo Zener de protección de 5.6V** que salvaba al EC cuando le inyectaban 19V directamente.
- **`AD_TYPE` (Pin 67 del EC)**: Depende de la resistencia del cargador conectado.
- **`AD_SELECT` (Pin 73 del EC)**: Fijo por resistencias de la placa (strap de hardware). El EC compara `AD_TYPE` contra `AD_SELECT`.
- Si el voltaje de `AD_ID` es menor que el de `AD_SELECT`, el equipo puede no encender, no cargar, o sufrir *throttling*.

### J. Señal `BATT_EN#` en ASUS — El Tornillo que Carga Baterías
- En notebooks ASUS con batería interna, existe un **tornillo de fijación** junto al conector de la batería conectado al pin **`BATT_EN#`** (activo en nivel bajo).
- El aro de cobre del orificio del tornillo está conectado a `BATT_EN#` y aislado de GND en la placa.
- **Si el técnico olvida colocar ese tornillo**, `BATT_EN#` queda en nivel alto y el Charger/EC no habilita la carga aunque haya comunicación SMBus.
- **Síntoma**: LED ámbar de batería encendido pero la fuente marca apenas 11 mA (sin carga).

### K. Resetear Ciclos de Batería con Analizador NLBA
- En algunos casos, el chip inteligente (BMS) de la batería deshabilita por software sus MOSFETs internos de carga y descarga (`Charging/Discharging FET Disabled`), dejando 0V en el conector aunque las celdas estén intactas.
- **Procedimiento con NLBA**:
  1. Leer la batería por SMBus.
  2. **`Unseal`** para obtener `Full Access`.
  3. **`Clear Chip Errors`** (borra los flags de error).
  4. Escribir ciclos de carga a `1` y volver a **`Seal`**.

---

## 3. Circuitos Específicos — OPAMPS, Load Switches, Comparadores

### A. Amplificadores Operacionales (OPAMPS) — Teoría Aplicada
- **Entradas**: No Inversora (`+`) e Inversora (`-`). **Salida**: Satura hacia `+VCC` si `V+ > V-`, o hacia GND si `V- > V+`.
- **Tipos de salida**:
  - **Push-Pull**: Entrega directamente el voltaje `+VCC` cuando `V+ > V-`.
  - **Colector Abierto (Open Collector, ej. `LM393`)**: Cuando `V+ < V-`, conecta la salida a GND. Cuando `V+ > V-`, abre (alta impedancia), permitiendo que una resistencia pull-up eleve la línea.
- **Comparador típico en entrada (`LM393` en HP DV4/DV6/CQ40)**:
  - **Pin 6 (Inversora `-`)**: Referencia fija de **1.24V**.
  - **Pin 5 (No Inversora `+`)**: Recibe `VIN` mediante divisor de **100 kΩ / 10 kΩ** → Con 19V da **1.72V**.
  - Con 19V: `1.72V > 1.24V` → Salida en colector abierto → `PACIN`/`ACIN` suben a **~4.0V–4.3V** → Activan MOSFETs de entrada.
  - Con 13V: `1.18V < 1.24V` → Salida a tierra → MOSFETs se bloquean → Se corta `B+`.

### B. Load Switches — Interruptores de Voltajes Secundarios
- Los **Load Switches** convierten voltajes Always (`+3VALW`, `+5VALW`, `+1.8VALW`) en voltajes secundarios (`+3VS`, `+5VS`, `+1.8VS`) cuando reciben la orden de `SLP_S3#` (`SUSB#`).
- **Corte de voltaje secundario**: Si un Load Switch tiene su salida en corto a tierra (ej. capacitor cerámico), puede generar sobreconsumo inicial en S5 y apagado rápido al encender.
- **Inyección de voltaje**: Como no se sabe si esa línea es de 1.1V, 1.5V, 1.8V, 3.3V o 5V, **siempre inyectar 1V** por seguridad.
- **Síntoma típico**: El equipo enciende por ~500–600ms y se apaga (corto en línea secundaria S0).

### C. Circuito de Pantalla — Señales `DISPOFF#`, `BKOFF#`, `BL_EN`, `INVT_PWM`
- **Alimentación de Backlight (`+LEDVDD` / `B+`)**: 19V (o 11V–12V con batería). Presente incluso en S5.
- **Habilitación de Backlight (`DISPOFF#` / `BKOFF#` / `BL_EN`)**: Debe tener **3.3V** para encender. En 0V apaga el backlight.
- **Control de Brillo (`INVT_PWM`)**: Señal PWM del PCH/CPU. A brillo mínimo ~200Hz, a brillo máximo ~1kHz. En BIOS/arranque siempre arranca a brillo máximo (multímetro debe medir 3.3V).
- **Causa típica**: El KBC pone `EC_BKOFF#` a tierra, manteniendo el backlight apagado. Solución: Cortar la pista desde el KBC para liberar la señal (sin reemplazar el KBC).
- **Pantalla blanca**: Si el GPU lee EDID pero `+LCDVCC` está en 0V, todos los píceles quedan abiertos dejando pasar la luz trasera → Pantalla completamente blanca.

---

## 4. Protocolos de Reparación Específicos

### A. Reparación de Pistas Rotas Debajo de KBC/EC (Lenovo G475 AMD)
- Por sulfatación o golpes, las pistas debajo del KBC (bus LPC `LAD0..3`, `LPCCLK`, `PLT_RST#`) pueden quedar cortadas.
- **Procedimiento**:
  1. Aplicar flux y desoldar el KBC dañado.
  2. Con bisturí, raspar los vías circulares debajo del área del KBC.
  3. Utilizar **alambre de cobre esmaltado** para soldar jumpers desde el centro de cada vía.
  4. Aplicar **máscara UV (Solder Mask)** sobre los jumpers y curar con lámpara UV.
  5. Instalar KBC nuevo, alineando por esquinas y presionando los pines sobre los jumpers.
  6. Verificar pin por pin con aguja bajo microscopio que ninguna pata se mueva.

### B. Reballing de EC BGA (Encapsulado Ball Grid Array)
- **Herramientas recomendadas**: Stencils **Amaoe** (kit MacBook/Mac 4), base imantada (Qianli/Xinzhizao), espátula flexible (Mechanic/Riff).
- **Procedimiento**:
  1. Medir en modo diodo los pads principales (en buen estado: 424–500+ mV).
  2. Secar el estaño en pasta (presionar suavemente sobre papel secante, sin raspar).
  3. Rellenar todos los orificios del stencil con la espátula.
  4. Estación de aire caliente a **450°C y 60% de aire**, comenzando a 5cm de distancia.
  5. Cuando el estaño empieza a brillar, acercar la boquilla hasta que todas las esferas se formen.
  6. Levantar el stencil suavemente (sin forzar).
  7. Aplicar una gota de flux y dar un último toque de aire caliente para alinear las esferas por tensión superficial.

### C. Programación de EC ENE KB9542QG en Acer Nitro (`LA-L973P`)
- **La trampa de los 128 KB vs 160 KB**: El firmware del EC para `KB9542QG` es de **160 KB**, no de 128 KB como aparece en muchos dumps de internet (Vinafix/Telegram). El software SVOD detecta el ID y configura 128 KB por defecto, truncando la lectura.
- **Solución**:
  1. Usar **EC Finder** cargando el archivo de BIOS oficial y seleccionando la **opción 2** para extraer el binario limpio de 160 KB.
  2. En SVOD: Seleccionar `ENE` → `Select Motherboard` → **LA-L973P** (paso 0.5mm).
  3. Cambiar manualmente el parámetro `Config` de 128 KB a **160 KB**.
  4. Cargar el binario de 160 KB y dar `Write + Verify`.
  5. Al alimentar la placa, enciende el LED testigo y arranca.

### D. Reballing con Estaño en Pasta (Alternativa a Esferas Preformadas)
- **Ventajas**: Menor estrés térmico, no hace falta tener botes de esferas de distintos calibres, el flujo ya viene incorporado.
- **Procedimiento**:
  1. Limpiar el chip BGA y dejar los pads planos.
  2. Fijar el stencil con cinta en los 4 lados.
  3. Esparcir estaño en pasta uniformemente con espátula (secándolo primero sobre servilleta).
  4. Aplicar calor de forma homogénea y en movimiento constante desde los bordes hacia el centro, **sin quedarse quieto** para evitar que el estaño "hierva".
  5. En pocos segundos la pasta colapsa y forma las esferas.
  6. Desmoldar, aplicar un poco de flujo y dar un pase de aire para redondear.
  7. **NUNCA hacer reflow** (pistola de calor sin stencil) — siempre reballing completo.

### E. Recuperación de `U19` en Shuttle `71R-C14CU4-T810` (Sin el Chip)
- Si el switch BGA `U19` está abierto (sin corto ni calentamiento) y no se tiene repuesto:
  - Puente entre capacitor **`C460` y `C438`** (unir `+5VA` con `+5VS`).
  - Puente entre capacitor **`C471` y `C464`** (unir `+3.3VA` con `+3.3VS`).

### F. Reballing del PCH/FCH — Crítica al Reflow Casero
- Cuando un chip BGA está 100% sano internamente (solo fallan las esferas de soldadura), un reflow casero (pistola de calor por 2-3 minutos):
  - Dura pocos días generando reclamos de garantía.
  - O **quema/pone en corto internamente el chip**, arruinando una placa con 90-95% de probabilidad de recuperación.
- Si no se posee estación de Reballing, **derivar el trabajo a un laboratorio especializado**.

---

## 5. Señales de Encendido por Arquitectura

### A. Lenovo G480 AMD (KBC + FCH Hudson)
| Estado | Señal | Valor | Origen |
| :--- | :--- | :--- | :--- |
| **G3** | `RTCVCC` | 3.0V–3.3V | Pila CMOS / LDO `PU102` / `+3VLP` |
| **S5** | `VIN` | 19V–20V | Conector `JDC1` → fusible → bobina `PL101` |
| **S5** | `ACDET` | ~2.7V | Divisor 390kΩ/64.9kΩ desde `VIN` |
| **S5** | `VDD` (REGN) | 5.4V–6V | LDO interno del Charger `PU301` |
| **S5** | `ACOK` (`ACPRN#`) | 0V (activo bajo) | Salida del Charger `PU301` |
| **S5** | `ACIN` / `PACIN` | ~3.0V | Divisor 12kΩ/10kΩ desde `VDD` |
| **S5** | `B+` | 19V–20V | MOSFETs `PQ301`+`PQ302` (Canal P) saturados con Gates a ~8V |
| **S5** | `+3VALW` | 3.3V | Fuente `PU401` (habilitada por `SPOK` de 3V/5V) |
| **S5** | `SPOK` | 3.3V | Pin 23 de la fuente de 3V/5V |
| **S5** | `S5_ON` | 3.3V | KBC habilita `PQ106` para `PU102` |
| **S5** | `LID_SW#` | 3.3V | Sensor Hall de tapa |
| **S5** | `ACIN` (KBC) | 3.2V–3.3V | Verificación de cargador |
| **S0** | `EC_RSMRST#` | 3.3V | KBC → FCH (bloque ACPI) |
| **S0** | `PBTN_OUT#` | Pulso 3.3V→0V→3.3V | KBC → FCH (al presionar botón) |
| **S0** | `PM_SLP_S5#` | 3.3V | FCH → KBC |
| **S0** | `PM_SLP_S3#` | 3.3V | FCH → KBC |
| **S3** | `SYSON` | 3.3V | KBC habilita fuente de RAM `+1.5V` |
| **S0** | `SUSP#` | 0V (inverso de `SUSP#` = 3.3V) | KBC → MOSFETs de transferencia |
| **S0** | `VSB` | 19V | MOSFET Canal P habilitado por `SPOK` |
| **S0** | `+3VS`, `+5VS`, `+1.5VS`, `+1.1VS` | — | MOSFETs Canal N con 19V en Gate |
| **S0** | `+1.8VS` | 1.8V | Habilitado por `SUSP#` (divisor con 1MΩ) |
| **S0** | `PE_PWR_EN` / `PX_PWR_EN` | 3.3V | FCH habilita voltajes de GPU dedicada |

### B. HP DV4 / DV6 / CQ40 (Comparador LM393)
| Parámetro | Valor Normal | Valor de Falla |
| :--- | :--- | :--- |
| `VIN` (divisor 100k/10k) | 1.72V | < 1.24V (cargador < 14V) |
| `PACIN` / `ACIN` | 4.0V–4.3V | 0V |
| `CHG_EN#` | 0V (activo bajo) | 3.3V (carga deshabilitada) |
| Gates MOSFETs Canal P (`PQ102`/`PQ103`) | ~8V | 19V (bloqueados) |

### C. Sony Vaio (Protección `VA_OFF`)
| Condición | `VA_OFF` | Estado del MOSFET Canal P |
| :--- | :--- | :--- |
| Normal (cargador OK) | 0V (desactivado) | Gate a ~9.5V → Conduce |
| Subtensión en `VIN` | 0V (tirado a tierra) | Gate a 19V → Bloqueado |
| Sobretensión (>22V) | 0V (tirado a tierra) | Gate a 19V → Bloqueado |
| Pila RTC agotada/corrupta | 0V (enclavado) | Gate a 19V → Bloqueado permanente |

---

## 6. Distribución de Corriente y Reglas de Seguridad

### A. Por Qué Inyectar 1V (y Jamás 19V) en la Línea Principal `B+` (19V)
- La línea principal `B+` (19V del cargador o 11V de la batería) alimenta directamente los **MOSFETs Superiores (High-Side)** de **todas las fuentes Buck** (3V, 5V, RAM, `+1.05V` PCH, `VCC_CORE` CPU, GPU) incluso con el equipo apagado en S5.
- Si un MOSFET superior está en corto entre Drain y Source, al inyectar 19V en `B+` le meterías **19V directos al CPU, al PCH o a la RAM**, destruyéndolos.
- Al inyectar **1V** (el voltaje más bajo que maneja cualquier chip de la placa), circula corriente suficiente por el componente en corto para detectarlo por calentamiento (cámara térmica o alcohol isopropílico) **sin riesgo de dañar componentes sanos**.

### B. "No todo lo que calienta está dañado"
- Cuando se inyecta corriente antes del MOSFET de entrada (o cuando el MOSFET conduce hacia una línea en corto), **el MOSFET se calienta porque toda la corriente de cortocircuito pasa a través de él**, pero él solo está aguantando el paso de corriente; el corto real está más adelante.
- El punto correcto de inyección de voltaje en las placas Lenovo es directamente en la **resistencia de sensado de corriente `PR`** (después de los dos MOSFETs de entrada).
- Al inyectar 1.5V en `PR301` (Lenovo G50), el MOSFET de entrada **deja de calentar** y la cámara térmica revela inmediatamente el **condensador cerámico SMD** en corto.

### C. Carcasas Plásticas Conductoras (EMI Shielding)
- La cara interna de muchas carcasas plásticas de notebooks viene recubierta con una **pintura metálica conductora (EMI shielding)**.
- Apoyar la placa energizada sobre la carcasa durante las pruebas provoca cortocircuitos fatales.
- **Regla**: Nunca apoyar una placa energizada directamente sobre la carcasa plástica del equipo.

### D. Resistencia de Sensado — Valores de Referencia Rápido
- Si en la resistencia de sensado hay **0V a 0.7V**, suele haber un **corto a tierra** en la línea principal de 19V.
- Si hay **~3V**, casi nunca es un corto a tierra, sino un **problema en los MOSFETs de entrada** (el Charger intenta abrirlos y cae).
- Si hay **~18V–19V**, los MOSFETs están conduciendo correctamente.

### E. Señal `D/C#` — Diferencia entre 1 y 2 MOSFETs de Entrada
- **Diseño con 2 MOSFETs Canal N**: Si hay corto en `B+`, el cargador NO se apaga porque el Charger IC no eleva los 25V del Gate (`ACDRV`), manteniéndolos abiertos y aislando al cargador del corto.
- **Diseño con 1 solo MOSFET Canal P** (ej. Toshiba Quanta TE5 `DA0TE5MB6A0`): El voltaje pasa por un divisor de 220k/220k que aplica **9.5V** en el Gate, haciendo que el MOSFET conduzca automáticamente y apague el cargador.
- **Señal `D/C#` (Pin 32 del KBC)**: Cuando el KBC activa `D/C#` a 3.3V para desconectar el adaptador, un transistor PNP interno envía los 19V directamente al Gate del MOSFET Canal P, abriéndolo y permitiendo que la batería (11V) pase sin caída de diodo.

---

## 7. Protocolos Post-Reparación

### A. Protocolo de Revisión General Obligatorio
- Prueba arranque de Windows desde disco duro/SSD.
- Carga de batería completa (tiempo estimado según capacidad).
- Funcionamiento a batería (desconectar cargador y verificar que no se apaga).
- Pantalla táctil (si aplica).
- Wi-Fi, Bluetooth, audio.
- Puertos USB (todos).
- Teclado completo (tecla por tecla: `1-0`, `a-z`, mayúsculas).

### B. Guardar los BIOS Siempre
- Antes de cualquier intervención, **guardar siempre los dumps de BIOS originales** (tanto del BIOS principal como del EC si es posible).
- Esto permite restaurar la información del cliente (serial, Windows Key, DMI) si algo sale mal.

### C. Indicador DIU (Dispositivo Uruguayo)
- Un pendrive/dispositivo USB con indicador luminoso de actividad de datos/enumeración USB.
- Permite verificar rápidamente si la placa está booteando y dando video sin necesidad de conectar un monitor externo.
