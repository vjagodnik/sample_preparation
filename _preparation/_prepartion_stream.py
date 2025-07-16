#%%
import pandas as pd
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output


def preparation_volume(shape = "cylinder", diam = 5, height = 10,width=None,soil_type="SK00", density = 0.5):
    """
    Function to prepare volume based on shape and soil type.
    
    Parameters:
    shape (str): The shape of the volume (e.g., 'cylinder', 'cube').
    soil_type (str): The type of soil (e.g., 'SK00', 'SK10').
    
    Returns:
    float: The calculated volume.
    """
    # Example implementation, replace with actual logic
    if shape == "cylinder":
        Vt = diam**2 * np.pi / 4 * height
    elif shape == "rectangle":
        if width is None:
            raise ValueError("Width must be provided for rectangle shape")
        Vt = diam * width * height
    
    ###
    GsS = 2.7
    GsK = 2.6 
    data = {
              "Soil_type": ["SK00", "SK10", "SK15", "SK20"],
              "emin": [0.641, 0.47947069, 0.399169312, 0.319174427],
              "emax": [0.911, 0.725064375, 0.632629838, 0.540548105],
              "MsK_perc": [0.00, 0.10, 0.15, 0.20],
              "MsS_perc": [1.00, 0.90, 0.85, 0.80],
              "GsMix": [GsS,2.69,2.67,2.67]
              }
    df = pd.DataFrame(data)
    
    df["VsK_perc"] = GsS * df["MsK_perc"] / (df["MsS_perc"] * GsK + df["MsK_perc"] * GsS)
    df["VsS_perc"] = GsK * df["MsS_perc"]/ (df["MsK_perc"]*GsS+df["MsS_perc"]*GsK)
    #
    df["e0"] = df["emax"]  - density * (df["emax"] - df["emin"])
    df["Vsolid"] = Vt / (df["e0"] + 1)
    df["Ms_mix"] = df["Vsolid"] * df["GsMix"]
    df["MsK_mix"] = df["Ms_mix"] * df["MsK_perc"]
    df["MsS_mix"] = df["Ms_mix"] * df["MsS_perc"]
    df["V_voids"] = df["Vsolid"] * df["e0"]
    df["Msat_mix"] = df["Ms_mix"] + df["V_voids"] 


    df_selected = df[df["Soil_type"] == soil_type]
    return df_selected[["Soil_type", "MsK_mix","MsS_mix","Ms_mix","Msat_mix"]]


# %%
# Widgeti
shape_selector = widgets.ToggleButtons(
    options=["cylinder", "rectangle"],
    description="Shape:"
)

diam_selector = widgets.RadioButtons(
    options=[5, 7, 10],
    description="Diameter [cm]:"
)

height_input = widgets.FloatText(
    value=10,
    description='Height [cm]:',
)

width_input = widgets.FloatText(
    value=5,
    description='Width [cm]:',
    disabled=True
)

# Zbijenost i materijal u tabovima
densities = [0.3, 0.5, 0.8]
soil_types = ["SK00", "SK10", "SK15", "SK20"]
density_tabs = widgets.Tab()
density_contents = []

for i, d in enumerate(densities):
    material_dropdown = widgets.Dropdown(
        options=soil_types,
        description="Soil:"
    )
    output_box = widgets.Output()
    box = widgets.VBox([material_dropdown, output_box])
    density_contents.append((material_dropdown, output_box))
    density_tabs.children += (box,)
    density_tabs.set_title(i, f"Density {d}")

density_tabs.children = [widgets.VBox([dropdown, output]) for dropdown, output in density_contents]

# Ažuriranje width inputa
def on_shape_change(change):
    width_input.disabled = change['new'] != 'rectangle'

shape_selector.observe(on_shape_change, names='value')

# Izračun
def calculate_and_display(shape, diam, height, width, density, soil_type):
    df_result = preparation_volume(
        shape=shape,
        diam=diam,
        height=height,
        width=width if shape == "rectangle" else None,
        density=density,
        soil_type=soil_type
    )
    return df_result

# Glavno ažuriranje
def refresh_all(*args):
    for i, (material_dropdown, output_box) in enumerate(density_contents):
        with output_box:
            clear_output(wait=True)
            df = calculate_and_display(
                shape=shape_selector.value,
                diam=diam_selector.value,
                height=height_input.value,
                width=width_input.value,
                density=densities[i],
                soil_type=material_dropdown.value
            )
            display(df)

# Poveži evente
shape_selector.observe(refresh_all, names="value")
diam_selector.observe(refresh_all, names="value")
height_input.observe(refresh_all, names="value")
width_input.observe(refresh_all, names="value")

for dropdown, _ in density_contents:
    dropdown.observe(refresh_all, names="value")

# Prikaz
ui = widgets.VBox([
    shape_selector,
    diam_selector,
    height_input,
    width_input,
    widgets.HTML("<hr>"),
    density_tabs
])

display(ui)
refresh_all()
# %%
