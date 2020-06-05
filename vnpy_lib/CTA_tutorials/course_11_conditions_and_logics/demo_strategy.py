from vnpy.app.cta_strategy import (
    CtaTemplate
)
from vnpy.trader.object import (
    BarData
)

from vnpy.trader.constant import Interval

from typing import Any

from vnpy_lib.CTA_tutorials.course_10_customize_indicator.my_strategy_tool import NewBarGenerator
from vnpy_lib.CTA_tutorials.course_10_customize_indicator.my_strategy_tool import NewArrayManager


class DemoStrategy(CtaTemplate):
    """"""
    author = "sheepbear"

    fast_window = 10
    slow_window = 20

    fast_ma0 = 0.0
    fast_ma1 = 0.0
    slow_ma0 = 0.0
    slow_ma1 = 0.0

    # Course 11 content
    rsi_count = 0

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
        self.bg = NewBarGenerator(self.on_bar,
                                  window=7,
                                  on_window_bar=self.on_7_min_bar,
                                  interval=Interval.MINUTE)
        self.am = NewArrayManager()

    def on_init(self):
        self.write_log("init strategy")
        self.load_bar(10)

    def on_start(self):
        self.write_log("start strategy")

    def on_stop(self):
        self.write_log("stop strategy")

    def on_bar(self, bar: BarData):
        self.bg.update_bar(bar)

    def on_7_min_bar(self, bar: BarData):
        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # Course 11 content
        # indicator condition and logic
        fast_rsi = am.rsi(self.fast_window, array=True)
        slow_rsi = am.rsi(self.slow_window, array=True)

        fast_rsi_0 = fast_rsi[-1]
        slow_rsi_0 = slow_rsi[-1]

        # Example: greater than or smaller than
        if fast_rsi_0 > 70:
            print("over bought")
        elif fast_rsi_0 < 30:
            print("over sold")

        # Example: cross over/below
        fast_rsi_1 = fast_rsi[-2]
        slow_rsi_1 = fast_rsi[-2]

        rsi_cross_over = (
                fast_rsi_1 < slow_rsi_1 and
                fast_rsi_0 >= slow_rsi_0
        )

        rsi_cross_below = (
                fast_rsi_1 > slow_rsi_1 and
                fast_rsi_0 <= slow_rsi_0
        )

        if rsi_cross_over:
            print("we buy")
        elif rsi_cross_below:
            print("we sell")

        # Example: count
        if fast_rsi_0 > slow_rsi_0:
            self.rsi_count += 1
        else:
            self.rsi_count = 0

        if self.rsi_count >= 3:
            print("very strong up trend, we buy")

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
