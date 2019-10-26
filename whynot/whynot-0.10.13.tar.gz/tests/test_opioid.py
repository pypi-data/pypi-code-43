"""Unit tests for opioid epidemic simulator."""
import whynot as wn


def test_config():
    """Ensure intervention update works as expected."""
    intervention = wn.opioid.Intervention(year=2021, nonmedical_incidence=-.12)
    config = wn.opioid.Config()
    assert config.nonmedical_incidence.intervention_val == 0.
    config = config.update(intervention)
    assert config.nonmedical_incidence.intervention_val == -.12
