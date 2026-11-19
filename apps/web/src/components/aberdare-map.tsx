"use client";

import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import type { StyleSpecification } from "maplibre-gl";
import { DemoObservation, monitoredArea, observations as demoObservations } from "@/lib/demo";

type Props = {
  selectedId: string;
  observations?: DemoObservation[];
  onSelect: (observation: DemoObservation) => void;
};

const TERRAIN_SOURCE = "mapzen-terrain";
const TERRAIN_TILES = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png";

export function AberdareMap({ selectedId, observations = demoObservations, onSelect }: Props) {
  const container = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markers = useRef(new Map<string, maplibregl.Marker>());
  const currentRecords = useRef(observations);
  const currentSelection = useRef(onSelect);
  const terrainRequested = useRef(false);
  const [hasMap, setHasMap] = useState(false);
  const [retry, setRetry] = useState(0);
  const [mapMessage, setMapMessage] = useState("Loading geographic context. You can review the observations below.");
  const [terrain, setTerrain] = useState<"off" | "loading" | "on">("off");
  const [terrainMessage, setTerrainMessage] = useState("");

  useEffect(() => { currentRecords.current = observations; }, [observations]);
  useEffect(() => { currentSelection.current = onSelect; }, [onSelect]);

  useEffect(() => {
    if (!container.current) return;
    let destroyed = false;
    let basemapFailed = false;
    setHasMap(false);
    setMapMessage("Loading geographic context. You can review the observations below.");
    setTerrain("off");
    setTerrainMessage("");
    terrainRequested.current = false;

    const style: StyleSpecification = {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          maxzoom: 19,
          attribution: "© OpenStreetMap contributors",
        },
      },
      layers: [{ id: "osm", type: "raster", source: "osm" }],
    };

    let map: maplibregl.Map;
    try {
      maplibregl.setWorkerUrl("/vendor/maplibre-gl-worker.mjs");
      map = new maplibregl.Map({
        container: container.current,
        center: monitoredArea.center,
        zoom: 10,
        style,
        attributionControl: { compact: true },
      });
      mapRef.current = map;
      map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right");
    } catch {
      mapRef.current?.remove();
      mapRef.current = null;
      setMapMessage("The interactive map is unavailable on this device. Review an observation from the list.");
      return;
    }

    map.on("style.load", () => {
      if (destroyed || basemapFailed) return;
      setHasMap(true);
      setMapMessage("Loading base map imagery…");
      map.resize();
    });
    map.on("load", () => {
      if (destroyed || basemapFailed) return;
      const enableGfwContext = process.env.NEXT_PUBLIC_ENABLE_GFW_GLAD_S2_CONTEXT === "true";
      if (enableGfwContext) {
        const tiles = process.env.NEXT_PUBLIC_GFW_GLAD_S2_TILES
          ?? "https://tiles.globalforestwatch.org/umd_glad_sentinel2_alerts/latest/dynamic/{z}/{x}/{y}.png";
        map.addSource("gfw_glad_s2_context", {
          type: "raster", tiles: [tiles], tileSize: 256,
          attribution: "Global Forest Watch GLAD-S2 alert raster context",
        });
        map.addLayer({
          id: "gfw-glad-s2-context", type: "raster", source: "gfw_glad_s2_context",
          paint: { "raster-opacity": 0.34 },
        });
      }
      setHasMap(true);
      setMapMessage("");
      map.resize();
    });
    map.on("sourcedata", (event) => {
      if (!destroyed && terrainRequested.current && event.sourceId === TERRAIN_SOURCE && event.isSourceLoaded) {
        setTerrain("on");
        setTerrainMessage("Terrain elevations from Mapzen Terrain Tiles. Land-cover conditions require separate observations.");
      }
    });
    map.on("error", (event) => {
      if (destroyed) return;
      const sourceId = "sourceId" in event ? event.sourceId : undefined;
      if (sourceId === TERRAIN_SOURCE) {
        terrainRequested.current = false;
        map.setTerrain(null);
        map.easeTo({ pitch: 0, duration: 0 });
        setTerrain("off");
        setTerrainMessage("Terrain could not load. The 2D map remains available.");
      } else if (sourceId === "osm") {
        basemapFailed = true;
        setHasMap(false);
        setMapMessage("Base map tiles are unavailable. Review an observation from the list, or retry the map.");
      }
    });

    return () => {
      destroyed = true;
      markers.current.forEach((marker) => marker.remove());
      markers.current.clear();
      mapRef.current = null;
      map.remove();
    };
  }, [retry]);

  useEffect(() => {
    const map = mapRef.current;
    if (!hasMap || !map) return;
    const ids = new Set(observations.map((item) => item.id));
    markers.current.forEach((marker, id) => {
      if (!ids.has(id)) {
        marker.remove();
        markers.current.delete(id);
      }
    });
    observations.forEach((item, index) => {
      let marker = markers.current.get(item.id);
      if (!marker) {
        const element = document.createElement("button");
        element.type = "button";
        element.addEventListener("click", () => {
          const latest = currentRecords.current.find((record) => record.id === item.id);
          if (latest) currentSelection.current(latest);
        });
        marker = new maplibregl.Marker({ element, anchor: "bottom" }).setLngLat(item.coordinates).addTo(map);
        markers.current.set(item.id, marker);
      }
      const element = marker.getElement();
      element.className = "fp-map-marker" + (item.id === selectedId ? " selected" : "");
      element.setAttribute("aria-label", "Select " + item.title);
      element.setAttribute("aria-pressed", String(item.id === selectedId));
      element.setAttribute("data-label", String(index + 1));
      element.textContent = String(index + 1);
      marker.setLngLat(item.coordinates);
    });
  }, [hasMap, observations, selectedId]);

  function resetView() {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    mapRef.current?.easeTo({
      center: monitoredArea.center, zoom: 10, bearing: 0,
      pitch: terrainRequested.current ? 55 : 0, duration: reducedMotion ? 0 : 650,
    });
  }

  function toggleTerrain() {
    const map = mapRef.current;
    if (!hasMap || !map) return;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (terrainRequested.current) {
      terrainRequested.current = false;
      map.setTerrain(null);
      map.easeTo({ pitch: 0, duration: reducedMotion ? 0 : 650 });
      setTerrain("off");
      setTerrainMessage("");
      return;
    }
    try {
      if (!map.getSource(TERRAIN_SOURCE)) {
        map.addSource(TERRAIN_SOURCE, {
          type: "raster-dem", encoding: "terrarium", tiles: [TERRAIN_TILES], tileSize: 256, maxzoom: 15,
          bounds: [33, -5, 42, 6],
          attribution: '<a href="https://github.com/tilezen/joerd/blob/master/docs/attribution.md" target="_blank" rel="noreferrer">Mapzen terrain · USGS SRTM/GMTED2010 · NOAA ETOPO1</a>',
        });
      }
      terrainRequested.current = true;
      setTerrain("loading");
      setTerrainMessage("Loading terrain elevations…");
      map.setTerrain({ source: TERRAIN_SOURCE, exaggeration: 1 });
      map.easeTo({ pitch: 55, duration: reducedMotion ? 0 : 650 });
    } catch {
      terrainRequested.current = false;
      setTerrain("off");
      setTerrainMessage("Terrain is unavailable. Continue with the 2D map.");
    }
  }

  return (
    <div className="map-card card">
      <div className="map-header-overlay">
        <span className="demo-chip">DEMO locations</span>
        <span>Geographic context · provisional research area</span>
      </div>
      <div className="maplibre-container" ref={container} aria-hidden={!hasMap} inert={!hasMap} />
      {hasMap ? (
        <div className="atlas-map-toolbar" aria-label="Map view">
          <button className="button secondary" type="button" onClick={resetView}>Reset view</button>
          <button className="button secondary" type="button" aria-pressed={terrain !== "off"} onClick={toggleTerrain}>
            {terrain === "loading" ? "Cancel terrain loading" : terrain === "on" ? "Return to 2D" : "Explore 3D terrain"}
          </button>
          {mapMessage && <p role="status">{mapMessage}</p>}
          {terrainMessage && <p role="status">{terrainMessage}</p>}
        </div>
      ) : (
        <section className="atlas-map-fallback" aria-label="Observation list">
          <p className="eyebrow">Geographic context</p>
          <h2>Review an observation</h2>
          <p role="status">{mapMessage}</p>
          <ol className="atlas-observation-list">
            {observations.map((item) => (
              <li key={item.id}><button type="button" onClick={() => onSelect(item)} aria-pressed={selectedId === item.id}>
                <span>{item.title}</span><small>{item.id}</small>
              </button></li>
            ))}
          </ol>
          {observations.length === 0 && <p>No observations are available for this view.</p>}
          <button className="button secondary" type="button" onClick={() => setRetry((value) => value + 1)}>Retry interactive map</button>
        </section>
      )}
    </div>
  );
}
