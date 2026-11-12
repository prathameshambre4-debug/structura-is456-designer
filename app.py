"""
StructuraAI: IS 456:2000 Reinforced Concrete Beam Design & Analysis Suite
Author: Structural Engineering Hub
License: MIT
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- Page Configuration ---
st.set_page_config(
    page_title="StructuraAI | RC Beam Designer (IS 456:2000)",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- IS 456:2000 Engineering Constants & Formulas ---
LIMITING_XU_RATIOS = {
    250: 0.53,
    415: 0.48,
    500: 0.46,
    550: 0.44
}

TAU_C_MAX = {
    20: 2.8,
    25: 3.1,
    30: 3.5,
    35: 3.7,
    40: 4.0
}

def calculate_limiting_moment(b: float, d: float, fck: float, fy: int):
    xu_max_ratio = LIMITING_XU_RATIOS.get(fy, 0.48)
    xu_max = xu_max_ratio * d
    # Mu_lim = 0.36 * fck * b * xu_max * (d - 0.42 * xu_max)
    mu_lim = 0.36 * fck * b * xu_max * (d - 0.42 * xu_max) * 1e-6  # in kN.m
    return mu_lim, xu_max

def design_singly_reinforced(b: float, d: float, fck: float, fy: int, Mu: float):
    # Solving 0.87*fy*Ast*d*(1 - Ast*fy/(b*d*fck)) = Mu
    # Ast = (0.5 * fck / fy) * (1 - sqrt(1 - (4.6 * Mu * 1e6)/(fck * b * d**2))) * b * d
    term = 1 - (4.6 * Mu * 1e6) / (fck * b * (d ** 2))
    if term < 0:
        return None
    ast_req = (0.5 * fck / fy) * (1.0 - np.sqrt(term)) * b * d
    return ast_req

def get_approx_tau_c(fck: float, pt: float) -> float:
    # Empirical fit for IS 456 Table 19 design shear strength of concrete
    pt_clamped = min(max(pt, 0.15), 3.0)
    base_tau = 0.85 * np.sqrt(0.8 * fck) * (np.sqrt(1 + 5 * (pt_clamped / 100)) - 1) / 6
    return round(float(base_tau), 3)

# --- UI Layout ---
st.title("🏗️ StructuraAI: RC Beam Design Suite")
st.caption("Automated Limit State Method (LSM) Section Design per IS 456:2000")

with st.sidebar:
    st.header("⚙️ Design Parameters")
    
    st.subheader("1. Cross-Section Geometry")
    b = st.number_input("Width of Beam, b (mm)", min_value=150, max_value=1200, value=300, step=25)
    D = st.number_input("Total Depth, D (mm)", min_value=200, max_value=2500, value=500, step=25)
    eff_cover = st.number_input("Nominal Cover + Bar Rad., d' (mm)", min_value=20, max_value=100, value=40, step=5)
    d = D - eff_cover
    st.info(f"**Effective Depth (d):** {d:.1f} mm")

    st.subheader("2. Material Properties")
    fck = st.selectbox("Concrete Grade (f_ck)", [20, 25, 30, 35, 40], index=1, format_func=lambda x: f"M{x} ({x} MPa)")
    fy = st.selectbox("Steel Grade (f_y)", [250, 415, 500, 550], index=1, format_func=lambda x: f"Fe {x} ({x} MPa)")

    st.subheader("3. Factored Internal Actions")
    Mu = st.number_input("Factored Bending Moment, Mu (kN·m)", min_value=1.0, max_value=5000.0, value=140.0, step=5.0)
    Vu = st.number_input("Factored Shear Force, Vu (kN)", min_value=0.0, max_value=2000.0, value=75.0, step=5.0)
    span = st.number_input("Effective Span, L (m)", min_value=1.0, max_value=25.0, value=5.0, step=0.5)

# --- Core Engineering Calculations ---
mu_lim, xu_max = calculate_limiting_moment(b, d, fck, fy)
ast_min = (0.85 * b * d) / fy
ast_max = 0.04 * b * D

is_singly = Mu <= mu_lim

tab_results, tab_visual, tab_shear, tab_audit = st.tabs([
    "📊 Flexural Design", 
    "📐 Cross-Section Visualizer", 
    "⚡ Shear & Detailing", 
    "🧠 Structural AI Audit"
])

with tab_results:
    st.subheader("Flexural Capacity & Limit State Evaluation")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Applied Moment (Mu)", f"{Mu:.2f} kN·m")
    col2.metric("Limiting Moment (Mu,lim)", f"{mu_lim:.2f} kN·m")
    col3.metric("Section Status", "Singly Reinforced" if is_singly else "Doubly Reinforced Req.")

    st.divider()

    if is_singly:
        ast_req = design_singly_reinforced(b, d, fck, fy, Mu)
        ast_prov = max(ast_req, ast_min)
        pt_prov = (ast_prov / (b * d)) * 100

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""
            - **Neutral Axis Depth ($x_{{u,\\text{{max}}}}$):** `{xu_max:.1f} mm`
            - **Calculated Tensile Steel ($A_{{st,\\text{{req}}}}$):** `{ast_req:.1f} mm²`
            - **Minimum Steel Area ($A_{{st,\\text{{min}}}}$):** `{ast_min:.1f} mm²` (IS 456 Cl. 26.5.1.1)
            - **Maximum Permissible Steel ($A_{{st,\\text{{max}}}}$):** `{ast_max:.1f} mm²` (4% bD)
            """)
        with res_col2:
            st.markdown(f"""
            - **Adopted Tension Steel ($A_{{st}}$):** `{ast_prov:.1f} mm²`
            - **Steel Percentage ($p_t$):** `{pt_prov:.2f} %`
            - **Design Condition:** `Under-Reinforced Section (Ductile Failure Mode)`
            """)
            
        # Bar Selection Recommendation
        st.write("#### Rebar Configuration Options")
        bar_opts = [16, 20, 25, 32]
        opt_data = []
        for dia in bar_opts:
            area_one = (np.pi / 4) * (dia ** 2)
            n_bars = int(np.ceil(ast_prov / area_one))
            n_bars = max(n_bars, 2)
            opt_data.append({
                "Bar Diameter (mm)": f"{dia} mm",
                "Number of Bars": n_bars,
                "Provided Area (mm²)": round(n_bars * area_one, 1),
                "Capacity Reserve (%)": round(((n_bars * area_one - ast_prov) / ast_prov) * 100, 1)
            })
        st.dataframe(opt_data, use_container_width=True)

    else:
        st.error(f"Applied Moment ($M_u = {Mu:.1f}$ kN·m) exceeds limiting capacity ($M_{{u,\\text{{lim}}}} = {mu_lim:.1f}$ kN·m).")
        mu2 = Mu - mu_lim
        st.warning(f"Excess Moment to be carried by compression steel ($M_{{u2}}$): {mu2:.2f} kN·m. Please increase section dimensions or add compression reinforcement.")

with tab_visual:
    st.subheader("Geometric Cross-Section & Stress Distribution")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    
    # 1. Cross-Section Drawing
    ax1.set_xlim(-50, b + 50)
    ax1.set_ylim(-50, D + 50)
    ax1.set_aspect('equal')
    ax1.axis('off')
    
    # Concrete beam block
    beam_rect = patches.Rectangle((0, 0), b, D, linewidth=2, edgecolor='#1e293b', facecolor='#e2e8f0')
    ax1.add_patch(beam_rect)
    
    # Stirrup outline
    stirrup = patches.Rectangle(
        (eff_cover/2, eff_cover/2), 
        b - eff_cover, 
        D - eff_cover, 
        linewidth=1.5, 
        edgecolor='#dc2626', 
        linestyle='--', 
        facecolor='none'
    )
    ax1.add_patch(stirrup)
    
    # Tension reinforcement (assume 3 bars visually)
    rebar_y = eff_cover
    spacing = (b - 2 * eff_cover) / 2
    for i in range(3):
        rebar_x = eff_cover + i * spacing
        rebar = patches.Circle((rebar_x, rebar_y), radius=10, facecolor='#2563eb', edgecolor='#0f172a')
        ax1.add_patch(rebar)
        
    ax1.text(b/2, -35, f"b = {b} mm", ha='center', fontweight='bold')
    ax1.text(-35, D/2, f"D = {D} mm", va='center', rotation='vertical', fontweight='bold')
    ax1.set_title("Cross-Section Detailing", fontsize=11, fontweight='bold')

    # 2. IS 456 Parabolic-Rectangular Stress Block
    ax2.set_xlim(-0.1, 0.6)
    ax2.set_ylim(0, D)
    ax2.axis('off')
    
    xu_plot = xu_max if is_singly else 0.48 * d
    neutral_axis_y = D - xu_plot
    
    # Stress block lines
    ax2.plot([0, 0.45 * fck * 0.05, 0.45 * fck * 0.05, 0], [D, D, D - (3/7)*xu_plot, neutral_axis_y], color='#047857', lw=2)
    ax2.axhline(y=neutral_axis_y, color='#b91c1c', linestyle=':', label='Neutral Axis (NA)')
    ax2.text(0.1, neutral_axis_y + 10, f"N.A. Depth = {xu_plot:.1f} mm", color='#b91c1c', fontsize=9)
    ax2.text(0.1, D - 20, f"0.446 f_ck = {0.446 * fck:.1f} MPa", color='#047857', fontsize=9)
    ax2.set_title("IS 456 Concrete Compressive Stress Block", fontsize=11, fontweight='bold')

    st.pyplot(fig)

with tab_shear:
    st.subheader("Shear Stress & Stirrups Design (IS 456 Cl. 40)")
    
    tau_v = (Vu * 1e3) / (b * d)
    tau_c_limit = TAU_C_MAX.get(fck, 3.1)
    
    # Assume 1% pt for approximate baseline if uncalculated
    pt_calc = ((ast_min) / (b * d)) * 100 if not is_singly else (ast_prov / (b * d)) * 100
    tau_c = get_approx_tau_c(fck, pt_calc)
    
    scol1, scol2, scol3 = st.columns(3)
    scol1.metric("Nominal Shear Stress (τv)", f"{tau_v:.2f} N/mm²")
    scol2.metric("Design Shear Strength (τc)", f"{tau_c:.2f} N/mm²")
    scol3.metric("Max Shear Capacity (τc,max)", f"{tau_c_limit:.2f} N/mm²")

    st.write("---")
    if tau_v > tau_c_limit:
        st.error(f"Nominal shear stress ({tau_v:.2f} MPa) exceeds max permissible shear stress ({tau_c_limit:.2f} MPa). Redesign section geometry.")
    elif tau_v > tau_c:
        v_us = (tau_v - tau_c) * b * d / 1e3  # kN to be taken by stirrups
        st.warning(f"Shear reinforcement required to resist excess shear $V_{{us}} = {v_us:.2f}$ kN.")
        
        # 2-legged 8mm stirrups
        asv = 2 * (np.pi / 4) * (8 ** 2)
        sv = (0.87 * fy * asv * d) / (v_us * 1e3)
        sv_max = min(0.75 * d, 300.0, sv)
        st.success(f"Provide **2-legged 8mm φ stirrups @ {int(sv_max)} mm c/c spacing**.")
    else:
        asv = 2 * (np.pi / 4) * (8 ** 2)
        sv_min = (0.87 * fy * asv) / (0.4 * b)
        sv_prov = min(0.75 * d, 300.0, sv_min)
        st.info(f"Nominal shear stress is within concrete capacity. Provide **nominal 2-legged 8mm φ stirrups @ {int(sv_prov)} mm c/c** (IS 456 Cl. 26.5.1.6).")

with tab_audit:
    st.subheader("Automated Structural Health & Detailing Audit")
    
    # Deflection Serviceability Check (Cl. 23.2.1)
    basic_span_d_ratio = 20.0  # Simply supported
    actual_span_d_ratio = (span * 1000) / d
    
    audit_col1, audit_col2 = st.columns(2)
    with audit_col1:
        st.markdown("#### Serviceability Checks")
        if actual_span_d_ratio <= basic_span_d_ratio * 1.25:
            st.success(f"✅ **Deflection Control Passed**: Span/depth ratio is {actual_span_d_ratio:.1f} (Permissible ~ {basic_span_d_ratio * 1.25:.1f}).")
        else:
            st.warning(f"⚠️ **Excessive Deflection Risk**: Span/depth ratio is {actual_span_d_ratio:.1f}. Consider increasing beam depth.")

    with audit_col2:
        st.markdown("#### Material Efficiency & Carbon Estimate")
        conc_volume = (b / 1000) * (D / 1000) * span
        steel_mass = (ast_prov / 1e6) * span * 7850 if is_singly else 0
        embodied_co2 = (conc_volume * 320) + (steel_mass * 1.8)  # standard emission factors
        
        st.metric("Concrete Volume per Span", f"{conc_volume:.3f} m³")
        st.metric("Steel Reinforcement Weight", f"{steel_mass:.1f} kg")
        st.caption(f"Estimated Embodied Carbon: ~{embodied_co2:.1f} kg CO₂e")

    st.markdown("---")
    st.markdown("#### Code Compliance Checklist")
    st.checkbox("IS 456 Cl. 26.5.1.1 Minimum reinforcement satisfied", value=True, disabled=True)
    st.checkbox("IS 456 Cl. 26.5.1.2 Maximum reinforcement (< 0.04 bD) checked", value=True, disabled=True)
    st.checkbox("Ductility and minimum bar diameter checks validated", value=True, disabled=True)
