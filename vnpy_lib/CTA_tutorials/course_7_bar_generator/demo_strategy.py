from vnpy.app.cta_strategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager
)
from vnpy.trader.object import (
    BarData
)

from vnpy.trader.constant import Interval

from typing import Any


class DemoStrategy(CtaTemplate):
    """"""
    author = "sheepbear"

    fast_window = 10
    slow_window = 20

    fast_ma0 = 0.0
    fast_ma1 = 0.0
    slow_ma0 = 0.0
    slow_ma1 = 0.0

    parameters = [
        "fast_window",
        "slow_window"
    ]
    variables = [
        "fast_ma0",
        "fast_ma1",
        "slow_ma0",
        "slow_ma1"
    ]

    def __init__(
        self,
        cta_engine: Any,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ):

        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar,
                               window=5,
                               on_window_bar=self.on_5_min_bar,
                               interval=Interval.MINUTE)
        self.am = ArrayManager()

    def on_init(self):
        self.write_log("init strategy")
        self.load_bar(10)

    def on_start(self):
        self.write_log("start strategy")

    def on_stop(self):
        self.write_log("stop strategy")

    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)

    def on_5_min_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return
        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]
        self.fast_ma1 = fast_ma[-2]

        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]
        self.slow_ma1 = slow_ma[-2]

        cross_over = (
                self.fast_ma0 >= self.slow_ma0 and
                self.fast_ma1 < self.slow_ma1
        )

        cross_below = (
                self.fast_ma0 <= self.slow_ma0 and
                self.fast_ma1 > self.slow_ma1
        )

        if cross_over:
            price = bar.close_price + 5

            if not self.pos:
                self.buy(price, 1)
            elif self.pos < 0:
                self.cover(price, 1)
                self.buy(price, 1)
        elif cross_below:
            price = bar.close_price - 5

            if not self.pos:
                self.short(price, 1)
            elif self.pos > 0:
                self.sell(price, 1)
                self.short(price, 1)

        # Update UI
        self.put_event()
