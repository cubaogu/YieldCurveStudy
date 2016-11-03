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
    

#寻找个体公司的Spread:135401.SH，16盘锦水务，10.27号估值106.6656
issueDate = ql.Date(28, 4, 2016)
maturityDate = ql.Date(28, 4, 2019)
tenor = ql.Period(ql.Annual)

fixedRateBond = mybond(issueDate,maturityDate,tenor,0.068,100)

for i in range(1,10000):
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
    



    

def price_of_2plus5(issue_day,issue_mon,issue_year,coupon,spotRates): #算出2+5年的债的价格
    total_price = 0
    
    todaysDate = ql.Date(27, 10, 2016) #今天，即定价中的成交日
    ql.Settings.instance().evaluationDate = todaysDate
    
    calendar = ql.UnitedStates()
    dayCount = ql.Thirty360()
    interpolation = ql.Linear()
    compounding = ql.Compounded
    compoundingFrequency = ql.Annual
    
    spotDates = [ql.Date(27, 10, 2016)] + [ql.Date(27, j, i) for i in range(2017,2024) for j in [4,10]]
    spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,compounding, compoundingFrequency) 
    spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)
    bondEngine = ql.DiscountingBondEngine(spotCurveHandle)

    for i in range(issue_year+3,issue_year+8):
        issueDate = ql.Date(issue_day, issue_mon, issue_year)
        maturityDate = ql.Date(issue_day, issue_mon, i)
        tenor = ql.Period(ql.Annual)
        fixedRateBond_t = mybond(issueDate,maturityDate,tenor,coupon,20)
        fixedRateBond_t.setPricingEngine(bondEngine)
        total_price += fixedRateBond_t.NPV()
    return total_price

Market_price_16rzxy_1027 = price_of_2plus5(29,9,2016,0.0443,spotRates)

# 寻找市场与估值之间的Spread：16汝州鑫源1680388.IB,10.27估值100.9708,市场101.1467

for i in range(1,201):
    spotRates_TMP = [j+ i*0.00005 for j in spotRates]
    if abs(price_of_2plus5(29,9,2016,0.0443,spotRates_TMP)-100.9708) < 0.1:
        break

Spread1 = i* 0.00005 #认为这是公司个体与中债曲线之间的Spread

for i in range(1,201):
    spotRates_TMP = [j+ i*0.00005 for j in spotRates]
    if abs(price_of_2plus5(29,9,2016,0.0443,spotRates_TMP)-101.1467) < 0.1:
        break

Spread2 = i* 0.00005 #认为这是市场成交与中债估值之间的Spread

market_spread = Spread2 - Spread1  #认为这是市场成交与中债估值之间的Spread


myspread = CorpSpread + market_spread#我们要定价的债券与中债曲线之间的总利差（个体+市场）


#准备定价的债：1680429.IB,16盘锦水务专项，一个2+5的债，10.28发行

spotRates_TMP = [j+myspread for j in spotRates]

for i in range(-200,201):
    final_price = price_of_2plus5(27,10,2016,i*0.0005 + 0.03,spotRates_TMP)
    if abs(final_price - 100) <0.1:
        break

print(i*0.0005+0.03)
#total_price = 0
#
#tommorrowDate= ql.Date(28, 10, 2016) #明天。想估算的债券的发行日
#ql.Settings.instance().evaluationDate = tommorrowDate
#spotDates = [ql.Date(28, 10, 2016)] + [ql.Date(28, j, i) for i in range(2017,2024) for j in [4,10]]
#spotCurve = ql.ZeroCurve(spotDates, spotRates, dayCount, calendar, interpolation,compounding, compoundingFrequency) 
#spotCurveHandle = ql.YieldTermStructureHandle(spotCurve)
#bondEngine = ql.DiscountingBondEngine(spotCurveHandle)
#
#
#for i in range(2019,2024):
#    issueDate = ql.Date(28, 10, 2016)
#    maturityDate = ql.Date(27, 10, i)
#    tenor = ql.Period(ql.Annual)
#    fixedRateBond_t = mybond(issueDate,maturityDate,tenor,0.0518,20)
#    fixedRateBond_t.setPricingEngine(bondEngine)
#    total_price += fixedRateBond_t.NPV()
    





    