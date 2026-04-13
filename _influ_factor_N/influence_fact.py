import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import ScalarFormatter

st.set_page_config(page_title="Influence Lines", layout="wide")

# --------------------------------------------------
# Reference values for plotting background curves
# --------------------------------------------------
mFact = np.array([
    3, 2.5, 2.0, 1.8, 1.6, 1.4, 1.2, 1.0,
    0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1
])

nFact = np.concatenate((
    np.arange(0.01, 0.1, 0.01),
    np.arange(0.1, 1, 0.05),
    np.arange(1, 10, 0.5)
))

# Optional: denser n array for a smoother selected curve
nPlot = np.logspace(np.log10(0.01), np.log10(10), 500)


# --------------------------------------------------
# Function for one exact (m, n) point
# --------------------------------------------------
def influence_value(m, n):
    iq1 = (2 * m * n * np.sqrt(m**2 + n**2 + 1)) / (
        m**2 + n**2 + m**2 * n**2 + 1
    )

    iq2 = (m**2 + n**2 + 2) / (m**2 + n**2 + 1)

    denom = m**2 + n**2 - m**2 * n**2 + 1
    arg = (2 * m * n * np.sqrt(m**2 + n**2 + 1)) / denom

    if m**2 + n**2 + 1 < m**2 * n**2:
        iq3 = np.arctan(arg) + np.pi
    else:
        iq3 = np.arctan(arg)

    influ = 1 / (4 * np.pi) * (iq1 * iq2 + iq3)
    return influ


# --------------------------------------------------
# Function for a whole curve
# --------------------------------------------------
def influence_curve(m, n_array):
    return np.array([influence_value(m, n) for n in n_array])


# --------------------------------------------------
# Plotting
# --------------------------------------------------
def plot_influence_line(m_value=1.0, n_value=1.0):
    fig, ax = plt.subplots(figsize=(10, 8))

    # All reference curves in gray
    for m in mFact:
        ax.plot(nFact, influence_curve(m, nFact), color='gray', alpha=0.6, linewidth=1)

    # Selected curve, calculated more smoothly
    influ_selected_curve = influence_curve(m_value, nPlot)
    ax.plot(nPlot, influ_selected_curve, 'b-', linewidth=2.5, label=f'm = {m_value:.2f}')

    # Exact value for selected slider values
    actual_influ = influence_value(m_value, n_value)

    # Helper lines
    ax.plot([n_value, n_value], [0, actual_influ], 'r--', linewidth=1.2)
    ax.plot([nPlot.min(), n_value], [actual_influ, actual_influ], 'r--', linewidth=1.2)

    # Selected point
    ax.plot(n_value, actual_influ, 'ro', markersize=8)

    # Annotation
    ax.text(
        nPlot.min() * 1.2,
        actual_influ,
        f'N = {actual_influ:.4f}',
        verticalalignment='center',
        color='red',
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.85, edgecolor='none')
    )

    ax.set_xscale('log')
    ax.set_xlim(0.01, 10)
    ax.set_ylim(0, 0.25)
    ax.set_yticks(np.linspace(0, 0.25, 6))

    ax.grid(True, which="both", linestyle='-')
    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_major_formatter(ScalarFormatter())

    ax.set_xlabel('Dimensionless factor $n = L/z$')
    ax.set_ylabel('Influence factor $N$')
    ax.set_title(
        r"Influence Lines: $m = \frac{B}{z}$ = "
        + f"{m_value:.2f}, "
        + r"$n = \frac{L}{z}$ = "
        + f"{n_value:.2f}"
    )
    ax.legend()

    plt.tight_layout()
    return fig, actual_influ


# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.title("Influence lines")
st.write("Interaktivni prikaz utjecajnih linija s točnim izračunom prema vrijednostima slidera.")

with st.sidebar:
    st.header("Ulazni parametri")
    m_value = st.slider(
        "m = B/z",
        min_value=0.1,
        max_value=3.0,
        value=1.0,
        step=0.01
    )

    n_value = st.slider(
        "n = L/z",
        min_value=0.01,
        max_value=10.0,
        value=1.0,
        step=0.01
    )

fig, actual_influ = plot_influence_line(m_value, n_value)

st.pyplot(fig)

st.markdown(f"""
### Odabrane vrijednosti
- **m = {m_value:.2f}**
- **n = {n_value:.2f}**
- **N = {actual_influ:.4f}**
""")