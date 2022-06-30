# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid

import pytest
import numpy as np
from cavlib import CAV, compute_activations
from .utils import TEST_DATA_DIR, TEST_IMAGE

CAVSTUDIO_CAV_FILE = TEST_DATA_DIR / 'cavstudio_sample.cav'

def test_load_save_roundtrip(tmp_path):
    vector = np.random.rand(32000).astype(np.float32)

    cav1 = CAV(id=uuid.uuid4(), vector=vector, model_layer='googlenet_5b')
    cav1.save(tmp_path / 'cav.cav')

    cav2 = CAV.load(tmp_path / 'cav.cav')

    assert cav1.id == cav2.id
    assert cav1.vector == pytest.approx(cav2.vector)
    assert cav1.model_layer == cav2.model_layer


def test_load_save_extras(tmp_path):
    # cavstudio writes 'stats' into the CAV file. This isn't directly
    # supported in CAVlib, but it should be passed-through were possible.
    cav = CAV.load(CAVSTUDIO_CAV_FILE)

    assert 'stats' in cav._extra
    stats = cav._extra['stats']

    cav.save(tmp_path / 'cav.cav')
    cav2 = CAV.load(tmp_path / 'cav.cav')

    assert 'stats' in cav2._extra
    assert cav2._extra['stats'] == stats


def test_cav_score():
    cav = CAV.load(CAVSTUDIO_CAV_FILE)

    score = cav.score(TEST_IMAGE)
    expected_score = pytest.approx(-0.125, abs=0.001)

    assert score == expected_score

    # also check calculating score with an activation, instead of an image
    activations = compute_activations(TEST_IMAGE, model_layer=cav.model_layer)
    score = cav.score(activations)

    assert score == expected_score
