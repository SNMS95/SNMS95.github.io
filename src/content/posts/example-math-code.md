---
title: "Sample post: math, code and footnotes"
date: 2026-11-10
summary: "Only here to check that math, code highlighting and footnotes render. Draft, never published."
tags: ["meta"]
draft: true
---

This draft exists only to test rendering. It is excluded from the build while `draft: true`.

## Math

Inline math such as $\nabla_\lambda \mathcal{L}_{\text{val}}$ sits in the text, and display math gets its own line. For a hyperparameter $\lambda$ and trained weights $w^\ast(\lambda)$, the implicit function theorem gives the hypergradient

$$
\frac{d\mathcal{L}_{\text{val}}}{d\lambda}
= \frac{\partial \mathcal{L}_{\text{val}}}{\partial \lambda}
- \frac{\partial \mathcal{L}_{\text{val}}}{\partial w}
\left(\frac{\partial^2 \mathcal{L}_{\text{train}}}{\partial w^2}\right)^{-1}
\frac{\partial^2 \mathcal{L}_{\text{train}}}{\partial w\,\partial \lambda}
\Big|_{w = w^\ast(\lambda)}.
$$

## Code

```python
import jax
import jax.numpy as jnp


def loss(w, lam):
    return jnp.sum((w - lam) ** 2) + 0.1 * jnp.sum(w**4)


grad_w = jax.grad(loss, argnums=0)
hess_w = jax.hessian(loss, argnums=0)
```

Inline code like `jax.hessian` uses the mono face.

## Footnotes and tables

A claim that needs a side note.[^1]

| Quantity | Symbol |
| --- | --- |
| Weights | $w$ |
| Hyperparameters | $\lambda$ |

[^1]: Footnotes render at the bottom of the post.
