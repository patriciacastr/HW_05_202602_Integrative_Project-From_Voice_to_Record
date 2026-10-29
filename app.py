"""App Streamlit: lee resultados precalculados; solo el probador llama al motor (src.engine)."""
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))
P = CFG["paths"]
T = Path(P["tables"])
RUN = CFG.get("engine", {}).get("run", "large_cuda_fp16_gl")

st.set_page_config(page_title="De la voz al registro", layout="wide")
st.title("De la voz al registro")
st.caption("Entrevistas de trabajo y llamadas de venta: del audio a un registro verificado. "
           "Todo el corpus es inventado y grabado por la autora.")


@st.cache_data
def leer_csv(nombre):
    p = T / nombre
    return pd.read_csv(p) if p.exists() else None


@st.cache_data
def leer_texto(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else None


@st.cache_data
def leer_json(path):
    p = Path(path)
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def tabla(nombre, titulo=None):
    df = leer_csv(nombre)
    if titulo:
        st.markdown(f"**{titulo}**")
    if df is None:
        st.info(f"Falta `{T / nombre}`.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    return df


tab1, tab2, tab3, tab4 = st.tabs(["Problema y método", "Corpus", "Resultados", "Probador"])

# ------------------------------------------------------------------ 1. problema y método
with tab1:
    st.header("El problema: el audio que nadie procesa")
    st.markdown(
        "Transcribir es donde empieza el trabajo, no donde termina. Una organización no necesita texto: "
        "necesita **campos verificados, en una tabla, con una medida de cuánto confiar en ellos**.")
    st.markdown("""
**Tarea 1, entrevistas.** Audio de una entrevista a un registro de 6 campos: años de experiencia,
último puesto, tecnologías, pretensión salarial, disponibilidad y nivel de inglés.

**Tarea 2, llamadas de venta (restaurante).** Audio de una llamada a un pedido que se verifica solo:
cantidad por precio, menos promoción, contra el total dicho en voz alta.
""")
    st.subheader("Método")
    st.markdown("""
**Corre una vez:** guiones y grabación, ground truth, transcripción con caché (Whisper large-v3 en GPU),
construcción de la escalera de degradación (L1 a L3).

**Corre por cada audio (motor único `procesar_audio`):** transcripción, extracción (reglas o LLM),
verificación literal, validación aritmética y diagnóstico.

**Regla de verificación:** todo valor extraído debe existir literalmente en la transcripción; si no, queda
`sin_verificar`. Los números dichos con palabras se normalizan ("once mil quinientos" a 11500).

**Dos capas de métricas, siempre por separado:** transcripción (WER, CER) y registro (exactitud por campo,
F1 macro del inglés, error absoluto de años y salario).
""")
    st.warning("Este sistema no debe usarse para decidir contratación ni salarios, ni para cobrar pedidos reales "
               "sin revisión humana: puede extraer y verificar valores incorrectos.")

# ------------------------------------------------------------------ 2. corpus
with tab2:
    st.header("Corpus")
    tarea = st.radio("Tarea", ["t1 (entrevistas)", "t2 (llamadas)"], horizontal=True)
    clave = tarea[:2]
    clip = st.selectbox("Clip", CFG["clips"][clave])
    audio = next((Path(P["audio_original"]) / f"{clip}{e}" for e in (".m4a", ".wav", ".mp3")
                  if (Path(P["audio_original"]) / f"{clip}{e}").exists()), None)
    if audio:
        st.audio(str(audio))
    else:
        st.info("El audio no está en el repositorio (se pueden solicitar a la autora). "
                "Se muestran la referencia y la transcripción cacheada.")
    ref = leer_texto(Path(P["reference_dir"]) / f"{clip}.txt")
    asr = leer_json(Path(P["cache_asr"]) / "L0" / RUN / f"{clip}.json")
    c1, c2 = st.columns(2)
    c1.markdown("**Referencia (guion)**")
    c1.write(ref or "Sin referencia.")
    c2.markdown(f"**Transcripción ({RUN})**")
    c2.write(asr["text"] if asr else "Sin transcripción en caché.")
    st.markdown("**Ground truth**")
    if clave == "t1":
        gt = pd.read_csv(P["gt_t1"])
        st.dataframe(gt[gt["clip_id"] == clip], use_container_width=True, hide_index=True)
    else:
        gt = leer_json(P["gt_t2"])
        st.json(gt["clips"][clip])

# ------------------------------------------------------------------ 3. resultados
with tab3:
    st.header("Resultados")
    st.caption("Con 5 clips por corrida los intervalos bootstrap son optimistas y los pares clip-corrida no son "
               "independientes. Los extractores por reglas y la regla de diagnóstico v2 se ajustaron sobre estos mismos "
               "clips: no son exactitud esperada con audios nuevos.")

    st.subheader("Tarea 1: transcripción contra registro")
    tabla("resumen_t1_runs.csv", "Una fila por corrida de transcripción (extractor por reglas)")
    c1 = leer_csv("resumen_t1_clips.csv")
    if c1 is not None:
        st.markdown("**WER contra exactitud del registro** (cada punto es un clip en una corrida)")
        st.scatter_chart(c1, x="wer", y="acc", color="run")
        st.markdown("Un clip con WER alto y registro perfecto: *large fp16* en `t1_05` (bucle de repetición). "
                    "Un clip con WER bajo y registro roto: *large fp16* en `t1_02` (pierde VBA).")
    for nombre in ["benchmark_L0.csv"]:
        with st.expander("Benchmark de transcripción (WER, CER, s/min, VRAM)"):
            tabla(nombre)

    st.subheader("Tarea 2: escalera de degradación y validación aritmética")
    esc = tabla("resumen_t2_escalera.csv", "Trampas atrapadas contra perdidas, por nivel")
    c2 = leer_csv("resumen_t2_clips.csv")
    if c2 is not None:
        curva = c2.groupby("nivel").agg(WER=("wer", "mean"), exactitud_campos=("acc", "mean"))
        st.markdown("**Curva a lo largo de la escalera** (L0 original, L1 nota de voz, L2 teléfono, L3 ruido a 10 dB)")
        st.line_chart(curva)
    det = st.selectbox("Detalle del pedido por nivel", ["L0", "L1", "L2", "L3"])
    tabla(f"t2_pedido_{RUN}_{det}.csv")
    man = Path(P["tables"]) / "ladder_manifest.json"
    if man.exists():
        with st.expander("SNR logrado en L3 (ruido rosa, medido por RMS)"):
            st.json(json.load(open(man, encoding="utf-8")))

# ------------------------------------------------------------------ 4. probador
with tab4:
    st.header("Probador interactivo")
    st.markdown("Sube un clip y mira la transcripción, el registro y qué campos quedaron verificados. "
                "Esta pestaña llama al motor (`procesar_audio`), que necesita GPU para transcribir un audio nuevo.")
    esquema = st.radio("Esquema", ["entrevista", "pedido"], horizontal=True)
    nivel = st.selectbox("Nivel de la escalera (solo para la caché)", ["L0", "L1", "L2", "L3"])
    usar_cache = st.checkbox("Usar la transcripción cacheada si el archivo es de mi corpus (no requiere GPU)", value=True)
    up = st.file_uploader("Audio", type=["m4a", "wav", "mp3", "ogg", "flac"])
    if up and st.button("Procesar"):
        tmp = Path(tempfile.mkdtemp()) / up.name       # conserva el nombre para encontrar la caché por clip
        tmp.write_bytes(up.getvalue())
        st.audio(up.getvalue())
        try:
            from src.engine import procesar_audio
        except Exception as e:  # sin ctranslate2 / faster-whisper instalados
            st.error(f"No se pudo cargar el motor: {type(e).__name__}: {e}")
        else:
            with st.spinner("Procesando..."):
                res = procesar_audio(str(tmp), esquema, cfg=CFG, nivel=nivel, usar_cache=usar_cache)
            if res["error"]:
                st.error(res["error"])
            else:
                m1, m2, m3 = st.columns(3)
                m1.metric("Dispositivo", str(res["device"]))
                m2.metric("Segundos de transcripción", f"{res['elapsed_s']:.1f}" if res["elapsed_s"] else "-")
                m3.metric("Desde caché", str(res["desde_cache"]))
                st.markdown("**Transcripción**")
                st.write(res["transcript"])
                filas = [{"campo": k, "valor": json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v,
                          "verificado": "sí" if res["verificados"].get(k) else "NO"} for k, v in res["campos"].items()]
                st.markdown("**Registro**")
                st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)
                if "validacion" in res:
                    v = res["validacion"]
                    st.markdown("**Validación aritmética**")
                    (st.error if v["alerta"] else st.success)(
                        f"Total calculado {v['total_calculado']} contra total dicho {res['campos']['total_dicho']} "
                        f"(menciones: {v['menciones_total']}). Diagnóstico: {v['diagnostico']}.")
                st.caption("`verificado` significa que el valor aparece en la transcripción, no que sea correcto.")
