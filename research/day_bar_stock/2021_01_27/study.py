import pandas as pd
import logging
import time
import datetime as dt
import multiprocessing
import itertools
import os
import collections
import numpy as np
os.environ['NUMEXPR_MAX_THREADS'] = '12'
os.environ['NUMEXPR_NUM_THREADS'] = '12'


def create_logger():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _logger = logging.getLogger("study")
    current_time = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    log_file_name = 'study_{}.log'.format(current_time)
    handler = logging.FileHandler(log_file_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


logger = create_logger()


# 对于一组参数, 跑策略并且返回一组结果
def run_strategy_for_one_param_set(
        symbol_frame_dict,
        symbol_list,
        param
):
    logger.info("Start strategy run for param set:")
    logger.info(param)
    _start_time = time.time()
    # 创建一个list用于记录计算出的所有股票的buy signal data frame
    buy_signal_list = []
    for symbol in symbol_list:
        # 首先从内存中取出数据
        data = symbol_frame_dict[symbol]

        # 下面计算一些指标
        close = data.loc[:, "adj_close"]
        adj_close_change = (close - close.shift(1)) / close.shift(1)
        close_change_m_days_max = close.shift(1).rolling(param["m"]).max()
        close_change_m_days_max_percent = (close_change_m_days_max - close) / close

        close_change_m_days_min = close.shift(1).rolling(param["m"]).min()
        close_change_m_days_min_percent = (close_change_m_days_min - close) / close

        previous_high = close.shift(1).rolling(param["m"] + param["n"]).max()
        previous_high_percent = (previous_high - close) / close

        close_greater_than_min_price = (close > param["min_price"]) * 1

        # 根据指标计算买入信号.
        buy_signal = (
                (close_change_m_days_max_percent < param["float_factor"])
                & (close_change_m_days_min_percent > -param["float_factor"])
                & (previous_high_percent > param["high_factor"])
                & (close_greater_than_min_price == 1)
                & (close > close_change_m_days_max)
        )

        # 计算未来多少天的收益值
        next_7_days_avg_close_change = adj_close_change.rolling(7).mean().shift(-7)
        next_14_days_avg_close_change = adj_close_change.rolling(14).mean().shift(-14)
        next_21_days_avg_close_change = adj_close_change.rolling(21).mean().shift(-21)
        next_28_days_avg_close_change = adj_close_change.rolling(28).mean().shift(-28)

        # 构建buy signal dataframe
        buy_sig_index = buy_signal[buy_signal == True].index
        buy_signal_frame = pd.concat([
            data.loc[buy_sig_index],
            next_7_days_avg_close_change.loc[buy_sig_index].rename("next_7_days_avg_close_change"),
            next_14_days_avg_close_change.loc[buy_sig_index].rename("next_14_days_avg_close_change"),
            next_21_days_avg_close_change.loc[buy_sig_index].rename("next_21_days_avg_close_change"),
            next_28_days_avg_close_change.loc[buy_sig_index].rename("next_28_days_avg_close_change")],
            axis=1
        )

        # 把当前symbol的buy signal list存储在 buy signal中
        buy_signal_list.append(buy_signal_frame)

    # 把所有symbol的buy signal frame合成为一个summary buy signal frame
    buy_signal_summary_frame = pd.concat(buy_signal_list)

    # 接下来开始构筑一个返回策略结果的dictionary,这里使用collection里的list defaultdict, 图方便
    result_dict = collections.defaultdict(list)

    # 首先把param值存进去
    for key, value in param.items():
        result_dict[key].append(value)

    # 再储存buy signal总数量以及未来多少天的平均收益
    describe_frame = buy_signal_summary_frame.describe()
    result_dict["buy_signal_number"].append(len(buy_signal_summary_frame))
    result_dict["next_7_days_avg_close_change_avg"].append(
        describe_frame.loc["mean", "next_7_days_avg_close_change"])
    result_dict["next_14_days_avg_close_change_avg"].append(
        describe_frame.loc["mean", "next_14_days_avg_close_change"])
    result_dict["next_21_days_avg_close_change_avg"].append(
        describe_frame.loc["mean", "next_21_days_avg_close_change"])
    result_dict["next_28_days_avg_close_change_avg"].append(
        describe_frame.loc["mean", "next_28_days_avg_close_change"])

    # 记录用时
    _end_time = time.time()
    logger.info("strategy run finished using time {:.2f}".format(_end_time - _start_time))
    return result_dict


if __name__ == "__main__":

    start_time = time.time()
    logger.info("Start reading data.")
    stock_data_store = pd.HDFStore(r'E:\project\trade_engine\data_processing\quandl_data_processor\stock_day.h5')

    # 取出所有volume>3000000的股票的symbol组成一个list
    _symbol_list = pd.read_csv(
        r"E:\project\trade_engine\data_processing\quandl_data_processor\filter_stock_symbols.csv").loc[
                  :, "symbols"].tolist()

    # 用一个字典来把所有股票数据全部读到内存中去.
    _symbol_frame_dict = {}
    for _symbol in _symbol_list:
        # 从hdf中把数据读进内存中
        symbol_frame = stock_data_store.select('day', where=['symbol=="{}"'.format(_symbol)])
        # 我们只研究2000年后的股票数据, 之前的就不要了
        symbol_frame = symbol_frame[symbol_frame.index > dt.datetime(2000, 1, 1)]
        # 把数据缓存到一个字典中, symbol作为key
        _symbol_frame_dict[_symbol] = symbol_frame

    logger.info("Finished reading data.")
    end_time = time.time()
    logger.info("Reading data using time {:.2f}".format(end_time - start_time))
    # 首先要定义一个param list
    param_name_list = ["m", "n", "min_price", "float_factor", "high_factor"]

    # 在此定义策略中的所有参数取值范围, 用list数据结构
    param_value_selections = [
        np.arange(5, 50, 5),
        np.arange(5, 100, 5),
        [5],
        [0.05, 0.08, 0.11],
        [0.2, 0.4, 0.6, 0.8]
    ]

    # 创建多进程
    pool = multiprocessing.Pool(12)

    # 创建一个储存各个进程结果的list
    pool_result_list = []

    # 循环所有的参数可能的组合
    for param_values in itertools.product(*param_value_selections):
        # 把当前所有params的取值放在一个字典中
        _param = {}
        for index, param_name in enumerate(param_name_list):
            _param[param_name] = param_values[index]

        # 单次进程需要计算一组参数的结果, 返回值是一个多进程的特殊对象, 把它存在一个list中
        pool_result_list.append(
            pool.apply_async(
                run_strategy_for_one_param_set, args=(
                    _symbol_frame_dict,
                    _symbol_list,
                    _param)
            )
        )

    # 把所有策略结果的dict组合成一个dataframe
    opt_summary_frame = pd.DataFrame()
    for pool_result in pool_result_list:
        # pool_result.get得到的是那个进程return的字典
        opt_summary_frame = pd.concat([opt_summary_frame, pd.DataFrame(pool_result.get())])
    pool.close()
    pool.join()
    opt_summary_frame.to_csv("optimization_summary_1.csv", index=False)
