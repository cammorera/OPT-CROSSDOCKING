"""
LogiFast CR — Optimizador Cross Docking (MIP)
Universidad de Costa Rica · Ingeniería Industrial · I Semestre 2026

Instalación:
    pip install streamlit pulp pandas plotly

Ejecución:
    streamlit run logfast_crossdock.py
"""

import streamlit as st
import pulp
import pandas as pd
import plotly.graph_objects as go
from io import StringIO

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LogiFast CR — Cross Docking Optimizer",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  (light background, dark typography, clean cards)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #F0F2F8 !important;
    color: #111827 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #DDE1EC !important;
}
[data-testid="stSidebar"] * { color: #111827 !important; }

h1, h2, h3, h4, h5 { color: #0B1426 !important; font-family: 'DM Sans', sans-serif !important; font-weight: 700 !important; }
p, li, span, div { color: #1F2937; font-family: 'DM Sans', sans-serif !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 12px 12px 0 0;
    padding: 4px 8px 0;
    gap: 4px;
    border-bottom: 2px solid #DDE1EC;
}
.stTabs [data-baseweb="tab"] {
    color: #4B5563 !important;
    font-weight: 500 !important;
    border-radius: 8px 8px 0 0;
    padding: 10px 18px;
    font-size: 0.92rem;
}
.stTabs [aria-selected="true"] {
    color: #1D4ED8 !important;
    background: #EFF6FF !important;
    border-bottom: 2px solid #1D4ED8 !important;
}
[data-testid="stTabsContent"] {
    background: #FFFFFF;
    border-radius: 0 0 12px 12px;
    padding: 28px 24px;
    border: 1px solid #DDE1EC;
    border-top: none;
}

/* Cards */
.card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 22px 26px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border: 1px solid #E5E9F2;
    margin-bottom: 16px;
}
.card-blue  { border-left: 4px solid #2563EB; }
.card-green { border-left: 4px solid #16A34A; }
.card-amber { border-left: 4px solid #D97706; }
.card-red   { border-left: 4px solid #DC2626; }

.kpi-row { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
.kpi {
    flex: 1; min-width: 140px;
    background: #FFFFFF;
    border-radius: 10px;
    padding: 18px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border: 1px solid #E5E9F2;
    text-align: center;
}
.kpi .kpi-val { font-size: 2rem; font-weight: 700; color: #0B1426; }
.kpi .kpi-lbl { font-size: 0.8rem; color: #6B7280; text-transform: uppercase; letter-spacing: .04em; margin-top: 2px; }

.formula-box {
    background: #F8FAFF;
    border: 1px solid #C7D7F9;
    border-radius: 8px;
    padding: 14px 18px;
    font-family: 'DM Mono', monospace;
    font-size: 0.9rem;
    color: #1E3A8A;
    margin: 6px 0 12px;
}
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-blue   { background: #DBEAFE; color: #1D4ED8; }
.badge-green  { background: #DCFCE7; color: #15803D; }
.badge-purple { background: #EDE9FE; color: #6D28D9; }
.badge-orange { background: #FEF3C7; color: #B45309; }

/* Buttons */
.stButton > button {
    background: #1D4ED8 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 10px 20px !important;
    transition: background .2s;
}
.stButton > button:hover { background: #1E40AF !important; }

/* DataFrames */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Metrics */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 14px 18px;
    border: 1px solid #E5E9F2;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #0B1426 !important; font-weight: 700 !important; }
[data-testid="metric-container"] [data-testid="stMetricLabel"] { color: #6B7280 !important; }

/* Code blocks */
code { background: #F0F4FF; color: #1E3A8A; border-radius: 4px; padding: 2px 6px; font-family: 'DM Mono', monospace; }
pre { background: #1E293B !important; color: #E2E8F0 !important; border-radius: 10px; }

/* Expander */
.streamlit-expanderHeader { color: #0B1426 !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# DEFAULT DATA (TS5)
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_TS5 = (
    "i\t5\t\to\t3\t\tn\t8\t\t"
    "r\t1\t1\t170\t"
    "r\t2\t1\t6\tr\t2\t2\t6\tr\t2\t3\t19\tr\t2\t4\t50\tr\t2\t5\t38\tr\t2\t6\t6\tr\t2\t7\t19\tr\t2\t8\t56\t"
    "r\t3\t1\t49\tr\t3\t2\t31\tr\t3\t3\t60\tr\t3\t6\t12\tr\t3\t7\t37\tr\t3\t8\t31\t"
    "r\t4\t5\t143\tr\t4\t7\t47\t"
    "r\t5\t4\t58\tr\t5\t5\t36\tr\t5\t7\t72\tr\t5\t8\t14\t"
    "s\t1\t1\t75\ts\t1\t2\t12\ts\t1\t3\t59\ts\t1\t6\t9\ts\t1\t7\t98\ts\t1\t8\t40\t"
    "s\t2\t1\t150\ts\t2\t5\t217\t"
    "s\t3\t2\t25\ts\t3\t3\t20\ts\t3\t4\t108\ts\t3\t6\t9\ts\t3\t7\t77\ts\t3\t8\t61"
)


# ──────────────────────────────────────────────────────────────────────────────
# DATA PARSING
# ──────────────────────────────────────────────────────────────────────────────
def parse_ts_data(content: str) -> dict:
    tokens = content.split()
    result = {"num_inbound": 0, "num_outbound": 0, "num_products": 0,
               "inbound": {}, "outbound": {}}
    idx = 0
    while idx < len(tokens):
        t = tokens[idx]
        if t == "i" and idx + 1 < len(tokens):
            result["num_inbound"] = int(tokens[idx + 1]); idx += 2
        elif t == "o" and idx + 1 < len(tokens):
            result["num_outbound"] = int(tokens[idx + 1]); idx += 2
        elif t == "n" and idx + 1 < len(tokens):
            result["num_products"] = int(tokens[idx + 1]); idx += 2
        elif t == "r" and idx + 3 < len(tokens):
            tr, pr, qty = int(tokens[idx+1]), int(tokens[idx+2]), int(tokens[idx+3])
            result["inbound"].setdefault(tr, {})[pr] = qty
            idx += 4
        elif t == "s" and idx + 3 < len(tokens):
            tr, pr, qty = int(tokens[idx+1]), int(tokens[idx+2]), int(tokens[idx+3])
            result["outbound"].setdefault(tr, {})[pr] = qty
            idx += 4
        else:
            idx += 1
    return result


# ──────────────────────────────────────────────────────────────────────────────
# MIP SOLVER
# ──────────────────────────────────────────────────────────────────────────────
def solve_crossdock(data: dict, t_unit: int = 1, t_transfer: int = 5,
                    t_change: int = 10, time_limit: int = 300) -> dict:
    """
    Mixed-Integer Programming model for cross-docking scheduling.

    Variables
    ---------
    C_max      : continuous, makespan
    a[i]       : continuous, start of unloading for inbound truck i
    d[j]       : continuous, start of loading for outbound truck j
    x[i,j,k]  : integer >= 0, units of product k from inbound i to outbound j
    v[i,j]    : binary, 1 if any transfer between i and j
    u[i,i']   : binary, 1 if inbound i precedes i'
    w[j,j']   : binary, 1 if outbound j precedes j'
    """
    I = list(range(1, data["num_inbound"] + 1))
    J = list(range(1, data["num_outbound"] + 1))
    K = list(range(1, data["num_products"] + 1))

    r = {i: {k: data["inbound"].get(i, {}).get(k, 0)  for k in K} for i in I}
    s = {j: {k: data["outbound"].get(j, {}).get(k, 0) for k in K} for j in J}

    P = {i: sum(r[i][k] for k in K) * t_unit for i in I}
    Q = {j: sum(s[j][k] for k in K) * t_unit for j in J}

    M = (sum(P.values()) + sum(Q.values())
         + t_change * (len(I) + len(J)) * 3
         + t_transfer * len(I) * len(J) + 1000)

    prob = pulp.LpProblem("CrossDocking_MIP", pulp.LpMinimize)

    # --- Decision variables ---
    C_max = pulp.LpVariable("C_max", lowBound=0)
    a = {i: pulp.LpVariable(f"a_{i}", lowBound=0) for i in I}
    d = {j: pulp.LpVariable(f"d_{j}", lowBound=0) for j in J}

    x = {}
    for i in I:
        for j in J:
            for k in K:
                ub = min(r[i][k], s[j][k])
                x[i, j, k] = pulp.LpVariable(
                    f"x_{i}_{j}_{k}", lowBound=0, upBound=ub,
                    cat="Integer" if ub > 0 else "Continuous"
                )

    v = {(i, j): pulp.LpVariable(f"v_{i}_{j}", cat="Binary") for i in I for j in J}
    u = {(i, ip): pulp.LpVariable(f"u_{i}_{ip}", cat="Binary")
         for i in I for ip in I if i != ip}
    w = {(j, jp): pulp.LpVariable(f"w_{j}_{jp}", cat="Binary")
         for j in J for jp in J if j != jp}

    # --- Objective ---
    prob += C_max

    # R1 — Makespan definition
    for j in J:
        prob += C_max >= d[j] + Q[j], f"R1_makespan_{j}"

    # R2 — Inbound flow conservation
    for i in I:
        for k in K:
            prob += pulp.lpSum(x[i, j, k] for j in J) == r[i][k], f"R2_inflow_{i}_{k}"

    # R3 — Outbound flow conservation
    for j in J:
        for k in K:
            prob += pulp.lpSum(x[i, j, k] for i in I) == s[j][k], f"R3_outflow_{j}_{k}"

    # R4 — Link x and v
    for i in I:
        for j in J:
            M_ij = min(sum(r[i][k] for k in K), sum(s[j][k] for k in K))
            if M_ij > 0:
                prob += pulp.lpSum(x[i, j, k] for k in K) <= M_ij * v[i, j], f"R4_link_{i}_{j}"
            else:
                prob += v[i, j] == 0, f"R4_zero_{i}_{j}"

    # R5–R7 — Inbound sequencing (Big-M)
    for i in I:
        for ip in I:
            if i != ip:
                prob += (a[ip] >= a[i] + P[i] + t_change - M * (1 - u[i, ip]),
                         f"R5_inseq_{i}_{ip}")

    # R8 — Inbound antisymmetry
    for i in I:
        for ip in I:
            if i < ip:
                prob += u[i, ip] + u[ip, i] == 1, f"R8_inanti_{i}_{ip}"

    # R9–R11 — Outbound sequencing (Big-M)
    for j in J:
        for jp in J:
            if j != jp:
                prob += (d[jp] >= d[j] + Q[j] + t_change - M * (1 - w[j, jp]),
                         f"R9_outseq_{j}_{jp}")

    # R12 — Outbound antisymmetry
    for j in J:
        for jp in J:
            if j < jp:
                prob += w[j, jp] + w[jp, j] == 1, f"R12_outanti_{j}_{jp}"

    # R13 — Connection inbound → outbound
    for i in I:
        for j in J:
            prob += (d[j] >= a[i] + P[i] + t_transfer - M * (1 - v[i, j]),
                     f"R13_conn_{i}_{j}")

    solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
    prob.solve(solver)

    return {
        "status":    pulp.LpStatus[prob.status],
        "C_max":     pulp.value(C_max) or 0,
        "a":         {i: pulp.value(a[i]) or 0 for i in I},
        "d":         {j: pulp.value(d[j]) or 0 for j in J},
        "x":         {(i, j, k): pulp.value(x[i, j, k]) or 0
                      for i in I for j in J for k in K},
        "v":         {(i, j): pulp.value(v[i, j]) or 0 for i in I for j in J},
        "P": P, "Q": Q, "I": I, "J": J, "K": K, "r": r, "s": s,
        "t_unit": t_unit, "t_transfer": t_transfer, "t_change": t_change,
    }


# ──────────────────────────────────────────────────────────────────────────────
# GANTT CHART
# ──────────────────────────────────────────────────────────────────────────────
def make_gantt(sol: dict) -> go.Figure:
    I, J   = sol["I"], sol["J"]
    a, d   = sol["a"], sol["d"]
    P, Q   = sol["P"], sol["Q"]
    C_max  = sol["C_max"]

    palette_in  = ["#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD"]
    palette_out = ["#B45309", "#D97706", "#F59E0B", "#FCD34D", "#FDE68A"]

    fig = go.Figure()

    sorted_in  = sorted(I, key=lambda i: a[i])
    sorted_out = sorted(J, key=lambda j: d[j])

    for pos, i in enumerate(sorted_in):
        fig.add_trace(go.Bar(
            x=[P[i]], y=["🔵 Muelle Entrada"], base=[a[i]],
            orientation="h",
            marker_color=palette_in[pos % len(palette_in)],
            marker_line_width=0,
            name=f"Entrada C{i}",
            text=[f"  E{i} ({P[i]:.0f} min)"],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="white", size=11),
            hovertemplate=(
                f"<b>Camión Entrada {i}</b><br>"
                f"Inicio: {a[i]:.1f} min<br>"
                f"Fin: {a[i]+P[i]:.1f} min<br>"
                f"Duración: {P[i]:.0f} min<extra></extra>"
            ),
        ))

    for pos, j in enumerate(sorted_out):
        fig.add_trace(go.Bar(
            x=[Q[j]], y=["🟠 Muelle Salida"], base=[d[j]],
            orientation="h",
            marker_color=palette_out[pos % len(palette_out)],
            marker_line_width=0,
            name=f"Salida C{j}",
            text=[f"  S{j} ({Q[j]:.0f} min)"],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#1C1C1C", size=11),
            hovertemplate=(
                f"<b>Camión Salida {j}</b><br>"
                f"Inicio: {d[j]:.1f} min<br>"
                f"Fin: {d[j]+Q[j]:.1f} min<br>"
                f"Duración: {Q[j]:.0f} min<extra></extra>"
            ),
        ))

    fig.add_vline(
        x=C_max,
        line_dash="dash", line_color="#DC2626", line_width=2,
        annotation_text=f"  Makespan: {C_max:.1f} min",
        annotation_font=dict(color="#DC2626", size=13),
        annotation_bgcolor="rgba(255,255,255,0.85)",
    )

    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Tiempo (minutos)", color="#374151",
                   gridcolor="#E5E9F2", zeroline=False),
        yaxis=dict(color="#374151", gridcolor="#E5E9F2"),
        paper_bgcolor="white",
        plot_bgcolor="#FAFBFF",
        height=320,
        margin=dict(l=20, r=20, t=40, b=40),
        showlegend=True,
        legend=dict(orientation="h", y=-0.25, x=0, font=dict(size=11)),
        font=dict(family="DM Sans, sans-serif", color="#374151"),
        title=dict(
            text="Diagrama de Gantt — Operación Cross Docking",
            font=dict(size=15, color="#0B1426"),
            x=0.01,
        ),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 4px;'>
      <span style='font-size:2.6rem;'>🚛</span>
      <div style='font-size:1.3rem; font-weight:800; color:#0B1426; letter-spacing:-0.02em;'>LogiFast CR</div>
      <div style='font-size:0.78rem; color:#6B7280; margin-top:2px;'>Optimizador Cross Docking</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("**📁 Datos de entrada**")
    use_default = st.checkbox("Usar datos TS5 (predeterminado)", value=True)
    uploaded_file = None
    if not use_default:
        uploaded_file = st.file_uploader(
            "Cargar archivo .txt (formato TS)", type=["txt"]
        )
        if uploaded_file is None:
            st.caption("⚠️ Cargue un archivo para continuar.")

    st.divider()
    st.markdown("**⚙️ Parámetros operativos**")
    t_unit     = st.number_input("Tiempo/unidad (min)",          1, 10,  1)
    t_transfer = st.number_input("Traslado interno (min)",        1, 60,  5)
    t_change   = st.number_input("Cambio de camión (min)",        1, 60, 10)
    time_limit = st.number_input("Límite tiempo solver (seg)",   30, 600, 300)
    st.divider()

    solve_btn = st.button("🚀  Optimizar", use_container_width=True)

    st.markdown("""
    <div style='margin-top:24px; font-size:0.75rem; color:#9CA3AF; line-height:1.6;'>
    Universidad de Costa Rica<br>
    Ingeniería Industrial<br>
    Programación Entera Mixta<br>
    I Semestre 2026
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
if use_default:
    raw_content = DEFAULT_TS5
elif uploaded_file is not None:
    raw_content = uploaded_file.read().decode("utf-8")
else:
    raw_content = None

data = parse_ts_data(raw_content) if raw_content else None


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 8px 0 20px;'>
  <h1 style='margin:0; font-size:2rem; letter-spacing:-0.03em;'>
    🚛 LogiFast CR — Optimizador Cross Docking
  </h1>
  <p style='color:#6B7280; margin:6px 0 0; font-size:0.93rem;'>
    Universidad de Costa Rica · Ingeniería Industrial · Programación Entera Mixta · I Semestre 2026
  </p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────────────────
tab_data, tab_model, tab_sol, tab_code = st.tabs([
    "📊  Datos del Problema",
    "📐  Formulación MIP",
    "🎯  Solución Óptima",
    "💻  Código",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATOS
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    if data is None:
        st.info("👈 Cargue un archivo de datos en la barra lateral o active 'Usar datos TS5'.")
    else:
        I = list(range(1, data["num_inbound"] + 1))
        J = list(range(1, data["num_outbound"] + 1))
        K = list(range(1, data["num_products"] + 1))

        st.markdown("""
        <div class='card card-blue'>
        <b>¿Qué es este archivo?</b> El archivo TS describe la operación diaria del centro de
        distribución: qué camiones llegan (r), qué camiones salen (s), y cuántas unidades
        de cada producto transportan.
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("🚚 Camiones de Entrada", data["num_inbound"])
        c2.metric("🚛 Camiones de Salida",  data["num_outbound"])
        c3.metric("📦 Tipos de Producto",   data["num_products"])

        st.subheader("Camiones de Entrada (Proveedores)")
        rows_in = []
        for i in I:
            row = {"Camión": f"Entrada {i}"}
            total = 0
            for k in K:
                q = data["inbound"].get(i, {}).get(k, 0)
                row[f"P{k}"] = q if q > 0 else "—"
                total += q
            row["Total uds."] = total
            rows_in.append(row)
        st.dataframe(pd.DataFrame(rows_in), hide_index=True, use_container_width=True)

        st.subheader("Camiones de Salida (Clientes)")
        rows_out = []
        for j in J:
            row = {"Camión": f"Salida {j}"}
            total = 0
            for k in K:
                q = data["outbound"].get(j, {}).get(k, 0)
                row[f"P{k}"] = q if q > 0 else "—"
                total += q
            row["Total uds."] = total
            rows_out.append(row)
        st.dataframe(pd.DataFrame(rows_out), hide_index=True, use_container_width=True)

        st.subheader("Verificación de Balance Oferta–Demanda")
        balance_rows = []
        all_ok = True
        for k in K:
            supply = sum(data["inbound"].get(i, {}).get(k, 0)  for i in I)
            demand = sum(data["outbound"].get(j, {}).get(k, 0) for j in J)
            ok = supply == demand
            if not ok: all_ok = False
            balance_rows.append({
                "Producto": f"P{k}",
                "Oferta (entrada)": supply,
                "Demanda (salida)": demand,
                "Balance": "✅ OK" if ok else f"❌ Diferencia: {supply - demand:+d}",
            })
        st.dataframe(pd.DataFrame(balance_rows), hide_index=True, use_container_width=True)
        if all_ok:
            st.success("✅ Balance verificado: oferta = demanda para todos los productos.")
        else:
            st.error("❌ Desbalance detectado. Verifique los datos antes de optimizar.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FORMULACIÓN
# ══════════════════════════════════════════════════════════════════════════════
with tab_model:
    st.header("Formulación del Modelo de Programación Entera Mixta")

    # ── Q1 ──
    with st.expander("1️⃣  Decisiones que debe tomar la empresa", expanded=True):
        st.markdown("""
        Para organizar la operación del centro de cross-docking, la empresa debe decidir:

        - **Secuencia de camiones de entrada**: ¿En qué orden se atienden en el muelle de recepción?
        - **Secuencia de camiones de salida**: ¿En qué orden se cargan en el muelle de despacho?
        - **Asignación de productos por ruta**: ¿Cuántas unidades de cada producto del camión de entrada *i* se destinan al camión de salida *j*?
        - **Uso de almacenamiento temporal**: ¿Los productos van directo del camión de entrada al camión de salida, o pasan por almacenamiento temporal?

        La combinación de estas decisiones determina el tiempo total de operación.
        """)

    # ── Q2 ──
    with st.expander("2️⃣  ¿Qué se busca optimizar?"):
        st.markdown("""
        Se busca **minimizar el makespan**: el tiempo total desde que inicia la primera operación
        hasta que el último camión de salida termina su carga y abandona el muelle.

        Un makespan mínimo implica:
        - Menor tiempo de operación del almacén
        - Reducción de costos fijos (personal, equipos, instalación)
        - Mayor nivel de servicio (entregas más rápidas a clientes)
        - Menor acumulación de productos en almacenamiento temporal
        """)

    # ── Q4 ──
    with st.expander("4️⃣  Función objetivo en Programación Lineal Mixta"):
        st.markdown("**Minimizar el makespan** (tiempo total de operación del almacén):")
        st.latex(r"\min \quad C_{\max}")
        st.markdown("Sujeto a que el makespan sea al menos el tiempo de salida del último camión de despacho:")
        st.latex(r"C_{\max} \geq d_j + Q_j \qquad \forall\, j \in J")
        st.caption("donde *d_j* es el tiempo de inicio de carga del camión de salida *j* y *Q_j* es su tiempo de carga total.")

    # ── Q5 ──
    with st.expander("5️⃣  Variables de decisión"):
        st.markdown("##### Continuas")
        rows_v = [
            ("Cₘₐₓ ≥ 0",   "Continua",  "Makespan — tiempo total de operación (función objetivo)"),
            ("aᵢ ≥ 0",      "Continua",  "Tiempo de inicio de descarga del camión de entrada *i*"),
            ("dⱼ ≥ 0",      "Continua",  "Tiempo de inicio de carga del camión de salida *j*"),
        ]
        st.dataframe(pd.DataFrame(rows_v, columns=["Variable", "Tipo", "Descripción"]),
                     hide_index=True, use_container_width=True)

        st.markdown("##### Enteras no binarias")
        rows_v2 = [
            ("xᵢⱼₖ ≥ 0, entero", "Entera",
             "Unidades del producto *k* transferidas del camión entrada *i* al camión salida *j*"),
        ]
        st.dataframe(pd.DataFrame(rows_v2, columns=["Variable", "Tipo", "Descripción"]),
                     hide_index=True, use_container_width=True)

        st.markdown("##### Binarias")
        rows_v3 = [
            ("vᵢⱼ ∈ {0,1}",    "Binaria", "1 si hay transferencia de productos entre el camión entrada *i* y el camión salida *j*"),
            ("uᵢᵢ' ∈ {0,1}",   "Binaria", "1 si el camión de entrada *i* se atiende antes que el camión *i'*"),
            ("wⱼⱼ' ∈ {0,1}",   "Binaria", "1 si el camión de salida *j* se carga antes que el camión *j'*"),
        ]
        st.dataframe(pd.DataFrame(rows_v3, columns=["Variable", "Tipo", "Descripción"]),
                     hide_index=True, use_container_width=True)

    # ── Q6 ──
    with st.expander("6️⃣  Restricciones del modelo (13 restricciones)"):
        constraints_info = [
            ("R1",   "Definición del makespan",
             r"C_{\max} \geq d_j + Q_j \quad \forall\, j \in J",
             "El makespan debe ser mayor o igual al tiempo de finalización del último camión de salida."),
            ("R2",   "Conservación de flujo — entrada",
             r"\sum_{j \in J} x_{ijk} = r_{ik} \quad \forall\, i \in I,\, k \in K",
             "Todos los productos de cada camión de entrada deben ser asignados a algún camión de salida."),
            ("R3",   "Conservación de flujo — salida",
             r"\sum_{i \in I} x_{ijk} = s_{jk} \quad \forall\, j \in J,\, k \in K",
             "Cada camión de salida recibe exactamente las unidades que necesita de cada producto."),
            ("R4",   "Vínculo entre xᵢⱼₖ y vᵢⱼ",
             r"\sum_{k \in K} x_{ijk} \leq M_{ij}\cdot v_{ij} \quad \forall\, i,\, j",
             "Si se transfieren productos entre i y j, entonces vᵢⱼ = 1. Linealiza la relación lógica."),
            ("R5–R7", "Secuencia válida — entrada (3 restricciones)",
             r"a_{i'} \geq a_i + P_i + t_{\text{cambio}} - M\,(1 - u_{ii'}) \quad \forall\, i \neq i'",
             "Garantiza que si el camión i precede a i', el segundo no puede iniciar antes de que el primero termine más el tiempo de cambio."),
            ("R8",   "Antisimetría — entrada",
             r"u_{ii'} + u_{i'i} = 1 \quad \forall\, i < i'",
             "Un camión no puede preceder y ser precedido por otro simultáneamente. Evita subtours."),
            ("R9–R11", "Secuencia válida — salida (3 restricciones)",
             r"d_{j'} \geq d_j + Q_j + t_{\text{cambio}} - M\,(1 - w_{jj'}) \quad \forall\, j \neq j'",
             "Análogo a R5–R7 para camiones de salida."),
            ("R12",  "Antisimetría — salida",
             r"w_{jj'} + w_{j'j} = 1 \quad \forall\, j < j'",
             "Análogo a R8 para camiones de salida."),
            ("R13",  "Conexión entrada–salida",
             r"d_j \geq a_i + P_i + t_{\text{traslado}} - M\,(1 - v_{ij}) \quad \forall\, i,\, j",
             "El camión de salida j no puede iniciar su carga hasta que el camión de entrada i haya terminado de descargarse, más el tiempo de traslado interno."),
        ]

        for tag, title, latex_formula, description in constraints_info:
            col_tag, col_body = st.columns([0.08, 0.92])
            with col_tag:
                st.markdown(f"""<div class='badge badge-blue' style='margin-top:14px;'>{tag}</div>""",
                            unsafe_allow_html=True)
            with col_body:
                st.markdown(f"**{title}**")
                st.latex(latex_formula)
                st.caption(description)
            st.divider()

        st.markdown("""
        **Parámetros clave:**
        - *Pᵢ* = tiempo total de descarga del camión de entrada *i* = Σₖ rᵢₖ · t_unidad
        - *Qⱼ* = tiempo total de carga del camión de salida *j*   = Σₖ sⱼₖ · t_unidad
        - *M*  = constante Big-M (valor suficientemente grande)
        - *Mᵢⱼ* = min(Σₖ rᵢₖ, Σₖ sⱼₖ) — cota superior natural para xᵢⱼ
        """)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SOLUCIÓN
# ══════════════════════════════════════════════════════════════════════════════
with tab_sol:
    if data is None:
        st.info("👈 Cargue datos primero desde la barra lateral.")
    else:
        # Trigger solve
        if solve_btn:
            with st.spinner("⏳ Resolviendo el modelo MIP… esto puede tomar algunos segundos."):
                sol = solve_crossdock(data, t_unit, t_transfer, t_change, time_limit)
                st.session_state["solution"] = sol
                st.session_state["sol_params"] = (t_unit, t_transfer, t_change)

        sol = st.session_state.get("solution")

        if sol is None:
            st.markdown("""
            <div class='card card-amber'>
            ⚡ Presione <b>🚀 Optimizar</b> en la barra lateral para resolver el modelo MIP
            con los datos cargados y los parámetros configurados.
            </div>
            """, unsafe_allow_html=True)
        elif sol["status"] not in ("Optimal", "Feasible"):
            st.error(f"El solver no encontró solución. Estado: **{sol['status']}**. "
                     "Aumente el límite de tiempo o verifique los datos.")
        else:
            I, J, K = sol["I"], sol["J"], sol["K"]
            status_label = "✅ Óptimo" if sol["status"] == "Optimal" else "🔶 Factible"
            params_used  = st.session_state.get("sol_params", (t_unit, t_transfer, t_change))

            # ── KPIs ──
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Estado",             status_label)
            c2.metric("⏱️ Makespan",         f"{sol['C_max']:.1f} min")
            c3.metric("🚚 Camiones Entrada", len(I))
            c4.metric("🚛 Camiones Salida",  len(J))
            c5.metric("📦 Productos",        len(K))

            # ── Parámetros usados ──
            st.caption(
                f"Parámetros: tiempo/unidad={params_used[0]} min · "
                f"traslado interno={params_used[1]} min · "
                f"cambio de camión={params_used[2]} min"
            )
            st.divider()

            # ── Q7: Orden de camiones ──
            st.subheader("7️⃣  Orden óptimo de los camiones")

            col_in, col_out = st.columns(2)

            with col_in:
                st.markdown("**🔵 Muelle de Recepción — Camiones de Entrada**")
                sorted_in = sorted(I, key=lambda i: sol["a"][i])
                rows_in = []
                for pos, i in enumerate(sorted_in, 1):
                    ai = sol["a"][i]
                    rows_in.append({
                        "Pos.": pos,
                        "Camión": f"Entrada {i}",
                        "Inicio (min)": f"{ai:.1f}",
                        "Fin (min)":    f"{ai + sol['P'][i]:.1f}",
                        "Duración (min)": f"{sol['P'][i]:.0f}",
                    })
                st.dataframe(pd.DataFrame(rows_in), hide_index=True, use_container_width=True)
                seq_in = " → ".join([f"E{i}" for i in sorted_in])
                st.markdown(f"""<div class='formula-box'>Secuencia: &nbsp; {seq_in}</div>""",
                            unsafe_allow_html=True)

            with col_out:
                st.markdown("**🟠 Muelle de Despacho — Camiones de Salida**")
                sorted_out = sorted(J, key=lambda j: sol["d"][j])
                rows_out = []
                for pos, j in enumerate(sorted_out, 1):
                    dj = sol["d"][j]
                    rows_out.append({
                        "Pos.": pos,
                        "Camión": f"Salida {j}",
                        "Inicio (min)": f"{dj:.1f}",
                        "Fin (min)":    f"{dj + sol['Q'][j]:.1f}",
                        "Duración (min)": f"{sol['Q'][j]:.0f}",
                    })
                st.dataframe(pd.DataFrame(rows_out), hide_index=True, use_container_width=True)
                seq_out = " → ".join([f"S{j}" for j in sorted_out])
                st.markdown(f"""<div class='formula-box'>Secuencia: &nbsp; {seq_out}</div>""",
                            unsafe_allow_html=True)

            st.divider()

            # ── Q8: Makespan ──
            st.subheader("8️⃣  Tiempo mínimo de operación")
            st.markdown(f"""
            <div class='card card-green'>
              <span style='font-size:1.7rem; font-weight:800; color:#15803D;'>
                ⏱️ Makespan óptimo = {sol['C_max']:.1f} minutos
              </span><br>
              <span style='color:#374151;'>
                El almacén completa todas las operaciones (descarga de camiones de entrada +
                carga de camiones de salida) en un mínimo de <b>{sol['C_max']:.1f} minutos</b>
                con la secuencia mostrada.
              </span>
            </div>
            """, unsafe_allow_html=True)

            # ── Gantt ──
            st.subheader("Diagrama de Gantt")
            st.plotly_chart(make_gantt(sol), use_container_width=True)

            # ── Transfer matrix ──
            st.subheader("Matriz de Transferencia de Productos (xᵢⱼₖ)")
            st.caption(
                "Unidades de cada producto k transferidas desde el camión de entrada i "
                "hacia el camión de salida j."
            )

            any_product_shown = False
            for k in K:
                # check if this product is actually traded
                has_data = any(
                    (sol["x"].get((i, j, k), 0) > 0.5)
                    for i in I for j in J
                )
                if not has_data:
                    continue
                any_product_shown = True
                matrix_rows = []
                for i in I:
                    row = {"Camión": f"Entrada {i}"}
                    for j in J:
                        val = sol["x"].get((i, j, k), 0)
                        row[f"Salida {j}"] = int(round(val)) if val > 0.5 else 0
                    matrix_rows.append(row)
                df_m = pd.DataFrame(matrix_rows)
                st.markdown(f"**Producto P{k}**")
                st.dataframe(df_m, hide_index=True, use_container_width=True)

            if not any_product_shown:
                st.info("No se encontraron transferencias con cantidad > 0.")

            # ── v_ij summary ──
            st.subheader("Flujos Activos (vᵢⱼ = 1)")
            flow_rows = []
            for i in I:
                for j in J:
                    if sol["v"].get((i, j), 0) > 0.5:
                        total_units = sum(
                            int(round(sol["x"].get((i, j, k), 0)))
                            for k in K
                        )
                        flow_rows.append({
                            "Camión Entrada": f"Entrada {i}",
                            "Camión Salida":  f"Salida {j}",
                            "Unidades":       total_units,
                            "Inicio traslado (min)": f"{sol['a'][i] + sol['P'][i]:.1f}",
                        })
            if flow_rows:
                st.dataframe(pd.DataFrame(flow_rows), hide_index=True, use_container_width=True)
            else:
                st.info("No se identificaron flujos activos.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CÓDIGO
# ══════════════════════════════════════════════════════════════════════════════
with tab_code:
    st.header("💻 Código fuente de la solución")

    code_tab1, code_tab2 = st.tabs(["🐍 Python (PuLP)", "⚡ AMPL"])

    with code_tab1:
        st.markdown("Modelo MIP completo implementado con la librería `PuLP` de Python.")
        python_code = r'''
import pulp

def solve_crossdock(data, t_unit=1, t_transfer=5, t_change=10):
    """
    Cross-Docking MIP Scheduler
    ---------------------------
    Minimiza el makespan (tiempo total) secuenciando camiones
    de entrada y salida en un centro de cross-docking.

    Parámetros
    ----------
    data       : dict con num_inbound, num_outbound, num_products, inbound, outbound
    t_unit     : minutos por unidad cargada/descargada
    t_transfer : tiempo de traslado interno (minutos por lote)
    t_change   : tiempo de cambio entre camiones (minutos)
    """
    I = list(range(1, data["num_inbound"]  + 1))
    J = list(range(1, data["num_outbound"] + 1))
    K = list(range(1, data["num_products"] + 1))

    r = {i: {k: data["inbound"].get(i, {}).get(k, 0)  for k in K} for i in I}
    s = {j: {k: data["outbound"].get(j, {}).get(k, 0) for k in K} for j in J}

    P = {i: sum(r[i][k] for k in K) * t_unit for i in I}   # Tiempos descarga
    Q = {j: sum(s[j][k] for k in K) * t_unit for j in J}   # Tiempos carga

    # Big-M conservador
    M = (sum(P.values()) + sum(Q.values())
         + t_change * (len(I) + len(J)) * 3
         + t_transfer * len(I) * len(J) + 1000)

    prob = pulp.LpProblem("CrossDocking_MIP", pulp.LpMinimize)

    # ── Variables de decisión ───────────────────────────────────────────────
    C_max = pulp.LpVariable("C_max", lowBound=0)                  # Makespan
    a = {i: pulp.LpVariable(f"a_{i}", lowBound=0) for i in I}     # Inicio descarga
    d = {j: pulp.LpVariable(f"d_{j}", lowBound=0) for j in J}     # Inicio carga

    # Unidades producto k de camión entrada i a camión salida j
    x = {(i, j, k): pulp.LpVariable(f"x_{i}_{j}_{k}", lowBound=0,
                                      upBound=min(r[i][k], s[j][k]),
                                      cat="Integer")
         for i in I for j in J for k in K}

    v = {(i, j): pulp.LpVariable(f"v_{i}_{j}", cat="Binary")        # Flujo i->j
         for i in I for j in J}
    u = {(i, ip): pulp.LpVariable(f"u_{i}_{ip}", cat="Binary")      # Orden entrada
         for i in I for ip in I if i != ip}
    w = {(j, jp): pulp.LpVariable(f"w_{j}_{jp}", cat="Binary")      # Orden salida
         for j in J for jp in J if j != jp}

    # ── Función objetivo ────────────────────────────────────────────────────
    prob += C_max

    # ── Restricciones ───────────────────────────────────────────────────────

    # R1: Makespan >= fin del último camión de salida
    for j in J:
        prob += C_max >= d[j] + Q[j]

    # R2: Conservación de flujo (entrada) — todos los productos salen
    for i in I:
        for k in K:
            prob += pulp.lpSum(x[i, j, k] for j in J) == r[i][k]

    # R3: Conservación de flujo (salida) — camión recibe lo que necesita
    for j in J:
        for k in K:
            prob += pulp.lpSum(x[i, j, k] for i in I) == s[j][k]

    # R4: Vínculo entre xijk y vij
    for i in I:
        for j in J:
            M_ij = min(sum(r[i][k] for k in K), sum(s[j][k] for k in K))
            if M_ij > 0:
                prob += pulp.lpSum(x[i, j, k] for k in K) <= M_ij * v[i, j]
            else:
                prob += v[i, j] == 0

    # R5–R7: Secuencia de camiones de entrada (Big-M)
    for i in I:
        for ip in I:
            if i != ip:
                prob += a[ip] >= a[i] + P[i] + t_change - M * (1 - u[i, ip])

    # R8: Antisimetría — entrada (sin auto-precedencia)
    for i in I:
        for ip in I:
            if i < ip:
                prob += u[i, ip] + u[ip, i] == 1

    # R9–R11: Secuencia de camiones de salida (Big-M)
    for j in J:
        for jp in J:
            if j != jp:
                prob += d[jp] >= d[j] + Q[j] + t_change - M * (1 - w[j, jp])

    # R12: Antisimetría — salida
    for j in J:
        for jp in J:
            if j < jp:
                prob += w[j, jp] + w[jp, j] == 1

    # R13: Conexión entrada–salida
    for i in I:
        for j in J:
            prob += d[j] >= a[i] + P[i] + t_transfer - M * (1 - v[i, j])

    # ── Resolver ────────────────────────────────────────────────────────────
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=300))

    return {
        "status": pulp.LpStatus[prob.status],
        "makespan": pulp.value(C_max),
        "a":  {i: pulp.value(a[i]) for i in I},
        "d":  {j: pulp.value(d[j]) for j in J},
        "x":  {(i, j, k): pulp.value(x[i, j, k]) or 0
               for i in I for j in J for k in K},
    }
'''
        st.code(python_code, language="python")

    with code_tab2:
        st.markdown("Modelo MIP equivalente para **AMPL** (con solver CBC o CPLEX).")
        ampl_code = r'''
# ──────────────────────────────────────────────────────
# Cross-Docking MIP — AMPL
# LogiFast CR · UCR Ingeniería Industrial
# ──────────────────────────────────────────────────────

# Conjuntos
set I;           # Camiones de entrada
set J;           # Camiones de salida
set K;           # Tipos de productos

# Parámetros de demanda / oferta
param r{I, K} >= 0 integer;   # Unidades de k en camión entrada i
param s{J, K} >= 0 integer;   # Unidades de k requeridas por camión salida j

# Parámetros de tiempo
param t_unit     := 1;    # min/unidad
param t_transfer := 5;    # min traslado interno
param t_change   := 10;   # min cambio de camión
param BIG_M      := 1e6;  # Big-M

# Tiempos de proceso derivados
param P{i in I} := sum{k in K} r[i, k] * t_unit;
param Q{j in J} := sum{k in K} s[j, k] * t_unit;

# ── Variables de decisión ──────────────────────────────
var C_max >= 0;                                # Makespan
var a{I}  >= 0;                                # Inicio descarga camión entrada i
var d{J}  >= 0;                                # Inicio carga camión salida j

var x{i in I, j in J, k in K} >= 0,
    <= min(r[i,k], s[j,k]), integer;           # Unidades k de i a j

var v{I, J} binary;                            # 1 si flujo activo entre i y j
var u{i in I, ip in I: i <> ip} binary;        # 1 si entrada i antes de i'
var w{j in J, jp in J: j <> jp} binary;        # 1 si salida j antes de j'

# ── Objetivo ──────────────────────────────────────────
minimize Makespan: C_max;

# ── Restricciones ─────────────────────────────────────

# R1 — Makespan
subject to R1_makespan {j in J}:
    C_max >= d[j] + Q[j];

# R2 — Conservación de flujo (entrada)
subject to R2_inbound {i in I, k in K}:
    sum{j in J} x[i,j,k] = r[i,k];

# R3 — Conservación de flujo (salida)
subject to R3_outbound {j in J, k in K}:
    sum{i in I} x[i,j,k] = s[j,k];

# R4 — Vínculo x y v
subject to R4_link {i in I, j in J}:
    sum{k in K} x[i,j,k] <=
        min(sum{k in K} r[i,k], sum{k in K} s[j,k]) * v[i,j];

# R5–R7 — Secuencia entrada
subject to R5_inbound_seq {i in I, ip in I: i <> ip}:
    a[ip] >= a[i] + P[i] + t_change - BIG_M * (1 - u[i,ip]);

# R8 — Antisimetría entrada
subject to R8_inbound_anti {i in I, ip in I: i < ip}:
    u[i,ip] + u[ip,i] = 1;

# R9–R11 — Secuencia salida
subject to R9_outbound_seq {j in J, jp in J: j <> jp}:
    d[jp] >= d[j] + Q[j] + t_change - BIG_M * (1 - w[j,jp]);

# R12 — Antisimetría salida
subject to R12_outbound_anti {j in J, jp in J: j < jp}:
    w[j,jp] + w[jp,j] = 1;

# R13 — Conexión entrada–salida
subject to R13_connection {i in I, j in J}:
    d[j] >= a[i] + P[i] + t_transfer - BIG_M * (1 - v[i,j]);
'''
        st.code(ampl_code, language="text")

    st.divider()
    st.markdown("""
    **Dependencias Python:**
    ```
    pip install streamlit pulp pandas plotly
    ```
    **Ejecución:**
    ```
    streamlit run logfast_crossdock.py
    ```
    El solver predeterminado es **CBC** (incluido con PuLP). Para instancias grandes
    se recomienda usar CPLEX o Gurobi mediante la API de PuLP.
    """)
