import numpy as np
import pandas as pd

from scipy.sparse import coo_matrix

class ClickModel(object):

    def __init__(
            self,
            data,
            query_col='query',
            result_col='result',
            position_col='position',
            sessions_count='n_sessions',
            events_count='n_clicks',
            history=True,
            strategy='prior'
        ):
        self._init_graph(data, query_col, result_col, position_col, sessions_count, events_count)
        pos_size = len(self.pos_dict)
        qr_size = len(self.qr_dict)
        self._init_parameters(pos_size, qr_size, strategy=strategy)
        self.history = history
        if self.history:
            self.pos_history = []
            self.pos_diff_history = []
            self.qr_history = []
            self.qr_diff_history = []

        self.result_col = result_col
        self.query_col = query_col
        self.position_col = position_col


    def _init_graph(self, data, query_col, result_col, position_col, sessions_count, events_count):
        df = data.copy()
        if 'float' in str(df[result_col].dtype):
            df[result_col] = df[result_col].astype(int)
        df['__qr_pair'] = df.apply(lambda row: str(row[query_col]) + '_' + str(row[result_col]), axis=1)
        pos_list = df[position_col].unique()
        pos_list.sort()
        self.pos_dict = {x:x for x in pos_list}

        qr_list = df['__qr_pair'].unique()
        self.qr_dict = {val:i for i,val in enumerate(qr_list)}
        df['__pos_idx'] = df[position_col].apply(lambda x: self.pos_dict[x])
        df['__qr_idx'] = df['__qr_pair'].apply(lambda x: self.qr_dict[x])
        df['__n_no_clicks'] = df[sessions_count] - df[events_count]
        self.graph = df[['__pos_idx', '__qr_idx', events_count, '__n_no_clicks']].values



    def _init_parameters(self, pos_size, qr_size, strategy):
        if strategy == 'random':
            self.pos = np.random.random(size=(pos_size,))
            self.qr = np.random.random(size=(qr_size,))
        elif isinstance(strategy, float):
            self.pos = np.array([strategy for _ in range(pos_size)])
            self.qr = np.array([.1 for _ in range(qr_size)])
        elif strategy == 'prior':
            pos_idx = self.graph[:, 0]
            qr_idx = self.graph[:, 1]
            n_clicks = self.graph[:, 2]
            nums = np.array(coo_matrix((n_clicks, (qr_idx, pos_idx))).sum(axis=0)).reshape(-1)
            n_no_clicks = self.graph[:, 3]
            denoms = np.array(coo_matrix((n_no_clicks, (qr_idx, pos_idx))).sum(axis=0)).reshape(-1)
            denoms = denoms + nums
            estimate = nums/denoms
            self.pos = estimate * (.99/estimate.max())

            ctrs = n_clicks / (n_clicks+n_no_clicks)
            P_inspect = self.pos[pos_idx]
            P_click = ctrs/P_inspect
            #constrain value between .01 and .99
            P_click = np.where(P_click > .99, .99, P_click)
            P_click = np.where(P_click < .01, .01, P_click)
            weights = n_clicks + n_no_clicks
            nums = np.array(coo_matrix((P_click * weights, (qr_idx, pos_idx))).sum(axis=1)).reshape(-1)
            denoms = np.array(coo_matrix((weights, (qr_idx, pos_idx))).sum(axis=1)).reshape(-1)

            self.qr = nums/denoms
        else:
            self.pos = np.random.random(size=(pos_size,))
            self.qr = np.random.random(size=(qr_size,))



    def _compute_update(self, kind=None):
        #these values are shared in both updates
        qr_idx = self.graph[:, 1]
        alpha = self.qr[qr_idx]
        pos_idx = self.graph[:, 0]
        gamma = self.pos[pos_idx]
        ctr = self.graph[:, 2]
        no_ctr = self.graph[:, 3]
        #these terms appears in both updates
        shared_term = (1 - gamma * alpha)
        denom = ctr + no_ctr
        denom_mat = coo_matrix((denom, (qr_idx, pos_idx)))

        if kind == 'qr' or kind is None:
            #here we compute update to alpha params
            qr_update = (ctr + (no_ctr * (((1 - gamma) * alpha) / shared_term)))
            qr_mat = coo_matrix((qr_update, (qr_idx, pos_idx)))
            qr_vec = qr_mat.sum(axis=1)

            denom_mat = coo_matrix((denom, (qr_idx, pos_idx)))
            qr_denom_vec = denom_mat.sum(axis=1)

            #this vector is the new set of alpha params
            new_qr = np.array(qr_vec / qr_denom_vec).reshape(-1)

            if kind == 'qr':
                return new_qr

        if kind == 'pos' or kind is None:

            #here we compute update to gamma params
            pos_update = (ctr + (no_ctr * (((1 - alpha) * gamma) / shared_term)))
            pos_mat = coo_matrix((pos_update, (qr_idx, pos_idx)))
            pos_vec = pos_mat.sum(axis=0)

            pos_denom_vec = denom_mat.sum(axis=0)

            #this vector is the new set of alpha params
            new_pos = np.array((pos_vec / pos_denom_vec)).reshape(-1)

            if kind == 'pos':
                return new_pos

        #return both if none specified
        return new_pos, new_qr

    def compute_diff(self, v0, v1):
        return np.linalg.norm(v0 - v1)

    def update_pos(self):
        if self.history:
            self.pos_history.append(self.pos.copy())
        new_pos = self._compute_update(kind='pos')
        self.pos = new_pos
        diff_pos = self.compute_diff(self.pos, new_pos)
        if self.history:
            self.pos_diff_history.append(diff_pos)

    def update_qr(self):
        if self.history:
            self.qr_history.append(self.qr.copy())
        new_qr = self._compute_update(kind='qr')
        self.qr = new_qr
        diff_qr = self.compute_diff(self.qr, new_qr)
        if self.history:
            self.qr_diff_history.append(diff_qr)

    def update_both(self):
        if self.history:
            self.pos_history.append(self.pos.copy())
            self.qr_history.append(self.qr.copy())
        new_pos, new_qr = self._compute_update()
        diff_pos = self.compute_diff(self.pos, new_pos)
        diff_qr = self.compute_diff(self.qr, new_qr)
        if self.history:
            self.pos_diff_history.append(diff_pos)
            self.qr_diff_history.append(diff_qr)
        self.pos = new_pos
        self.qr = new_qr


    def do_update(self, alternate=True):
        if alternate:
            self.update_pos()
            self.update_qr()
        else:
            self.update_both()

    def decode_qr_pairs(self, items):
        split = [x.split('_') for x in items]
        terms = ['_'.join(x[:-1]) for x in split]
        results = [x[-1] for x in split]
        return results, terms

    def fit(self, n_iterations=10000, alternate=True):
        for i in range(n_iterations):
            self.do_update(alternate)

        qr_map = {self.qr_dict[key]:key for key in self.qr_dict}
        qr_keys = [qr_map[i] for i in range(len(self.qr))]
        pids, results = self.decode_qr_pairs(qr_keys)
        qr_values = self.qr
        qr_results = pd.DataFrame(columns=[self.result_col, self.query_col, 'attractiveness'])
        qr_results[self.result_col] = pids
        qr_results[self.query_col] = results
        qr_results['attractiveness'] = qr_values

        pos_results = pd.DataFrame(columns=[self.position_col, 'p_examine'])
        pos_results[self.position_col] = list(range(len(self.pos)))
        pos_results['p_examine'] = self.pos

        return qr_results, pos_results
