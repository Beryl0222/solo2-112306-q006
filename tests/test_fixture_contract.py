"""检查采集资料的身份、形状和可交叉引用性。"""

import json
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def read_fixture(name):
    return json.loads((ROOT / "fixtures" / name).read_text(encoding="utf-8"))


class FixtureContractTests(unittest.TestCase):
    def test_record_manifest(self):
        manifest = read_fixture("manifest.json")
        primary = read_fixture("primary.json")
        revision = read_fixture("revision.json")
        self.assertEqual(manifest["fixture"], "trace_alignment")
        self.assertEqual(manifest["records"], ["primary.json", "revision.json"])
        self.assertTrue(manifest["synthetic"])
        self.assertEqual(revision["replaces"], primary["capture"])
        self.assertNotEqual(revision["capture"], primary["capture"])

    def test_related_input_records(self):
        primary = read_fixture("primary.json")
        revision = read_fixture("revision.json")
        times = primary["sampling"]
        observed = {}
        for fragment in primary["fragments"]:
            name = fragment["sequence"]
            values = fragment["values"]
            ids = fragment.get("frame_ids", range(fragment["first_frame"], fragment["first_frame"] + len(values)))
            for index, data in zip(ids, values, strict=True):
                self.assertIn(index, range(len(times[name])))
                self.assertEqual(np.asarray(data).shape, (2,))
                self.assertEqual(observed.setdefault((name, index), data), data)
        self.assertTrue(all(("observed", i) not in observed for i in primary["missing_observed"]))
        for replacement in revision["anchor_replacements"]:
            self.assertIn(replacement["old"], primary["anchors"])
