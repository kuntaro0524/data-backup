#!/usr/bin/env python3
"""Preliminary comparison of existing models/maps; no new refinement."""
import json
from pathlib import Path
import numpy as np
import gemmi

BASE = Path('/media/kuntaro/KBU-005/hirota/_kamoproc')
OUT = Path(__file__).resolve().parents[1] / 'analysis' / 'hirota_density'
SOURCES = {
    'TBOC': 'merge_ccc_1.31S_CRY1PHR_TBOC/cc_1.94A_final/cluster_0054/run_03/ccp4',
    'AN174': 'merge_ccc_1.31S_CRY1PHR_AN174/cc_2.21A_final/cluster_0063/run_03/ccp4',
}


def atoms(path):
    result = []
    for line in path.read_text().splitlines():
        if line.startswith(('ATOM  ', 'HETATM')) and line[16] in (' ', 'A'):
            result.append(dict(record=line[:6].strip(), name=line[12:16].strip(),
                               resname=line[17:20], chain=line[21], resnum=int(line[22:26]),
                               xyz=np.array([float(line[30:38]), float(line[38:46]), float(line[46:54])]),
                               b=float(line[60:66])))
    return result


def ca_map(aa):
    return {(a['resnum'], a['resname']): a['xyz'] for a in aa
            if a['record'] == 'ATOM' and a['chain'] == 'A' and a['name'] == 'CA'}


def fit(a, b):
    keys = sorted(set(a) & set(b))
    x = np.array([a[k] for k in keys]); y = np.array([b[k] for k in keys])
    u, _, vt = np.linalg.svd((x-x.mean(0)).T @ (y-y.mean(0)))
    fix = np.eye(3); fix[2, 2] = np.linalg.det(u @ vt)
    rot = u @ fix @ vt; shift = y.mean(0) - x.mean(0) @ rot
    return rot, shift, keys


def sample(grid, xyz):
    return np.array([grid.interpolate_value(gemmi.Position(*map(float, p))) for p in xyz])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    aa = {name: atoms(BASE / sub / 'jelly01.pdb') for name, sub in SOURCES.items()}
    ca = {name: ca_map(value) for name, value in aa.items()}
    # Coordinates displayed in the TBOC frame.
    rot, shift, keys = fit(ca['AN174'], ca['TBOC'])
    reference = atoms(BASE / 'Models/CRY1-KL044_6kx5.pdb')
    rr, tt, ref_keys = fit(ca_map(reference), ca['TBOC'])
    ligand = np.array([a['xyz'] @ rr + tt for a in reference
                       if a['record'] == 'HETATM' and a['resname'] == 'DYR' and a['chain'] == 'A'])
    # Reference ligand is a site locator only, not an assigned ligand in these data.
    center = ligand.mean(0)
    _, _, axes = np.linalg.svd(ligand - center, full_matrices=False)
    regions = {'reference_KL044_site': center,
               'residues_451_453': np.mean([p for (n, _), p in ca['TBOC'].items() if 451 <= n <= 453], axis=0),
               'residues_485_492': np.mean([p for (n, _), p in ca['TBOC'].items() if 485 <= n <= 492], axis=0)}
    output = {'sources': SOURCES, 'base': str(BASE), 'common_resolution_A': 2.21,
              'map_method': 'Existing FWT/PHWT and DELFWT/PHDELWT; cut both at 2.21 A; FFT sample_rate=3; each map normalized to global mean 0 / standard deviation 1.',
              'limitations': ['Existing model-phased maps, not independent omit maps.',
                             'No new refinement, ligand fitting, or chemical identification.',
                             'Non-isomorphous cells: no direct Fo-Fo map calculated.',
                             'Atom-center density is descriptive, not RSCC or model validation.'],
              'reference_locator': '6KX5 chain A DYR (KL044); aligned by common chain A CA atoms',
              'reference_alignment_CA': len(ref_keys), 'models': {}}
    archive = {}
    x = np.array([ca['TBOC'][k] for k in keys]); y = np.array([ca['AN174'][k] for k in keys]) @ rot + shift
    archive['resnums'] = np.array([k[0] for k in keys]); archive['displacement'] = np.linalg.norm(x-y, axis=1)
    output['global_CA_rmsd_A'] = float(np.sqrt(np.mean(np.sum((x-y)**2, axis=1))))
    axis = np.linspace(-10, 10, 101); xx, yy = np.meshgrid(axis, axis)
    archive['slice_axis'] = axis
    for name, sub in SOURCES.items():
        mtz = gemmi.read_mtz_file(str(BASE / sub / 'jelly01.mtz'))
        keep = mtz.make_d_array() >= 2.21
        mtz.set_data(np.array(mtz.array[keep], copy=True))
        maps = {}
        for label, amp, phase in [('2fofc', 'FWT', 'PHWT'), ('fofc', 'DELFWT', 'PHDELWT')]:
            grid = mtz.transform_f_phi_to_map(amp, phase, sample_rate=3)
            grid.normalize(); maps[label] = grid
        to_native = (lambda points: (points-shift) @ rot.T) if name == 'AN174' else (lambda points: points)
        ligand_native = to_native(ligand)
        protein = np.array([a['xyz'] for a in aa[name] if a['record'] == 'ATOM'])
        distances = np.linalg.norm(ligand_native[:, None, :] - protein[None, :, :], axis=2).min(axis=1)
        pocket_samples = sample(maps['fofc'], ligand_native)
        details = {'cell': [mtz.cell.a, mtz.cell.b, mtz.cell.c], 'spacegroup': mtz.spacegroup.hm,
                   'reference_ligand_atoms': len(ligand),
                   'reference_ligand_atoms_overlapping_protein_lt_2A': int(np.sum(distances < 2)),
                   'positive_fofc_over_3sigma_at_reference_atoms': int(np.sum(pocket_samples > 3)),
                   'max_fofc_at_reference_atoms_sigma': float(pocket_samples.max()), 'regions': {}}
        for region, ctr in regions.items():
            points = ctr + xx.ravel()[:, None]*axes[0] + yy.ravel()[:, None]*axes[1]
            native = to_native(points)
            for label, grid in maps.items():
                archive[name+'_'+region+'_'+label] = sample(grid, native).reshape(xx.shape)
            if region != 'reference_KL044_site':
                low, high = (451, 453) if region == 'residues_451_453' else (485, 492)
                selected = [a for a in aa[name] if low <= a['resnum'] <= high and a['name'] == 'CA']
                values = sample(maps['2fofc'], np.array([a['xyz'] for a in selected]))
                details['regions'][region] = {'CA_count': len(selected), 'mean_2fofc_at_CA_sigma': float(values.mean()),
                                              'min_2fofc_at_CA_sigma': float(values.min())}
            transformed = np.array([a['xyz'] for a in aa[name] if a['name'] == 'CA'])
            if name == 'AN174': transformed = transformed @ rot + shift
            relative = transformed - ctr
            mask = np.abs(relative @ axes[2]) < 2
            archive[name+'_'+region+'_CA_xy'] = np.column_stack((relative[mask] @ axes[0], relative[mask] @ axes[1]))
        output['models'][name] = details
    ligand_rel = ligand - center
    archive['reference_ligand_xy'] = np.column_stack((ligand_rel @ axes[0], ligand_rel @ axes[1]))
    np.savez_compressed(str(OUT / 'density_slices.npz'), **archive)
    (OUT / 'results.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
