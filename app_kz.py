import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Экотуризм: Шарын және Ақсу-Жабағылы", layout="wide")
st.title("🌿 Экотуризм: Шарын шатқалы және Ақсу-Жабағылы")
st.caption("Идея: уақыт бойынша ақылы кіру (QR) + жүктеме шектеуі + жергілікті халыққа табыс")

# ---------- Нүктелер (координаталар ШАМАМЕН — өз GPS-трегіңізбен нақтылаңыз) ----------
POINTS = [
    # атауы, аймақ, lat, lon, қауіпсіздік, қолжетімділік, көрнекілік, табиғатқа төзімділік, түрі
    ("Кіру аймағы (Шарын)", "Шарын", 43.3500, 79.0800, 4, 5, 3, 3, "Кіру"),
    ("«Шатқалды көру нүктесі»", "Шарын", 43.3480, 79.0850, 4, 3, 5, 3, "Көру алаңы"),
    ("Шарын өзенінің жағасы", "Шарын", 43.3370, 79.1180, 3, 4, 4, 3, "Демалыс"),
    ("Жасыл тоғай (ясень)", "Шарын", 43.3340, 79.1250, 3, 3, 5, 2, "Табиғат"),
    ("Қорыққа кіру (Жабағылы)", "Ақсу-Жабағылы", 42.3900, 70.5100, 4, 5, 3, 4, "Кіру"),
    ("Көру нүктесі", "Ақсу-Жабағылы", 42.4000, 70.5300, 4, 2, 5, 5, "Көру алаңы"),
    ("Соқпақ басы (Демалақ)", "Ақсу-Жабағылы", 42.4100, 70.5500, 4, 3, 3, 4, "Соқпақ"),
    ("Демалыс / кемпинг алаңы", "Ақсу-Жабағылы", 42.3950, 70.5200, 4, 4, 3, 4, "Демалыс"),
]
COLORS = {"Шарын": "orange", "Ақсу-Жабағылы": "green"}
ICONS = {"Кіру": "sign-in", "Көру алаңы": "camera", "Демалыс": "home", "Табиғат": "leaf", "Соқпақ": "road"}

# ---------- Бүйір панель: экономика ----------
st.sidebar.header("⚙️ Маршрут экономикасы")
T = st.sidebar.slider("Ашық тұру уақыты, сағ (T)", 4, 12, 8)
tau = st.sidebar.slider("Топтар арасындағы аралық, сағ (τ)", 0.5, 3.0, 1.0, 0.5)
n = st.sidebar.slider("Бір топтағы адам саны (n)", 5, 15, 15)
price = st.sidebar.number_input("Эко-билет бағасы, ₸", 500, 20000, 3000, 500)
days = st.sidebar.slider("Маусымдағы жұмыс күндері", 30, 250, 120)
load = st.sidebar.slider("Слоттардың орташа жүктемесі, %", 10, 100, 60)
guide_extra = st.sidebar.number_input(
    "Турист жергілікті халыққа жұмсайтын қосымша шығын (гид, тамақ, үй), ₸", 0, 50000, 8000, 1000
)

S = (T / tau) * n
visitors_day = S * load / 100
season_visitors = visitors_day * days
ticket_rev = season_visitors * price
local_rev = season_visitors * guide_extra

# ---------- Көрсеткіштер ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Шек S, адам/күн", f"{S:.0f}")
c2.metric("Нақты келушілер/күн", f"{visitors_day:.0f}")
c3.metric("Маусымдағы билет табысы", f"{ticket_rev/1e6:.1f} млн ₸")
c4.metric("Жергілікті халық табысы", f"{local_rev/1e6:.1f} млн ₸")

st.subheader("Билет табысын бөлу")
a = st.columns(3)
p1 = a[0].slider("Табиғатты қорғау және соқпақтар, %", 0, 100, 40)
p2 = a[1].slider("Жергілікті гидтер мен қауымдастық, %", 0, 100 - p1, 40)
p3 = 100 - p1 - p2
a[2].metric("Дамыту (QR, маркетинг), %", p3)
st.write(
    f"🌲 Табиғатқа: **{ticket_rev*p1/100/1e6:.2f} млн ₸** · "
    f"👥 Жергілікті халыққа: **{ticket_rev*p2/100/1e6:.2f} млн ₸** · "
    f"📱 Дамытуға: **{ticket_rev*p3/100/1e6:.2f} млн ₸**"
)

# ---------- Карта ----------
st.subheader("🗺 Маршрут картасы")
area = st.radio("Көрсету", ["Екі аймақ", "Шарын", "Ақсу-Жабағылы"], horizontal=True)
shown = [p for p in POINTS if area == "Екі аймақ" or p[1] == area]

lat = sum(p[2] for p in shown) / len(shown)
lon = sum(p[3] for p in shown) / len(shown)
zoom = 6 if area == "Екі аймақ" else 12
m = folium.Map(location=[lat, lon], zoom_start=zoom, tiles="OpenStreetMap")
folium.TileLayer("Esri.WorldImagery", name="Спутник").add_to(m)

for name, ar, la, lo, saf, com, view, nat, kind in shown:
    total = saf + com + view + nat
    html = (
        f"<b>{name}</b><br>{ar} · {kind}<br>"
        f"Қауіпсіздік: {saf}/5<br>Қолжетімділік: {com}/5<br>"
        f"Көрнекілік: {view}/5<br>Табиғатқа төзімділік: {nat}/5<br><b>Жалпы: {total}/20</b>"
    )
    folium.Marker(
        [la, lo],
        popup=folium.Popup(html, max_width=250),
        tooltip=name,
        icon=folium.Icon(color=COLORS[ar], icon=ICONS.get(kind, "info-sign"), prefix="fa"),
    ).add_to(m)
    # жүктеме шеңбері: радиус келушілер санына байланысты
    folium.Circle([la, lo], radius=150 + visitors_day * 2, color=COLORS[ar], fill=True, fill_opacity=0.15).add_to(m)

for ar in ("Шарын", "Ақсу-Жабағылы"):
    if area in ("Екі аймақ", ar):
        pts = [[p[2], p[3]] for p in POINTS if p[1] == ar]
        folium.PolyLine(pts, color=COLORS[ar], weight=4, dash_array="8").add_to(m)

folium.LayerControl().add_to(m)
st_folium(m, height=520, use_container_width=True)

# ---------- Идеялар ----------
with st.expander("💡 Туризм экономикасын қалай дамытуға болады"):
    st.markdown(
        """
- **Уақыт бойынша QR-билет** — ағынды бақылау және алдын ала төлем.
- **Эко-жинақ** — қаражат соқпақтарға, қоқыс жәшіктеріне, күзетке кетеді.
- **Жергілікті гидтер мен қонақ үйлер** — табыс ауылда қалады.
- **Жергілікті өнімдер мен кәдесыйлар** — кіреберістегі жәрмеңке.
- **Пакеттік тур** «Шарын → Ақсу-Жабағылы» (Алматы ↔ Түркістан).
- **«Бұрын/кейін» мониторингі** — қауіпсіздік пен қоқыс көрсеткіштері әкімдікке есеп ретінде.
"""
    )
