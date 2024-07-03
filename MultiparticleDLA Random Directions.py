import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import colors 

# Constants
GRID_SIZE = 200
SEED_FIELD_SIZE = GRID_SIZE // 2  # Size of the seed field
NUM_SEEDS = 5
NUM_PARTICLES = 5
MAX_TIME_STEPS = 30
OUTPUT_FILE = "bottom_source_no_return_multi_seed_dla_animation.gif"

# Probability of moving downwards (versus upwards)
DOWNWARD_PROBABILITY = 0.1

# Initialize the grid with seed particles in the centered smaller field
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)
seed_field_start_x = (GRID_SIZE - SEED_FIELD_SIZE) // 2
seed_field_start_y = (GRID_SIZE - SEED_FIELD_SIZE) // 2

# Randomly place seeds within the smaller field
for _ in range(NUM_SEEDS):
    x = np.random.randint(seed_field_start_x, seed_field_start_x + SEED_FIELD_SIZE)
    y = np.random.randint(seed_field_start_y, seed_field_start_y + SEED_FIELD_SIZE)
    #x = 100
    #y = 60
    grid[x, y] = True

# Create a figure and axis for visualization
fig, ax = plt.subplots()
ax.set_xlim(0, GRID_SIZE)
ax.set_ylim(0, GRID_SIZE)

# Initialize an empty list to store animation frames
frames = []

# Initialize a set to track particles that have left the grid
particles_left = set()

# Animation initialization
def init():
    return []

# Function to check if a particle can aggregate
def can_aggregate(x, y):
    if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if 0 <= x + dx < GRID_SIZE and 0 <= y + dy < GRID_SIZE and grid[x + dx, y + dy]:
                    return True
    return False

# Animation update function
def update(frame):
    for _ in range(NUM_PARTICLES):
        # Generate random initial positions for new particles at the bottom
        x = np.random.randint(GRID_SIZE)
        y = np.random.randint(GRID_SIZE)

        while not can_aggregate(x, y):
            # Randomly decide whether to move upwards or downwards
            if np.random.rand() < DOWNWARD_PROBABILITY:
                dx, dy = np.random.randint(-1, 2), -1  # Move downwards
            else:
                dx, dy = np.random.randint(-1, 2), 1  # Move upwards

            x_new, y_new = (x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE

            # Check if the particle has left the grid
            if y_new == 0 and (x_new < 0 or x_new >= GRID_SIZE):
                particles_left.add((x, y))
                break

            x, y = x_new, y_new

        # Aggregate the particle
        grid[x, y] = True

    # Remove particles that have left the grid from consideration
    for x, y in list(particles_left):
        if y == 0 and (x < 0 or x >= GRID_SIZE):
            particles_left.remove((x, y))

    # Visualization
    ax.clear()
    cmap = colors.ListedColormap(['linen','red'])
    img = ax.imshow(grid, cmap, origin="lower", aspect="auto")
    ax.axis('off')
    #ax.set_title(f"Bottom Source No Return Multi-Seed DLA - Frame {frame}/{MAX_TIME_STEPS}")
    frames.append([img])

# Create an animation
ani = animation.FuncAnimation(fig, update, frames=MAX_TIME_STEPS, init_func=init, blit=False)

# Save the animation as a .gif file
ani.save(OUTPUT_FILE, writer="pillow", dpi=80)

# Show the animation
plt.show()
