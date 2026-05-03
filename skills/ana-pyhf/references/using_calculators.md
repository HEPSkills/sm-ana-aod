# Using Calculators

Source: https://pyhf.readthedocs.io/en/v0.7.6/examples/notebooks/learn/UsingCalculators.html

## Overview

pyhf provides two low-level calculator classes that underpin `hypotest`. Use them directly when you need access to intermediate distributions or custom workflows.

## Calculator Types

| | `AsymptoticCalculator` | `ToyCalculator` |
|---|---|---|
| Approach | Analytical (Asimov dataset) | Empirical (sampled toys) |
| Speed | Fast (single fit) | Slow (one fit per toy) |
| Accuracy | Asymptotic limit | Controlled by `ntoys` |

## Creating Calculators

```python
import pyhf

model = pyhf.simplemodels.uncorrelated_background([6], [9], [3])
data  = [9] + model.config.auxdata

# Asymptotics
asymp_calc = pyhf.infer.calculators.AsymptoticCalculator(
    data, model, test_stat="qtilde"
)

# Toy-based
toy_calc = pyhf.infer.calculators.ToyCalculator(
    data, model, test_stat="qtilde", ntoys=500
)
```

## Unified Calculator API

All calculators share the same interface:

```python
poi_test = 1.0

# Observed test statistic
q_obs = asymp_calc.teststatistic(poi_test)

# Distributions under s+b and b-only hypotheses
sb_dist, b_dist = asymp_calc.distributions(poi_test)

# p-values: CL_{s+b}, CL_b, CL_s
p_sb, p_b, p_s = asymp_calc.pvalues(q_obs, sb_dist, b_dist)
print(f"CLs = {p_s}")

# Expected p-values at ±2σ (5 values each)
exp_p_sb, exp_p_b, exp_p_s = asymp_calc.expected_pvalues(sb_dist, b_dist)
```

## Factory Function

```python
calc = pyhf.infer.utils.create_calculator(
    "asymptotics",   # or "toybased"
    data, model,
    test_stat="qtilde",
    ntoys=1000,      # only for toybased
)
```

## Key Points

- `distributions(poi)` returns `(sb_dist, b_dist)` — distribution objects with `.p_value(stat)` method
- `pvalues` returns `(p_{s+b}, p_b, CLs)` — CLs = p_{s+b} / p_b
- `expected_pvalues` returns 3-tuple of 5-element lists: [−2σ, −1σ, median, +1σ, +2σ] for each
- For most use cases, prefer `pyhf.infer.hypotest(..., calctype="asymptotics"|"toybased")`
- Calculators are useful when you need the intermediate distribution objects (e.g., for plotting)
