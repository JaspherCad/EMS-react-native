import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch

# Define figure and axes
fig, ax = plt.subplots(figsize=(15, 12))

# Define phases and their components
phases = {
    "Data Generation Phase": [
        "Generate Patient Locations", 
        "Assign Severity Levels", 
        "Select Medical Conditions", 
        "Calculate Distances", 
        "Apply Hospital Selection", 
        "Calculate Response Times", 
        "Store Patient Records"
    ],
    "Model Training Phase": [
        "Preprocess Data", 
        "Encode Variables", 
        "Train Random Forest", 
        "Evaluate Model", 
        "Save Model"
    ],
    "Prediction System": [
        "Accept User Input", 
        "Calculate Distances", 
        "Predict Hospital", 
        "Generate Time Breakdown", 
        "Visualize Route"
    ]
}

# Define colors for each phase
phase_colors = {
    "Data Generation Phase": "#E6F3FF",  # Light blue
    "Model Training Phase": "#E6FFE6",   # Light green
    "Prediction System": "#FFE6E6"       # Light red
}

# Set y positions for each phase (columns)
phase_positions = {
    "Data Generation Phase": 0.2,
    "Model Training Phase": 0.5,
    "Prediction System": 0.8
}

# Set spacing parameters
phase_width = 0.2
step_height = 0.1

# Draw boxes for phases
for phase_idx, (phase_name, steps) in enumerate(phases.items()):
    # Draw phase box
    phase_x = phase_positions[phase_name]
    phase_y = 0.9 - (len(steps) * step_height) / 2
    
    # Draw phase title
    ax.text(phase_x, 0.95, phase_name, 
            ha='center', va='center', 
            fontsize=16, fontweight='bold',
            bbox=dict(facecolor='lightgray', alpha=0.7, boxstyle='round,pad=0.5'))
    
    # Draw steps in this phase
    for step_idx, step in enumerate(steps):
        step_y = phase_y - step_idx * step_height
        
        # Draw step box
        rect = plt.Rectangle((phase_x - phase_width/2, step_y - step_height/2), 
                           phase_width, step_height,
                           facecolor=phase_colors[phase_name],
                           edgecolor='black',
                           alpha=0.8,
                           zorder=1)
        ax.add_patch(rect)
        
        # Add step text
        ax.text(phase_x, step_y, step, 
                ha='center', va='center', 
                fontsize=11, fontweight='normal')
        
        # Draw arrow to next step in same phase
        if step_idx < len(steps) - 1:
            arrow = FancyArrowPatch(
                (phase_x, step_y - step_height/2),
                (phase_x, step_y - step_height),
                connectionstyle="arc3,rad=0",
                arrowstyle="-|>",
                mutation_scale=15,
                linewidth=1.5,
                color='black',
                zorder=2
            )
            ax.add_patch(arrow)

# Connect phases - specific connections
# 1. From "Store Patient Records" to "Preprocess Data"
arrow1 = FancyArrowPatch(
    (phase_positions["Data Generation Phase"] + phase_width/2, 
     0.9 - (len(phases["Data Generation Phase"]) * step_height) / 2 + (6 * step_height)),
    (phase_positions["Model Training Phase"] - phase_width/2, 
     0.9 - (len(phases["Model Training Phase"]) * step_height) / 2),
    connectionstyle="arc3,rad=0.3",
    arrowstyle="-|>",
    mutation_scale=20,
    linewidth=2,
    color='blue',
    zorder=2
)
ax.add_patch(arrow1)

# 2. From "Save Model" to "Predict Hospital"
arrow2 = FancyArrowPatch(
    (phase_positions["Model Training Phase"] + phase_width/2, 
     0.9 - (len(phases["Model Training Phase"]) * step_height) / 2 + (4 * step_height)),
    (phase_positions["Prediction System"] - phase_width/2, 
     0.9 - (len(phases["Prediction System"]) * step_height) / 2 + (2 * step_height)),
    connectionstyle="arc3,rad=0.3",
    arrowstyle="-|>",
    mutation_scale=20,
    linewidth=2,
    color='blue',
    zorder=2
)
ax.add_patch(arrow2)

# Add annotations for the connecting arrows
ax.text(0.35, 0.65, "Training Data", 
        ha='center', va='center', 
        fontsize=12, fontweight='bold',
        color='blue')

ax.text(0.65, 0.75, "Trained Model", 
        ha='center', va='center', 
        fontsize=12, fontweight='bold',
        color='blue')

# Add legend items
phases_legend = [plt.Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='black', alpha=0.8) 
                for color in phase_colors.values()]
plt.legend(phases_legend, phase_colors.keys(), 
           loc='upper center', bbox_to_anchor=(0.5, 0.05), ncol=3, fontsize=12)

# Format the plot
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig("ems_simulation_flow.png", dpi=300, bbox_inches='tight')
plt.show()