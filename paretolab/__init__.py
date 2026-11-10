"""Exact finite biobjective planning evidence."""
def analyze(p):
 from .engine import analyze as f
 return f(p)
def verify(r):
 from .certificate import verify as f
 return f(r)
