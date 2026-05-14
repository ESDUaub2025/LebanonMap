from flask import Flask, render_template_string
import folium
from folium.plugins import MarkerCluster

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Locations — all in Lebanon's Bekaa Valley region
# ---------------------------------------------------------------------------
LOCATIONS = [
    {"name": "تمنين",       "ar": "Tamnine",        "lat": 33.872, "lon": 36.006},
    {"name": "تربل",        "ar": "Tarboul",         "lat": 33.830, "lon": 36.062},
    {"name": "رياق",        "ar": "Riyaq",           "lat": 33.896, "lon": 36.044},
    {"name": "كفرذبد",      "ar": "Kfar Zabad",      "lat": 33.747, "lon": 35.877},
    {"name": "فرزل",        "ar": "Ferzol",          "lat": 33.837, "lon": 35.972},
    {"name": "نيحا",        "ar": "Niha",            "lat": 33.578, "lon": 35.771},
    {"name": "ابلح",        "ar": "Ablah",           "lat": 33.832, "lon": 35.962},
    {"name": "زحلة",        "ar": "Zahle",           "lat": 33.847, "lon": 35.902},
    {"name": "معلقة",       "ar": "Maalaka",         "lat": 33.855, "lon": 35.898},
    {"name": "مجدل عنجر",   "ar": "Majdel Anjar",    "lat": 33.724, "lon": 35.929},
    {"name": "عنجر",        "ar": "Anjar",           "lat": 33.726, "lon": 35.936},
    {"name": "المرج",       "ar": "Al Marj",         "lat": 33.698, "lon": 35.952},
    {"name": "برالياس",     "ar": "Bar Elias",       "lat": 33.770, "lon": 35.873},
    {"name": "قب الياس",    "ar": "Qab Elias",       "lat": 33.793, "lon": 35.842},
    {"name": "منصورة",      "ar": "Mansourieh",      "lat": 33.754, "lon": 35.921},
    {"name": "قرعون",       "ar": "Qaraoun",         "lat": 33.553, "lon": 35.688},
    {"name": "راشيا",       "ar": "Rashaya",         "lat": 33.500, "lon": 35.838},
]

# ---------------------------------------------------------------------------
# HTML template — dark‑themed shell that embeds the Folium iframe
# ---------------------------------------------------------------------------
PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>خريطة البقاع — Lebanon Bekaa Map</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:       #0d1117;
      --surface:  #161b22;
      --border:   #30363d;
      --accent:   #e8a020;
      --accent2:  #58a6ff;
      --text:     #e6edf3;
      --muted:    #7d8590;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Tajawal', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* ── Header ─────────────────────────────────────────────────── */
    header {
      padding: 1.4rem 2rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 1.2rem;
      background: var(--surface);
    }
    .logo {
      width: 38px; height: 38px;
      background: var(--accent);
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.3rem;
      flex-shrink: 0;
    }
    header h1 {
      font-size: 1.35rem;
      font-weight: 700;
      letter-spacing: 0.01em;
    }
    header h1 span {
      color: var(--accent);
    }
    .subtitle {
      font-size: 0.78rem;
      color: var(--muted);
      font-family: 'Space Mono', monospace;
      direction: ltr;
      text-align: left;
    }

    /* ── Main layout ─────────────────────────────────────────────── */
    main {
      display: flex;
      flex: 1;
      overflow: hidden;
      height: calc(100vh - 73px);
    }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    aside {
      width: 230px;
      flex-shrink: 0;
      background: var(--surface);
      border-left: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .sidebar-header {
      padding: 1rem 1rem 0.6rem;
      font-size: 0.7rem;
      font-family: 'Space Mono', monospace;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      border-bottom: 1px solid var(--border);
      direction: ltr;
    }
    .location-list {
      overflow-y: auto;
      flex: 1;
      padding: 0.5rem 0;
    }
    .location-list::-webkit-scrollbar { width: 4px; }
    .location-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

    .loc-item {
      padding: 0.55rem 1rem;
      display: flex;
      align-items: center;
      gap: 0.7rem;
      cursor: pointer;
      transition: background 0.15s;
      border-left: 3px solid transparent;
    }
    .loc-item:hover {
      background: rgba(232,160,32,0.08);
      border-left-color: var(--accent);
    }
    .pin-dot {
      width: 9px; height: 9px;
      background: var(--accent);
      border-radius: 50%;
      flex-shrink: 0;
    }
    .loc-ar {
      font-size: 0.95rem;
      font-weight: 700;
    }
    .loc-en {
      font-size: 0.7rem;
      color: var(--muted);
      font-family: 'Space Mono', monospace;
      direction: ltr;
    }
    .count-badge {
      margin: 0.8rem 1rem;
      padding: 0.5rem 0.8rem;
      background: rgba(232,160,32,0.1);
      border: 1px solid rgba(232,160,32,0.3);
      border-radius: 6px;
      font-size: 0.72rem;
      color: var(--accent);
      font-family: 'Space Mono', monospace;
      direction: ltr;
      text-align: center;
    }

    /* ── Map ─────────────────────────────────────────────────────── */
    .map-wrapper {
      flex: 1;
      position: relative;
    }
    .map-wrapper iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
  </style>
</head>
<body>

<header>
  <div class="logo">🗺</div>
  <div>
    <h1>خريطة <span>البقاع</span> — Bekaa Valley</h1>
    <div class="subtitle">Lebanon · {{ count }} locations pinned</div>
  </div>
</header>

<main>
  <div class="map-wrapper">
    {{ map_html | safe }}
  </div>
  <aside>
    <div class="sidebar-header">// locations</div>
    <div class="count-badge">{{ count }} مناطق محددة</div>
    <div class="location-list">
      {% for loc in locations %}
      <div class="loc-item">
        <div class="pin-dot"></div>
        <div>
          <div class="loc-ar">{{ loc.name }}</div>
          <div class="loc-en">{{ loc.ar }}</div>
        </div>
      </div>
      {% endfor %}
    </div>
  </aside>
</main>

</body>
</html>
"""

# ---------------------------------------------------------------------------
# Map builder
# ---------------------------------------------------------------------------
def build_map():
    # Centre on the Bekaa valley
    m = folium.Map(
        location=[33.75, 35.90],
        zoom_start=10,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    # Custom pin icon (amber / gold)
    for loc in LOCATIONS:
        popup_html = f"""
        <div style="font-family:'Tajawal',sans-serif;min-width:140px;">
          <b style="font-size:1.1rem;direction:rtl;">{loc['name']}</b><br/>
          <span style="color:#888;font-size:0.8rem;">{loc['ar']}</span><br/>
          <span style="color:#aaa;font-size:0.75rem;">{loc['lat']:.4f}, {loc['lon']:.4f}</span>
        </div>
        """
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{loc['name']} — {loc['ar']}",
            icon=folium.Icon(
                color="orange",
                icon_color="white",
                icon="map-marker",
                prefix="fa",
            ),
        ).add_to(m)

    # Add a subtle polygon outline roughly around the points (optional visual)
    return m._repr_html_()


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    map_html = build_map()
    return render_template_string(
        PAGE_TEMPLATE,
        map_html=map_html,
        locations=LOCATIONS,
        count=len(LOCATIONS),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
