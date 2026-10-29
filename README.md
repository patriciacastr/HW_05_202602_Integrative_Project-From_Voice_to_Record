# De la voz al registro: entrevistas y llamadas de venta

Proyecto integrador individual (HW_05_202602). Autora: Patricia Castro Hilario.

- Video (máx. 8 min): [COMPLETAR enlace]
- Documento del pipeline (Notion/Miro, público): [COMPLETAR enlace]

## 1. Qué hace

Convierte audio grabado en registros estructurados y verificados.

- **Tarea 1, entrevistas:** audio de una entrevista de trabajo a un registro con 6 campos (años de experiencia, último puesto, tecnologías, pretensión salarial, disponibilidad, nivel de inglés).
- **Tarea 2, llamadas de venta (dominio: restaurante, Chifa Dragón Dorado, inventado):** audio de una llamada a un pedido (ítems, promoción, dirección, método de pago, total dicho) que se verifica a sí mismo con aritmética.

Regla central: todo valor extraído debe existir literalmente en la transcripción. Si no, el campo queda `sin_verificar`. Los números dichos con palabras ("once mil quinientos") se normalizan a 11500 antes de verificar.

## 2. Instalación y ejecución

```bash
pip install -r requirements.txt
cp .env.example .env          # solo nombres de variables, sin credenciales en el repo
```

Todo lo configurable (rutas, modelos, umbrales, prompts) está en `config.yaml` y `prompts.yaml`.

Los audios y los pesos de los modelos **no** están en el repo. Los audios (`data/audio/original/t1_01..t2_05.m4a`) se pueden solicitar a la autora; los pesos se descargan solos al transcribir.

Comandos principales (transcribir requiere GPU, por ejemplo Colab):

```bash
python scripts/run_asr_benchmark.py --runs large_cuda_fp16_gl --tasks t1 t2   # transcribe y cachea
python scripts/make_ladder.py                                                  # escalera L1-L3 (ffmpeg)
python scripts/run_asr_benchmark.py --level L2 --runs large_cuda_fp16_gl --tasks t2
python -m src.extract_rules large_cuda_fp16_gl     # T1, camino 1 (reglas)
python -m src.extract_fix large_cuda_fp16_gl       # T1, reglas con ajustes
python -m src.extract_llm large_cuda_fp16_gl       # T1, camino 2 (LLM)
python -m src.extract_order large_cuda_fp16_gl L0  # T2, pedido + validación (L0..L3)
python scripts/make_summary.py                     # tablas resumen
streamlit run app.py                               # [COMPLETAR cuando exista la app]
```

Evaluar nunca re-transcribe: lee `results/cache/asr/`. Por eso un flujo de CI sin GPU podría recalcular métricas.

**Comprobar que el motor no importa ninguna librería de interfaz** (no debe imprimir nada):

```bash
grep -rnE "import (streamlit|gradio|tkinter)|from (streamlit|gradio)" src/
```

## 3. Corpus y ground truth

- 5 entrevistas (t1_01..t1_05) y 5 llamadas (t2_01..t2_05), de unos 2 a 4 minutos, grabadas por mí con una compañera, alternando voces A y B. Aparezco en todos los clips.
- **Todo lo dicho es inventado.** No hay salarios, direcciones ni datos personales reales.
- **Todas las personas que aparecen aceptaron participar** y no se nombra a nadie que no haya aceptado ser nombrado.
- **Autoría de los guiones:** [COMPLETAR con honestidad: quién escribió cada guion, qué cambié yo, y que cada una grabó, transcribió y analizó por su cuenta].
- Ground truth: `ground_truth/t1_ground_truth.csv`, `ground_truth/t2_ground_truth.json` y `ground_truth/reference_transcripts/`. Se escribió antes de grabar, por eso no costó nada: la referencia es el propio guion, no subtítulos automáticos (evita la trampa de la evaluación circular).
- Generadores de guiones y ground truth: `scripts/guiones_data.py`, `relleno.py`, `medir_duracion.py`, `build_ground_truth.py`. La tabla oficial es la de `ground_truth/`.
- Cómo varié la posición de cada campo en T1: ver `docs/guiones/guiones_t1.md`.
- Trampas de T2: 3 autocorrecciones (t2_02, t2_03, t2_05), 3 totales mal dichos a propósito (t2_02: 72 en vez de 62; t2_04: 76 en vez de 71; t2_05: 148 en vez de 143) y direcciones con dígitos (t2_01, t2_02, t2_04, t2_05).

Distribución de campos: [COMPLETAR con la salida de `build_ground_truth.py` o un conteo propio].

## 4. Transcripción en GPU (Tarea 1, Fase 2)

Normalización antes de comparar: minúsculas, sin puntuación, espacios colapsados, dígitos a palabras y tildes conservadas (`config.yaml`, sección `normalization`).

| Corrida | Dispositivo | WER medio | WER sin t1_05 | s por min de audio | VRAM pico |
|---|---|---|---|---|---|
| small fp16 | cuda | 0.108 | 0.103 | 2.0-2.7 | 1032-1334 MB |
| small int8 | cpu | 0.113 | 0.109 | ~34 | 447 MB (sin GPU) |
| large-v3 fp16 | cuda | 0.132 | 0.057 | ~7 (20.6 en t1_05) | 5590 MB |
| large-v3 int8_float16 | cuda | 0.085 | 0.059 | ~7.4 | 3958 MB |
| large-v3 fp16 + glosario | cuda | 0.054 | 0.051 | ~7.7 | 4694 MB |

Lectura honesta:

- **Prueba de GPU:** el dispositivo se lee de la corrida (`[cuda]` / `[cpu]`) y se respalda con la VRAM medida; la corrida en CPU muestra delta de VRAM 0 y es unas 15 veces más lenta (34 contra 2 s/min).
- **int8_float16** significa pesos en int8 y cálculo en float16, no int8 puro. Baja la VRAM un 29% (5590 a 3958 MB) con velocidad casi igual. El texto cambió en 3 de 5 clips, así que no es "gratis".
- **Bucle de repetición:** large-v3 fp16 sin glosario entró en un bucle en t1_05 (WER 0.433, 20.6 s/min). La misma clip no repitió con glosario ni en int8, pero con n=1 no se puede atribuir eso al glosario. En t2_03 pasó algo parecido y al repetir la corrida el WER cambió (0.172 a 0.206): los clips estables se reprodujeron exactos y el clip con bucle no. Por eso se evalúa sobre transcripciones cacheadas.
- **La VRAM entre corridas hechas en la misma sesión no es comparable limpiamente:** small fp16 dio 1334 MB y luego 1032 MB con el mismo modelo.
- **Glosario:** faster-whisper 1.2.1 acepta tanto `initial_prompt` como `hotwords`. Usé `initial_prompt`. Diferencia de WER con y sin glosario con intervalo de confianza: [COMPLETAR tras correr el bootstrap]. Con 5 clips el intervalo es optimista.

## 5. De texto a registro (Tarea 1, Fase 3)

Dos caminos sobre las mismas transcripciones:

1. **Reglas** (`src/extract_rules.py` + `src/extract_fix.py`). Normalizador de números en dos direcciones: palabras a número y dígitos con regla de miles ("11.500" es 11500). Maneja "seis meses = 0.5", "dos años y medio = 2.5", autocorrección del salario (gana el último valor) y fechas relativas calculadas desde 2026-11-02.
2. **LLM** (`src/extract_llm.py`, Qwen2.5-3B-Instruct local, elegido por ser gratis, local y caber en la T4). Devuelve JSON con evidencia literal.

| Camino | Exactitud (35 campos) | Nota |
|---|---|---|
| Reglas v1, antes de ver los clips | 27/35 (77%) | cifra no ajustada |
| Reglas v2, tras ajustes | 35/35 | **ajustadas sobre los mismos 5 clips: no es exactitud esperada** |
| LLM Qwen2.5-3B, sin ajustes | 24/35 (69%) | corrida anterior; [COMPLETAR si repites y subes el CSV] |

Errores del LLM: copia la empresa en el puesto, calcula mal fechas (2026-02-01 en vez de 2027-02-01) e inventó años (4.5 y 10.5, atrapados como `sin_verificar`).

### WER contra registro (reglas v2 sobre cada transcripción)

| Transcripción | WER medio | Exactitud del registro | F1 macro inglés | Error absoluto años | Error absoluto salario |
|---|---|---|---|---|---|
| small fp16 | 0.108 | 0.714 | 1.0 | 0 | 0 (1 clip sin valor) |
| small cpu int8 | 0.113 | 0.686 | 1.0 | 0 | 0 (1 clip sin valor) |
| large fp16 | 0.132 | 0.943 | 1.0 | 0 | 0 |
| large int8 | 0.085 | 0.943 | 1.0 | 0 | 0 |
| large fp16 + glosario | 0.054 | 1.000 | 1.0 | 0 | 0 |

**¿Se sabe si el registro sirve mirando solo el WER? No.**

- WER alto, registro perfecto: large fp16 en t1_05, WER 0.433 por el bucle, 7 de 7 campos bien (los datos se dijeron antes del bucle).
- WER bajo, registro roto: large fp16 en t1_02, WER 0.056, pierde "VBA".

Asimetría por tipo de campo: lo categórico (inglés) y lo dicho en una frase larga (años) sobreviven a cualquier transcripción; las listas de nombres propios cortos (VBA, Git, SAP, Canva) no. Spearman WER-exactitud = -0.56 sobre 25 pares no independientes: descriptivo, no una prueba.

**Limitaciones del verificador:** `verificado` no significa `correcto`. Prueba que el texto existe, no que esté bien recortado ("diseñadora UX en nube creativa") ni bien oído ("analista financiera sin niña"). Una fecha calculada mal sobre una frase real también sale verificada. La lista de tecnologías no avisa si falta un elemento, y las tecnologías se buscan con el glosario, así que solo se encuentran las ya conocidas.

## 6. Llamadas de venta (Tarea 2)

Pedido extraído con `src/extract_order.py`. Validación: suma de cantidad por precio de carta, menos promoción, contra el total dicho. Diagnóstico de un desajuste:

- **v1:** si el total dicho se repite 2 o más veces con el mismo valor, error del hablante; si no, sospecha de ASR.
- **v2:** además, si al valor dicho le falta un dígito respecto al cálculo ("13" por "113"), error del ASR. Esta regla se ajustó sobre el único caso de ASR que apareció (t2_03, en dos niveles). La v1 acertaba 11 de 13 alertas y nunca detectaba ASR.

### Escalera de degradación (large-v3 fp16 + glosario)

| Nivel | Simula | WER medio | WER sin t2_03 | Campos | Trampas atrapadas | Perdidas | Falsas alarmas | Diagnóstico (sobre alertas) |
|---|---|---|---|---|---|---|---|---|
| L0 | original | 0.094 | 0.066 | 30/30 | 3/3 | 0 | 0 | 3/3 |
| L1 | nota de voz (Opus 16 kbps mono) | 0.055 | 0.053 | 30/30 | 3/3 | 0 | 0 | 3/3 |
| L2 | teléfono (300-3400 Hz, 8 kHz) | 0.064 | 0.066 | 28/30 | 2/3 | 1 | 1 | 3/3 |
| L3 | L1 + ruido rosa a 10 dB | 0.097 | 0.067 | 26/30 | 3/3 | 0 | 1 | 4/4 |

- **Ruido L3:** ruido rosa, semilla 42, SNR objetivo 10 dB, definido como 20·log10(RMS señal / RMS ruido). El SNR logrado (10.0 dB en los 5 clips) está en `results/tables/ladder_manifest.json`.
- **El WER casi no se mueve (0.066 a 0.067 sin t2_03) pero los campos caen de 30 a 26.** Reportar solo WER engaña.
- WER alto, registro perfecto: t2_03 en L0 (0.206, 6 de 6 campos bien). WER bajo, registro roto: t2_03 en L2 (0.056; Whisper oyó "13" por "113").
- **Lo que el validador no ve:** t2_04 en L2. El extractor perdió la promoción "tres por dos", calculó 76 y coincidió con el total mal dicho: dos errores que se tapan. La validación aritmética es tan buena como el extractor que la alimenta.
- En L3 fallan sobre todo las direcciones (se dicen una o dos veces; el total se repite varias).
- La "falsa alarma" de t2_03 en L2 y L3 es una alerta correcta (el total extraído estaba mal por ASR), pero no era una trampa plantada.

## 7. Un motor, dos esquemas

[COMPLETAR: pendiente de crear `src/engine.py` con una función `procesar_audio(ruta, esquema)` que devuelva transcript, campos, verificación, dispositivo, tiempo y error, y explicar aquí cómo sirve a los esquemas de T1 y T2. Hoy la lógica está repartida entre `src/asr.py`, `extract_rules.py` y `extract_order.py`.]

## 8. Herramientas de IA declaradas

- Claude (chat, claude.ai): [COMPLETAR qué hizo: apoyo con el código de ASR, extractores, validador y resúmenes; yo ejecuté, verifiqué y puedo explicar el pipeline].
- Agentes de código / servidores MCP usados: [COMPLETAR o indicar "ninguno"].
- Qwen2.5-3B-Instruct (local) como modelo del camino 2.

## 9. Limitaciones

- Muestra de 5 clips por tarea: unas 35 observaciones por corrida en T1 y 30 por nivel en T2. Los intervalos bootstrap son optimistas porque no pueden salirse del rango observado; los pares clip-corrida no son independientes.
- Extractores por reglas, alias de productos y regla de diagnóstico v2 ajustados sobre estos mismos clips: el 35/35 y el 13/13 no son exactitud esperada con audios nuevos.
- Solo hubo un caso real de error de ASR en totales, así que la regla de diagnóstico está poco probada.
- Voces de pocas personas, con acento limeño, grabadas con teléfono; no generaliza a otros acentos ni salas.
- **Este sistema no debe usarse** para decidir contratación ni salarios, ni para cobrar o validar pedidos reales sin revisión humana: puede extraer y verificar valores incorrectos.
