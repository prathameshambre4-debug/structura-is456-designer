# StructuraAI: RC Beam Analysis & Design Suite (IS 456:2000)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)

**StructuraAI** is an engineering application built for civil and structural engineers. It automates the flexural and shear design of reinforced concrete beams according to Indian Standard code **IS 456:2000 (Plain and Reinforced Concrete - Code of Practice)** using the Limit State Method (LSM).

---

## 🎯 Key Features

- **Limit State Flexural Design**: Computes neutral axis depth ($x_{u}$), limiting moment ($M_{u,\text{lim}}$), and required tension steel ($A_{st}$) with quadratic equilibrium solvers.
- **Dynamic Cross-Section & Stress Block Rendering**: Live parametric visualizations of the beam geometry, rebar layout, and compressive stress block using Matplotlib.
- **IS 456 Shear Reinforcement Module**: Evaluates nominal shear stress ($\tau_v$), design shear strength ($\tau_c$ via Table 19), and calculates two-legged stirrup spacing ($s_v$).
- **Serviceability & Sustainability Audit**: Evaluates span-to-depth deflection compliance (Cl. 23.2.1), concrete volume, total rebar mass, and estimated embodied carbon footprint.

---

## 📐 Mathematical Formulation (IS 456:2000)

### 1. Limiting Moment of Resistance ($M_{u,\text{lim}}$)
$$M_{u,\text{lim}} = 0.36 \cdot f_{ck} \cdot b \cdot x_{u,\text{max}} \cdot (d - 0.42 \cdot x_{u,\text{max}})$$

Where $x_{u,\text{max}}/d$ values:
- Fe 250: $0.53$
- Fe 415: $0.48$
- Fe 500: $0.46$
- Fe 550: $0.44$

### 2. Required Tensile Reinforcement ($A_{st}$)
$$A_{st} = \frac{0.5 \cdot f_{ck}}{f_y} \left[1 - \sqrt{1 - \frac{4.6 \cdot M_u}{f_{ck} \cdot b \cdot d^2}}\right] b \cdot d$$

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- Python 3.10 or higher installed.
- Git installed.

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/structura-is456-designer.git
   cd structura-is456-designer
