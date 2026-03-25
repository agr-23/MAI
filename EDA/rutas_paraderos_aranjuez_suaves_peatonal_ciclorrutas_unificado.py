"""
Cruza paraderos Aranjuez Santa Cruz en tramos suaves con red peatonal y ciclorrutas.
Similar a rutas_paradas_suaves_peatonal_ciclorrutas_unificado.py pero usando
paraderos del shapefile Aranjuez Santa Cruz (solo inclinación suave -6° a 6°).
Genera mapas unificados + Excel con paraderos sin peatonal/ciclorruta cercana.
"""

import re
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent
RUTAS_DIR = DATA_DIR / "rutas 2"
RESULTADO_DIR = Path(__file__).resolve().parent
PARADEROS_SHP = DATA_DIR / "Paraderos Aranjuez Santa Cruz" / "Paraderos_Aranjuez_Santa_Cruz.shp"
RED_PEATONAL_SHP = DATA_DIR / "shp_pot48_2014_red_peatonal" / "pot48_2014_red_peatonal.shp"
CICLORRUTAS_SHP = DATA_DIR / "shp_pot48_2014_ciclorrutas" / "pot48_2014_ciclorrutas.shp"
RUTAS_A_PROCESAR = ["022", "023", "024", "041", "042"]
DISTANCIA_PARADAS_M = 30
DISTANCIA_RED_M = 150
DISTANCIA_PARADA_A_RED_M = 10


def extraer_coordenadas_ruta(html_path: Path) -> list:
    segmentos = extraer_segmentos_con_inclinacion(html_path)
    puntos = [segmentos[0][0][0]] if segmentos else []
    for seg, _ in segmentos:
        puntos.append(seg[1])
    return puntos


def extraer_segmentos_con_inclinacion(html_path: Path) -> list:
    with open(html_path, "r", encoding="utf-8") as f:
        contenido = f.read()
    patron_coords = r"\[\s*(\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\]\s*,\s*\[\s*(\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\]"
    patron_incl = r"bindTooltip\s*\([\s\S]*?(-?\d+\.?\d*)\s*°"
    coincidencias = re.findall(patron_coords, contenido)
    inclinaciones = re.findall(patron_incl, contenido)
    segmentos = []
    for i, m in enumerate(coincidencias):
        lat1, lon1, lat2, lon2 = float(m[0]), float(m[1]), float(m[2]), float(m[3])
        seg = [(lat1, lon1), (lat2, lon2)]
        incl = float(inclinaciones[i]) if i < len(inclinaciones) else 0.0
        segmentos.append((seg, incl))
    return segmentos


def color_por_inclinacion(grados: float) -> str:
    if grados <= -12: return "#8B0000"
    if grados <= -6: return "#DC143C"
    if grados <= -2: return "#FF8C00"
    if grados < 2: return "#228B22"
    if grados < 6: return "#87CEEB"
    if grados < 12: return "#4169E1"
    return "#00008B"


def distancia_y_segmento_cercano(lat: float, lon: float, segmentos: list) -> tuple:
    from math import radians, sin, cos, sqrt, atan2
    def haversine_m(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi, dlam = radians(lat2 - lat1), radians(lon2 - lon1)
        a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))
    min_dist, idx_cercano = float("inf"), 0
    for i, (seg, _) in enumerate(segmentos):
        lat1, lon1, lat2, lon2 = seg[0][0], seg[0][1], seg[1][0], seg[1][1]
        d_seg = haversine_m(lat1, lon1, lat2, lon2)
        if d_seg < 1e-3:
            d = haversine_m(lat, lon, lat1, lon1)
        else:
            t = ((lat - lat1) * (lat2 - lat1) + (lon - lon1) * (lon2 - lon1)) / (
                (lat2 - lat1) ** 2 + (lon2 - lon1) ** 2 + 1e-12
            )
            t = max(0, min(1, t))
            plat, plon = lat1 + t * (lat2 - lat1), lon1 + t * (lon2 - lon1)
            d = haversine_m(lat, lon, plat, plon)
        if d < min_dist:
            min_dist, idx_cercano = d, i
    return min_dist, idx_cercano


def distancia_punto_linea(lat: float, lon: float, linea: list) -> float:
    from math import radians, sin, cos, sqrt, atan2
    def haversine_m(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi, dlam = radians(lat2 - lat1), radians(lon2 - lon1)
        a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))
    min_dist = float("inf")
    for i in range(len(linea) - 1):
        lat1, lon1 = linea[i][0], linea[i][1]
        lat2, lon2 = linea[i + 1][0], linea[i + 1][1]
        d_seg = haversine_m(lat1, lon1, lat2, lon2)
        if d_seg < 1e-3:
            d = haversine_m(lat, lon, lat1, lon1)
        else:
            t = ((lat - lat1) * (lat2 - lat1) + (lon - lon1) * (lon2 - lon1)) / (
                (lat2 - lat1) ** 2 + (lon2 - lon1) ** 2 + 1e-12
            )
            t = max(0, min(1, t))
            plat, plon = lat1 + t * (lat2 - lat1), lon1 + t * (lon2 - lon1)
            d = haversine_m(lat, lon, plat, plon)
        min_dist = min(min_dist, d)
    return min_dist


def cargar_tramos_shp(shp_path: Path) -> list:
    import geopandas as gpd
    gdf = gpd.read_file(shp_path).to_crs("EPSG:4326")
    tramos = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        attrs = {k: v for k, v in row.to_dict().items() if k != "geometry"}
        if geom.geom_type == "LineString":
            coords = [(c[1], c[0]) for c in geom.coords]
            if len(coords) >= 2:
                tramos.append({"coords": coords, **attrs})
        elif geom.geom_type == "MultiLineString":
            for line in geom.geoms:
                coords = [(c[1], c[0]) for c in line.coords]
                if len(coords) >= 2:
                    tramos.append({"coords": coords, **attrs})
    return tramos


def main():
    try:
        import folium
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "folium"])
        import folium
    try:
        import geopandas as gpd
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "geopandas"])
        import geopandas as gpd

    print("Cargando paraderos Aranjuez Santa Cruz...")
    gdf = gpd.read_file(PARADEROS_SHP).to_crs("EPSG:4326")
    paradas_list = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        lon, lat = geom.x, geom.y
        paradas_list.append({
            "latitud": lat, "longitud": lon,
            "id_paradero": row.get("ID_PARADER"),
            "direccion": row.get("DIRECCION", ""),
            "codigo_ruta": str(row.get("CODIGO_RUT", "")),
            "nombre_ruta": str(row.get("NOMBRE_RUT", "")),
            "recorrido": str(row.get("RECORRIDO", "")),
            "nro_parada": row.get("NRO_PARADA", ""),
        })
    print(f"  Paraderos totales: {len(paradas_list)}")

    print("Cargando red peatonal...")
    tramos_peatonal = cargar_tramos_shp(RED_PEATONAL_SHP)
    print(f"  Tramos peatonal: {len(tramos_peatonal)}")

    print("Cargando red ciclorrutas...")
    tramos_ciclorrutas = cargar_tramos_shp(CICLORRUTAS_SHP)
    print(f"  Tramos ciclorrutas: {len(tramos_ciclorrutas)}")

    print(f"\nProcesando rutas {RUTAS_A_PROCESAR}...\n")

    resumen_excel = []
    detalle_sin_peatonal = []
    detalle_sin_ciclorruta = []

    for codigo in RUTAS_A_PROCESAR:
        ruta_html = RUTAS_DIR / f"ruta_{codigo}.html"
        if not ruta_html.exists():
            print(f"  Ruta {codigo}: No existe {ruta_html}, omitiendo.")
            continue

        segmentos_con_incl = extraer_segmentos_con_inclinacion(ruta_html)
        puntos_ruta = extraer_coordenadas_ruta(ruta_html)
        linea_ruta = [puntos_ruta[0]]
        for seg, _ in segmentos_con_incl:
            linea_ruta.append(seg[1])

        # Paraderos Aranjuez cercanos a la ruta (solo suaves -6° a 6°)
        paradas_cercanas = []
        seen = set()
        for p in paradas_list:
            p_copy = p.copy()
            lat, lon = p_copy["latitud"], p_copy["longitud"]
            dist, idx_seg = distancia_y_segmento_cercano(lat, lon, segmentos_con_incl)
            if dist <= DISTANCIA_PARADAS_M:
                incl_seg = segmentos_con_incl[idx_seg][1]
                if -6 <= incl_seg < 6:  # Solo paradas suaves
                    key = (round(lat, 5), round(lon, 5))
                    if key not in seen:
                        seen.add(key)
                        p_copy["distancia_metros"] = round(dist, 1)
                        p_copy["inclinacion_segmento"] = incl_seg
                        paradas_cercanas.append(p_copy)

        paradas_suaves = pd.DataFrame(paradas_cercanas)
        if paradas_suaves.empty:
            print(f"  Ruta {codigo}: Sin paraderos Aranjuez en tramos suaves.")
            continue

        # Tramos peatonal cercanos a la ruta
        peatonal_cercana = []
        for t in tramos_peatonal:
            min_dist = min(distancia_punto_linea(c[0], c[1], linea_ruta) for c in t["coords"])
            if min_dist <= DISTANCIA_RED_M:
                t = t.copy()
                t["distancia_ruta"] = round(min_dist, 1)
                peatonal_cercana.append(t)

        # Tramos ciclorrutas cercanos a la ruta
        ciclorrutas_cercanas = []
        for t in tramos_ciclorrutas:
            min_dist = min(distancia_punto_linea(c[0], c[1], linea_ruta) for c in t["coords"])
            if min_dist <= DISTANCIA_RED_M:
                t = t.copy()
                t["distancia_ruta"] = round(min_dist, 1)
                ciclorrutas_cercanas.append(t)

        # Paraderos sin peatonal cercana (≤10m)
        paradas_sin_peatonal = []
        for _, p in paradas_suaves.iterrows():
            lat, lon = p["latitud"], p["longitud"]
            dist_min = min(distancia_punto_linea(lat, lon, t["coords"]) for t in peatonal_cercana) if peatonal_cercana else float("inf")
            if dist_min > DISTANCIA_PARADA_A_RED_M:
                row = {k: v for k, v in p.items() if not (isinstance(v, float) and (v != v))}
                row["ruta"] = codigo
                row["dist_min_peatonal_m"] = round(dist_min, 1)
                paradas_sin_peatonal.append(row)

        # Paraderos sin ciclorruta cercana (≤10m)
        paradas_sin_ciclorruta = []
        for _, p in paradas_suaves.iterrows():
            lat, lon = p["latitud"], p["longitud"]
            dist_min = min(distancia_punto_linea(lat, lon, t["coords"]) for t in ciclorrutas_cercanas) if ciclorrutas_cercanas else float("inf")
            if dist_min > DISTANCIA_PARADA_A_RED_M:
                row = {k: v for k, v in p.items() if not (isinstance(v, float) and (v != v))}
                row["ruta"] = codigo
                row["dist_min_ciclorruta_m"] = round(dist_min, 1)
                paradas_sin_ciclorruta.append(row)

        resumen_excel.append({
            "ruta": codigo,
            "paraderos_aranjuez_suaves_total": len(paradas_suaves),
            "paraderos_sin_peatonal": len(paradas_sin_peatonal),
            "paraderos_sin_ciclorruta": len(paradas_sin_ciclorruta),
        })
        detalle_sin_peatonal.extend(paradas_sin_peatonal)
        detalle_sin_ciclorruta.extend(paradas_sin_ciclorruta)

        # Mapa unificado
        lat_centro = sum(p[0] for p in puntos_ruta) / len(puntos_ruta)
        lon_centro = sum(p[1] for p in puntos_ruta) / len(puntos_ruta)
        m = folium.Map(location=[lat_centro, lon_centro], zoom_start=14)

        # 1. Ruta con inclinaciones
        for seg, incl in segmentos_con_incl:
            folium.PolyLine(
                seg, color=color_por_inclinacion(incl), weight=5, opacity=0.9,
                tooltip=folium.Tooltip(f"Inclinación: {incl:.1f}°")
            ).add_to(m)

        # 2. Paraderos Aranjuez suaves (rojos)
        for _, p in paradas_suaves.iterrows():
            folium.CircleMarker(
                location=[p["latitud"], p["longitud"]],
                radius=8, color="red", fill=True, fillColor="red", fillOpacity=0.8,
                tooltip=folium.Tooltip(
                    f"<b>{p.get('direccion','N/A')}</b><br>"
                    f"{p.get('codigo_ruta','')} - {p.get('nombre_ruta','')}<br>"
                    f"Incl: {p['inclinacion_segmento']:.1f}°"
                ),
            ).add_to(m)

        # 3. Red peatonal (negra, punteada)
        fg_peatonal = folium.FeatureGroup(name="Red peatonal", overlay=True)
        for t in peatonal_cercana:
            folium.PolyLine(
                t["coords"], color="#000000", weight=3, opacity=1.0, dash_array="8, 6",
                tooltip=folium.Tooltip(
                    f"<b>Red peatonal</b><br>"
                    f"Tipo: {t.get('tipo_redpeatonal','')}<br>"
                    f"Estado: {t.get('estado','')}<br>"
                    f"Dist. ruta: {t.get('distancia_ruta',0)}m"
                ),
            ).add_to(fg_peatonal)
        fg_peatonal.add_to(m)

        # 4. Red ciclorrutas (morada/dorada, punteada)
        fg_ciclorrutas = folium.FeatureGroup(name="Red ciclorrutas", overlay=True)
        for t in ciclorrutas_cercanas:
            folium.PolyLine(
                t["coords"], color="#9370DB", weight=3, opacity=1.0, dash_array="8, 6",
                tooltip=folium.Tooltip(
                    f"<b>Ciclorruta</b><br>"
                    f"Nombre: {t.get('nombre','')}<br>"
                    f"Estado: {t.get('estado','')}<br>"
                    f"Dist. ruta: {t.get('distancia_ruta',0)}m"
                ),
            ).add_to(fg_ciclorrutas)
        fg_ciclorrutas.add_to(m)

        folium.LayerControl(collapsed=False).add_to(m)

        output_path = RESULTADO_DIR / f"ruta_{codigo}_paraderos_aranjuez_suaves_peatonal_ciclorrutas_unificado.html"
        m.save(output_path)
        print(f"  Ruta {codigo}: {len(paradas_suaves)} paraderos Aranjuez suaves | {len(peatonal_cercana)} peatonal | {len(ciclorrutas_cercanas)} ciclorrutas | sin peatonal: {len(paradas_sin_peatonal)} | sin ciclorruta: {len(paradas_sin_ciclorruta)}")
        print(f"    -> {output_path.name}")

    # Excel unificado
    if resumen_excel:
        excel_path = RESULTADO_DIR / "paraderos_aranjuez_suaves_peatonal_ciclorrutas_unificado.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            pd.DataFrame(resumen_excel).to_excel(writer, sheet_name="Resumen", index=False)
            if detalle_sin_peatonal:
                pd.DataFrame(detalle_sin_peatonal).to_excel(writer, sheet_name="Paraderos sin peatonal", index=False)
            if detalle_sin_ciclorruta:
                pd.DataFrame(detalle_sin_ciclorruta).to_excel(writer, sheet_name="Paraderos sin ciclorruta", index=False)
        print(f"\nExcel guardado: {excel_path}")

    print(f"\nMapas guardados en: {RESULTADO_DIR}")


if __name__ == "__main__":
    main()
