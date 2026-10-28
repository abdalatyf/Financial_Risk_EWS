"""
Financial Risk EWS - Compatibility Wrapper.
Delegates execution to the production Quantitative Risk Analytics Engine in src/analytics/06_calculate_risk_metrics.py.
"""
import os
import sys
import importlib.util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
analytics_script = os.path.join(BASE_DIR, "src", "analytics", "06_calculate_risk_metrics.py")

spec = importlib.util.spec_from_file_location("risk_analytics_engine", analytics_script)
module = importlib.util.module_from_spec(spec)
sys.modules["risk_analytics_engine"] = module
spec.loader.exec_module(module)

if __name__ == "__main__":
    calculator = module.RiskMetricsCalculator()
    calculator.run()
