"""Independent bounded planar sketch constraint solver; all lengths in mm."""
import math


class ConstraintError(ValueError):
    pass


def clean_constraints(raw, count):
    if not isinstance(raw, list) or len(raw) > 60:
        raise ConstraintError('Use até 60 relações por esboço.')
    result = []
    for item in raw:
        if not isinstance(item, dict):
            raise ConstraintError('Relação de esboço inválida.')
        kind = item.get('type')
        if kind not in ('horizontal','vertical','length','fixed','parallel','perpendicular','equal','dx','dy'):
            raise ConstraintError('Tipo de relação não suportado.')
        fields = ['a','b'] if kind in ('parallel','perpendicular','equal','dx','dy') else ['a']
        c = {'type': kind}
        for key in fields:
            value = item.get(key)
            if isinstance(value,bool) or not isinstance(value,int) or not 0 <= value < count:
                raise ConstraintError('A relação aponta para um elemento inexistente.')
            c[key] = value
        if 'b' in c and c['a'] == c['b']:
            raise ConstraintError('Selecione dois elementos diferentes.')
        for key in (['x','y'] if kind == 'fixed' else ['value'] if kind in ('length','dx','dy') else []):
            value = item.get(key)
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or abs(value)>10000:
                raise ConstraintError('Cota inválida. Use um número finito entre −10000 e 10000.')
            if kind == 'length' and value < .1:
                raise ConstraintError('O comprimento deve ser pelo menos 0,1 mm.')
            c[key] = float(value)
        result.append(c)
    return result


def solve_points(raw_points, raw_constraints):
    if not isinstance(raw_points,list) or not 3 <= len(raw_points) <= 40:
        raise ConstraintError('Um esboço com relações deve ter de 3 a 40 vértices.')
    points=[]
    for p in raw_points:
        if not isinstance(p,(list,tuple)) or len(p)!=2:
            raise ConstraintError('Vértice inválido.')
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or abs(v)>10000 for v in p):
            raise ConstraintError('Coordenada inválida no esboço.')
        points.append([float(v) for v in p])
    cs=clean_constraints(raw_constraints,len(points))
    if not cs:
        return points,cs,dict(freedom=2*len(points),rank=0,error=0.)
    import numpy as np
    from scipy.optimize import least_squares
    n=len(points)
    def residual(flat):
        p=flat.reshape(n,2)
        def segment(i): return p[(i+1)%n]-p[i]
        rows=[]
        for c in cs:
            t,a=c['type'],c['a']
            if t=='fixed':rows.extend([p[a,0]-c['x'],p[a,1]-c['y']]);continue
            if t in ('dx','dy'):
                dim=0 if t=='dx' else 1
                rows.append(p[c['b'],dim]-p[a,dim]-c['value']);continue
            u=segment(a)
            if t=='horizontal':rows.append(u[1])
            elif t=='vertical':rows.append(u[0])
            elif t=='length':rows.append(np.linalg.norm(u)-c['value'])
            else:
                v=segment(c['b'])
                if t=='equal':rows.append(np.linalg.norm(u)-np.linalg.norm(v))
                else:
                    scale=max(np.linalg.norm(u),np.linalg.norm(v),.1)
                    rows.append((u[0]*v[1]-u[1]*v[0] if t=='parallel' else np.dot(u,v))/scale)
        return np.asarray(rows)
    fit=least_squares(residual,np.asarray(points).flatten(),bounds=(-10000.00001,10000.00001),
                      max_nfev=350,ftol=1e-11,xtol=1e-11,gtol=1e-11)
    error=float(np.max(np.abs(residual(fit.x))))
    if error>1e-5 or not np.isfinite(fit.x).all():
        raise ConstraintError('Relações conflitantes ou sem solução. Remova a última relação ou revise as cotas.')
    rank=int(np.linalg.matrix_rank(fit.jac,tol=1e-6))
    return fit.x.reshape(n,2).tolist(),cs,dict(freedom=2*n-rank,rank=rank,error=error)
