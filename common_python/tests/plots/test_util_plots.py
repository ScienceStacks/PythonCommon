"""Tests for util_plots."""

from common_python.plots import util_plots
import common_python.constants as cn

import matplotlib.pyplot as plt
import pandas as pd
import unittest

IGNORE_TEST = False
IS_PLOT = False

DF = pd.DataFrame({
  'a': [-1, 0, 1],
  'b': [0, 1, -1],
  'c': [1, -1, 0],
  })


class TestFunction(unittest.TestCase):

  def testPlotTrinaryHeatmap(self):
    # Smoke tests
    if IGNORE_TEST:
      return
    util_plots.plotTrinaryHeatmap(DF, is_plot=IS_PLOT)
    plt.figure()
    ax = plt.gca()
    util_plots.plotTrinaryHeatmap(DF, ax=ax, is_plot=IS_PLOT)

  def testPlotCategoricalHeatmap(self):
    # Smoke tests
    if IGNORE_TEST:
      return
    df = pd.DataFrame({
        'a': [0, 0, 1],
        'b': [0, 1, 0],
        'c': [0, 1, 0],
        })
    df.index = ['x', 'y', 'z']
    opts = {
        cn.PLT_TITLE: "test",
        cn.PLT_XLABLE: "x",
        cn.PLT_YLABLE: "y",
        }
    util_plots.plotCategoricalHeatmap(df, **opts)


if __name__ == '__main__':
  unittest.main()
