import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import pandas as pd
from scipy import stats
import numpy as np

def create_interactive_plots(coffeeshops_by_zipcode):
    """
    Create interactive plots using Plotly
    :param coffeeshops_by_zipcode: DataFrame with the coffeeshops data grouped by zipcode
    :return: Four interactive plots
    """
    # Calculate the average rating, score, number of reviews and number of coffeeshops per zipcode
    score_by_zipcode = coffeeshops_by_zipcode['SCORE'].mean().reset_index()
    rating_by_zipcode = coffeeshops_by_zipcode['rating'].mean().reset_index()
    average_reviews_by_zipcode = coffeeshops_by_zipcode['total_reviews'].mean().reset_index()
    number_of_coffeeshops_by_zipcode = coffeeshops_by_zipcode.size().reset_index(name='count')

    # Load the shapefile with the map of New York zip codes
    zipcodes_shapefile = gpd.read_file('maps/NY/NY-zipcodes.shp')
    # Rename the column to merge the dataframes
    zipcodes_shapefile.rename(columns={'ZCTA5CE20': 'zip_code'}, inplace=True)
    # Convert the column to numeric
    zipcodes_shapefile['zip_code'] = pd.to_numeric(zipcodes_shapefile['zip_code'])

    # Merge the average ratings with the shapefile
    merged_rating = zipcodes_shapefile.merge(rating_by_zipcode, left_on='zip_code', right_on='ZIPCODE')
    # Merge the average score with the shapefile
    merged_score = zipcodes_shapefile.merge(score_by_zipcode, left_on='zip_code', right_on='ZIPCODE')
    # Merge the average number of reviews with the shapefile
    merged_reviews = zipcodes_shapefile.merge(average_reviews_by_zipcode, left_on='zip_code', right_on='ZIPCODE')
    # Merge the number of coffeeshops with the shapefile
    merged_coffeeshops = zipcodes_shapefile.merge(number_of_coffeeshops_by_zipcode, left_on='zip_code', right_on='ZIPCODE')

    # Create interactive plots using Plotly
    fig1 = px.choropleth(merged_rating, geojson=merged_rating.geometry, locations=merged_rating.index, color='rating',
                        hover_data=['zip_code'], title='Average Rating per Zipcode', color_continuous_scale='PuBuGn', range_color=(1, 5))
    fig1.update_geos(fitbounds="locations", visible=False)
    fig1.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})

    fig2 = px.choropleth(merged_score, geojson=merged_score.geometry, locations=merged_score.index, color='SCORE',
                        hover_data=['zip_code'], title='Average Score per Zipcode', color_continuous_scale='PuBuGn_r')
    fig2.update_geos(fitbounds="locations", visible=False)
    fig2.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})

    fig3 = px.choropleth(merged_coffeeshops, geojson=merged_coffeeshops.geometry, locations=merged_coffeeshops.index, color='count',
                        hover_data=['zip_code'], title='Number of Coffeeshops per Zipcode', color_continuous_scale='PuBuGn_r')
    fig3.update_geos(fitbounds="locations", visible=False)
    fig3.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})

    fig4 = px.choropleth(merged_reviews, geojson=merged_reviews.geometry, locations=merged_reviews.index, color='total_reviews',
                        hover_data=['zip_code'], title='Average Number of Reviews per Zipcode', color_continuous_scale='PuBuGn', range_color=(0, 1500))
    fig4.update_geos(fitbounds="locations", visible=False)
    fig4.update_layout(height=400, margin={"r":0,"t":40,"l":0,"b":0})

    # Add zip code boundaries to each plot
    boundary_traces = []
    for geom in zipcodes_shapefile.geometry.boundary:
        if geom.geom_type == 'MultiLineString':
            for part in geom.geoms:
                lon, lat = part.xy
                boundary_traces.append(go.Scattergeo(
                    lon=list(lon),
                    lat=list(lat),
                    mode='lines',
                    line=dict(width=1, color='lightgray'),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        elif geom.geom_type == 'LineString':
            lon, lat = geom.xy
            boundary_traces.append(go.Scattergeo(
                lon=list(lon),
                lat=list(lat),
                mode='lines',
                line=dict(width=1, color='lightgray'),
                showlegend=False,
                hoverinfo='skip'
            ))

    for trace in boundary_traces:
        fig1.add_trace(trace)
        fig2.add_trace(trace)
        fig3.add_trace(trace)
        fig4.add_trace(trace)

    return fig1, fig2, fig3, fig4


# Function to calculate the proportion of a specific violation
def calculate_proportion(data, violation):
    total_violations = len(data)
    specific_violations = len(data[data['VIOLATION_DESCRIPTION'] == violation])
    return specific_violations, total_violations

# Function to perform z-test for proportions
def z_test_proportions(count1, nobs1, count2, nobs2):
    p1 = count1 / nobs1
    p2 = count2 / nobs2
    p = (count1 + count2) / (nobs1 + nobs2)
    se = np.sqrt(p * (1 - p) * (1/nobs1 + 1/nobs2))
    z = (p1 - p2) / se
    pval = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, pval

# Function to calculate the combined proportion of specific violations
def calculate_combined_proportion(data, violations):
    total_violations = len(data)
    specific_violations = len(data[data['VIOLATION_DESCRIPTION'].isin(violations)])
    return specific_violations, total_violations
