import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import numpy as np

# Simplified representation of the human body with labeled regions
body_parts = {
    "Left Foot": (-1, -5),
    "Right Foot": (1, -5),
    "Left Foreleg": (-1, -4),
    "Right Foreleg": (1, -4),
    "Left Front Thigh": (-1, -3),
    "Right Front Thigh": (1, -3),
    "Left Back Thigh": (-1, -2),
    "Right Back Thigh": (1, -2),
    "Pelvis": (0, -1),
    "Back Side": (0, 0),
    "Head": (0, 5),
    "Crown": (0, 6),
    "Left Hand": (-2, 2),
    "Right Hand": (2, 2),
    "Left Forearm": (-2, 1),
    "Right Forearm": (2, 1),
    "Left Upper Arm": (-2, 3),
    "Right Upper Arm": (2, 3),
    "Chest Left": (-1, 4),
    "Chest Right": (1, 4),
    "Back Left": (-1, 3),
    "Back Right": (1, 3),
    "Stability": (0, 0),  # Placeholder position
}

# Normalize data for mapping to color scale (assuming -0.2 to 0.2 range for simplicity)
temp_data = {
    key: np.random.uniform(-0.2, 0.2) for key in body_parts.keys()
}  # Replace this with actual data later

# Create color mapping
cmap = plt.cm.coolwarm
norm = plt.Normalize(-0.2, 0.2)

# Plotting the body diagram
fig, ax = plt.subplots(figsize=(6, 10))
ax.set_xlim(-3, 3)
ax.set_ylim(-6, 7)
ax.set_aspect('equal')
ax.axis('off')

# Plot each body part
for part, (x, y) in body_parts.items():
    color = cmap(norm(temp_data[part]))
    ax.add_patch(Circle((x, y), 0.4, color=color))
    ax.text(x, y, part, fontsize=8, ha='center', va='center')

# Add a colorbar for reference
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', fraction=0.03, pad=0.04)
cbar.set_label("Temperature Change (°C)")

plt.title("Body Cooling Effects Visualization")
plt.show()
