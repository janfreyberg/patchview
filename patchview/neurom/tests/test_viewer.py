# Copyright (c) 2015, Ecole Polytechnique Federale de Lausanne, Blue Brain Project
# All rights reserved.
#
# This file is part of NeuroM <https://github.com/BlueBrain/NeuroM>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright
#        notice, this list of conditions and the following disclaimer.
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#     3. Neither the name of the copyright holder nor the names of
#        its contributors may be used to endorse or promote products
#        derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os
import shutil
import tempfile
import mock
import sys

import matplotlib

if "DISPLAY" not in os.environ:  # noqa
    matplotlib.use("Agg")  # noqa

import neurom
from neurom.view import common, plotly
from neurom import load_neuron, viewer, NeuriteType

from nose import tools as nt
from numpy.testing import assert_allclose

_PWD = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(_PWD, "../../test_data/swc")
MORPH_FILENAME = os.path.join(DATA_PATH, "Neuron.swc")

nrn = load_neuron(MORPH_FILENAME)


def _reload_module(module):
    """Force module reload"""
    if sys.version_info >= (3,):
        import importlib

        importlib.reload(module)
    else:
        reload(module)


def test_plotly_extra_not_installed():
    with mock.patch.dict(sys.modules, {"plotly": None}):
        try:
            _reload_module(neurom.view.plotly)
            nt.ok_(False, "ImportError not triggered")
        except ImportError as e:
            nt.assert_equal(
                str(e),
                "neurom[plotly] is not installed. "
                "Please install it by doing: pip install neurom[plotly]",
            )


def test_plotly_draw_neuron3d():
    plotly.draw(nrn, plane="3d", auto_open=False)
    plotly.draw(nrn.neurites[0], plane="3d", auto_open=False)


def test_plotly_draw_neuron2d():
    plotly.draw(nrn, plane="xy", auto_open=False)
    plotly.draw(nrn.neurites[0], plane="xy", auto_open=False)


def test_draw_neuron():
    viewer.draw(nrn)
    common.plt.close("all")


def test_draw_filter_neurite():
    for mode in ["2d", "3d"]:
        viewer.draw(nrn, mode=mode, neurite_type=NeuriteType.basal_dendrite)
        assert_allclose(common.plt.gca().get_ylim(), [-30.0, 78], atol=5)

    common.plt.close("all")


def test_draw_neuron3d():
    viewer.draw(nrn, mode="3d")
    common.plt.close("all")


def test_draw_tree():
    viewer.draw(nrn.neurites[0])
    common.plt.close("all")


def test_draw_tree3d():
    viewer.draw(nrn.neurites[0], mode="3d")
    common.plt.close("all")


def test_draw_soma():
    viewer.draw(nrn.soma)
    common.plt.close("all")


def test_draw_soma3d():
    viewer.draw(nrn.soma, mode="3d")
    common.plt.close("all")


def test_draw_dendrogram():
    viewer.draw(nrn, mode="dendrogram")
    common.plt.close("all")

    viewer.draw(nrn.neurites[0], mode="dendrogram")
    common.plt.close("all")


def test_draw_dendrogram_empty_segment():
    neuron = load_neuron(os.path.join(DATA_PATH, "empty_segments.swc"))
    viewer.draw(neuron, mode="dendrogram")
    common.plt.close("all")


@nt.raises(viewer.InvalidDrawModeError)
def test_invalid_draw_mode_raises():
    viewer.draw(nrn, mode="4d")


@nt.raises(viewer.NotDrawableError)
def test_invalid_object_raises():
    class Dummy(object):
        pass

    viewer.draw(Dummy())


@nt.raises(viewer.NotDrawableError)
def test_invalid_combo_raises():
    viewer.draw(nrn.soma, mode="dendrogram")


def test_writing_output():
    fig_name = "Figure.png"

    tempdir = tempfile.mkdtemp("test_viewer")
    try:
        old_dir = os.getcwd()
        os.chdir(tempdir)
        viewer.draw(nrn, mode="2d", output_path="subdir")
        nt.ok_(os.path.isfile(os.path.join(tempdir, "subdir", fig_name)))
    finally:
        os.chdir(old_dir)
        shutil.rmtree(tempdir)
        common.plt.close("all")
