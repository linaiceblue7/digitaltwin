import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Цифровой двойник ЭЗС")
st.title("Цифровой двойник зарядной инфраструктуры")
st.caption("Оптимальное размещение ЭЗС с учётом спроса, сети и экономики")

df = pd.read_csv(r"C:\rosa_project\output\result.csv")

st.sidebar.header("Фильтры")
top_n = st.sidebar.slider("Сколько станций показать", 5, len(df), 20)
min_power = st.sidebar.selectbox("Минимальная мощность, кВт", [0, 50, 150, 350], index=0)

filtered = df[df["power_kw"] >= min_power].head(top_n)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Станций", len(filtered))
col2.metric("Средний NPV, млн руб", f"{filtered['npv'].mean()/1e6:.1f}")
col3.metric("Средний IRR", f"{filtered['irr'].mean()*100:.1f}%")
col4.metric("Средняя окупаемость, лет", f"{filtered['payback_years'].mean():.1f}")

layer = pdk.Layer(
    "ScatterplotLayer",
    filtered,
    get_position=["longitude", "latitude"],
    get_radius=300,
    get_fill_color=[255, 80, 0, 180],
    pickable=True,
)

view = pdk.ViewState(latitude=55.7558, longitude=37.6173, zoom=10, pitch=40)
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view,
    tooltip={"text": "NPV: {npv}\nIRR: {irr}\nPayback: {payback_years}"}
))

st.subheader("Топ локаций")
st.dataframe(filtered[["priority", "latitude", "longitude", "power_kw",
                       "predicted_demand_kwh", "npv", "irr", "payback_years"]])
