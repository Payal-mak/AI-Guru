import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import json
import requests

# Setting page configuration for the Streamlit app
st.set_page_config(
    page_title="India Population Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enabling dark theme for Altair
alt.themes.enable("dark")

# Loading the Excel file
@st.cache_data
def load_data():
    try:
        # Load the Excel file, using the second row (index 1) as the header
        df = pd.read_excel(r"D:\AI GURU Internship\A-1_NO_OF_VILLAGES_TOWNS_HOUSEHOLDS_POPULATION_AND_AREA.xlsx", header=1)
        
        # Debugging: Print column names before cleaning
        st.write("Column names before cleaning:", list(df.columns))
        
        # Cleaning headers: removing extra spaces, newlines, and quotes, and converting to uppercase
        df.columns = (df.columns
                      .str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with single space
                      .str.replace(r'\n', ' ', regex=True)   # Remove newlines
                      .str.strip()                           # Remove leading/trailing spaces
                      .str.replace(r'^"|"$', '', regex=True) # Remove quotes
                      .str.upper())                          # Convert to uppercase
        
        # Debugging: Print column names after cleaning
        st.write("Column names after cleaning:", list(df.columns))
        
        # Define the level column in uppercase to match the normalized column names
        level_column = 'INDIA/STATE/UNION TERRITORY/DISTRICT/SUB-DISTRICT'
        
        if level_column not in df.columns:
            st.error(f"Column '{level_column}' not found in the Excel file. Available columns: {list(df.columns)}")
            return pd.DataFrame()
        
        # Debugging: Display unique values in the level column to verify 'STATE'
        st.write(f"Unique values in '{level_column}':", df[level_column].unique())
        
        # Filtering for state-level data where the level column is 'STATE' and 'TOTAL/RURAL/URBAN' is 'Total'
        df_states = df[
            (df[level_column].str.strip().str.upper() == 'STATE') & 
            (df['TOTAL/RURAL/URBAN'].str.strip().str.title() == 'Total')
        ].copy()
        
        if df_states.empty:
            st.error("No state-level data found after filtering. Please check the filter conditions.")
            return pd.DataFrame()
        
        # Selecting relevant columns and renaming for consistency
        df_states = df_states[[
            'STATE CODE', 'NAME', 'POPULATION', 'AREA (IN SQ.KM)', 'POPULATION PER SQ.KM.'
        ]].rename(columns={
            'STATE CODE': 'state_code',
            'NAME': 'states',
            'POPULATION': 'population',
            'AREA (IN SQ.KM)': 'area_sq_km',
            'POPULATION PER SQ.KM.': 'population_density'
        })
        
        # Adding a year column (assuming 2011 based on context)
        df_states['year'] = 2011
        
        # Cleaning state names: removing special characters like '@&'
        df_states['states'] = df_states['states'].str.replace(r'[@&]', '', regex=True).str.strip()
        
        # Creating a standardized state code for GeoJSON (e.g., 'IN-01' for Jammu & Kashmir)
        df_states['state_code_geo'] = 'IN-' + df_states['state_code'].astype(str).str.zfill(2)
        
        # Converting population to numeric, handling any non-numeric values
        df_states['population'] = pd.to_numeric(df_states['population'], errors='coerce')
        
        # Dropping rows with missing population data
        df_states = df_states.dropna(subset=['population'])
        
        return df_states
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Loading GeoJSON for Indian states
@st.cache_data
def load_geojson():
    geojson_url = "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
    try:
        response = requests.get(geojson_url)
        response.raise_for_status()
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error loading GeoJSON: {str(e)}")
        return {}

df_reshaped = load_data()

# Check if df_reshaped is empty before proceeding
if df_reshaped.empty:
    st.error("Data loading failed. Please check the error messages above and ensure the Excel file is correctly formatted.")
    st.stop()

geojson_data = load_geojson()

# Sidebar configuration
with st.sidebar:
    st.title('🇮🇳 India Population Dashboard')
    
    # Since we only have one year (2011), disable year selection or set to 2011
    year_list = [2011]  # Only 2011 available in the Excel file
    selected_year = st.selectbox('Select a year', year_list, index=0)
    df_selected_year = df_reshaped[df_reshaped.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="population", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

# Function to create a heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'max({input_color}):Q',
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=900).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    return heatmap

# Function to create a choropleth map using GeoJSON
def make_choropleth(input_df, input_id, input_column, input_color_theme, geojson):
    if not geojson or input_df.empty:
        st.error("Cannot render choropleth map due to missing data or GeoJSON.")
        return None
    choropleth = px.choropleth(
        input_df,
        geojson=geojson,
        locations=input_id,
        color=input_column,
        featureidkey="properties.ST_ISO",
        color_continuous_scale=input_color_theme,
        range_color=(0, max(input_df[input_column])),
        labels={'population': 'Population'},
        title="India Population by State"
    )
    choropleth.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=50, b=0),
        height=450,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='mercator',
            fitbounds="locations",
            visible=True
        )
    )
    choropleth.update_geos(
        center=dict(lon=78.9629, lat=20.5937),
        scope="asia"
    )
    return choropleth

# Function to calculate population difference (mocked for single-year data)
def calculate_population_difference(input_df, input_year):
    selected_year_data = input_df[input_df['year'] == input_year].reset_index()
    selected_year_data['population_difference'] = 0
    return pd.concat([selected_year_data['states'], selected_year_data['state_code'], selected_year_data['population'], selected_year_data['population_difference']], axis=1).sort_values(by="population_difference", ascending=False)

# Function to format numbers
def format_number(num):
    if pd.isna(num):
        return '0'
    num = int(num)
    if num > 1000000:
        if not num % 1000000:
            return f'{num // 1000000} M'
        return f'{round(num / 1000000, 1)} M'
    return f'{num // 1000} K'

# Function to create a donut chart
def make_donut(input_response, input_text, input_color):
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    elif input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    elif input_color == 'orange':
        chart_color = ['F39C12', '#875A12']
    elif input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color=alt.Color("Topic:N",
                        scale=alt.Scale(
                            domain=[input_text, ''],
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text

# App Layout
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.markdown('#### Gains/Losses')

    df_population_difference_sorted = calculate_population_difference(df_reshaped, selected_year)

    # Displaying metrics
    first_state_name = df_population_difference_sorted['states'].iloc[0] if not df_population_difference_sorted.empty else '-'
    first_state_population = format_number(df_population_difference_sorted['population'].iloc[0]) if not df_population_difference_sorted.empty else '-'
    first_state_delta = format_number(df_population_difference_sorted['population_difference'].iloc[0]) if not df_population_difference_sorted.empty else ''
    
    st.metric(label=first_state_name, value=first_state_population, delta=first_state_delta)

    last_state_name = df_population_difference_sorted['states'].iloc[-1] if not df_population_difference_sorted.empty else '-'
    last_state_population = format_number(df_population_difference_sorted['population'].iloc[-1]) if not df_population_difference_sorted.empty else '-'
    last_state_delta = format_number(df_population_difference_sorted['population_difference'].iloc[-1]) if not df_population_difference_sorted.empty else ''
    
    st.metric(label=last_state_name, value=last_state_population, delta=last_state_delta)

    st.markdown('#### States Migration')

    states_migration_greater = 0
    states_migration_less = 0
    donut_chart_greater = make_donut(states_migration_greater, 'Inbound Migration', 'green')
    donut_chart_less = make_donut(states_migration_less, 'Outbound Migration', 'red')

    migrations_col = st.columns((0.2, 1, 0.2))
    with migrations_col[1]:
        st.write('Inbound')
        st.altair_chart(donut_chart_greater)
        st.write('Outbound')
        st.altair_chart(donut_chart_less)
        
with col[1]:
    st.markdown('#### Total Population')
    
    choropleth = make_choropleth(df_selected_year, 'state_code_geo', 'population', selected_color_theme, geojson_data)
    if choropleth:
        st.plotly_chart(choropleth, use_container_width=True)
    
    heatmap = make_heatmap(df_reshaped, 'year', 'states', 'population', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)
    
with col[2]:
    st.markdown('#### Top States')

    st.dataframe(df_selected_year_sorted,
                 column_order=("states", "population"),
                 hide_index=True,
                 width=None,
                 column_config={
                     "states": st.column_config.TextColumn("States"),
                     "population": st.column_config.ProgressColumn(
                         "Population",
                         format="%f",
                         min_value=0,
                         max_value=max(df_selected_year_sorted.population),
                     )}
                 )
    
    with st.expander('About', expanded=True):
        st.write('''
            - Data: Census of India 2011 (A-1 Number of Villages, Towns, Households, Population and Area).
            - :orange[**Gains/Losses**]: Placeholder for states with high inbound/outbound migration (data limited to 2011).
            - :orange[**States Migration**]: Placeholder for percentage of states with annual inbound/outbound migration > 50,000 (data limited to 2011).
            - Note: Multi-year data not available in the provided Excel file; showing 2011 data only.
        ''')