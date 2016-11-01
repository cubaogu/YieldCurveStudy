#! /usr/bin/python
# -*- coding: utf-8 -*-

'''
This is a py3.4 version.

Created on ${20161025}
 
@author: ${ChenCHEN}
'''


import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.decomposition import PCA

import pandas as pd

import seaborn as sns

import QuantLib as ql


#读取数据，清理到index为时间，columns为0-10年期限的格式
yc = pd.read_excel("C:/Users/chenchen/Desktop/lb.xlsx")

yc.drop(12,inplace=True)
yc.drop(11,inplace=True)

yc.index = yc[yc.columns[0]]
yc.drop(yc.columns[0],axis = 1,inplace= True)
yc1 = yc.T

#curve的PCA分析，取前三个变量
pca = PCA(n_components=3)
X_r = pca.fit(yc1).transform(yc1)
pca.explained_variance_ratio_

pc_yc = pd.DataFrame(X_r)
pc_yc.columns = ['level','slope','curve']
sns.pairplot(pc_yc)
sns.pairplot(pc_yc,vars=['level','slope'])

#构建spotrate curve
todaysDate = ql.Date(24, 10, 2016) #今天，即定价中的成交日
ql.Settings.instance().evaluationDate = todaysDate

spotDates = [ql.Date(24, 10, i) for i in range(2016,2027)]

SR = yc1[1:2].values.tolist()
spotRates = [x/100 for x in SR[0]] #取第一行数据的spotrates做实验，记住此处一定要是list

calendar = ql.UnitedStates()
dayCount = ql.Thirty360()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Annual
#这个schedule构建的时候用tenor之间的间隔算出真实的天数，然后按照dayCount的规则（此处是按每年都365天来算）得到每个rate对应的年份
spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,compounding, compoundingFrequency) 
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

#构建债券
issueDate = ql.Date(17, 3, 2016)
maturityDate = ql.Date(17, 3, 2023)
tenor = ql.Period(ql.Annual)

bussinessConvention = ql.Unadjusted
dateGeneration = ql.DateGeneration.Backward
monthEnd = False
#这个schedule构建的时候用tenor之间的间隔算出真实的天数，然后按照dayCount的规则（此处是按每年都365天来算）得到每个rate对应的年份
schedule = ql.Schedule (issueDate, maturityDate, tenor, calendar, bussinessConvention, bussinessConvention, dateGeneration, monthEnd)

#list(schedule)

# Now lets build the coupon
dayCount =ql.Thirty360()
couponRate = .0275
coupons = [couponRate]

# Now lets construct the FixedRateBond
settlementDays = 0  #settlementDays值清算日，如果需要2天清算则需要多给两天利息？看settlementValue(不过利息貌似有100倍的误差？)
faceValue = 100
fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, coupons, dayCount)

# create a bond engine with the term structure as input;
# set the bond to use this bond engine
bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
fixedRateBond.setPricingEngine(bondEngine)

# Finally the price
print(fixedRateBond.NPV())

#enableExtrapolation (bool b=true)
#enable extrapolation in subsequent calls 

