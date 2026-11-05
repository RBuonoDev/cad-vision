"""Independent parametric CAD prototype. Units: millimetres. No SolidWorks code."""
from __future__ import annotations

import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory


class ModelError(ValueError):
    pass


EXAMPLE = [
    dict(name="Base", operation="add", profile="rectangle", x=0, y=0,
         z=0, length=100, width=60, diameter=20, depth=20, enabled=True),
    dict(name="Furo central", operation="cut", profile="circle", x=0, y=0,
         z=0, length=20, width=20, diameter=16, depth=20, enabled=True,
         placement='max', extent='through'),
]


def _number(value, label, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ModelError(f'{label}: informe um número finito.')
    if abs(value) > 10000 or (positive and value < 0.1):
        raise ModelError(f'{label}: valor fora do intervalo permitido.')
    return float(value)


def validate_polygon(raw):
    if not isinstance(raw, list) or not 3 <= len(raw) <= 100:
        raise ModelError('O polígono deve ter entre 3 e 100 vértices.')
    pts = []
    for point in raw:
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ModelError('Vértice inválido no polígono.')
        pts.append([_number(point[0], 'Coordenada U'), _number(point[1], 'Coordenada V')])
    def orient(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on_segment(a, b, p):
        return (abs(orient(a,b,p)) < 1e-8 and min(a[0],b[0])-1e-8 <= p[0] <= max(a[0],b[0])+1e-8
                and min(a[1],b[1])-1e-8 <= p[1] <= max(a[1],b[1])+1e-8)
    def crosses(a,b,c,d):
        o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
        return ((o1*o2 < 0 and o3*o4 < 0) or on_segment(a,b,c) or on_segment(a,b,d)
                or on_segment(c,d,a) or on_segment(c,d,b))
    n = len(pts)
    for i in range(n):
        if math.dist(pts[i], pts[(i+1)%n]) < .01:
            raise ModelError('O esboço contém vértices repetidos ou segmentos muito curtos.')
        for j in range(i+1,n):
            if j == i+1 or (i == 0 and j == n-1):
                continue
            if crosses(pts[i],pts[(i+1)%n],pts[j],pts[(j+1)%n]):
                raise ModelError('O contorno se cruza ou encosta em si mesmo. Revise o esboço.')
    if abs(sum(pts[i][0]*pts[(i+1)%n][1]-pts[(i+1)%n][0]*pts[i][1] for i in range(n))) < .02:
        raise ModelError('O contorno não possui área suficiente para extrudar.')
    return pts


def validate(features):
    if not isinstance(features, list) or len(features) > 50:
        raise ModelError("O projeto pode conter até 50 operações.")
    clean = []
    for index, item in enumerate(features, 1):
        if not isinstance(item, dict):
            raise ModelError(f"Operação {index}: formato inválido.")
        f = {key: item.get(key) for key in ("name", "operation", "profile", "enabled")}
        if not isinstance(f['name'], str) or not f['name'].strip() or len(f['name']) > 80:
            raise ModelError(f"Operação {index}: informe um nome de até 80 caracteres.")
        if f['operation'] not in ('add', 'cut') or f['profile'] not in ('rectangle', 'circle', 'polygon'):
            raise ModelError(f"Operação {index}: tipo não suportado.")
        if not isinstance(f['enabled'], bool):
            raise ModelError(f"Operação {index}: estado inválido.")
        for key in ('x', 'y', 'z', 'length', 'width', 'diameter', 'depth'):
            f[key] = _number(item.get(key), f'Operação {index}: {key}',
                             key in ('length', 'width', 'diameter', 'depth'))
        f['plane'] = item.get('plane', 'XY')
        if f['plane'] not in ('XY','XZ','YZ'):
            raise ModelError('Plano inválido. Escolha XY, XZ ou YZ.')
        f['direction'] = item.get('direction', 1 if f['operation'] == 'add' else -1)
        if isinstance(f['direction'], bool) or f['direction'] not in (-1,1):
            raise ModelError('Direção inválida.')
        f['extent'] = item.get('extent', 'blind')
        f['placement'] = item.get('placement', 'absolute')
        if f['extent'] not in ('blind', 'symmetric', 'through'):
            raise ModelError('Condição de profundidade inválida.')
        if f['extent'] == 'through' and f['operation'] != 'cut':
            raise ModelError('Atravessar tudo está disponível somente para cortes.')
        if f['placement'] not in ('absolute', 'max', 'min'):
            raise ModelError('Referência do esboço inválida.')
        if f['profile'] == 'polygon':
            raw_points = item.get('points')
            relations = item.get('constraints', [])
            if not isinstance(relations,list):
                raise ModelError('As relações do esboço devem ser uma lista.')
            if relations:
                from constraints import solve_points
                raw_points, relations, _ = solve_points(raw_points, relations)
            f['points'] = validate_polygon(raw_points)
            f['constraints'] = relations
        clean.append(f)
    return clean


def build(features):
    """Replay ordered operations; retain a single connected solid after each step."""
    import cadquery as cq

    features = validate(features)
    model = None
    history = []
    for index, f in enumerate(features, 1):
        if not f['enabled']:
            history.append(dict(name=f['name'], status='suprimida', volume=None))
            continue
        try:
            plane = cq.Plane.named(f['plane'])
            low = high = None
            if model is not None:
                box = model.val().BoundingBox()
                projections = [cq.Vector(x,y,z).dot(plane.zDir)
                               for x in (box.xmin,box.xmax) for y in (box.ymin,box.ymax)
                               for z in (box.zmin,box.zmax)]
                low, high = min(projections), max(projections)
            offset = f['z']
            if f['placement'] != 'absolute':
                if model is None:
                    raise ModelError('Crie uma base antes de referenciar os limites do sólido.')
                offset += high if f['placement'] == 'max' else low
            distance = f['depth'] * f['direction']
            if f['extent'] == 'symmetric':
                offset -= f['depth']/2
                distance = f['depth']
            elif f['extent'] == 'through':
                if model is None:
                    raise ModelError('Crie uma base antes de fazer um corte.')
                distance = ((high-offset+1) if f['direction'] == 1 else -(offset-low+1))
                if distance*f['direction'] <= 0:
                    raise ModelError('O sólido está no sentido oposto ao corte.')
            profile = cq.Workplane(plane).workplane(offset=offset).center(f['x'], f['y'])
            if f['profile'] == 'rectangle':
                profile = profile.rect(f['length'], f['width'])
            elif f['profile'] == 'circle':
                profile = profile.circle(f['diameter'] / 2)
            else:
                profile = profile.polyline([tuple(p) for p in f['points']]).close()
            tool = profile.extrude(distance)
            if model is None:
                if f['operation'] != 'add':
                    raise ModelError('A primeira operação ativa precisa adicionar material.')
                result = tool
                previous_volume = 0.0
            else:
                previous_volume = model.val().Volume()
                result = model.union(tool) if f['operation'] == 'add' else model.cut(tool)
            if len(result.solids().vals()) != 1 or not result.val().isValid():
                raise ModelError('A operação deve produzir um único sólido válido e conectado.')
            volume = result.val().Volume()
            if volume <= 1e-8:
                raise ModelError('A operação removeu toda a peça.')
            if abs(volume - previous_volume) <= max(1e-8, previous_volume * 1e-10):
                raise ModelError('A operação não altera o volume. Verifique posição e profundidade.')
            model = result
            history.append(dict(name=f['name'], status='válida', volume=volume,
                                plane=f['plane'], offset=offset, distance=distance))
        except Exception as exc:
            raise ModelError(f"Operação {index} ({f['name']}): {exc}") from exc
    if model is None:
        raise ModelError('Ative ao menos uma extrusão.')
    return model, history


def mesh(model):
    vertices, triangles = model.val().tessellate(0.15, 0.15)
    edges = []
    for edge in model.val().Edges():
        # Display actual BRep edges, rather than tessellation triangle boundaries.
        points = edge.sample(48)[0] if edge.geomType() != 'LINE' else [edge.startPoint(), edge.endPoint()]
        edges.append([[p.x,p.y,p.z] for p in points])
    return {'vertices': [[v.x, v.y, v.z] for v in vertices],
            'triangles': [list(t) for t in triangles], 'edges': edges}


def export_model(model, kind):
    import cadquery as cq

    if kind not in ('STEP', 'STL'):
        raise ModelError('Formato de exportação não suportado.')
    with TemporaryDirectory() as folder:
        path = Path(folder) / ('peca.' + kind.lower())
        cq.exporters.export(model, str(path), exportType=kind, tolerance=0.1, angularTolerance=0.1)
        return path.read_bytes()


def dumps(features):
    return json.dumps(dict(format='cad-academico', version=3, unit='mm', features=validate(features)),
                      ensure_ascii=False, indent=2, allow_nan=False)


def loads(data):
    if len(data) > 200_000:
        raise ModelError('O projeto deve ter no máximo 200 KB.')
    doc = json.loads(data)
    if not isinstance(doc, dict) or doc.get('format') != 'cad-academico' or doc.get('version') not in (1,2,3) or doc.get('unit') != 'mm':
        raise ModelError('Arquivo de projeto incompatível.')
    return validate(doc.get('features'))
