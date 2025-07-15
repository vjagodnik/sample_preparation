#%%
import streamlit as st
import pandas as pd
import numpy as np

def undercompaction(mass_of_material = 883.42, Uni = 0.05,nT =10, hT = 140.4 ):
    """
    Calculate the undercompaction of a material 
    Parameters:
    mass_of_material (float): Mass of the material in g.
    Uni (float): percent of undercompaction
    nT (int): Number of layers.
    hT (float): Height of sample.
    mTl (float): Mass per layer.

    Returns:
    float: Undercompaction value.
    """
    under = pd.DataFrame({
              "layers": np.arange(1, nT+1 ),

    })
    under["udercompaction"] = (Uni - (Uni*(under["layers"]-1)/(nT - 1)))*100
    under["height_layer"] = round(hT / nT * ((under["layers"]-1)+(1+ under["udercompaction"]/100)),3)

    mass_per_layer = mass_of_material / nT

    return under["height_layer"], mass_per_layer



# Streamlit app
st.title("Undercompaction Calculator")

# Input widgets
col1, col2 = st.columns(2)

with col1:
    mass_of_material = st.number_input(
        "Mass of material (g)",
        min_value=0.0,
        value=883.42,
        step=10.0,
        format="%.2f"
    )
    
    hT = st.number_input(
        "Height of sample (mm)",
        min_value=0.0,
        value=140.4,
        step=1.0,
        format="%.1f"
    )

with col2:
    nT = st.number_input(
        "Number of layers",
        min_value=1,
        value=10,
        step=1
    )
    
    Uni_option = st.radio(
        "Undercompaction percentage",
        options=["2%", "5%", "10%"],
        index=1  # Default to 5%
    )
    
    # Convert radio selection to numeric value
    Uni = {
        "2%": 0.02,
        "5%": 0.05,
        "10%": 0.10
    }[Uni_option]

# Calculate button
if st.button("Calculate"):
    height_layer, mass_per_layer = undercompaction(mass_of_material, Uni, nT, hT)
    
    # Display results
    st.subheader("Results")
    
    # Create a results DataFrame for nice display
    results = pd.DataFrame({
        "Layer": np.arange(1, nT+1),
        "Height per layer (mm)": height_layer
    })
    
    st.dataframe(results, hide_index=True)
    
    st.metric("Mass per layer", f"{mass_per_layer:.2f} g")
    
    # Optional visualization
    st.subheader("Visualization")
    st.line_chart(results.set_index("Layer"))