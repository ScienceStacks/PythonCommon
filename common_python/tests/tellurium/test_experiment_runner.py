from common_python.tellurium import experiment_runner

import lmfit
import numpy as np
import pandas as pd
import unittest


MODEL = """
     A -> B; k1*A
      
     A = 50; 
     B = 0;
     C = 0;
     k1 = 0.15
"""
CONSTANTS = ['k1']
COLUMNS = ['time', 'A', 'B']
#
MODEL = """
     A -> B; k1*A
     B -> C; k2*B
      
     A = 50; 
     B = 0;
     C = 0;
     k1 = 0.15
     k2 = 0.25
"""
CONSTANTS = ['k1', 'k2']
COLUMNS = ['time', 'A', 'B', 'C']
#
MODEL1 = """
     A -> B; k1*A
      
     A = 50; 
     B = 0;
     k1 = 0.15
"""
CONSTANT1S = ['k1']
SIMULATION_TIME = 30
NUM_POINTS = 5
COLUMN1S = ['time', 'A', 'B']


class TestModelRunner(unittest.TestCase):

  def testConstructor(self):
    runner = experiment_runner.ModelRunner(MODEL, CONSTANTS,
        SIMULATION_TIME, NUM_POINTS)
    trues = [c in COLUMNS for c in runner.df_observation.columns]
    assert(all(trues))
    assert(len(runner.df_observation) > 0)
  
  def testGenerateObservations(self):
    runner = experiment_runner.ModelRunner(MODEL, CONSTANTS,
        SIMULATION_TIME, NUM_POINTS)
    df, _ = runner.generateObservations(std=0.1)
    assert(len(set(df.columns).symmetric_difference(
        runner.df_observation.columns)) == 0)
  
  def testResiduals(self):
    runner = experiment_runner.ModelRunner(MODEL, CONSTANTS,
        SIMULATION_TIME, NUM_POINTS)
    runner.df_observation, _ = runner.generateObservations(std=0.1)
    experiment_runner.runner = runner
    parameters = lmfit.Parameters()
    for constant in CONSTANTS:
      parameters.add(constant, value=1, min=0, max=10)
    residuals = experiment_runner.residuals(parameters)
    assert(len(residuals) ==  \
        NUM_POINTS*len(runner.df_observation.columns))
  
  def testFit(self):
    for constants, model in [(CONSTANTS, MODEL), (CONSTANT1S, MODEL1)]:
      runner = experiment_runner.ModelRunner(model, constants,
          SIMULATION_TIME, NUM_POINTS, noise_std=0.0)
      df = runner.fit(count=20)
      assert(len(df.columns) == 2)
      assert(len(df) == len(constants))
  
  def testDfToSer(self):
    data = range(5)
    df = pd.DataFrame({'a': data, 'b': [2*d for d in data]})
    ser = experiment_runner.dfToSer(df)
    assert(len(ser) == len(df.columns)*len(df))


if __name__ == '__main__':
  unittest.main()
