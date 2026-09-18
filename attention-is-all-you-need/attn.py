# import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

class SingleHeadAttn(nn.Module):
  def __init__(self, d):
    super().__init__()
    # assume sequence length is n, model dimension is d
    # x: (n, d)
    self.d = d
    self.Wq = nn.Linear(d, d)
    self.Wk = nn.Linear(d, d)
    self.Wv = nn.Linear(d, d)
  
  def forward(self, X):
    Q = self.Wq(X) # (n ,d)
    K = self.Wk(X) # (n ,d)
    V = self.Wv(X) # (n, d)
    # Q @ K.T => (n, n)
    # F.softmax(Q @ K.T / math.sqrt(self.d), dim=-1) => (n, n)
    return F.softmax(Q @ K.T / math.sqrt(self.d), dim=-1) @ V

class Encoder(nn.Module):
  def __init__(self, d):
    super().__init__()
    self.singleHeadAttn = SingleHeadAttn(d)
    self.norm1 = nn.LayerNorm(d)
    self.norm2 = nn.LayerNorm(d)
    self.feedForward = nn.Sequential(
      nn.Linear(d, 4 * d),
      nn.ReLU(),
      nn.Linear(4 * d, d)
    )
        
  def forward(self, X):
    attnOut = self.singleHeadAttn(X)
    X = self.norm1(X + attnOut)
    FFOut = self.feedForward(X)
    X = self.norm2(X + FFOut)
    return X
