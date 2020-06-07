from datetime import time

from vnpy.app.cta_strategy.strategies.dual_thrust_strategy import DualThrustStrategy


class MyDualThrustStrategy(DualThrustStrategy):
    """"""

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        """"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.exit_time = time(hour=15, minute=55)
