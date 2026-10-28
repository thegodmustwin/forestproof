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

function FallbackMap({ selectedId, observations = demoObservations, onSelect }: Props) {
  const pointPositions = [
    { left: "42%", top: "46%" },
    { left: "66%", top: "33%" },
    { left: "30%", top: "66%" },
    { left: "53%", top: "23%" },
  ];
  return (
    <div className="map-canvas" role="img" aria-label="Illustrative interactive map of the Aberdare demo area">
      <div className="map-grid" />
      <svg className="map-ridge" width="100%" height="100%" viewBox="0 0 800 620" preserveAspectRatio="none" aria-hidden="true">
        <path d="M-20 430 C 125 290, 175 472, 304 290 S 500 370, 620 166 S 753 210, 850 64 L850 700 L-20 700Z" fill="#b7cba9" opacity=".85" />
        <path d="M-20 474 C 100 340, 210 505, 338 340 S 560 430, 684 230 S 760 290, 850 120" fill="none" stroke="#94af8b" strokeWidth="35" opacity=".48" />
      </svg>
      <div className="map-road" /><div className="map-water" />
      <span className="map-label" style={{ left: "12%", top: "22%" }}>ILLUSTRATIVE ABERDARE AREA</span>
      <span className="map-label" style={{ left: "61%", top: "73%" }}>CATCHMENT CONTEXT</span>
      {observations.map((item, index) => {
        const position = pointPositions[index % pointPositions.length];
        return (
          <button
            key={item.id}
            aria-label={`Select ${item.title}`}
            className={`marker ${selectedId === item.id ? "selected" : index === 1 ? "muted" : ""}`}
            onClick={() => onSelect(item)}
            style={position}
          ><span>{index + 1}</span></button>
        );
      })}
      <div className="map-control" aria-hidden="true"><button>+</button><button>−</button></div>
      <div className="map-credit">Illustrative fallback · not an authoritative boundary map</div>
      <div className="map-legend"><div><i className="legend-dot" style={{ background: "#d99a2b" }} /> review cue</div><div><i className="legend-dot" style={{ background: "#698a7a" }} /> context cue</div></div>
    </div>
  );
}

export function AberdareMap({ selectedId, observations = demoObservations, onSelect }: Props) {
  const container = useRef<HTMLDivElement | null>(null);
  const [hasMap, setHasMap] = useState(false);

  useEffect(() => {
    if (!container.current) return;
    let destroyed = false;
    const enableGfwContext = process.env.NEXT_PUBLIC_ENABLE_GFW_GLAD_S2_CONTEXT === "true";
    const gfwGladS2Tiles = process.env.NEXT_PUBLIC_GFW_GLAD_S2_TILES
      ?? "https://tiles.globalforestwatch.org/umd_glad_sentinel2_alerts/latest/dynamic/{z}/{x}/{y}.png";
    const style: StyleSpecification = {
      version: 8,
      sources: {
        osm: {
          type: "raster",
          tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
          tileSize: 256,
          attribution: "© OpenStreetMap contributors",
        },
      },
      layers: [
        { id: "osm", type: "raster", source: "osm" },
      ],
    };
    const map = new maplibregl.Map({
      container: container.current,
      center: monitoredArea.center,
      zoom: 10,
      style,
    });
    map.on("load", () => {
      if (destroyed) return;
      if (enableGfwContext) {
        map.addSource("gfw_glad_s2_context", { type: "raster", tiles: [gfwGladS2Tiles], tileSize: 256, attribution: "Global Forest Watch GLAD-S2 alert raster context" });
        map.addLayer({ id: "gfw-glad-s2-context", type: "raster", source: "gfw_glad_s2_context", paint: { "raster-opacity": 0.34 } });
      }
      setHasMap(true);
      observations.forEach((item, index) => {
        const element = document.createElement("button");
        element.className = `fp-map-marker ${item.id === selectedId ? "selected" : ""}`;
        element.setAttribute("aria-label", `Select ${item.title}`);
        element.textContent = String(index + 1);
        element.addEventListener("click", () => onSelect(item));
        new maplibregl.Marker({ element, anchor: "bottom" }).setLngLat(item.coordinates).addTo(map);
      });
    });
    return () => { destroyed = true; map.remove(); };
  }, [onSelect, selectedId, observations]);

  return (
    <div className="map-card card">
      <div className="map-header-overlay"><span className="demo-chip">Illustrative AOI</span><span>Map context only · optional GFW raster is not a case finding</span></div>
      <div className="maplibre-container" ref={container} aria-hidden={!hasMap} />
      {!hasMap && <FallbackMap selectedId={selectedId} observations={observations} onSelect={onSelect} />}
    </div>
  );
}
