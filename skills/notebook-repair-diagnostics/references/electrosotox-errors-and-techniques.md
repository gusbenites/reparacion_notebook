# Errores Comunes, Técnicas de Diagnóstico y Carga de Firmware KBC (ElectroSotox)

Compendio técnico extraído de los videos de **ElectroSotox** (canal de reparación de laptops de Colombia), enfocado en errores comunes de técnicos, técnicas de diagnóstico con osciloscopio/cámara térmica, y el mecanismo de carga de firmware del KBC.

---

## 1. Los 10 Errores Más Comunes al Reparar Laptops (`z7JFK5lYdRQ`)

### Error 1: No Habilitar OCP en la Fuente de Laboratorio
- Sin OCP, si hay un MOSFET de alta en corto, la fuente sigue entregando 20V que pueden dañar el CPU/GPU (que funcionan a ~0.8V).
- **Regla**: Habilitar siempre OCP en la fuente de laboratorio para proteger el procesador.

### Error 2: No Considerar la Línea PSID/Identificación del Adaptador
- Equipos HP corporativos usan línea PSID controlada por voltaje. Dell usa protocolo 1-Wire.
- Si no se emula esta línea, el equipo puede encender pero no dar video o no cargar batería.
- **Solución**: Usar cable de extensión universal con puntas que emulen el adaptador correcto.

### Error 3: Pensar que Todo lo que se Calienta Está Malo
- El KBC no debe calentarse; si se calienta, hay un problema (ej. corto en la línea `+3V_KBC`).
- Un controlador de fuente 3V/5V ALW puede calentarse por un corto en el KBC conectado a su salida.
- **Valor de referencia**: En tarjeta buena, la caída de tensión en diodos del pin 4 del KBC = **714 mV**.
- **Solución**: Medir continuidad y resistencia en las líneas de alimentación del KBC antes de cambiar el IC.

### Error 4: Pensar que Todo lo que Enciende sin Video es BIOS o Chip de Video
- Primero verificar que **todas** las fuentes estén trabajando y haya voltajes de memoria, alimentación del PCH, etc.
- No reprogramar BIOS sin antes verificar que no haya líneas abiertas o resistencias desvalorizadas.

### Error 5: Encender y Luego Medir con el Multímetro
- **Incorrecto**: Encender primero y medir después. Si una fuente se protege por corto, nunca veremos el voltaje.
- **Correcto**: Conectar la punta del multímetro primero → encender → observar si hay voltaje momentáneo que luego cae.
- Esto permite captar el pulso inicial de una fuente que intenta arrancar pero se protege.

### Error 6: No Tener en Cuanta lo que se Mide con Multímetros de Autorango
- Los multímetros de autorango (como UT39C+) pueden mostrar valores incorrectos en pulsos de conmutación.
- En un lado de la bobina marca 3.3V, en el otro lado puede marcar 11.3V o 14V (**falso**).
- **Solución**: Usar multímetro de **rango manual** o referirse siempre al lado de salida (capacitores) para medir voltaje DC real.

### Error 7: Energizar la Tarjeta y Luego Medir con Osciloscopio
- **Incorrecto**: Conectar fuente y luego poner la sonda del osciloscopio. Se pierde la ventana de comunicación de la BIOS.
- **Correcto**: Sonda primero → energizar → observar si hay actividad en pines 2, 5, 6 (datos).
- En S5 (apagado), algunas BIOS ya están comunicándose; otras solo cuando se presiona el botón.

### Error 8: Reprogramar BIOS Solo Verificando que Tenga Voltaje
- Tener voltaje en VCC (1.8V o 3.3V) no significa que la BIOS funcione.
- Debe verificarse **actividad de datos** en líneas 2, 5 y 6 con osciloscopio.
- Si una línea de comunicación está abierta (hacia PCH o KBC), la BIOS no cargará el firmware.

### Error 9: Pensar que una Fuente que "Pita" (Baja Resistencia) Está en Corto
- En fuentes de CPU/GPU de gama alta, valores de 0.2Ω o 2Ω son **NORMALES**.
- El CPU tiene muy baja impedancia interna; eso se refleja en la medición.
- **Solución**: Comparar con valores de referencia; calibrar las puntas del multímetro (pueden tener 1Ω de resistencia).

### Error 10: Empezar Inyectando un Voltaje Igual al de la Línea en Corto
- Si la línea es de 20V, **NO inyectar 20V directamente**.
- Los MOSFETs de alta en corto pueden enviar 20V al CPU (0.8V) y quemarlo.
- **Solución**: Comenzar con **1V** para localizar el componente caliente sin dañar otros componentes. Subir gradualmente según experiencia.

---

## 2. Mecanismo de Carga del Firmware del KBC (`NxbPUIdFkjo`)

### Cómo Funciona la Carga del Firmware del KBC en Equipos con Microcontroladores IT
- Cuando el equipo está apagado y se conecta el adaptador, **inmediatamente la BIOS principal carga el firmware al KBC**.
- El **pin 1 de la BIOS principal** muestra actividad: latea brevemente y luego se estabiliza en nivel alto (1.8V para equipos AMD, 3.3V para Intel).
- Una vez cargado el firmware, el KBC tiene sus pines de entrada/salida configurados para controlar el arranque.

### Secuencia de Encendido
1. **Paso 1**: Conectar adaptador → la BIOS carga el firmware del KBC → pin 1 latea → se estabiliza en nivel alto.
2. **Paso 2**: Presionar botón de encendido → el KBC empieza a reconfigurar el hardware → se observan múltiples paquetes de datos en el osciloscopio.

### Nota Importante
- Si no hay pila de CMOS, el equipo hace varios reinicios porque necesita reconfigurar la BIOS cada vez.

### Problemas de Firmware del KBC (Teclado con Caracteres Incorrectos)
- **Causa**: Problema de firmware del KBC, no del hardware del teclado.
- **Solución de reprogramación** (válida solo para chips **IT**):
  1. Usar programador CH341A con conexión I2C a través del **conector de batería**.
  2. Líneas: Data, Clock, Tierra (mismo I2C que usa el circuito charger).
  3. Leer el firmware del KBC → guardarlo.
  4. **Blanquear** el KBC (dejarlo sin firmware).
  5. **Reprogramar la BIOS principal** con firmware de fábrica limpio.
  6. Al conectar la energía, la BIOS principal cargará el firmware limpio al KBC en blanco.

---

## 3. Técnicas de Diagnóstico con Osciloscopio y Cámara Térmica

### A. Diagnóstico de MCP/PCH por Patrón Térmico
- En algunos casos, el chip MCP/PCH tiene un fallo interno que no se detecta con multímetro.
- **Técnica**: Usar cámara térmica (FLIR) para observar la distribución de calor.
- **Indicador clave**: Un patrón de "titilación" térmica (calor que se enciende y apaga repetidamente) en un sector del chip indica un corto intermitente interno.
- **Solución**: Cambiar el chip MCP/PCH (no es reparable).

### B. Diagnóstico de KBC por Resistencia Anormal
- Medir la resistencia en la línea de 3.3V que alimenta al KBC (con respecto a tierra).
- **Valor normal**: ~997.2Ω.
- **Valor anormal**: 96.3Ω (indica corto parcial en el microcontrolador).
- **Solución**: Cambiar el KBC/EC.

### C. Diagnóstico de Línea RTC con Inyección de Voltaje
- La línea RTC maneja un consumo muy pequeño (microamperios).
- **Técnica**: Inyectar 3V en la línea RTC.
- **Indicador**: Si el consumo es de 35mA (en lugar de microamperios), hay un corto en el sector RTC del chip principal.
- **Confirmación**: El cristal del chip principal (PCH/MCP) se calienta levemente en una esquina con cámara térmica.
- **Solución**: Cambiar el chip principal (PCH/MCP).

### D. Diagnóstico de MOSFETs de Entrada
- **Identificación**: La resistencia de sensado de la batería es diferente a la de la línea principal. No confundirlas.
- **Técnica**: Medir en escala 60K para verificar MOSFETs individuales.
- **Indicador**: Si un MOSFET mide 21-23 por un lado y diferente por el otro → está en corto.
- **Verificación**: Retirar el MOSFET y comprobar que el corto desaparece de la línea principal.
- **Reemplazo**: Usar MOSFET canal N equivalente (ej. A7410 como reemplazo común).

### E. Diagnóstico de Fuente Buck con Osciloscopio
- **Procedimiento correcto**: Conectar punta del osciloscopio primero → energizar → observar pulsos de conmutación.
- **Indicador de falla**: Si los pulsos desaparecen y queda solo un voltaje residual bajo, la fuente se está deshabilitando por sobreconsumo.
- **Comparación**: La fuente de 5V puede deshabilitarse por sobreconsumo mientras la de 3V sigue trabajando, permitiendo identificar en qué línea está el problema.

### F. Diagnóstico de Líneas SATA/BIOS con Osciloscopio
- **Técnica**: Medir en líneas SATA (o BIOS) con escala de diodos para verificar capacitores de acoplamiento.
- **Indicador**: Un capacitor que marca 301Ω (cuando debería marcar valor similar al normal) está en corto.
- **Nota**: Este diagnóstico se puede aplicar a líneas BIOS, HDMI, oscilador de cristal, etc.

---

## 4. Técnicas de Inyección de Voltaje y Detección de Cortos

### A. Inyección Progresiva (1V → 2V → 3V)
- **Procedimiento**: Comenzar con 1V y aumentar gradualmente, observando el consumo y la temperatura.
- **Indicador**: Al inyectar 1V en una línea en corto, el componente defectuoso se calienta (visible con cámara térmica o alcohol isopropílico).
- **Regla de oro**: El componente que se calienta NO necesariamente está en corto. Es necesario verificar con multímetro antes de condenar un componente.

### B. Capacitores en Paralelo como Componentes "Sacrificables"
- Los capacitores en paralelo pueden retirarse individualmente para pruebas sin afectar el funcionamiento del circuito.
- **Técnica**: Retirar un capacitor a la vez y verificar si el corto desaparece.
- **Referencia**: Los capacitores en paralelo pueden retirarse y el equipo seguirá funcionando (con menos filtrado, pero funcional).

### C. Levantar Bobinas para Aislar Fases
- En equipos gamer con múltiples fases del procesador, si una fase tiene un MOSFET de alta en corto, puede dañar el CPU.
- **Técnica**: Levantar las 4 bobinas (una por una) para identificar cuál fase tiene el corto.
- **Indicador**: Al levantar la bobina defectuosa, el corto desaparece de la línea principal.
- **Solución**: Cambiar el MOSFET de alta en corto de la fase defectuosa. El equipo puede funcionar temporalmente con 3 fases, pero no es recomendado para uso forzado.

### D. Corto en VRAM de GPU (Tarjetas Gráficas)
- **Indicador**: Módulos VRAM que se calientan con la inyección de voltaje.
- **Técnica**: Levantar fases una por una para identificar la fase defectuosa.
- **Precaución**: No asumir que el GPU está malo solo porque se calienta al inyectar voltaje.
- **Solución**: Cambiar el controlador de la fuente de VRAM y los módulos VRAM dañados.

### E. Corto en Línea Principal — MOSFET vs. Capacitor
- **Técnica**: Medir la resistencia de sensado principal. Si marca 0.5Ω, hay un corto.
- **Inyección de 1V**: Si el consumo es de 2A, hay un componente en corto.
- **Diferenciación**: Si el MOSFET de entrada se calienta, puede ser por el paso de corriente hacia el corto (no necesariamente el MOSFET está dañado).
- **Solución**: Inyectar directamente después de la resistencia de sensado (en lugar de antes del MOSFET) para evitar que el MOSFET se caliente por el paso de corriente y confundir el diagnóstico.

---

## 5. Señales Específicas por Arquitectura

### A. Lenovo G480 AMD — Secuencia Completa (con KBC IT8227S y FCH Hudson)
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
| **S0** | `EC_RSMRST#` | 3.3V | KBC → FCH (bloque ACPI) |
| **S0** | `PBTN_OUT#` | Pulso 3.3V→0V→3.3V | KBC → FCH (al presionar botón) |
| **S0** | `PM_SLP_S5#` | 3.3V | FCH → KBC |
| **S0** | `PM_SLP_S3#` | 3.3V | FCH → KBC |
| **S3** | `SYSON` | 3.3V | KBC habilita fuente de RAM `+1.5V` |
| **S0** | `SUSP#` | 0V (inverso de `SUSP#` = 3.3V) | KBC → MOSFETs de transferencia |
| **S0** | `VSB` | 19V | MOSFET Canal P habilitado por `SPOK` |
| **S0** | `+3VS`, `+5VS`, `+1.5VS`, `+1.1VS` | — | MOSFETs Canal N con 19V en Gate |
| **S0** | `+1.8VS` | 1.8V | Habilitado por `SUSP#` (divisor con 1MΩ) |

### B. Valores de Referencia Rápido (ElectroSotox)
| Medición | Valor Normal | Valor de Falla |
| :--- | :--- | :--- |
| Caída de tensión en diodos del pin 4 del KBC | 714 mV | Valor muy bajo o muy alto |
| Resistencia en línea 3.3V hacia KBC | ~997.2Ω | 96.3Ω (corto parcial) |
| Resistencia de sensado principal | 0.5Ω (sano) | 0.04Ω (corto directo) |
| Consumo RTC | Microamperios | 35mA (corto en PCH/MCP) |
| Fuente VRAM (fases en ohms) | 0.5Ω (normal) | 0.003Ω (corto directo) |
| Consumo S5 normal | 8–42 mA | 102–278 mA (anormal) |
| Voltaje 5V standby | 5.0V estable | 4.5V–5.3V fluctuante (módulo WiFi en corto) |
| Voltaje `PP3_42_G3H` (SMC) | 3.42V | 0.7V (muy bajo, diodo dual defectuoso) |
| Caída de tensión en cristal 32.768 kHz | 767/768/753 (sano) | Diferencia alta → no funciona |

---

## 6. Herramientas de Laboratorio Recomendadas (ElectroSotox)

1. **Cámara térmica**: FLIR Super C X / InfiRay P2 Pro — diagnóstico térmico de chips BGA.
2. **Osciloscopio**: Rigol DS202 / Hantek DSO2C15 — análisis de señales en fuentes Buck/Boost.
3. **Fuente de laboratorio**: CDP 305X (lineal) / Wanptek 3010U (conmutada) — 20V/5A con OCP/OVP.
4. **Trazador de curvas**: XBO 4 — comparación de componentes sin corriente, programación BIOS y KBC.
5. **Power Z (KM003C)**: Con comunicación USB-C, para análisis de voltaje/corriente en equipos USB-C.
6. **Lavadora de ultrasonido**: ADADI 8120 — limpieza profunda de tarjetas con humedad/oxidación.
7. **Estación de calor**: Sugon 8260 DX (4 canales) / Quick 857D — reballing.
8. **Multímetro**: UNI-T UT89 (rango manual) / UT61E (con función PEAK) — mediciones de voltaje/corriente/resistencia.
9. **Probador de carga**: UNI-T UTL821 — verificar que las fuentes entreguen la corriente adecuada.
10. **Cargador de baterías**: Para cargar baterías descargadas al límite antes de diagnosticar.
