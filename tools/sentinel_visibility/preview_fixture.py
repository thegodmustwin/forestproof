"""Loopback-only browser-test fixture. Never a provider refresh or production report."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import UTC, datetime
import json

from tools.sentinel_visibility.visibility_service import serve


def fixture():
    days = [
        ("2026-11-08", [("36MZE",27722,6424,6346),("37MBV",27724,7675,7578)]),
        ("2026-11-10", [("36MZE",27722,0,0),("37MBV",27724,12,12)]),
        ("2026-11-13", [("36MZE",27722,3,0),("37MBV",27724,3,0)]),
    ]
    acquisitions=[]
    for day,rows in days:
        tiles=[]
        for grid,sampled,visible,vegetation in rows:
            counts=[0]*12
            counts[4],counts[5],counts[8]=vegetation,visible-vegetation,sampled-visible
            tiles.append(dict(tile=grid,sampled_centres=sampled,surface_classified_visible=visible,
                              vegetation_classified_visible=vegetation,scl_counts_0_to_11=counts))
        acquisitions.append(dict(date=day,tiles=tiles))
    now=datetime.now(UTC).isoformat()
    return dict(attempted_at=now,failed=False,report=dict(
        schema="forestproof.sentinel2_visibility.v1",area="Provisional Geta research rectangle",
        bounds_wgs84=[36.60,-0.49,36.63,-0.46],native_resolution_metres=20,checked_at=now,
        acquisitions=acquisitions))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port",type=int,default=18462)
    args=parser.parse_args()
    with TemporaryDirectory(prefix="forestproof-public-fixture-") as tmp:
        state=Path(tmp)/"fixture.json"
        state.write_text(json.dumps(fixture()),encoding="utf-8")
        print(f"Browser-test fixture: http://127.0.0.1:{args.port}/atlas/geta",flush=True)
        serve(state,args.port,f"localhost:{args.port}")
