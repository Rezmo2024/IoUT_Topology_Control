import math
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import random
from mpl_toolkits.mplot3d import Axes3D

def generate_3d_grid(x_range, y_range, z_range, R):
    """
    Generate 3D grid coordinates for sensor nodes.
    """
    # Calculate the spacing between adjacent nodes
    spacing = R - 10 #10 meters for the border margin

    # Determine the number of nodes along each dimension
    grid_size = (
        int(x_range // spacing),
        int(y_range // spacing),
        int(z_range // spacing)
    )

    # Generate the grid using numpy's meshgrid
    x = np.arange(0, grid_size[0] * spacing, spacing)
    y = np.arange(0, grid_size[1] * spacing, spacing)
    z = np.arange(0, grid_size[2] * spacing, spacing)

    # Create a 3D meshgrid
    x, y, z = np.meshgrid(x, y, z, indexing='ij')

    # Flatten the grid and format coordinates as strings
    nodes = []
    for xi, yi, zi in zip(x.ravel(), y.ravel(), z.ravel()):
        nodes.append(f"{int(xi)},{int(yi)},{int(zi)}\n")

    return nodes

def generate_Random_nodes(x_range, y_range, z_range, nn):
    nodes = []
    n=0
    for i in range(nn):
        x = random.randint(0, x_range)
        y = random.randint(0, y_range)
        z = random.randint(0, z_range)
        nodes.append(f"{int(x)},{int(y)},{int(z)}\n")
        n=n+1
    print("Number of nodes within  environment(Random) =", n)
    return nodes
def generate_RD_nodes(x_range, y_range, z_range, rc,rs):
    nodes = []
    R=min(rc/math.sqrt(2),rs)
    step = 2 * R / np.sqrt(5)  # Step size based on the formula
    n = 0
    for u in np.arange(-2000, 2000, step):
        for v in np.arange(-2000, 2000, step):
            for w in np.arange(-2000, 2000, step):
                # Generate nodes using the formula
                x = (2 * u + w)
                y = (2 * v + w)
                z = w
                # Check if the node is within the defined 3D environment
                if 0 <= x <= x_range and 0 <= y <= y_range and 0 <= z <= z_range:
                    nodes.append(f"{int(x)},{int(y)},{int(z)}\n")   # Add the node to the list
                    n += 1
    print("Number of nodes within  environment(RD) =", n)
    return nodes
def generate_TO_nodes(x_range, y_range, z_range, rc,rs):
    nodes = []
    R=min(rc*math.sqrt(5)/4,rs)
    step =  R / np.sqrt(2)  # Step size based on the formula
    n = 0
    for u in np.arange(-2000, 2000, step):
        for v in np.arange(-2000, 2000, step):
            for w in np.arange(-2000, 2000, R):
                # Generate nodes using the formula
                x = (2 * u + w)
                y = (2 * v + w)
                z = w
                # Check if the node is within the defined 3D environment
                if 0 <= x <= x_range and 0 <= y <= y_range and 0 <= z <= z_range:
                    nodes.append(f"{int(x)},{int(y)},{int(z)}\n")   # Add the node to the list
                    n += 1
    print("Number of nodes within  environment (TO) =", n)
    return nodes
def generate_CB_nodes(x_range, y_range, z_range, rc,rs):
    nodes = []
    R=min(rc*math.sqrt(3)/2,rs)
    step =  2*R / np.sqrt(3)  # Step size based on the formula
    n = 0
    for u in np.arange(-2000, 2000, step):
        for v in np.arange(-2000, 2000, step):
            for w in np.arange(-2000, 2000, step):
                # Generate nodes using the formula
                x = u
                y = v
                z = w
                # Check if the node is within the defined 3D environment
                if 0 <= x <= x_range and 0 <= y <= y_range and 0 <= z <= z_range:
                    nodes.append(f"{int(x)},{int(y)},{int(z)}\n")   # Add the node to the list
                    n += 1
    print("Number of nodes within  environment (CB) =", n)
    return nodes

def generate_HP_nodes(x_range, y_range, z_range, rc,rs):
    nodes = []
    n = 0
    a=min(rc/np.sqrt(3),rs*np.sqrt(2)/np.sqrt(3))
    b=min((2*np.sqrt(rs**2-a**2)),rc)
    for u in np.arange(-2000, 2000, 3*a/2):
        for v in np.arange(-2000, 2000, a*np.sqrt(3)):
            for w in np.arange(-2000, 2000, b):
                # Generate nodes using the formula
                x = u
                y = (u/2)+v
                z = w
                # Check if the node is within the defined 3D environment
                if 0 <= x <= x_range and 0 <= y <= y_range and 0 <= z <= z_range:
                    nodes.append(f"{int(x)},{int(y)},{int(z)}\n")   # Add the node to the list
                    n += 1
    print("Number of nodes within  environment (HP) =", n)
    return nodes
def read_coordinates(file_path):
    """Read coordinates from a file and return them as a NumPy array."""
    try:
        data = np.loadtxt(file_path, delimiter=',')
        return data
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

def plot_3d_coordinates(coordinates):
    """Plot the 3D coordinates using matplotlib."""
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    # Extract x, y, z coordinates
    x = coordinates[:, 0]
    y = coordinates[:, 1]
    z = coordinates[:, 2]
    # Create a scatter plot
    ax.scatter(x, y, z, c='b', marker='o')
    # Set labels
    ax.set_xlabel('X Axis')
    ax.set_ylabel('Y Axis')
    ax.set_zlabel('Z Axis')
    # Set title
    plt.title('3D Scatter Plot of Coordinates')
    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Example usage
    coordinates = generate_3d_grid(1000,1000,1000,200)

    # Print the generated coordinates
    print("Generated 3D Coordinates:")
    print(coordinates)
