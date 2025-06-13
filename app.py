import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go
import reverse_geocoder as rg

# === data ===
nodes = pd.read_csv("nodes_colabs.csv")
edges = pd.read_csv("edges_colabs.csv")

# === Mapping the continent ===
country_to_continent = {
    'US': 'North America', 'CA': 'North America', 'MX': 'North America',
    'BR': 'South America', 'AR': 'South America', 'CL': 'South America',
    'CO': 'South America', 'PE': 'South America', 'VE': 'South America', 'EC': 'South America', 'UY': 'South America',
    'FR': 'Europe', 'DE': 'Europe', 'GB': 'Europe', 'IT': 'Europe', 'ES': 'Europe', 'NL': 'Europe', 'SE': 'Europe', 'BE': 'Europe',
    'CN': 'Asia', 'JP': 'Asia', 'IN': 'Asia', 'KR': 'Asia', 'RU': 'Asia',
    'ZA': 'Africa', 'EG': 'Africa', 'NG': 'Africa', 'KE': 'Africa',
    'AU': 'Oceania', 'NZ': 'Oceania'
}

# === Countries and continents ===
@st.cache_data
def enrich_nodes(df):
    coords = list(zip(df["latitude"], df["longitude"]))
    results = rg.search(coords, mode=1)
    df["country"] = [r["cc"] for r in results]
    df["continent"] = [country_to_continent.get(r["cc"], "Unknown") for r in results]
    return df

nodes = enrich_nodes(nodes)

# === Filters ===
st.sidebar.title("🔍 Filters")
search_term = st.sidebar.text_input("Search institution name")

continents = sorted(nodes["continent"].unique())
selected_continents = st.sidebar.multiselect("Continent", continents, default=continents)

filtered_countries = nodes[nodes["continent"].isin(selected_continents)]["country"].unique()
selected_countries = st.sidebar.multiselect("Country", sorted(filtered_countries), default=list(filtered_countries))

mod_classes = sorted(nodes["modularity_class"].unique())
selected_mods = st.sidebar.multiselect("Modularity class", mod_classes, default=mod_classes)

colab_min = int(nodes["colabs_total"].min())
colab_max = int(nodes["colabs_total"].max())
selected_colabs = st.sidebar.slider("Minimum collaborations", colab_min, colab_max, (colab_min, colab_max))

filtered_nodes = nodes[
    (nodes["continent"].isin(selected_continents)) &
    (nodes["country"].isin(selected_countries)) &
    (nodes["modularity_class"].isin(selected_mods)) &
    (nodes["colabs_total"].between(selected_colabs[0], selected_colabs[1]))
]

if search_term:
    filtered_nodes = filtered_nodes[filtered_nodes["Label"].str.contains(search_term, case=False, na=False)]

top_nodes = filtered_nodes.sort_values(by="colabs_total", ascending=False).head(1000)
valid_ids = set(top_nodes["Id"])
filtered_edges = edges[edges["Source"].isin(valid_ids) & edges["Target"].isin(valid_ids)]

# === Map ===
st.header("📍 Institutions Map")
fig_map = px.scatter_mapbox(
    top_nodes,
    lat="latitude",
    lon="longitude",
    hover_name="Label",
    size="colabs_total",
    color="modularity_class",
    zoom=2,
    height=600
)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig_map)

# === Grafo ===
st.header("🔗 Collaboration Network")
G = nx.from_pandas_edgelist(filtered_edges, 'Source', 'Target')
pos = {
    row['Id']: (row['longitude'], row['latitude'])
    for _, row in top_nodes.iterrows()
    if row['Id'] in G.nodes
}

node_x = [pos[n][0] for n in G.nodes()]
node_y = [pos[n][1] for n in G.nodes()]
node_text = [nodes[nodes['Id'] == n]['Label'].values[0] for n in G.nodes()]

node_trace = go.Scattergl(
    x=node_x, y=node_y, text=node_text,
    mode='markers',
    marker=dict(size=10, color='blue'),
    hoverinfo='text'
)

edge_x, edge_y = [], []
for src, tgt in G.edges():
    x0, y0 = pos[src]
    x1, y1 = pos[tgt]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scattergl(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines'
)

fig_net = go.Figure(data=[edge_trace, node_trace],
    layout=go.Layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        height=600
    )
)
st.plotly_chart(fig_net)

# === Tabela ===
st.header("🏆 Top 1000 Institutions by Collaborations")
st.dataframe(
    top_nodes[["Label", "colabs_total", "modularity_class", "continent", "country"]]
    .style.background_gradient(subset=["colabs_total"], cmap="Blues")
)
