# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "scikit-learn",
# ]
# ///

"""scikit-learn — the estimator API: fit/predict, pipelines, and the contract (C1, L2)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="sklearn: estimator API")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # scikit-learn: the estimator API

    Seed notebook (taxonomy C1). Everything in sklearn is one contract:
    `fit(X, y)` learns and returns `self`; learned state lands in
    trailing-underscore attributes; `predict`/`transform` apply it. Pipelines
    compose anything that honors the contract.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/scikit-learn/scikit-learn>
    - In the source: start at
      `sklearn/base.py` (`BaseEstimator`, the mixins).
    - Architecture corpus: the `scikit-learn` study (157 files).
    """)
    return


@app.cell
def _():
    import marimo as mo
    from sklearn.datasets import make_moons
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    return LogisticRegression, StandardScaler, make_moons, make_pipeline, mo


@app.cell
def _(LogisticRegression, StandardScaler, make_moons, make_pipeline):
    features, labels = make_moons(n_samples=200, noise=0.25, random_state=42)
    moon_clf = make_pipeline(StandardScaler(), LogisticRegression())
    moon_clf.fit(features, labels)
    return features, labels, moon_clf


@app.cell
def _(features, labels, mo, moon_clf):
    _lr = moon_clf.named_steps["logisticregression"]
    mo.md(
        f"""
    ## fit, predict, and the trailing underscore

    `fit` returned the pipeline itself and stashed learned state in
    trailing-underscore attributes — that suffix *is* the "I have been
    fitted" convention:

    - `moon_clf.score(X, y)` = **{moon_clf.score(features, labels):.2%}**
    - `lr.coef_` = `{_lr.coef_.round(3).tolist()}` · `lr.intercept_` =
      `{_lr.intercept_.round(3).tolist()}`
    - `predict(X[:5])` = `{moon_clf.predict(features[:5]).tolist()}` vs gold
      `{labels[:5].tolist()}`
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Pipelines and get_params
    """)
    return


@app.cell
def _(mo, moon_clf):
    mo.vstack(
        [
            mo.md(
                "`get_params(deep=True)` exposes every knob through the same"
                " contract — which is what makes `GridSearchCV` and friends"
                " possible without special-casing any estimator:"
            ),
            mo.tree(
                {
                    name: value
                    for name, value in moon_clf.get_params(deep=True).items()
                    if "__" in name
                },
                label="pipeline hyperparameters",
            ),
        ],
        gap=0.5,
    )
    return


if __name__ == "__main__":
    app.run()
