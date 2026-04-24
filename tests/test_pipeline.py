import pandas as pd

from clinical_qc.pipeline import run_pipeline


def test_pipeline_runs():
    df = pd.DataFrame({
        "age": [10, 20, None],
        "sex": ["M", "F", "X"]
    })

    result = run_pipeline(df)

    assert result.n_rows == 3
    assert isinstance(result.issues, list)
    
def test_pipeline_detects_missing():
    df = pd.DataFrame({
        "age": [10, None, None],
    })

    result = run_pipeline(df)

    issues_df = result.issues_table()

    assert len(issues_df) > 0
def test_pipeline_with_config():
    from clinical_qc.config import QCConfig, RangeRule

    df = pd.DataFrame({
        "age": [-5, 200],
    })

    config = QCConfig(
        value_ranges={"age": RangeRule(min=0, max=120)}
    )

    result = run_pipeline(df, config)

    issues_df = result.issues_table()

    assert len(issues_df) > 0