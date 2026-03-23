import streamlit as st
import pandas as pd
import numpy as np
import time

st.set_page_config(page_title="Triaxial Checklist v0.1.0", layout="wide")

st.title("🧪 Triaxial Test Preparation")

# -------------------------
# LOG SYSTEM
# -------------------------
if "log" not in st.session_state:
    st.session_state.log = []

if "last_values" not in st.session_state:
    st.session_state.last_values = {}

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.log.append(f"[{timestamp}] {message}")

def log_input(key, value):
    prev = st.session_state.last_values.get(key)
    if prev is None:
        st.session_state.last_values[key] = value
    elif prev != value:
        log_event(f"{key} → {value}")
        st.session_state.last_values[key] = value

def log_checkbox(key, value):
    prev = st.session_state.last_values.get(key)
    if prev is None:
        st.session_state.last_values[key] = value
    elif prev != value:
        state = "ON" if value else "OFF"
        log_event(f"{key} → {state}")
        st.session_state.last_values[key] = value

# -------------------------
# FUNCTIONS
# -------------------------
def undercompaction(mass_of_material, Uni, nT, hT):
    under = pd.DataFrame({
        "layers": np.arange(1, nT + 1),
    })

    under["undercompaction"] = (Uni - (Uni * (under["layers"] - 1) / (nT - 1))) * 100
    under["height_layer"] = round(
        hT / nT * ((under["layers"] - 1) + (1 + under["undercompaction"] / 100)), 3
    )

    mass_per_layer = mass_of_material / nT
    return under, mass_per_layer

# -------------------------
# SHARED COMPONENTS
# -------------------------
def cp_check():
    st.header("CP Check")

    line_open = st.checkbox("CP line OPEN", key="cp_line_open")
    zeroed = st.checkbox("CP transducer ZEROED ❗", key="cp_zeroed")
    valves = st.checkbox('Wall panel valves "1-0-1"', key="cp_valves")

    log_checkbox("CP line open", line_open)
    log_checkbox("CP zeroed", zeroed)
    log_checkbox("CP valves 1-0-1", valves)

    return {
        "line_open": line_open,
        "zeroed": zeroed,
        "valves": valves
    }

# -------------------------
# SESSION INIT
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

if "data" not in st.session_state:
    st.session_state.data = {}

if "undercompaction_done" not in st.session_state:
    st.session_state.undercompaction_done = False

if "co2_start_time" not in st.session_state:
    st.session_state.co2_start_time = None

if "co2_flush_done" not in st.session_state:
    st.session_state.co2_flush_done = False

if "co2_interrupted" not in st.session_state:
    st.session_state.co2_interrupted = False

# -------------------------
# NEXT BUTTON LOGIC
# -------------------------
disable_next = False

if st.session_state.step == 7 and st.session_state.data.get("method") == "CO2":
    if not st.session_state.co2_flush_done:
        disable_next = True

# -------------------------
# NAVIGATION
# -------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("⬅ Back") and st.session_state.step > 1:
        st.session_state.step -= 1

with col2:
    if st.button("Next ➡", disabled=disable_next):
        st.session_state.step += 1

st.write(f"### Step {st.session_state.step}")

# -------------------------
# STEP 1 (Sample ID added)
# -------------------------
if st.session_state.step == 1:
    st.header("Test Setup")

    sample_id = st.text_input("Sample ID")
    log_input("Sample ID", sample_id)
    st.session_state.data["sample_id"] = sample_id

    st.session_state.data["test_type"] = st.selectbox(
        "Test Type", ["TRIAX", "DYNATRIAX", "CRS"]
    )
    log_input("Test Type", st.session_state.data["test_type"])

    st.session_state.data["mode"] = st.selectbox(
        "Mode", ["Compression", "Extension", "Cyclic"]
    )
    log_input("Mode", st.session_state.data["mode"])

    st.session_state.data["system"] = st.selectbox(
        "System", ["1", "2", "3", "Manual"]
    )
    log_input("System", st.session_state.data["system"])

# -------------------------
# STEP 2 (Gs + e added)
# -------------------------
elif st.session_state.step == 2:
    st.header("Sample Preparation")

    st.session_state.data["diameter"] = st.selectbox(
        "Diameter", [38, 50, 70, 100]
    )
    log_input("Diameter", st.session_state.data["diameter"])

    st.session_state.data["material"] = st.selectbox(
        "Material", ["Sand", "Clay", "Silt", "Gravel"]
    )
    log_input("Material", st.session_state.data["material"])

    # NEW
    gs = st.number_input("Specific gravity Gs", value=2.65)
    e = st.number_input("Void ratio e", value=0.6)

    log_input("Gs", gs)
    log_input("Void ratio e", e)

    st.session_state.data["Gs"] = gs
    st.session_state.data["e"] = e

    prep = st.selectbox(
        "Preparation Method",
        ["Undercompaction", "Wet Tamping", "Pluviation", "Dry"]
    )
    st.session_state.data["prep"] = prep
    log_input("Preparation", prep)

    if prep == "Undercompaction":
        st.subheader("Undercompaction")

        col1, col2 = st.columns(2)

        with col1:
            mass = st.number_input("Mass (g)", value=800.0)
            h = st.number_input("Height (mm)", value=140.0)

        with col2:
            n = st.number_input("Layers", min_value=2, value=10)
            Uni_option = st.radio("Undercompaction (%)", ["2%", "5%", "10%"])
            Uni = {"2%": 0.02, "5%": 0.05, "10%": 0.10}[Uni_option]

        log_input("Mass", mass)
        log_input("Height", h)

        if st.button("Calculate"):
            df, m_layer = undercompaction(mass, Uni, n, h)

            st.dataframe(pd.DataFrame({
                "Layer": df["layers"],
                "Height (mm)": df["height_layer"]
            }), hide_index=True)

            st.metric("Mass per layer", f"{m_layer:.2f} g")
            st.session_state.undercompaction_done = True
            st.session_state.data["mass"] = mass
            log_event("Undercompaction calculated")

        if not st.session_state.undercompaction_done:
            st.warning("⚠️ Required")

# -------------------------
# STEP 3
# -------------------------
elif st.session_state.step == 3:
    st.header("Saturation Method")

    method = st.radio("Method", ["BP", "CO2"])
    st.session_state.data["method"] = method
    log_input("Method", method)

# =====================================================
# CO2 WORKFLOW (UNCHANGED + timer fix)
# =====================================================
elif st.session_state.data.get("method") == "CO2":

    step = st.session_state.step

    if step == 4:
        st.header("PWP Check")

        flushed = st.checkbox("Flushed ❗", key="pwp_flush")
        zeroed = st.checkbox("Zeroed ❗", key="pwp_zero")

        log_checkbox("PWP flushed", flushed)
        log_checkbox("PWP zeroed", zeroed)

    elif step == 5:
        st.session_state.data["cp"] = cp_check()

    elif step == 6:
        st.header("Raise CP")
        st.session_state.data["cp_pressure"] = st.number_input("kPa", value=20)
        log_input("CP pressure", st.session_state.data["cp_pressure"])

    elif step == 7:
        st.header("CO₂ Percolation")

        duration = 15 * 60

        co2_closed_1 = st.checkbox("CO₂ line CLOSED")
        connected = st.checkbox("CO₂ connected behind sample")
        drain_open = st.checkbox("Drainage line OPEN ❗")

        if st.button("Start CO₂ flush"):
            st.session_state.co2_start_time = time.time()
            st.session_state.co2_flush_done = False
            st.session_state.co2_interrupted = False
            log_event("CO₂ flush STARTED")

        if st.session_state.co2_start_time:

            elapsed = time.time() - st.session_state.co2_start_time
            remaining = max(0, duration - elapsed)

            st.progress(min(elapsed / duration, 1.0))
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            st.write(f"Remaining: {mins:02d}:{secs:02d}")

            if remaining > 0:
                if st.button("⚠️ Interrupt CO₂ flush"):
                    st.session_state.co2_flush_done = True
                    st.session_state.co2_interrupted = True
                    log_event("CO₂ flush INTERRUPTED")

            if remaining <= 0:
                st.session_state.co2_flush_done = True
                log_event("CO₂ flush COMPLETED")
                st.success("✅ CO₂ flush completed")

        disabled = not st.session_state.co2_flush_done

        co2_closed_2 = st.checkbox(
            "CO₂ line CLOSED (after flow)", disabled=disabled
        )
        drain_closed = st.checkbox(
            "Drainage line CLOSED ❗", disabled=disabled
        )

        st.session_state.data["co2"] = {
            "co2_closed_1": co2_closed_1,
            "connected": connected,
            "drain_open": drain_open,
            "co2_closed_2": co2_closed_2,
            "drain_closed": drain_closed
        }

        for k, v in st.session_state.data["co2"].items():
            log_checkbox(f"CO2 {k}", v)

        if not st.session_state.co2_flush_done:
            st.error("⛔ Cannot continue until flush is complete")

    elif step == 8:
        st.header("Water Percolation (BP via PWP)")

        st.session_state.data["bpw"] = {
            "bp_to_pwp": st.checkbox("BP → PWP"),
            "flush_air": st.checkbox("Flush ❗"),
            "zeroed": st.checkbox("Zero ❗"),
            "drain_open": st.checkbox("Drain OPEN ❗"),
            "bp_pwp_open": st.checkbox("BP + PWP OPEN ❗")
        }

        for k, v in st.session_state.data["bpw"].items():
            log_checkbox(f"BPW {k}", v)

    elif step == 9:
        st.header("End of Percolation")

        st.session_state.data["final"] = {
            "bp_pwp_closed": st.checkbox("BP + PWP CLOSED ❗"),
            "drain_closed": st.checkbox("Drain CLOSED ❗"),
            "bp_to_bp": st.checkbox("BP → BP line")
        }

        for k, v in st.session_state.data["final"].items():
            log_checkbox(f"FINAL {k}", v)

# =====================================================
# BP WORKFLOW (UNCHANGED)
# =====================================================
elif st.session_state.data.get("method") == "BP":

    step = st.session_state.step

    if step == 4:
        st.header("BP Setup")

        st.session_state.data["bp"] = {
            "bp_line_open": st.checkbox("BP line OPEN"),
            "flush_air": st.checkbox("Flush air ❗"),
            "zeroed": st.checkbox("BP transducer ZEROED ❗"),
            "volume_set": st.checkbox("Volume set"),
            "valves": st.checkbox('Wall panel valves "1-0-1"')
        }

        for k, v in st.session_state.data["bp"].items():
            log_checkbox(f"BP {k}", v)

    elif step == 5:
        st.header("PWP Check")

        st.session_state.data["pwp"] = {
            "flushed": st.checkbox("Flushed ❗"),
            "zeroed": st.checkbox("Zeroed ❗")
        }

        for k, v in st.session_state.data["pwp"].items():
            log_checkbox(f"PWP {k}", v)

    elif step == 6:
        st.session_state.data["cp"] = cp_check()

    elif step == 7:
        st.header("Validation")

        errors = []

        if not st.session_state.data["bp"]["flush_air"]:
            errors.append("BP flush")

        if not st.session_state.data["cp"]["zeroed"]:
            errors.append("CP")

        if st.session_state.data.get("prep") == "Undercompaction":
            if not st.session_state.undercompaction_done:
                errors.append("Undercompaction")

        if errors:
            st.error(errors)
        else:
            st.success("✅ Ready")

# -------------------------
# LOG EXPORT
# -------------------------
st.header("Log")

log_text = "\n".join(st.session_state.log)

st.text_area("Event log", log_text, height=200)

st.download_button(
    "Download log",
    log_text,
    file_name="triaxial_log.txt"
)

# -------------------------
# PROGRESS
# -------------------------
st.progress(min(st.session_state.step / 10, 1.0))