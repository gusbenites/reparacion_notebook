# Secuencia de Encendido (S5 a S0), EC, PCH, Subsistema RAM y Cargadores Gamer

Referencia técnica basada en las clases y diagnósticos reales de **Xtreme PC RGB** sobre el uso de las tablas `PM Table` / `Power Plane`, las señales del EC (Embedded Controller), el PCH, la memoria RAM DDR4 y la identificación de cargadores.

---

## 1. Cómo Leer las Tablas `PM Table` y `Power Plane` en el Esquemático

El concepto antiguo de *"primero medir 19V y luego buscar siempre 3V y 5V en las bobinas en Standby"* **ya no se cumple en todas las laptops modernas**:
- Algunas placas modernas no tienen bobina de 3.3V dedicada en S5 o solo activan las bobinas de 3V y 5V **después de presionar el botón de encendido** (mientras que en Standby solo existe el LDO de 3.3V).
- Otras placas exigen en Standby (estado S5) **más voltajes además de 3V y 5V** (por ejemplo: `+1.8V_PRIM`, `+1.0V_PRIM`, `+1.0V_MPHYGT`, `+3.3V_ALW_PCH`, `+3.3V_M`, `+1.05V_M`).

### Regla de los Estados ACPI:
- **Estado `S5 (AC ON)`**: Equipo **apagado** pero con el cargador conectado.
  - Si presionas el botón de encendido y el equipo no hace nada (consumo fijo en ~18–30 mA), tu placa está en **S5**.
  - Ve a la tabla `PM Table` / `Power Plane`, ubica la fila **`S5`** y revisa **todas las columnas que digan `ON`**. Todos esos voltajes tienen que estar presentes antes de tocar el botón.
  - **Truco de velocidad**: Empieza midiendo el **último voltaje de abajo** de la lista de S5 (ej. `+1.0V_MPHYGT` o `+1.05V_M`). Como las fuentes siguen una cascada lógica donde cada una habilita la siguiente, si el último voltaje de S5 está presente, todos los anteriores de esa cadena ya están funcionando.
- **Estado `S0`**: Equipo **encendido** (aunque no dé imagen en pantalla o se apague a los pocos segundos).
  - Si el consumo sube al pulsar el botón (ej. 100 mA, 250 mA, 500 mA), la placa intentó pasar a **S0**. Debes verificar cuáles fuentes de la columna `S0 = ON` alcanzan a activarse.
  - **Truco de velocidad en S0**: Mide la última fuente antes de VCORE, típicamente **`+1.0VS_VCCIO`** (voltaje auxiliar del CPU, generado por ej. por un `TPS62134C` / `PU401`). Si `+1.0VS_VCCIO` llega a subir a 1V durante los segundos que la placa permanece encendida, casi todas las fuentes anteriores de la placa están sanas y el problema es de comunicación lógica, BIOS, RAM o CPU.

### Cambio de Nombre de Señales y Rieles en Esquemáticos (`PJP` / `PAD` / `GAP`)
- Cuando busques un voltaje (ej. `+3.3V_ALW` o `+1.05V_M`) en el PDF y te lleve a un pequeño símbolo de unión llamado **`PJP102`**, **`PAD`** o **`GAP`**, observa que del otro lado el nombre cambia a **`+3.3V_ALW_P`** o **`+1.05V_MP`**.
- Los fabricantes usan jumpers de soldadura (`PJP`) para separar la salida del circuito generador (`_P`) del riel que alimenta al sistema. Si copias el nombre con `_P` no encontrarás los componentes que alimenta; debes buscar ambos nombres en el PDF.

---

## 2. El Embedded Controller (EC / KBC / Super I/O): Requisitos y Salidas

Cuando todos los voltajes del estado **S5** están presentes en la placa pero el equipo no enciende (o sube a ~100 mA y cae), el diagnóstico pasa obligatoriamente al **EC** (chip cuadrado de 128 pines como ITE/Nuvoton/ENE, o de esferas BGA `UE1` que se mide fácilmente localizando los componentes amarillos asociados en el BoardView).

### Checklist Ordenado del EC (Entradas → Salidas):
1. **Alimentación Principal del EC (`+3.3V_ALW_EC` / `+3V_AUX_KBC` / `VSTBY`)**:
   - Debe tener **3.3V** estables en Standby (proviene del LDO de 3.3V o de la fuente `+3VALW`).
2. **Cristal Oscilador de 32.768 kHz y `EC_RST#` (`WRST#`)**:
   - El pin de reset del EC (terminado en `#`) debe estar en **3.3V** (desactivado el reset) y el cristal de 32 kHz debe oscilar (medible con osciloscopio).
3. **Señal de Tapa Abierta (`LID_SW#` / `LID_CL_NB#`)**:
   - Debe medir **3.3V**. Si está en `0V` (por falla del sensor Hall magnético o resistencia pull-up abierta), el EC cree que la pantalla de la laptop está cerrada e ignora el botón de encendido.
4. **Detección de Cargador (`ACIN` / `HV_ACIN` o `ACIN#`)**:
   - Proviene del pin `ACOK` del Charger IC.
   - Si no tiene `#` (`ACIN`): debe medir **3.3V**.
   - Si tiene `#` (`ACIN#`): es Active-Low y debe medir **0V**.
5. **Botón de Encendido (`PWR_SW#` / `ON/OFFBTN#` / `PWRBTN_IN#`)**:
   - En reposo debe medir **3.3V** (sostenidos por una resistencia pull-up conectada a los 3.3V del EC; si ese voltaje cae a `~2.8V` o menos por fuga, el equipo puede encenderse solo automáticamente).
   - Al presionar el botón, une la línea con GND y el voltaje **debe caer a `0V` durante unos milisegundos** y volver a `3.3V` al soltar.
   - **Falla típica de botón en el teclado (Lenovo, ASUS, Acer)**: El botón de encendido forma parte de la matriz del conector del teclado (ej. pin 31 `ON/OFFBTN#` y pin 32 `GND`). Si el teclado tiene pistas sulfatadas o una tecla en corto:
     - Prueba encender puenteando con pinzas los **dos pads de bronce de prueba** situados junto al conector del teclado en la placa, o usando el **Novo Button** lateral (en Lenovo).
     - Si enciende por los pads y al cargar Windows parece tener una tecla presionada sola, desconecta el flex del teclado interno para confirmar el diagnóstico.
6. **Habilitación de Fuentes S5 (`S5_ON` / `ALW_ON` / `+3_5V_ALW_EN`)**:
   - Salida del EC (ej. pin 85) con **3.3V** que viaja al pin `EN` de los controladores PWM de 3V y 5V.
7. **Señal `EC_RSMRST#` (`PCH_RSMRST#` - Resume Reset)**:
   - Es la "cachetada" que despierta al bloque suspendido del PCH sacándolo del estado de reset. Debe medir **3.3V** (al tener `#`, es activa en bajo = en 0V mantiene al PCH reseteado; al subir a **3.3V** libera al PCH para que despierte).
   - **¡TRAMPA CLÁSICA ENTRE EL EC Y EL PCH!**:
     - Nunca midas `RSMRST#` solo a la salida del EC asumiendo que ya llegó al PCH. Mídelo también en el test point o resistencia junto al **PCH**.
     - **Caso real**: El EC sí enviaba **3.3V** en `EC_RSMRST#`, pero al PCH le llegaban **0V**. Al rastrear la línea entre ambos, pasaba por una **compuerta lógica AND de 5 patas (`UZ6`)**:
       - Pin 1 (Entrada B): `EC_RSMRST#` = **3.3V** (OK)
       - Pin 2 (Entrada A): `ALW_PWRGD_3V_5V` (PowerGood de 3V y 5V) = **3.3V** (OK)
       - Pin 3 (GND): **0V**
       - Pin 4 (Salida `PCH_RSMRST#_AND`): **0V** (Falla)
       - Pin 5 (Alimentación `P` = `+3.3V_ALW`): **0V** (Pista abierta entre el capacitor de al lado que sí tenía 3.3V y el pin 5 de la compuerta). Un simple puente de estaño al pin 5 restauró los 3.3V en `PCH_RSMRST#` y la laptop encendió dando video.
8. **Señal `SIO_PWRBTN#` (`DNBSWON#` / `PM_PWRBTN#`)**:
   - Es la réplica del pulso del botón de encendido que el EC envía directamente al PCH para ordenarle pasar de S5 a S0.
   - Reposo: **3.3V**. Al pulsar el botón de encendido: cae a **0V** momentáneamente y regresa a **3.3V**.

---

## 3. Respuesta del PCH y Secuencia hasta `PLT_RST#`

Una vez que el PCH tiene sus voltajes S5 (`+3.3V_ALW_PCH`, `+1.0V_PRIM`, `+3V_RTC`), recibe `PCH_RSMRST#` (3.3V) y el pulso a 0V en `SIO_PWRBTN#`:
1. **El PCH libera `SLP_S4#` (3.3V)**:
   - Sale del estado de hibernación/apagado y actúa como **`ENABLE`** (directamente o a través del EC) para las fuentes del subsistema de memoria RAM:
     - **`+1.2V_DDR` (`VDDQ`)**
     - **`+2.5V_VPP`** (en DDR4)
     - **`+1.0V_VCCST`** (alimentación de sostenimiento del CPU)
2. **El PCH libera `SLP_S3#` (3.3V)**:
   - Ordena activar todas las fuentes de estado **S0 (`RUN` / `VS`)**:
     - `+3VS`, `+5VS`, `+1.8VS`
     - **`+1.0VS_VCCIO`**, **`+1.05VS_VCCSA`** (System Agent)
     - Fuentes principales de CPU (**`VCORE`**) y GPU.
3. **Generación de `ALL_SYS_PWRGD` → `PCH_PWROK` → `SYS_PWROK` → `PLT_RST#` (3.3V)**:
   - Cuando todas las fuentes S0 confirman su `PGOOD`, el PCH libera **`PLT_RST#` (Platform Reset = 3.3V)** hacia el CPU, GPU, puerto M.2 NVMe, puerto Wi-Fi CNVi, etc.
   - *Tip con tester ALEXSOF PCH (conectado al slot M.2 o Wi-Fi)*: permite verificar de un vistazo la presencia de `3V3`, `SUSCLK` (32 kHz), `PLT_RST#` (3.3V) y los pares diferenciales de datos PCIe (`4x` en M.2, `1x` + USB en Wi-Fi) y su `CLK`.

---

## 4. Subsistema de Memoria RAM DDR4 y Señal `DRAM_RST#`

Para que la memoria RAM DDR4 funcione e inicialice con el controlador de memoria integrado en el CPU, no basta con medir 1.2V en la bobina de RAM:

| Señal / Voltaje en Slot DDR4 | Valor Normal | Significado en Diagnóstico |
| :--- | :--- | :--- |
| **`VDD` (`VDDQ`)** | **1.2 V** | Voltaje principal de la bobina de RAM (habilitado tras `SLP_S4#`). |
| **`VPP`** | **2.5 V** | Voltaje de activación de palabras de memoria DDR4. |
| **`VTT`** | **0.6 V** | Voltaje de terminación (siempre es exactamente la mitad de `VDD`: `1.2V / 2 = 0.6V`). |
| **`VDDSPD`** | **3.3 V** | Alimentación del chip EEPROM SPD de la memoria (le dice al CPU qué RAM está instalada). |
| **`SDA` / `SCL` (Data y Clock)** | Pulsos (3.3V) | Comunicación SMBus entre CPU/PCH y la memoria. Si los voltajes están bien pero falta Data/Clock, revisar líneas hacia el CPU. |
| **`DRAM_RST#` (`RAM_RESET#`)** | **1.2 V** | **Señal clave de estado avanzado**: indica que el controlador de memoria del CPU ya se comunica con la RAM. Si hay 1.2V en la bobina (`VDD`) pero `DRAM_RST#` está en **0V**, el equipo quedará en pantalla negra (típico cuando la RAM onboard soldada está dañada o deshabilitada sin módulo externo). |

---

## 5. Cargadores de Laptops Gamer: El Pin Central `ID`

Al conectar una laptop Gamer (ASUS ROG/TUF, HP Omen/Pavilion Gaming, Lenovo Legion, Dell Alienware/G-Series) a una fuente de laboratorio usando solo positivo (`VIN`) y negativo (`GND`):
- **Síntoma**: La laptop no enciende, no carga la batería o se apaga automáticamente.
- **Causa**: Los cargadores originales de alta potencia (180W, 230W, 240W, 300W, 330W) tienen un **tercer cable central (`ID` / `ADAPTER_ID`)** que informa al EC la potencia exacta del cargador:
  - En **ASUS, HP y Lenovo**: utiliza un valor de resistencia / divisor específico según el vataje (simulable con placa selectora de jumpers por vataje o usando el cable de un cargador original cortado).
  - En **Dell**: utiliza un protocolo de comunicación digital **1-Wire** desde una memoria interna en el cargador hacia el EC.
