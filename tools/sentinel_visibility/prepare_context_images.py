"""Manually prepare two pinned historical public context illustrations.

This bounded research read does not enable an alert feed or alter the scheduled
visibility refresh. Run with the existing raster environment and an output folder.
The generated manifest records source identities, windows and output hashes.
"""

from pathlib import Path
from datetime import datetime, UTC
import hashlib,json,math,sys,urllib.request,warnings
import rasterio
from rasterio.warp import transform_bounds
from rasterio.windows import Window,from_bounds
out=Path(sys.argv[1]);out.mkdir(exist_ok=True)
bounds=[36.60,-0.49,36.63,-0.46];records=[]
for day in ['2026-11-08','2026-11-13']:
    query={'collections':['sentinel-2-l2a'],'bbox':bounds,'datetime':day+'T00:00:00Z/'+day+'T23:59:59Z','limit':5}
    req=urllib.request.Request('https://earth-search.aws.element84.com/v1/search',data=json.dumps(query).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as response: found=json.load(response)['features']
    matches=[x for x in found if x['properties'].get('grid:code')=='MGRS-36MZE']
    assert len(matches)==1
    item=matches[0];url=item['assets']['visual']['href']
    assert url.startswith('https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/36/M/ZE/2026/11/') and url.endswith('/TCI.tif')
    with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=20) as h:
        assert h.status==200 and 0<int(h.headers['Content-Length'])<800*1024*1024
        etag=h.headers['ETag']
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT='20',GDAL_HTTP_MAX_RETRY='1',GDAL_HTTP_MULTIRANGE='SERIAL',GDAL_HTTP_HEADERS='If-Match: '+etag):
        with rasterio.open(url) as src:
            assert src.count==3 and src.dtypes==('uint8','uint8','uint8') and src.crs.to_epsg()==32736 and src.res==(10.0,10.0)
            loose=from_bounds(*transform_bounds('EPSG:4326',src.crs,*bounds),transform=src.transform)
            w=Window(math.floor(loose.col_off),math.floor(loose.row_off),math.ceil(loose.col_off+loose.width)-math.floor(loose.col_off),math.ceil(loose.row_off+loose.height)-math.floor(loose.row_off))
            assert 0<w.width*w.height<150000
            pixels=src.read(window=w)
            assert pixels.shape==(3,int(w.height),int(w.width)) and pixels.max()>0
            file=out/('geta-context-'+day+'.png')
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',rasterio.errors.NotGeoreferencedWarning)
                with rasterio.open(file,'w',driver='PNG',width=int(w.width),height=int(w.height),count=3,dtype='uint8') as dest: dest.write(pixels)
            records.append({'date':day,'acquired_at':item['properties']['datetime'],'scene':item['id'],'grid':'T36MZE','source_url':url,'source_etag':etag,'native_resolution_metres':10,'source_window':list(w.flatten()),'window_transform':list(src.window_transform(w))[:6],'png':file.name,'width':int(w.width),'height':int(w.height),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'bytes':file.stat().st_size})
            print('Prepared verified image window:',day,int(w.width),int(w.height),file.stat().st_size)
meta={'title':'Sentinel-2 true-colour research context','prepared_at':datetime.now(UTC).isoformat(),'research_bounds_wgs84':bounds,'meaning':'Static historical context windows around the provisional research rectangle. Not an official forest boundary, cloud-free mosaic, change classification or current alert. No colour enhancement or generated content.','attribution':'Contains modified Copernicus Sentinel data [2026]. Earth Search / Element 84 cloud-optimized visualization assets.','items':records}
(out/'geta-context.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
