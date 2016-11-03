# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 15:50:56 2016

@author: 陈陈
"""




import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.decomposition import PCA

import pandas as pd

import seaborn as sns

import QuantLib as ql


#读取10.27号中债城投即期收益率数据（0.1年间隔）
yc = pd.read_excel("C:/Users/chenchen/Desktop/key_spot.xlsx")

#找出来半年或者整数年的rate
ttt = lambda x : int(x/0.5) - x/0.5 == 0
tmp_rate = yc['Rate'][yc['Term'].map(ttt)]

#构建spotrate curve
todaysDate = ql.Date(27, 10, 2016) #今天，即定价中的成交日
ql.Settings.instance().evaluationDate = todaysDate

spotDates = [ql.Date(27, 10, 2016)] + [ql.Date(27, j, i) for i in range(2017,2024) for j in [4,10]]

spotRates = [x/100 for x in tmp_rate] #取第一行数据的spotrates做实验，记住此处一定要是list

#len(list(spotDates))

calendar = ql.UnitedStates()
dayCount = ql.Thirty360()
interpolation = ql.Linear()
compounding = ql.Compounded
compoundingFrequency = ql.Annual






def mybond(issueDate, maturityDate, tenor, couponRate,faceValue):
    calendar = ql.UnitedStates()
    bussinessConvention = ql.Unadjusted
    dateGeneration = ql.DateGeneration.Backward
    monthEnd = False
    #这个schedule构建的时候用tenor之间的间隔算出真实的天数，然后按照dayCount的规则（此处是按每年都365天来算）得到每个rate对应的年份
    schedule = ql.Schedule (issueDate, maturityDate, tenor, calendar, bussinessConvention, bussinessConvention, dateGeneration, monthEnd)
    #list(schedule)

    # Now lets build the coupon
    dayCount =ql.Thirty360()
    #couponRate = .068
    coupons = [couponRate]

    # Now lets construct the FixedRateBond
    settlementDays = 0  #settlementDays值清算日，如果需要2天清算则需要多给两天利息？看settlementValue(不过利息貌似有100倍的误差？)
    #faceValue = 100
    fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, coupons, dayCount)
    
    return fixedRateBond
    

#寻找个体公司的构Spread:135401.SH，16盘锦水务，10.27号估值106.6656
issueDate = ql.Date(28, 4, 2016)
maturityDate = ql.Date(28, 4, 2019)
tenor = ql.Period(ql.Annual)

fixedRateBond = mybond(issueDate,maturityDate,tenor,0.068,100)

for i in range(1,201):
    spotRates_TMP = [j+ i*0.00005 for j in spotRates]
    #这个schedule构建的时候用tenor之间的间隔算出真实的天数，然后按照dayCount的规则（此处是按每年都365天来算）得到每个rate对应的年份
    spotCurve = ql.ZeroCurve(spotDates, spotRates_TMP, dayCount, calendar, interpolation,compounding, compoundingFrequency) 
    spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

    bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
    fixedRateBond.setPricingEngine(bondEngine)
    if abs(fixedRateBond.NPV()-106.6656) < 0.1:
        break

CorpSpread = i* 0.00005 #认为这是公司个体与中债曲线之间的Spread


print(CorpSpread)
    
    

# 寻找市场与估值之间的Spread：1680388.IB,10.27估值100.9709,市场101.1467
issueDate = ql.Date(28, 4, 2016)
maturityDate = ql.Date(28, 4, 2019)
tenor = ql.Period(ql.Annual)

fixedRateBond = mybond(issueDate,maturityDate,tenor,0.0443,100)

for i in range(1,201):
    spotRates_TMP = [j+ i*0.00005 for j in spotRates]
    #这个schedule构建的时候用tenor之间的间隔算出真实的天数，然后按照dayCount的规则（此处是按每年都365天来算）得到每个rate对应的年份
    spotCurve = ql.ZeroCurve(spotDates, spotRates_TMP, dayCount, calendar, interpolation,compounding, compoundingFrequency) 
    spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)

    bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
    fixedRateBond.setPricingEngine(bondEngine)
    if abs(fixedRateBond.NPV()-106.6656) < 0.1:
        break

CorpSpread = i* 0.00005 #认为这是公司个体与中债曲线之间的Spread


#1680429.IB,16盘锦水务专项，一个2+5的债，10.28发行
total_price = 0

tommorrowDate= ql.Date(28, 10, 2016) #明天。想估算的债券的发行日
ql.Settings.instance().evaluationDate = tommorrowDate
spotDates = [ql.Date(28, 10, 2016)] + [ql.Date(28, j, i) for i in range(2017,2024) for j in [4,10]]
spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,compounding, compoundingFrequency) 
spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)
bondEngine = ql.DiscountingBondEngine(spotCurveHandle)


for i in range(2019,2024):
    issueDate = ql.Date(28, 10, 2016)
    maturityDate = ql.Date(27, 10, i)
    tenor = ql.Period(ql.Annual)
    fixedRateBond_t = mybond(issueDate,maturityDate,tenor,0.0518,20)
    fixedRateBond_t.setPricingEngine(bondEngine)
    total_price += fixedRateBond_t.NPV()
    
print(total_price)
    



    