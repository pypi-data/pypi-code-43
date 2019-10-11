from grc1_toolbox.update_check import updateCheck
from grc1_toolbox.Problem1DataSource import Problem1DataSource
import pandas as pd
import numpy as np

class GRCSubmission():
    def __init__(self, problem1):
        if updateCheck():
            raise ValueError("Your competition package is not updated please update it using 'pip install -U auquan_grc1_toolbox'")
        self.ds= Problem1DataSource("https://qq-15-data.s3.eu-west-2.amazonaws.com", problem1.dataset)
        self.data = self.ds.readData()
        self.lookback = problem1.lookback
        self.updateFrequency = problem1.updateFrequency
        self.skip = problem1.skip
        self.problem_class = problem1
        self.metrics = None


    def preprocess(self, data, remove_y = False):
        X = data.copy()

        X['NAs'] = X.isnull().sum(axis=1)
        X = X.replace([np.inf, -np.inf], np.nan)
        X.fillna(-50, inplace=True)

        if remove_y:
            del X['Y']

        X = X.drop(['TRR', 'ERR', 'Date' , 'AssetGroup','F2', 'F12', 'F15', 'F17', 'F19', 'Q12', 'Q3', 'Q2', 'Q7', 'Q6','Q10','Q9','q'], axis=1)

        return X

    def getReward(self, port_returns, port_volatility, sharpe_ratio, asset_weights, reward_list, turnover_list, duration_list,
                  spread_list,
                  wt, wt_1, ri, l, k):
        if (ri is None) or (wt is None):
            port_returns.append(0)
            sharpe_ratio.append(0)
            port_volatility.append(0)
            reward = 0
        else:
            ri.fillna(0, inplace=True)
            returns = np.dot(wt, ri)
            port_returns.append(returns)
            downside_returns = [x for x in port_returns if x < 0]
            volatility = np.std(downside_returns)  # np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
            sharpe = np.sqrt(12) * np.mean(port_returns) / volatility if volatility != 0 else 0
            sharpe_ratio.append(sharpe)
            port_volatility.append(volatility)
            if (wt_1 is None):
                phi = 0
            else:
                ix = wt.index | wt_1.index
                tn = wt.reindex(ix) - wt_1.reindex(ix)
                tn[tn.isnull() & tn.index.isin(wt.index)] = wt
                tn[tn.isnull() & tn.index.isin(wt_1.index)] = -wt_1
                phi = k * tn.abs().sum()
            reward = returns - l * volatility - phi
        #         print('returns, volatility, phi, sharpe, reward')
        #         print(returns, volatility, phi, sharpe, reward)
        return reward

    def checkFinalConstraints(self, Idx_R, Idx_Vol, Idx_VolD, Port_R, Port_Vol, Port_VolD):
        violated = False
        if Port_R < Idx_R:
            # print("Total Return Constraint Violated: Total Return is less than Index Return")
            violated = True
        if Port_Vol > Idx_Vol:
            # print("Volatility Constraint Violated: Vol is higher than Index Vol")
            violated = True
        if Port_VolD > Idx_VolD:
            # print("Downside Volatility Constraint Violated: Vol is higher than Index Vol")
            violated = True
        if Port_R / Port_Vol < Idx_R / Idx_Vol:
            # print("Sharpe Ratio Constraint Violated: SR is less than Index SR")
            violated = True
        if Port_R / (np.sqrt(12) * Port_VolD) < Idx_R / (np.sqrt(12) * Idx_VolD):
            # print("SDRSR Constraint Violated: SR is less than Index SR")
            violated = True

        return violated

    def checkConstraints(self, port_returns, port_volatility, sharpe_ratio, asset_weights, reward_list, turnover_list,
                         duration_list, spread_list,
                         wt, wt_1, wi, Dt, St, Qt, g, U, t, T, P, delta, chi, eta):
        violated = False
        tol = 0.009
        if np.abs(wt.sum() - 1) > tol:
            print(wt.sum())
            print("Fully Invested Constraint Violated: Sum of weights is not 1")
            violated = True
        div_constraint = np.maximum(g, 1 / float(Qt.sum()))
        if (wt.abs() - div_constraint > tol).any():
            print(wt[(wt.abs() - div_constraint > tol)])
            print("Diversification Constraint Violated: All weights are not less than parameter %.2f" % div_constraint)
            violated = True
        if wt_1 is None:
            turnover = 0
        else:
            ix = wt.index | wt_1.index
            tn = wt.reindex(ix) - wt_1.reindex(ix)
            tn[tn.isnull() & tn.index.isin(wt.index)] = wt
            tn[tn.isnull() & tn.index.isin(wt_1.index)] = -wt_1
            turnover = (tn).abs().sum() / 2
        turnover_list.append(turnover)
        print('turnover: ', turnover)
        if (np.sum(turnover_list[-12:]) > U):
            print("%0.2f Turnover Constraint Violated: Turnover Limit exceeded" % np.sum(turnover_list[-12:]))
            violated = True
        if (wt < t).any():
            print("Shortsell Constraint Violated: all weights are not greater than parameter t")
            print(wt[wt < t])
            violated = True
        if wt[wt < 0].sum() < T:
            print("Max Shortsell Constraint Violated: sum of all weights are not greater than parameter T")
            violated = True
        if wt[wt != 0].count() < np.minimum(P, len(wt)):
            print(
                "Min number of positions Constraint Violated: count of all weights <>0 %i are not greater than parameter P%i" % (
                wt[wt != 0].count(), np.minimum(P, len(wt))))
            violated = True
        if ((wt * Dt).sum() / (wi * Dt).sum() - 1) - delta > tol:
            print("Duration Constraint Violated: wt*Dt/ wi*Dt %.2f is greater than parameter delta" % (
                        (wt * Dt).sum() / (wi * Dt).sum()))
            violated = True
        if ((wt * St).sum() / (wi * St).sum() - 1) - chi > tol:
            print("Spread Constraint Violated: wt*St/ wi*St %.2f is greater than parameter chi" % (
                        (wt * St).sum() / (wi * St).sum()))
            violated = True
        if (wt * (1 - Qt)).abs().sum() > tol:
            print("Qualification Constraint Violated: wt*(1-qt) is not zero %.2f" % (wt * (1 - Qt)).abs().sum())
            violated = True
        #     if returns - Rlow/ volatility <= np.sqrt(1-eta):
        #         print("Max Risk probability Constraint Violated: returns - Rlow/ volatility <= np.sqrt(1-eta)")

        return violated

    def startTrading(self):

        penalty = 0.5
        port_returns = []
        port_volatility = []
        sharpe_ratio = []
        asset_weights = []
        reward_list = []
        turnover_list = []
        duration_list = []
        spread_list = []
        idx_duration_list = []
        idx_spread_list = []
        idx_returns = []
        costs = []

        ri = None

        # empty dict to store values by date
        dict_metrics_by_date = {}

        ### Evaluator to getweights at everytime t and calcuate reward + check if constraints are met

        ## specifying all the constants
        START = self.skip
        counter = START
        l = 0.3
        k = 0.3
        g = 0.04  # percent of portfolio contraint
        U = 2.5  #
        t = 0
        T = 0
        P = 40
        delta = 0.05
        chi = 0.05
        eta = 0.95

        wi = None

        dates = self.data['Date'].unique()
        for i in range(self.skip, len(dates)):
            counter = i
            date= dates[i]
            if(i%self.updateFrequency ==0 or i == self.skip):
                train_data = self.data[self.data['Date']<dates[i]]
                train_data = self.preprocess(train_data)
                self.problem_class.trainModel(train_data)

            temp = date + '-' + self.data.loc[self.data.Date == date, 'Identifier']

            date_data = self.data[self.data.index.isin(temp)]
            date_data.set_index(date_data['Identifier'], inplace=True)
            date_data = date_data[~date_data.index.duplicated()]
            cusips = date_data['Identifier']

            ## old weights
            wt_1 = asset_weights[-1] if len(asset_weights) > 0 else None
            wt_2 = asset_weights[-2] if len(asset_weights) > 1 else None

            ##old index weights
            wi_t_1 = None if wi is None else wi.copy()


            ## calculate reward at start of time t from weights allocated at time t-1
            reward = self.getReward(port_returns, port_volatility, sharpe_ratio, asset_weights, reward_list, turnover_list,
                               duration_list, spread_list, wt_1, wt_2, ri, l, k)

            if ri is None or wi_t_1 is None:
                idx_returns.append(0)
            else:
                idx_returns.append(np.dot(wi_t_1, ri))

            # load specific feature info for time t
            wi = pd.Series(date_data['wI'] / 100, index=date_data['Identifier'])
            Dt = pd.Series(date_data['d'], index=date_data['Identifier'])
            St = pd.Series(date_data['S'], index=date_data['Identifier'])
            qt = pd.Series(date_data['q'], index=date_data['Identifier'])

            ## get new weights
            old_turnover = np.minimum(0.9 * U, np.sum(turnover_list[-11:]) if len(turnover_list) > 10 else 0.9 * U)

            constraint_args={}
            constraint_args['diversification'] = g
            constraint_args['turnover'] = U
            constraint_args['short_position'] = t
            constraint_args['short_portfolio'] = T
            constraint_args['positions'] = P
            constraint_args['duration'] = delta
            constraint_args['spread'] = chi
            constraint_args['return'] = eta

            allowed = qt[qt == 1].index
            qt1 = qt.loc[allowed].copy()
            cusips1 = cusips.loc[allowed].copy()
            wi_arg = wi.loc[allowed].copy()
            Dt_arg = Dt.loc[allowed].copy()
            St_arg = St.loc[allowed].copy()
            date_data_arg = date_data[date_data.Identifier.isin(allowed)].copy()
            wt, cost = self.problem_class.getWeights(penalty, cusips1, wi_arg, Dt_arg, St_arg, qt1, constraint_args, \
                                                     self.preprocess(date_data_arg, remove_y=True), ri, wt_1,
                                                     old_turnover)

            wt_final = pd.Series(np.zeros(len(qt)), index = qt.index)
            wt_final[wt_final.index.isin(wt.index)] = pd.Series(wt.values, index=wt.index)
            wt_final[~wt_final.index.isin(wt.index)] = 0
            wt = wt_final


            if counter == START:
                wt[qt == 1] = 1 / float(len(allowed))
                wt[qt == 0] = 0
            asset_weights.append(wt)
            reward_list.append(reward)
            costs.append(cost)
            duration_list.append(np.dot(wt, Dt))
            spread_list.append(np.dot(wt, St))
            idx_duration_list.append(np.dot(wi, Dt))
            idx_spread_list.append(np.dot(wi, St))
            ## verify if all constraints are met
            self.checkConstraints(port_returns, port_volatility, sharpe_ratio, asset_weights, reward_list, turnover_list,
                                duration_list, spread_list,
                                wt, wt_1, wi, Dt, St, qt, g, U, t, T, P, delta, chi, eta)
                # print("ERROR!!!! weights don't meet contraints, exiting")
            #         break

            dict_metrics_by_date[date] = {'returns': port_returns[-1],
                                          'volatility': port_volatility[-1],
                                          'Sharpe Ratio': sharpe_ratio[-1],
                                          'Index Returns': idx_returns[-1],
                                          'Reward': reward_list[-1],
                                          '12m turnover': np.sum(turnover_list[-12:]),
                                          'cost': costs[-1],
                                          'Index Duration': idx_duration_list[-1],
                                          'Index Spread': idx_spread_list[-1],
                                          'Portfolio Duration': duration_list[-1],
                                          'Portfolio Spread': spread_list[-1],
                                          }
            if(dict_metrics_by_date[date]['volatility'] > 0):
                print("Sharpe Ratio : " , dict_metrics_by_date[date]['Sharpe Ratio'])
            else:
                print('Not enought points to calculate Sharpe Ratio')
            dict_metrics_by_date[date]['weights'] = asset_weights[-1]

            counter += 1

            ## Store end of month returns to calculate reward in next period
            del ri
            ri = pd.Series(date_data['TRR'], index=date_data['Identifier'])

            # print(ri[preds==3])

        ## Calculate returns for last period
        # if ri is not None:
        #     # reward = getReward(port_returns, port_volatility, sharpe_ratio, asset_weights, reward_list, turnover_list, duration_list, spread_list, wt_1, wt_2, ri, l, k)
        #     # reward_list.append(reward)
        #     idx_returns.append(np.dot(wi, ri))

        ## check if contraints on total return and risk are met
        self.metrics = dict_metrics_by_date
        Idx_R = ((((1 + np.array(idx_returns) / 100).prod()) ** (12 / float(len(idx_returns))) - 1) * 100)
        Idx_Vol = (np.sqrt(12) * np.array(idx_returns).astype(float).std())
        Idx_VolD = (np.sqrt(12) * np.std([np.minimum(x, 0) for x in np.array(idx_returns).astype(float)]))
        Port_R = ((((1 + np.array(port_returns) / 100).prod()) ** (12 / float(len(port_returns))) - 1) * 100)
        Port_Vol = (np.sqrt(12) * np.array(port_returns).astype(float).std())
        Port_VolD = (np.sqrt(12) * np.std([np.minimum(x, 0) for x in np.array(port_returns).astype(float)]))
        if self.checkFinalConstraints(Idx_R, Idx_Vol, Idx_VolD, Port_R, Port_Vol, Port_VolD):
            print("ERROR!!!! weights don't meet return/risk limit contraints, exiting")

        print("Portfolio Metrics:")
        print("Total Return: %.2f" % np.sum(port_returns))
        print("Standard Deviation: %.2f" % port_volatility[-1])
        print("Sharpe Ratio: %.2f" % sharpe_ratio[-1])

        return 0

    def getMetrics(self):
        return self.metrics