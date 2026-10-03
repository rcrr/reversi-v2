# Design principles

The house design policy, cross-cutting: it binds any new code in the pipeline, not one module.

- Dual scalar/array API: public functions accept a scalar OR a 1-D array and return the input kind. Not a style choice —
  it follows the numpy design, which the solution's performance is built on.
- Pydantic: `@validate_call` on public functions, when the function is public, has no specific performance problem, and
  has no convoluted backstory (the state-machine Context is the standing exception).
- Numba: when performance is the goal and the benefit is proven, hot loops run as `njit(cache=True)` kernels — the best
  performance is the objective. The kernel is always embedded in a normal Python function, scalar or vectorized: the
  kernel never leaks into the API.
