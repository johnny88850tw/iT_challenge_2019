import os
import numpy as np
import matplotlib.pyplot as plt

class MinMaxScaler:
    __min = 0.
    __max = 1.
    __range = 1.
    __feature_range = (0, 1)
    __scale = 1.
    def __init__(self):
        pass
    def getScalerData(self, dataset, offset=0.1, feature_range=(0, 1)):
        data_max = np.max(dataset)
        data_min = np.min(dataset)
        if len(dataset) == 1:
            range_temp = dataset * offset
        else:
            range_temp = (data_max - data_min) * (1 + offset)
        self.__min = data_max - range_temp
        self.__max = data_min + range_temp
        self.__range = self.__max - self.__min
        self.__feature_range = feature_range
        self.__scale = (feature_range[1] - feature_range[0]) / self.__range
        return self.getTransformData(dataset)
    def getTransformData(self, dataset):
        return (dataset - self.__min) * self.__scale + self.__feature_range[0]
    def getInverseData(self, scalerDataset):
        return (scalerDataset - self.__feature_range[0]) / self.__scale + self.__min
    def getParameter(self):
        return self.__min, self.__max, self.__range, self.__feature_range, self.__scale
    def updatePatameter(self, parameter):
        if parameter is not None:
            self.__min, self.__max, self.__range, self.__feature_range, self.__scale = parameter

class stockEvn_single:
    __lot = 0
    __mean_price = 0
    __state_assets = 0
    __handling_fee = 0.001425
    __transaction_tax = 0.003
    __handling_fee_acc = 0.
    
    def __init__(self, money=1000, handling_fee=None, transaction_tax=None):
        self.__money = money
        self.__money_init = money
        self.updateHandlingFee(handling_fee=handling_fee, transaction_tax=transaction_tax)
        self.__state_assets = self.getAssets()
    
    def resetEnv(self):
        self.__lot = 0
        __mean_price = 0
        __state_assets = 0
        __handling_fee_acc = 0.
        self.__money = self.__money_init
        
    def getInfo(self):
        return{'stock count':self.__lot, 'stock value':self.__mean_price, 'money leave':self.__money,
              'assets':self.__state_assets, 'handling fee':self.__handling_fee, 'transaction tax':self.__transaction_tax, 
               'handling fee acc':self.__handling_fee_acc}
    
    def updateHandlingFee(self, handling_fee=None, transaction_tax=None):
        if handling_fee is not None:
            self.__handling_fee = handling_fee
        if transaction_tax is not None:
            self.__transaction_tax = transaction_tax
    
    def doAction(self, stock_price, action, s_prop, stint=65535):
        '''
        stock_price : the price of stock
        action : 0, sell; 1, do nothing, 2, buy
        s_prop : a float between 0-1
        stint : the max number you can buy or sell
        '''
        return self.__calculate_price(stock_price=stock_price, action=action, s_prop=s_prop, stint=stint)
    
    def __calculate_price(self, stock_price, action, s_prop, stint):
        if action == 0:
            can_sell = self.__lot
            sell = min(int(s_prop * can_sell), stint)
            handling_fee = self.__handling_fee + self.__transaction_tax
            stock_price_d = stock_price * handling_fee
            self.__doSell(stock_price=stock_price-stock_price_d, quan=sell)
            self.__handling_fee_acc += (sell * stock_price_d)
        elif action == 1:
            self.__doNothing()
        elif action == 2:
            handling_fee = self.__handling_fee
            stock_price_d = stock_price * handling_fee
            can_buy = int(self.__money / (stock_price + stock_price_d))
            buy = min(int(s_prop * can_buy), stint)
            self.__doBuy(stock_price=stock_price, quan=buy)
            self.__handling_fee_acc += (buy * stock_price_d)
        now_state = self.getAssets()
        loss = self.__state_assets - now_state
#         do_nothing_count = 0
#         if loss == 0 and self.__lot == 0:
#             do_nothing_count += 1
#             if do_nothing_count > 50:
#                 loss = 1
#             else:
#                 loss = 0.01
#         elif loss < 0:
#             loss /= -100
#         elif loss > 0:
#             loss /= 100
#         else:
#             loss = 0.001
#         self.__state_assets = now_state
        return loss
    
    # Action calculate
    def __doSell(self, stock_price, quan):
        if quan < 1:
            return self.__doNothing()
        else:
            if stock_price < self.__mean_price:
                loss = 1
            else:
                loss = 0
            self.__lot -= quan
            self.__money += (quan * stock_price)
            return 
        
    def __doBuy(self, stock_price, quan):
        if quan < 1:
            return self.__doNothing()
        else:
            if stock_price > self.__mean_price:
                loss = 1
            else:
                loss = 0
            value_stock = self.__lot * self.__mean_price
            self.__lot += quan
            value_stock += (quan * stock_price)
            self.__mean_price = value_stock / self.__lot
            self.__money -= (quan * stock_price)
            return
        
    def __doNothing(self):
        return
    
    # Assets
    def getAssets(self):
        handling_fee = 1 - (self.__handling_fee + self.__transaction_tax)
        return self.__lot * self.__mean_price * handling_fee + self.__money

    
# dataset summary
def countDataset(path):
    return len(getDataset(path))
    
def getDatasetSummary(dataset_path="./dataset/Taiwan_5s/", choose=500):
    summary = [0] * 100
    paths = []

    for dirPath, dirNames, fileNames in os.walk(dataset_path):
        if dirPath == dataset_path:
            continue
        total = 0
        for datapath in fileNames:
            count = countDataset(dirPath + '/' + datapath)
            summary[count // 10 - 1] += 1
            if count == choose:
                paths.append(dirPath + '/' + datapath)
    print(choose, len(paths))
    # plot results
    plt.plot(summary, color = 'blue', label = 'count')
    plt.title('summary')
    plt.xlabel('range * 10')
    plt.ylabel('count')
    plt.legend()
    plt.show()
    # save paths
    np.save(dataset_path + 'paths_500.npy')
