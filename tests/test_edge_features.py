"""Regression checks for parametric edge operations."""
import copy
import json
import math
import unittest

from engine import EXAMPLE, ModelError, build, dumps, loads, validate


def base():
    feature = copy.deepcopy(EXAMPLE[0])
    feature.update(length=20, width=10, depth=5)
    return feature


def edge_feature(kind, size, edges='vertical'):
    return dict(name=kind, operation=kind, radius=size, edges=edges, enabled=True)


class EdgeFeatureTests(unittest.TestCase):
    def test_round_trip_and_older_projects(self):
        features = validate([base(), edge_feature('fillet', 2)])
        self.assertEqual(loads(dumps(features)), features)
        for version in (1, 2, 3):
            old = json.loads(dumps([base()]))
            old['version'] = version
            self.assertEqual(loads(json.dumps(old)), validate([base()]))

    def test_invalid_edge_settings(self):
        for radius in (0, -1, float('nan')):
            with self.assertRaises(ModelError):
                validate([base(), edge_feature('fillet', radius)])
        with self.assertRaises(ModelError):
            validate([base(), edge_feature('chamfer', 1, 'not-an-edge')])

    @unittest.skipUnless(__import__('importlib').util.find_spec('cadquery'), 'CadQuery não instalado')
    def test_rebuild_geometry_and_failure(self):
        fillet, history = build([base(), edge_feature('fillet', 2)])
        expected = (20 * 10 - (4 - math.pi) * 2**2) * 5
        self.assertAlmostEqual(fillet.val().Volume(), expected, places=3)
        self.assertEqual(history[-1]['edges'], 'vertical')
        chamfer, _ = build([base(), edge_feature('chamfer', 1)])
        self.assertAlmostEqual(chamfer.val().Volume(), 990, places=3)
        with self.assertRaises(ModelError):
            build([base(), edge_feature('fillet', 100)])
        with self.assertRaises(ModelError):
            build([edge_feature('chamfer', 1)])


if __name__ == '__main__':
    unittest.main()
