"""
Created on 2018/11/20
@author: yby
@desc    : 2018-11-20
contact author:ybychem@gmail.com
"""


import pandas as pd
import logging
from tasks.backend.orm import build_primary_key
from datetime import date, datetime, timedelta
from tasks.utils.fh_utils import try_2_date, STR_FORMAT_DATE, datetime_2_str, split_chunk, try_n_times
from tasks import app
from sqlalchemy.types import String, Date, Integer,Text
from sqlalchemy.dialects.mysql import DOUBLE,TINYINT
from tasks.backend import engine_md
from tasks.merge.code_mapping import update_from_info_table
from tasks.utils.db_utils import with_db_session, add_col_2_table, alter_table_2_myisam, \
    bunch_insert_on_duplicate_update
from tasks.tushare.ts_pro_api import pro

DEBUG = False
logger = logging.getLogger()
DATE_BASE = datetime.strptime('2005-01-01', STR_FORMAT_DATE).date()
ONE_DAY = timedelta(days=1)
# 标示每天几点以后下载当日行情数据
BASE_LINE_HOUR = 16
STR_FORMAT_DATE_TS = '%Y%m%d'

INDICATOR_PARAM_LIST_TUSHARE_FUTURE_TRADE_CAL = [
    ('exchange', String(20)),
    ('cal_date', Date),
    ('is_open', TINYINT),
    ('pretrade_date', Date),
]
# 设置 dtype
DTYPE_TUSHARE_FUTURE_TRADE_CAL = {key: val for key, val in INDICATOR_PARAM_LIST_TUSHARE_FUTURE_TRADE_CAL}

@app.task
def import_future_trade_cal(chain_param=None):
    """
    插入股票日线数据到最近一个工作日-1。
    如果超过 BASE_LINE_HOUR 时间，则获取当日的数据
    :return:
    """
    table_name = 'tushare_future_trade_cal'
    logging.info("更新 %s 开始", table_name)

    has_table = engine_md.has_table(table_name)


    try:
        data_df = pro.trade_cal(exchange='DCE')
        if len(data_df) > 0:
            data_count = bunch_insert_on_duplicate_update(data_df, table_name, engine_md, DTYPE_TUSHARE_FUTURE_TRADE_CAL,myisam_if_create_table=True)
            logging.info("更新期货交易日历数据结束， %d 条信息被更新",  data_count)
        else:
            logging.info("无数据信息可被更新")
    finally:

            logger.info('%s 表 数据更新完成', table_name)


if __name__ == "__main__":
    # DEBUG = True
    import_future_trade_cal()

