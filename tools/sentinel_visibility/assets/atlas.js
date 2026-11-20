/* ForestProof geographic atlas. Real geometry and dated public aggregates only. */
(() => {
  "use strict";
  const root = document.documentElement;
  const archive = document.querySelector("[data-atlas-archive]");
  const host = document.querySelector("[data-atlas-map]");
  if (!archive || !host) return;
  const observations = Array.from(archive.querySelectorAll("[data-observation-date]")).map(pass => ({
    date: pass.dataset.observationDate,
    label: pass.querySelector("time")?.textContent || pass.dataset.observationDate,
    tiles: Array.from(pass.querySelectorAll("[data-grid]")).map(row => ({
      grid: row.dataset.grid, visible: Number(row.dataset.visible), sampled: Number(row.dataset.sampled), vegetation: Number(row.dataset.vegetation),
    })),
  }));
  const valid = observations.length && observations.every(pass => /^\d{4}-\d{2}-\d{2}$/.test(pass.date) && pass.tiles.length && pass.tiles.every(tile =>
    /^T\d{2}[A-Z]{3}$/.test(tile.grid) && Number.isInteger(tile.visible) && Number.isInteger(tile.sampled) && Number.isInteger(tile.vegetation) && tile.sampled > 0 && tile.visible >= 0 && tile.visible <= tile.sampled && tile.vegetation >= 0 && tile.vegetation <= tile.visible));
  const text = (selector, value) => { const node = document.querySelector(selector); if (node) node.textContent = value; };
  const message = value => text("[data-map-message]", value);
  const count = new Intl.NumberFormat("en-KE");
  let map = null, geo = null, mapReady = false, imageVisible = true, terrainActive = false, terrainQualified = false;
  let fallbackReady=false, fallbackView=null, fallbackHome=null;
  let grid = valid ? observations[0].tiles[0].grid : "T36MZE", date = valid ? observations[0].date : null;
  const dateInput = document.querySelector("[data-atlas-date]");
  const compactDate = document.querySelector("[data-atlas-date-compact]");
  const terrainButton = document.querySelector("[data-map-terrain]");
  const imageButton = document.querySelector("[data-map-image]");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const narrowViewport=window.matchMedia("(max-width:760px)");
  const evidenceSheet=document.querySelector(".atlas-mobile-sheet");
  if(evidenceSheet && narrowViewport.matches)evidenceSheet.open=false;
  narrowViewport.addEventListener("change",event=>{if(evidenceSheet&&!event.matches)evidenceSheet.open=true;});
  const images = {
    "T36MZE:2026-11-08": {url:"/assets/geta-context-2026-11-08.png",scene:"S2C_36MZE_20261108_0_L2A"},
    "T36MZE:2026-11-13": {url:"/assets/geta-context-2026-11-13.png",scene:"S2B_36MZE_20261113_0_L2A"},
  };
  function share(tile) { const value = tile.visible / tile.sampled * 100; return !tile.visible ? "0%" : value < .1 ? "<0.1%" : value.toFixed(1) + "%"; }
  function selected() { const pass = observations.find(pass => pass.date === date); return {pass,tile:pass?.tiles.find(tile => tile.grid === grid)}; }
  function clearest() { return observations.reduce((best,pass) => { const next=pass.tiles.find(t=>t.grid===grid), prior=best.tiles.find(t=>t.grid===grid); return next && (!prior || next.visible/next.sampled>prior.visible/prior.sampled) ? pass : best; }, observations[0]); }
  function readLocation() {
    if (!valid) return;
    const params = new URL(location.href).searchParams;
    grid = observations[0].tiles.some(t=>t.grid===params.get("grid")) ? params.get("grid") : observations[0].tiles[0].grid;
    date = observations.some(p=>p.date===params.get("date")) ? params.get("date") : clearest().date;
  }
  function writeLocation() { const url = new URL(location.href); url.searchParams.set("grid",grid);url.searchParams.set("date",date);history.replaceState(null,"",url.pathname+url.search+url.hash); }
  function update(announce = false) {
    if (!valid) return;
    const {pass,tile}=selected();if (!pass || !tile) return;
    dateInput.value=date;
    compactDate.value=date;
    document.querySelectorAll("[data-atlas-grid-choice]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.atlasGridChoice===grid)));
    const value=share(tile);
    text("[data-atlas-share]",value);text("[data-sheet-share]",pass.label+" · "+value);text("[data-atlas-visible]",count.format(tile.visible));text("[data-atlas-unassessed]",count.format(tile.sampled-tile.visible));text("[data-atlas-vegetation]",count.format(tile.vegetation));
    text("[data-atlas-denominator]",count.format(tile.visible)+" of "+count.format(tile.sampled)+" sampled centres · "+grid);
    document.querySelector("[data-atlas-ring]").style.setProperty("--atlas-share",tile.visible/tile.sampled*100+"%");
    text("[data-atlas-meaning-title]",tile.visible===0?"The sampled ground remained unassessed.":tile.visible/tile.sampled<.01?"Almost no usable view.":"A partial view of the landscape.");
    text("[data-atlas-meaning]",tile.visible===0?"This pass did not classify usable surface in the sample. Ground conditions remain unknown.":count.format(tile.sampled-tile.visible)+" centres remained unassessed. Usable coverage alone does not establish forest loss.");
    const context=images[grid+":"+date];
    text("[data-atlas-image-title]",context?"Matched historical image":"Matching imagery unavailable");
    text("[data-atlas-image-state]",context?pass.label+" · "+context.scene+" · native 10 m true-colour context. Classification counts use 20 m centres.":"No published image crop matches "+grid+" on "+pass.label+". The coverage counts remain available.");
    document.querySelectorAll("[data-atlas-laboratory]").forEach(link=>{link.href="/visibility?grid="+encodeURIComponent(grid)+"&date="+encodeURIComponent(date);});
    imageButton.disabled=!context || !mapReady;imageButton.setAttribute("aria-pressed",String(Boolean(context)&&imageVisible));
    host.dataset.selectedGrid=grid;host.dataset.selectedDate=date;
    if(mapReady)updateImage();
    if(announce)writeLocation();
  }
  if(valid){
    const grids=document.querySelector("[data-atlas-grid]");
    observations[0].tiles.forEach(tile=>{const button=document.createElement("button");button.type="button";button.dataset.atlasGridChoice=tile.grid;button.textContent=tile.grid;button.addEventListener("click",()=>{grid=tile.grid;update(true);});grids.append(button);});
    compactDate.replaceChildren();
    [...observations].reverse().forEach(pass=>{const option=document.createElement("option");option.value=pass.date;option.textContent=pass.label;dateInput.append(option);compactDate.append(option.cloneNode(true));});
    compactDate.disabled=false;
    dateInput.addEventListener("change",()=>{date=dateInput.value;update(true);});
    compactDate.addEventListener("change",()=>{date=compactDate.value;update(true);});
    document.querySelector("[data-atlas-selection]").hidden=false;
    readLocation();update();window.addEventListener("popstate",()=>{readLocation();update();});
  } else message("Observation selection is unavailable. You can still explore the research geometry and open the report.");
  function imageCorners(){const corners=geo?.image_corners;return Array.isArray(corners)&&corners.length===4&&corners.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite))?corners:null;}
  function updateImage(){
    if(!mapReady)return;
    if(map.getLayer("observation-image"))map.removeLayer("observation-image");
    if(map.getSource("observation-image"))map.removeSource("observation-image");
    const context=images[grid+":"+date],corners=imageCorners();
    if(!context||!imageVisible||!corners)return;
    map.addSource("observation-image",{type:"image",url:context.url,coordinates:corners});
    map.addLayer({id:"observation-image",type:"raster",source:"observation-image",paint:{"raster-opacity":.9,"raster-resampling":"nearest","raster-fade-duration":0}},"research-outline");
  }
  function resetView(){if(!mapReady)return;map.fitBounds([[geo.research_bounds[0],geo.research_bounds[1]],[geo.research_bounds[2],geo.research_bounds[3]]],{padding:{top:100,bottom:130,left:70,right:70},maxZoom:12.9,pitch:terrainActive?54:0,bearing:terrainActive?-18:0,duration:reduced?0:700});}
  function drawFallback(){
    const relief=geo?.relief, coordinates=relief?.coordinates;
    if(!relief?.url?.startsWith("/assets/")||!Array.isArray(coordinates)||coordinates.length!==4)return false;
    const svg=document.querySelector(".atlas-reference"), ns="http://www.w3.org/2000/svg";
    const west=coordinates[0][0],east=coordinates[1][0],north=coordinates[0][1],south=coordinates[2][1];
    const merc=lat=>Math.log(Math.tan(Math.PI/4+lat*Math.PI/360));
    const point=(lon,lat)=>[(lon-west)/(east-west)*512,(merc(north)-merc(lat))/(merc(north)-merc(south))*512];
    const box=geo.research_bounds, topLeft=point(box[0],box[3]),bottomRight=point(box[2],box[1]);
    const node=(tag,attrs={},text)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([key,value])=>n.setAttribute(key,String(value)));if(text)n.textContent=text;return n;};
    svg.replaceChildren(node("title",{id:"reference-title"},"Actual regional elevation context around the provisional Geta research rectangle"),node("desc",{id:"reference-desc"},"Historical elevation-coloured shaded relief. Colours show height, not forest cover. The outlined rectangle is the published research extent, not an official forest boundary. Drag to pan; use arrow keys, plus and minus, or the map buttons to navigate."));
    const raster=node("image",{href:relief.url,x:0,y:0,width:512,height:512,preserveAspectRatio:"none"});
    raster.addEventListener("error",()=>message("Regional relief could not load. The research extent and dated evidence remain available."));
    svg.append(raster,node("rect",{x:topLeft[0],y:topLeft[1],width:bottomRight[0]-topLeft[0],height:bottomRight[1]-topLeft[1],fill:"#8ce4bd0d",stroke:"#8ce4bd","stroke-width":1.5,"vector-effect":"non-scaling-stroke"}));
    svg.style.touchAction="none";svg.style.cursor="grab";svg.tabIndex=0;
    fallbackHome={x:(topLeft[0]+bottomRight[0])/2-90,y:(topLeft[1]+bottomRight[1])/2-90,size:180};fallbackView={...fallbackHome};fallbackReady=true;paintFallback();
    let drag=null;
    svg.addEventListener("pointerdown",event=>{if(event.button!==0)return;drag={x:event.clientX,y:event.clientY,view:{...fallbackView}};svg.setPointerCapture(event.pointerId);svg.style.cursor="grabbing";});
    svg.addEventListener("pointermove",event=>{if(!drag)return;const bounds=svg.getBoundingClientRect(), scale=fallbackView.size/Math.min(bounds.width,bounds.height);fallbackView.x=drag.view.x-(event.clientX-drag.x)*scale;fallbackView.y=drag.view.y-(event.clientY-drag.y)*scale;paintFallback();});
    const end=()=>{drag=null;svg.style.cursor="grab";};svg.addEventListener("pointerup",end);svg.addEventListener("pointercancel",end);
    svg.addEventListener("keydown",event=>{const delta=fallbackView.size*.1;if(event.key==="ArrowLeft")fallbackView.x-=delta;else if(event.key==="ArrowRight")fallbackView.x+=delta;else if(event.key==="ArrowUp")fallbackView.y-=delta;else if(event.key==="ArrowDown")fallbackView.y+=delta;else if(["+","="].includes(event.key)){zoomFallback(.75);event.preventDefault();return;}else if(event.key==="-"){zoomFallback(1.3);event.preventDefault();return;}else return;event.preventDefault();paintFallback();});
    return true;
  }
  function paintFallback(){if(!fallbackView)return;fallbackView.x=Math.max(0,Math.min(512-fallbackView.size,fallbackView.x));fallbackView.y=Math.max(0,Math.min(512-fallbackView.size,fallbackView.y));document.querySelector(".atlas-reference").setAttribute("viewBox",fallbackView.x+" "+fallbackView.y+" "+fallbackView.size+" "+fallbackView.size);}
  function zoomFallback(factor){if(!fallbackReady)return;const size=Math.max(45,Math.min(512,fallbackView.size*factor));fallbackView.x+=(fallbackView.size-size)/2;fallbackView.y+=(fallbackView.size-size)/2;fallbackView.size=size;paintFallback();}
  function terrainOff(note){
    terrainActive=false;terrainButton.setAttribute("aria-pressed","false");terrainButton.textContent="3D terrain";
    if(mapReady){map.setTerrain(null);map.easeTo({pitch:0,bearing:0,duration:reduced?0:450});}
    text("[data-map-view-label]","2D geographic context · Kenya");if(note)message(note);
  }
  function fallback(note){
    root.classList.remove("atlas-ready");host.dataset.ready="false";document.querySelector("[data-atlas-controls]").hidden=true;
    mapReady=false;terrainActive=false;message(note);if(map){try{map.remove();}catch(_){}map=null;}host.replaceChildren();
    if(!fallbackReady)drawFallback();
    if(fallbackReady){document.querySelector("[data-atlas-controls]").hidden=false;terrainButton.disabled=true;terrainButton.textContent="2D context";imageButton.hidden=true;text("[data-map-view-label]","2D local relief · Drag or use arrow keys to pan");text("[data-atlas-fallback]","Historical regional elevation · Approx. 153 m source spacing. Colours show height, not vegetation. The outline locates the provisional research rectangle.");}
  }
  document.querySelectorAll("[data-map-zoom]").forEach(button=>button.addEventListener("click",()=>{if(mapReady)button.dataset.mapZoom==="in"?map.zoomIn({duration:reduced?0:250}):map.zoomOut({duration:reduced?0:250});else zoomFallback(button.dataset.mapZoom==="in"?.75:1.3);}));
  document.querySelector("[data-map-reset]").addEventListener("click",()=>{if(mapReady)resetView();else if(fallbackReady){fallbackView={...fallbackHome};paintFallback();}});
  imageButton.addEventListener("click",()=>{imageVisible=!imageVisible;imageButton.setAttribute("aria-pressed",String(imageVisible));updateImage();});
  terrainButton.addEventListener("click",()=>{
    if(!mapReady||!terrainQualified)return;
    if(terrainActive){terrainOff("");message("");return;}
    if(!map.getSource("regional-elevation")){
      const terrain=geo.terrain;
      map.addSource("regional-elevation",{type:"raster-dem",tiles:terrain.tiles,tileSize:terrain.tileSize||256,encoding:terrain.encoding,minzoom:terrain.minzoom,maxzoom:terrain.maxzoom,bounds:terrain.bounds,attribution:terrain.attribution});
    }
    terrainActive=true;terrainButton.setAttribute("aria-pressed","true");terrainButton.textContent="2D view";
    map.setTerrain({source:"regional-elevation",exaggeration:1});map.easeTo({pitch:54,bearing:-18,duration:reduced?0:700});
    text("[data-map-view-label]","3D elevation context · 1× elevation scale");message("Terrain is contextual elevation. The source image and measured coverage retain their own dates and resolution.");
  });
  async function loadLibrary(){
    return import("/assets/maplibre-gl.mjs");
  }
  async function start(){
    const loadingMessage="Loading local geographic context… The dated evidence remains available below.";
    if(valid)message(loadingMessage);
    try{
      const response=await fetch("/assets/geta-geography.json",{credentials:"omit",cache:"force-cache",signal:AbortSignal.timeout(15000)});if(!response.ok)throw new Error("Geographic context unavailable");
      geo=await response.json();const bounds=geo.research_bounds;
      if(!Array.isArray(bounds)||bounds.length!==4||bounds.some((v,i)=>v!==[36.60,-.49,36.63,-.46][i]))throw new Error("Research geometry mismatch");
      drawFallback();
      const library=await loadLibrary();if(typeof library.supported==="function"&&!library.supported())throw new Error("WebGL unavailable");
      if(typeof library.setWorkerCount==="function")library.setWorkerCount(1);
      if(typeof library.setMaxParallelImageRequests==="function")library.setMaxParallelImageRequests(4);
      if(typeof library.setWorkerUrl==="function")library.setWorkerUrl("/assets/maplibre-gl-worker.mjs");
      const rectangle={type:"Feature",properties:{label:"Provisional Geta research rectangle"},geometry:{type:"Polygon",coordinates:[[[bounds[0],bounds[1]],[bounds[2],bounds[1]],[bounds[2],bounds[3]],[bounds[0],bounds[3]],[bounds[0],bounds[1]]]]}};
      const sources={research:{type:"geojson",data:rectangle}};
      const layers=[{id:"background",type:"background",paint:{"background-color":"#0b2118"}}];
      if(geo.context?.type==="FeatureCollection"){
        sources.geographic={type:"geojson",data:geo.context};layers.push({id:"geographic-fill",type:"fill",source:"geographic",paint:{"fill-color":"#18392a","fill-opacity":.6}},{id:"geographic-lines",type:"line",source:"geographic",paint:{"line-color":"#64836b","line-width":1,"line-opacity":.65}});
      }
      if(geo.relief?.url?.startsWith("/assets/")&&Array.isArray(geo.relief.coordinates)&&geo.relief.coordinates.length===4){
        sources["regional-relief"]={type:"image",url:geo.relief.url,coordinates:geo.relief.coordinates};
        layers.push({id:"regional-relief",type:"raster",source:"regional-relief",paint:{"raster-opacity":.9,"raster-fade-duration":0}});
      }
      const terrain=geo.terrain;
      terrainQualified=Boolean(terrain&&Array.isArray(terrain.tiles)&&terrain.tiles.length&&terrain.tiles.every(url=>typeof url==="string"&&url.startsWith("/assets/"))&&terrain.attribution&&["terrarium","mapbox"].includes(terrain.encoding));
      // Elevation tiles are requested only when the visitor enables terrain.
      layers.push({id:"research-fill",type:"fill",source:"research",paint:{"fill-color":"#8ce4bd","fill-opacity":.07}},{id:"research-outline",type:"line",source:"research",paint:{"line-color":"#8ce4bd","line-width":2,"line-opacity":.95}});
      const viewBounds=terrainQualified&&Array.isArray(terrain.bounds)&&terrain.bounds.length===4?[[terrain.bounds[0],terrain.bounds[1]],[terrain.bounds[2],terrain.bounds[3]]]:[[36.2,-.71],[36.92,.01]];
      map=new library.Map({container:host,style:{version:8,sources,layers},center:[(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2],maxBounds:viewBounds,zoom:12,bearing:0,pitch:0,maxZoom:15,minZoom:9.5,attributionControl:{compact:true},renderWorldCopies:false,fadeDuration:0});
      const deadline=setTimeout(()=>{if(!mapReady)fallback("Interactive geography could not initialize. Use the geographic reference and dated report below.");},15000);
      map.on("load",()=>{
        clearTimeout(deadline);mapReady=true;host.dataset.ready="true";root.classList.add("atlas-ready");document.querySelector("[data-atlas-controls]").hidden=false;
        terrainButton.disabled=!terrainQualified;terrainButton.title=terrainQualified?"Use the documented local elevation model":"3D terrain is unavailable; 2D geography remains available";
        if(!terrainQualified)terrainButton.textContent="2D context";
        map.addControl(new library.ScaleControl({maxWidth:100,unit:"metric"}),"bottom-left");
        resetView();update();text("[data-map-view-label]","2D geographic context · Drag to pan, scroll to zoom");
        if(document.querySelector("[data-map-message]").textContent===loadingMessage)message("");
        if(valid)archive.open=false;
      });
      map.on("click","research-fill",()=>{new library.Popup({closeOnClick:true,maxWidth:"22rem"}).setLngLat([(bounds[0]+bounds[2])/2,(bounds[1]+bounds[3])/2]).setText("Provisional Geta research rectangle. This geographic extent supports the published research sample; it is not an official forest boundary.").addTo(map);});
      map.on("mouseenter","research-fill",()=>{map.getCanvas().style.cursor="pointer";});map.on("mouseleave","research-fill",()=>{map.getCanvas().style.cursor="";});
      map.on("error",event=>{
        if(event.sourceId==="regional-elevation"){terrainQualified=false;terrainButton.disabled=true;terrainOff("Elevation context could not load. The atlas remains available in 2D.");}
        else if(event.sourceId==="observation-image"){text("[data-atlas-image-state]","The matching image could not load. The dated coverage counts remain available.");}
      });
      map.getCanvas().addEventListener("webglcontextlost",event=>{event.preventDefault();fallback("The graphics context was lost. The geographic reference and complete dated report remain available.");});
    }catch(_){console.warn("Atlas initialization unavailable", _.message);fallback("Interactive geography is unavailable on this device. Use the geographic reference and complete observation report below.");}
  }
  start();
})();
