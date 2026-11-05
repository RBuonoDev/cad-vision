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
         z=20, length=20, width=20, diameter=16, depth=20, enabled=True),
]


def validate(features):
    if not isinstance(features, list) or not 1 <= len(features) <= 50:
        raise ModelError("O projeto deve conter entre 1 e 50 operações.")
    clean = []
    for index, item in enumerate(features, 1):
        if not isinstance(item, dict):
            raise ModelError(f"Operação {index}: formato inválido.")
        f = {key: item.get(key) for key in ("name", "operation", "profile", "enabled")}
        if not isinstance(f['name'], str) or not f['name'].strip() or len(f['name']) > 80:
            raise ModelError(f"Operação {index}: informe um nome de até 80 caracteres.")
        if f['operation'] not in ('add', 'cut') or f['profile'] not in ('rectangle', 'circle'):
            raise ModelError(f"Operação {index}: tipo não suportado.")
        if not isinstance(f['enabled'], bool):
            raise ModelError(f"Operação {index}: estado inválido.")
        for key in ('x', 'y', 'z', 'length', 'width', 'diameter', 'depth'):
            value = item.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ModelError(f"Operação {index}: {key} deve ser um número finito.")
            if abs(value) > 10000 or (key in ('length', 'width', 'diameter', 'depth') and value < 0.1):
                raise ModelError(f"Operação {index}: {key} fora do intervalo permitido.")
            f[key] = float(value)
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
            profile = cq.Workplane('XY').workplane(offset=f['z']).center(f['x'], f['y'])
            profile = (profile.rect(f['length'], f['width']) if f['profile'] == 'rectangle'
                       else profile.circle(f['diameter'] / 2))
            tool = profile.extrude(f['depth'] if f['operation'] == 'add' else -f['depth'])
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
            history.append(dict(name=f['name'], status='válida', volume=volume))
        except Exception as exc:
            raise ModelError(f"Operação {index} ({f['name']}): {exc}") from exc
    if model is None:
        raise ModelError('Ative ao menos uma extrusão.')
    return model, history


def mesh(model):
    vertices, triangles = model.val().tessellate(0.15, 0.15)
    return {'vertices': [[v.x, v.y, v.z] for v in vertices],
            'triangles': [list(t) for t in triangles]}


def export_model(model, kind):
    import cadquery as cq

    if kind not in ('STEP', 'STL'):
        raise ModelError('Formato de exportação não suportado.')
    with TemporaryDirectory() as folder:
        path = Path(folder) / ('peca.' + kind.lower())
        cq.exporters.export(model, str(path), exportType=kind, tolerance=0.1, angularTolerance=0.1)
        return path.read_bytes()


def dumps(features):
    return json.dumps(dict(format='cad-academico', version=1, unit='mm', features=validate(features)),
                      ensure_ascii=False, indent=2, allow_nan=False)


def loads(data):
    if len(data) > 200_000:
        raise ModelError('O projeto deve ter no máximo 200 KB.')
    doc = json.loads(data)
    if not isinstance(doc, dict) or doc.get('format') != 'cad-academico' or doc.get('version') != 1 or doc.get('unit') != 'mm':
        raise ModelError('Arquivo de projeto incompatível.')
    return validate(doc.get('features'))
