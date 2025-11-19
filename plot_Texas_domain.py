import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import cartopy.feature as cfeature

# 1. Define the coordinates and settings
# Bounding box coordinates: [lon_min, lat_min, lon_max, lat_max]
BOX_COORDS = [-106.75, 25.75, -93.5, 36.75]
DPI_VALUE = 600
FONT_SIZE = 24
OUTPUT_FILENAME = 'Texas_box.png'

# Unpack the coordinates for easy use
lon_min, lat_min, lon_max, lat_max = BOX_COORDS

# 2. Create the figure and axes
# Use PlateCarree projection for a simple lat/lon grid
fig = plt.figure(figsize=(18, 18))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

# 3. Set the map extent (slightly larger than the box for context)
# The order is [lon_start, lon_end, lat_start, lat_end]
extent = [lon_min - 2, lon_max + 2, lat_min - 2, lat_max + 2]
ax.set_extent(extent, crs=ccrs.PlateCarree())

# 4. Add map features for context
ax.coastlines(resolution='50m', color='black', linewidth=1)
ax.add_feature(ccrs.cartopy.feature.STATES, edgecolor='blue', linestyle='--')
ax.add_feature(ccrs.cartopy.feature.BORDERS, linestyle='-', edgecolor='black')
ax.add_feature(ccrs.cartopy.feature.LAND, facecolor='white')
ax.add_feature(ccrs.cartopy.feature.OCEAN, facecolor='lightblue')

"""
# With a higher-resolution states/provinces feature (using GSHHS):
ax.add_feature(
    cfeature.GSHHSFeature(scale='i', levels=[2]),  # 'i' for intermediate resolution, level 2 for political boundaries
    facecolor='none',
    edgecolor='gray',
    linestyle=':'
)
"""

# 5. Plot the bounding box (Rectangle)
# Create a rectangle patch
rect = mpatches.Rectangle(
    (lon_min, lat_min),  # Lower-left corner
    lon_max - lon_min,   # Width
    lat_max - lat_min,   # Height
    facecolor='none',
    edgecolor='red',
    linewidth=4,
    transform=ccrs.PlateCarree(),
    label='Texas study domain'
)
ax.add_patch(rect)

# 6. Add gridlines and labels
gl = ax.gridlines(
    crs=ccrs.PlateCarree(),
    draw_labels=True,
    linewidth=1,
    color='gray',
    alpha=0.7,
    linestyle='--'
)

# Configure the appearance of the labels
gl.top_labels = False  # Turn off top latitude labels
gl.right_labels = False # Turn off right longitude labels

# Set all font sizes
plt.rcParams.update({'font.size': FONT_SIZE})
gl.xlabel_style = {'size': FONT_SIZE}
gl.ylabel_style = {'size': FONT_SIZE}
ax.set_title("Study domain bounding box", fontsize=FONT_SIZE + 2)

# 7. Save the figure
plt.savefig(OUTPUT_FILENAME, dpi=DPI_VALUE, bbox_inches='tight')
print(f"Map successfully saved to {OUTPUT_FILENAME}.")
