import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from shapely.geometry import box
from matplotlib import rcParams

# --- Configuration ---
# Set the global font size to 24
FONT_SIZE = 24
rcParams['font.size'] = FONT_SIZE
rcParams['axes.titlesize'] = FONT_SIZE
rcParams['axes.labelsize'] = FONT_SIZE
rcParams['xtick.labelsize'] = FONT_SIZE
rcParams['ytick.labelsize'] = FONT_SIZE
rcParams['legend.fontsize'] = FONT_SIZE

# Belton Lake (approx label position)
belton_lon = -97.45
belton_lat = 31.20

# Leon River label
leon_lon   = -97.70
leon_lat   = 31.32

# Cowhouse Creek (Google map coordinate)
cow_lon = -97.8734669
cow_lat = 31.305827

# GAST2 USGS station (Leon R. at Gatesville)
gast2_lon = -97.7583
gast2_lat = 31.4347

# PICT2 NOAA station
pict2_lon = -97.8847
pict2_lat = 31.2847

# Local File Paths
RIVERS_PATH = "./shapefile/MajorRivers_dd83.shp"
#RIVERS_PATH = "./shapefile/LeonRiver2010_ss_interp83.shp"
#RIVERS_PATH = "./shapefile/LeonRiver_2ftcont.shp"
#RIVERS_PATH = "./shapefile/TWDB_MRBs_2014.shp"

RESERVOIRS_PATH = "./shapefile/TWDB_SWP2012_Major_Reservoirs.shp"

# Define the target bounding box (BBOX) in WGS84 (lat/lon)
lat_min = 31.00
lat_max = 31.50
lon_min = -97.95
lon_max = -97.25

# Create a Shapely Box geometry for spatial filtering
bbox_poly = box(lon_min, lat_min, lon_max, lat_max)

def load_filter_and_plot_basemap():
    """Loads, filters, and plots the geospatial data using Basemap."""
    try:
        # 1. Load the GeoDataFrames
        print("Loading GeoDataFrames...")
        rivers_gdf = gpd.read_file(RIVERS_PATH)
        reservoirs_gdf = gpd.read_file(RESERVOIRS_PATH)

        # 2. Ensure CRS consistency (reproject to WGS84 for lat/lon filtering)
        rivers_gdf = rivers_gdf.to_crs(epsg=4326)
        reservoirs_gdf = reservoirs_gdf.to_crs(epsg=4326)
        print(f"Rivers total features: {len(rivers_gdf)}. Reservoirs total features: {len(reservoirs_gdf)}.")

        # 3. Spatial Filtering
        #filtered_rivers = rivers_gdf[rivers_gdf.intersects(bbox_poly)]
        # Let use all rivers
        filtered_rivers = rivers_gdf
        filtered_reservoirs = reservoirs_gdf[reservoirs_gdf.intersects(bbox_poly)]

        print(f"Rivers filtered to BBOX: {len(filtered_rivers)} features.")
        print(f"Reservoirs filtered to BBOX: {len(filtered_reservoirs)} features.")

        if filtered_rivers.empty and filtered_reservoirs.empty:
            print("No water features found within the specified bounding box.")
            return

        # 4. Setup Matplotlib figure and Basemap
        fig, ax = plt.subplots(1, 1, figsize=(15, 15))
        ax.set_title(
            f'SWOT study domain ( {lat_min}°N to {lat_max}°N, {lon_min}°W to {lon_max}°W)', 
            pad=20
        )

        # Initialize Basemap object
        # Use 'cyl' (Cylindrical Equidistant) projection for simple lat/lon bounding box definition.
        m = Basemap(
            projection='cyl',
            llcrnrlat=lat_min, urcrnrlat=lat_max,
            llcrnrlon=lon_min, urcrnrlon=lon_max,
            resolution='i', # intermediate resolution
            ax=ax
        )
        
        # Draw coastlines/boundaries for context (optional, but good practice)
        # Note: Basemap drawing functions will re-use the global font size 24.
        m.drawcoastlines(linewidth=1.0)
        m.drawcountries(linewidth=1.0)
        m.drawstates(linewidth=1.0)

        # Downloads and plots an image using the arcgis REST API service
        m.arcgisimage(service="USA_Topo_Maps", xpixels=2000, dpi=600, verbose= True)
        m.drawcounties()
        m.drawrivers(color='#0000ff')

        # Draw parallels (latitude lines) and meridians (longitude lines)
        # Latitude/longitude grid
        m.drawparallels(
            [31.0, 31.2, 31.4],
            labels=[1,0,0,0],
            fontsize=FONT_SIZE,
            linewidth=0.5
        )
        m.drawmeridians(
            [-97.9, -97.7, -97.5, -97.3],
            labels=[0,0,0,1],
            fontsize=FONT_SIZE,
            linewidth=0.5
        )


        # Belton Lake
        x, y = m(belton_lon, belton_lat)
        plt.text(x, y, "Belton Lake", fontsize=FONT_SIZE, color="blue", fontweight="bold")

        # GAST2 station
        x, y = m(gast2_lon, gast2_lat)
        plt.plot(x, y, marker="o", markersize=10, color="magenta")
        plt.text(x, y, "GAST2", fontsize=FONT_SIZE, color="magenta")

        # PICT2 station
        x, y = m(pict2_lon, pict2_lat)
        plt.plot(x, y, marker="^", markersize=12, color="red")
        plt.text(x, y, "PICT2", fontsize=FONT_SIZE, color="red")

        # 5. Plotting Reservoirs (Polygons)
        # Iterate through the filtered reservoir geometries
        for idx, row in filtered_reservoirs.iterrows():
            geom = row.geometry
            # Basemap plotting is simpler when we iterate and use the polygon exterior coords
            if geom.geom_type == 'Polygon':
                # Convert the geometry's coordinates to the map projection coordinates
                lons, lats = geom.exterior.xy
                m.plot(
                    lons, lats, 
                    latlon=True,          # Coordinates are in lat/lon
                    color='blue', 
                    linewidth=1.5, 
                    ax=ax,
                    zorder=2
                )
                m.plot(
                    lons, lats, 
                    color='skyblue', 
                    zorder=1,
                    alpha=0.6
                )
            
        # 6. Plotting Rivers (LineStrings)
        # Iterate through the filtered river geometries
        for idx, row in filtered_rivers.iterrows():
            geom = row.geometry
            if geom.geom_type == 'LineString':
                lons, lats = geom.xy
                m.plot(
                    lons, lats, 
                    latlon=True,          # Coordinates are in lat/lon
                    color='darkblue', 
                    linewidth=2.0, 
                    ax=ax,
                    zorder=3
                )
    
        """
        # Create dummy legend handles for rivers and reservoirs since they were plotted iteratively
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        
        legend_handles = [
            Patch(facecolor='skyblue', edgecolor='blue', label='Reservoirs', alpha=0.6),
            Line2D([0], [0], color='darkblue', lw=2.5, label='Major Rivers')
        ]
        
        ax.legend(handles=legend_handles, loc='lower right', frameon=True)
        """

        # 7. Save the figure with specified DPI
        output_filename = 'SWOT_study_domain.png'
        plt.savefig(output_filename, dpi=600, bbox_inches='tight')
        print(f"\nPlot saved successfully to {output_filename} with DPI=600.")

    except FileNotFoundError:
        print("\nError: One or both shapefiles not found.")
        print(f"Please ensure your files are located at: {RIVERS_PATH} and {RESERVOIRS_PATH}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

# Execute the main function
if __name__ == '__main__':
    load_filter_and_plot_basemap()
