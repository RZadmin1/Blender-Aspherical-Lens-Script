import bpy
import math
import sys

# Parameters from the patent
RADIUS = 57.336 # Given Radius of curvature
OPENING = 30.6349 # Physical Diameter of lens

curv = 1 / RADIUS  # Inverse of the radius of curvature
CURV = -0.01671693  # Provided CURV value

K = 0  # Conic constant

COEFFICIENTS = [
    8.75413 * (10**-7),  # Coefficient 1
    -1.46573 * (10**-9),  # Coefficient 2
    2.5569 * (10**-12),  # Coefficient 3
    -4.86557 * (10**-15)  # Coefficient 4
]

POWERS = [4, 6, 8, 10] # Degree of each coefficient

# Settings
GENERATE_LENS = True # Just generates half curve
segments = 128 # Steps in the Screw Modifier if applied
num_points = 128  # Number of points along the radius
max_radius = OPENING / 2  # Maximum radius of the opening

# --------------------------------------------------------------------------------------- #

# Check if parameters are valid
if len(COEFFICIENTS) != len(POWERS):
    raise ValueError("The number of coefficients does not match the number of powers.")


# Function to calculate the sag (Z) at a given radial distance (Y)
def sag(Y, curv, CURV, K):
    vertPos = (curv * (Y ** 2)) / (1 + math.sqrt(1 - ((1 + K) * (CURV ** 2) * (Y ** 2))))
    for i in range(len(COEFFICIENTS)):
        vertPos += (COEFFICIENTS[i] * (Y ** POWERS[i]))
    return vertPos


# Generate points for the aspherical surface
vertices = []
for i in range(num_points):
    Y = max_radius * (i / (num_points - 1)) # Spanning from 0 to max_radius
    Z = -sag(Y, curv, CURV, K)
    vertices.append((Y, Z, 0))

# Create mesh and object
mesh = bpy.data.meshes.new("AsphericalSurface")
obj = bpy.data.objects.new("AsphericalSurface", mesh)

bpy.context.collection.objects.link(obj)


# Create mesh from vertices
edges = [(i, i + 1) for i in range(len(vertices) - 1)]
mesh.from_pydata(vertices, edges, [])
mesh.update()

# Optional: adjust view and orientation for better visibility
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
bpy.context.view_layer.objects.active = obj


# Add a screw modifier for the Y-axis if desired
if GENERATE_LENS == True:
    screw_modifier = obj.modifiers.new(name="Screw", type='SCREW')
    screw_modifier.axis = 'Y'
    screw_modifier.steps = segments
    screw_modifier.render_steps = segments
    screw_modifier.use_merge_vertices = True
    screw_modifier.merge_threshold = 0.0001

    # Update the object
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.view_layer.update()