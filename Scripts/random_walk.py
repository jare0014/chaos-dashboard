import numpy as np
import matplotlib.pyplot as plt

# 1. The Phyics
steps = 5000
# Generate random steps: normal distribution (Gaussian)
x_steps = np.random.randn(steps)
y_steps = np.random.randn(steps)

# Calculate the position by summing steps (Cumulative Sum)
x_position = np.cumsum(x_steps)
y_position = np.cumsum(y_steps)

# 2. The Visualization
plt.figure(figsize=(10, 10))
plt.plot(x_position, y_position, alpha=0.6, linewidth = 0.8, color='teal')

#Mark the start green and end red
plt.scatter(0,0, color='green', s=100, label='Start', zorder=5)
plt.scatter(x_position[-1], y_position[-1], color='red', s=100, label='End', zorder=5)

plt.title(f"2D Random Walk ({steps} steps)")
plt.legend()
plt.axis('equal') # Keeps proportions real
plt.grid(True, alpha=0.3)

#3. The Output (Save to Disk)
filename = "brownian_motion.png"
plt.savefig(filename, dpi=300)
print(f"Simulation complete. Image saved to {filename}")