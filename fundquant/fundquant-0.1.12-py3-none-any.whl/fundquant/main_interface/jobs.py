from fundquant.data_get.jsl_data import JslEtf
from fundquant.data_get.lixinren_data import persist_all_data_hand


def do_job(n_days=7):
    JslEtf().persist_all_data()
    # XqIndexData().persist_all_data(n_days)


def persist_lxr_data_hand(cookie):
    persist_all_data_hand(cookie)


if __name__ == '__main__':
    do_job()
