'''Constructs features for a binary classifier.'''

"""
BinaryFeatureClassifierOptimizer selects a
set of features that optimize a binary classifier.
The software constraints of the optimization are:
  Minimize the number of features
  The features selected result in a classifier
      that only have a a small degradation in accuracy
      compared with using all features (see max_degrade)
The hard constraints are:
  Maximum number of features considered (see max_iter)
  Minimum increase in accuracy when including the
      feature (see min_incr_score)

The algorithm operates in two phases.
1. Forward selection. Choose features that increase
   the classification score up to a small difference
   from the score achieved using all features
   (best score).
   The parameters are:
     min_incr_score (minimum increase in score achieved
         by each feature)
     max_degrade (degradation from best score)
     max_iterations (maximum number of features
         considered)
2. Backwards elimination. Drop those features that
   don't significantly impact the score.
   The parameters are:
     min_incr_score (maximum amount by which the
         score can decrease if a feature is eliminated)
"""

from common_python.classifier import util_classifier
from common_python.classifier.feature_collection  \
    import FeatureCollection
import common_python.constants as cn

import copy
import numpy as np
import pandas as pd
import random


# Default checkpoint callback
CHECKPOINT_CB = lambda : None
CHECKPOINT_INTERVAL = 5
BINARY_CLASSES = [cn.NCLASS, cn.PCLASS]
MAX_ITER = 100
MAX_BACKWARD_ITER = MAX_ITER  # Max
MIN_INCR_SCORE = 0.01
MAX_DEGRADE = 0.05


class BinaryClassifierFeatureOptimizer(object):
  """
  Does feature selection for binary classes.
  Exposes the following instance variables
    1. score - score achieved for features
    2  best_score
    3. features selected for classifier
    4. is_done - completed processing
  This is a computationally intensive activity and so
  the implementation allows for restarts.
  """

  def __init__(self, df_X, ser_y, base_clf,
      checkpoint_cb=CHECKPOINT_CB,
      feature_collection=None,
      min_incr_score=MIN_INCR_SCORE,
      max_iter=MAX_ITER, 
      max_degrade=MAX_DEGRADE,
      ):
    """
    :param pd.DataFrame df_X:
        columns: features
        index: instances
    :param pd.Series ser_y:
        index: instances
        values: binary class values (0, 1)
    :param Classifier base_clf:
        Exposes: fit, score, predict
    :param FeatureCollection feature_collection:
    :param float min_incr_score: min amount by which
        a feature must increase the score to be included
    :param int max_iter: maximum number of iterations
    :param float max_degrade: maximum difference between
        best score and actual
    """
    if len(ser_y.unique()) != 2:
      raise ValueError("Must have two classes.")
    ########### PRIVATE ##########
    self._checkpoint_cb = checkpoint_cb
    self._base_clf = copy.deepcopy(base_clf)
    self._df_X = df_X
    self._iteration = -1  # Counts feature evaluations
    self._ser_y = ser_y
    if feature_collection is None:
      feature_collection = FeatureCollection(
          self._df_X, self._ser_y)
    self._collection = feature_collection
    self._min_incr_score = min_incr_score
    self._max_iter = max_iter
    self._max_degrade = max_degrade
    self._test_idxs = self._makeTestIndices()
    ########### PUBLIC ##########
    # Score with all features
    self.best_score = util_classifier.scoreFeatures(
        self._base_clf, self._df_X, self._ser_y,
        test_idxs=self._test_idxs)
    # Score achieved for features in collection
    self.score = 0
    # Collection of features found
    self.features = []
    # Flag to indicate completed processing
    self.is_done = False

  def _updateIteration(self):
    if self._iteration % CHECKPOINT_INTERVAL == 0:
      self._checkpoint_cb()  #  Save state
    self._iteration += 1

  def _makeTestIndices(self):
    """
    Constructs the test indices so that positive
    and negative classes are equally represented.
    :return list-object:
    Notes
      1. Assumes that number of PCLASS < NCLASS
    """
    pclass_idxs = self._ser_y[
        self._ser_y==cn.PCLASS].index
    nclass_idxs = self._ser_y[
        self._ser_y==cn.NCLASS].index
    # Sample w/o replacement from the larger set
    if len(pclass_idxs) < len(nclass_idxs):
      length = len(pclass_idxs)
      test_idxs = pclass_idxs.tolist()
      sample_idxs = nclass_idxs.tolist()
    else:
      length = len(nclass_idxs)
      test_idxs = nclass_idxs.tolist()
      sample_idxs = pclass_idxs.tolist()
    sample_idxs = random.sample(sample_idxs, length)
    test_idxs.extend(sample_idxs)
    return test_idxs

  def run(self):
    """
    Construct the features, handling restarts by saving
    state and checkpointing.
    Result is in self.features.
    """
    # Forward selection of features
    for _ in range(len(self._collection.getCandidates())):
      self._updateIteration()
      if self._iteration >= self._max_iter:
        break  # Reached maximum number of iterations
      if not self._collection.add():
        break  # No more features to add
      new_score = util_classifier.scoreFeatures(
          self._base_clf, self._df_X, self._ser_y,
          features=self._collection.chosens,
          test_idxs=self._test_idxs)
      import pdb; pdb.set_trace()
      if new_score - self.score > self._min_incr_score:
          # Feature is acceptable
          self.score = new_score
      else:
        # Remove the feature
        self._collection.remove(cls)
      # See if close enough to best possible score
      if self.best_score - self.score  \
          < self._max_degrade:
        break
    # Backwards elimination to delete unneeded feaures
    # Eliminate features that do not affect accuracy
    for _ in range(MAX_BACKWARD_ITER):
      is_done = True
      self._updateIteration()
      for feature in self._collection.chosens:
        # Temporarily delete the feature
        self._collection.remove(feature=feature)
        new_score = util_classifier.scoreFeatures(
            self._base_clf, self._df_X, self._ser_y,
            features=self._collection.chosens,
            test_idxs=self._test_idxs)
        if self.score - new_score > self._min_incr_score:
          # Restore the feature
          self._collection.add(cls, feature=feature)
        else:
          # Permanently delete the feature
          self.score = new_score
          is_done = False
      if is_done:
        break
    #
    self.features = list(self._collection.chosens)
    self._checkpoint_cb()
    is_done = True
