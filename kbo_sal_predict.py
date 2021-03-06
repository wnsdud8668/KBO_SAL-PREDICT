# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 14:44:33 2020

@author: junyoung
"""


# matplotlib 한글 출력 가능하도록 만들기
from matplotlib import font_manager, rc
font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
rc('font', family=font_name)


# 데이터 크롤링 모듈
from selenium import webdriver
from bs4 import BeautifulSoup
import re

# 데이터 분석 모듈
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from datetime import datetime


driver = webdriver.Chrome('chromedriver.exe')
#%%
# 데이터 수집

#%% 한번에 5000개 정도의 데이터 추출. 하지만 어떨때는 데이터가 나오고 어떨때는 안나와서 타임슬립을 추가하여 사이트의 대기 시간 형성


for i in range(57):

    # 2000년 부터 2020년 까지 statiz에 기록된 선수들 필터링
    url = 'http://www.statiz.co.kr/stat.php?mid=stat&re=0&ys=2000&ye=2020&se=0&te=&tm=&ty=0\\\\&qu=auto&po=0&as\
        =&ae=&hi=&un=&pl=&da=1&o1=WAR_ALL_ADJ&o2=TPA&de=1&lr=0&tr=&cv=&ml=1&sn=100&pa={}&si=&cn='.format(i*100)
    
    driver.get(url)
    driver.implicitly_wait(5)
    time.sleep(1.5)
    
    html = driver.find_element_by_xpath('//*[@id="mytable"]/tbody').get_attribute("innerHTML") #기록 table을 str형태로 저장
    # 모든 태그의 id 속성에 'mytable' 속성값을 가진 모든 태그의 tbody 의 HTML 값을 가져온다
    
    soup = BeautifulSoup(html, 'html.parser') #str 객체를 BeautifulSoup 객체로 변경
    
    temp = [i.text.strip() for i in soup.findAll("tr")] #tr 태그에서, text만 저장하기
    
    # 모든 tr 태그에서 text만 temp에 리스트 형태로 저장
    
    temp = pd.Series(temp) #list 객체에서 series 객체로 변경
    
    #'순'이나 'W'로 시작하는 row 제거
    # 즉, 선수별 기록만 남기고, index를 reset 해주기
    temp = temp[~temp.str.match("[순W]")].reset_index(drop=True) 
    
    temp = temp.apply(lambda x: pd.Series(x.split(' '))) #띄어쓰기 기준으로 나눠서 dataframe으로 변경
    
    #선수 팀 정보 이후 첫번째 기록과는 space 하나로 구분, 그 이후로는 space 두개로 구분이 되어 있음 
    #그래서 space 하나로 구분을 시키면, 빈 column들이 존재 하는데, 해당 column들 제거 
    temp = temp.replace('', np.nan).dropna(axis=1) 
    
    #WAR 정보가 들어간 column이 2개 있다. (index가 1인 column과, 제일 마지막 column)
    #그 중에서 index가 1인 columm 제거 
    
    
    #선수 이름 앞의 숫자 제거
    temp[0] = temp[0].str.replace("^\d+", '')

    # 선수들의 생일 정보가 담긴 tag들 가지고 오기
    birth = [i.find("a") for i in soup.findAll('tr') if 'birth' in i.find('a').attrs['href']]
    
    # tag내에서, 생일 날짜만 추출하기 
    p = re.compile("\d{4}\-\d{2}\-\d{2}")
    birth = [p.findall(i.attrs['href'])[0] for i in birth]
    
    # 생일 column 추가
    temp['생일'] = birth
    
    # page별 완성된 dataframe을 계속해서 result에 추가 시켜주기 
    if i==0:
        result = temp
    else:
        result = result.append(temp)
        result = result.reset_index(drop=True)
   
                 
    print(i, "완료")
print('완료')
#%%
#column 명 정보 저장        
columns = ['선수']+['WAR'] + [i.text for i in soup.findAll("tr")[0].findAll("th")][4:-3] + ['타율', '출루', '장타', 'OPS', 'wOBA', 'wRC+', 'WAR+', '생일']

#column 명 추가
result.columns = columns



# 김동주04두3B 형태의 데이터를 선수명, 연도, 팀명, 포지션으로 분할하여 칼럼 추가 
player=result['선수']

import re

name=[]
year=[]
team=[]
for i in player:
    name.append(re.compile('[ㄱ-힣]+').findall(i)[0])
    year.append((re.compile('[|가-힣]+').sub('',i))[:2])
    if len(re.compile('[ㄱ-힣]+').findall(i))==2:
        team.append(re.compile('[ㄱ-힣]+').findall(i)[-1])
    else:
        team.append((re.compile('[|가-힣]+').sub('',i))[2:3])

position=[]
for i in player:
    if i[-1:]=='C':
        position.append(i[-1:])
    else:
        position.append(i[-2:])


result['선수명']=name
result['연도int']=year
result['팀명']=team
result['포지션']=position

# 출생연도 칼럼추가
result['출생연도']=pd.to_numeric(result['생일'].str[:4])

# 연도에서 출생연도를 빼서 나이 칼럼 추가
result['나이']=pd.to_numeric(result['연도int']) -pd.to_numeric(result['출생연도'])+2001

# result의 문자열 칼럼의 숫자형 변환
for i in result.columns:
    try:
        result[i]=pd.to_numeric(result[i])
    except ValueError as e:
        e
    except IndexError as e:
        e

result['연도int']=result['연도int']+2000

years=[]
for i in result['연도int']:
    years.append(str(i)[:4])

result['연도str']=years




#%%

#2000년부터 2020년까지 선수별 연봉 추출
for year in range(2000,2021):
    print(year)
    for t in range(1,11):
    
        url='http://www.statiz.co.kr/salary.php?opt=0&sopt={}&cnv=&pos=&te={}'.format(year,t)
        
        driver.get(url)
        time.sleep(1.5)
        
        html = driver.find_element_by_xpath('//*[@class="table table-striped"]/tbody').get_attribute("innerHTML") #기록 table을 str형태로 저장
                                            # 모든 태그의 id 속성에 'mytable' 속성값을 가진 모든 태그의 tbody 의 HTML 값을 가져온다
    
    
    
        soup = BeautifulSoup(html, 'html.parser') 
        
        
        
        td=soup.findAll("td")
        
        temp = [i.text for i in td] #tr 태그에서, text만 저장하기
        
        import pandas as pd
        temp = pd.Series(temp)
        temp=list(temp)
        
        # a리스트에 WAR값 추가
        a=[]
        for i in temp:
            if'.' in i:
                a.append(i)
        
        # WAR 제거
        for i in a:
            temp.remove(i)
        
        len(temp)
        for i in range(len(temp)):
            try:
                temp.remove('')
            except SyntaxError as e:
                e
            except ValueError as e:
                e
        
        name=[]
        for i in range(len(temp)):
            if i%4==0:
                name.append(temp[i])
        
        
        sal=[]
        for i in range(len(temp)):
            if i%4==3:
                sal.append(temp[i])
        
        len(name)
        len(sal)
        
        # 팀이름 이름 연도 연봉 DataFrame 만들기
        columns=['팀명','선수명','연도int','연봉']
        
        df=pd.DataFrame(name)
        
        if t==1:
            team_na='K'
        elif t==2:
            team_na='삼'
        elif t==3:
            team_na='두'
        elif t==4:
            team_na='S'
        elif t==5:
            team_na='L'
        elif t==6:
            team_na='롯'
        elif t==7:
            team_na='한'
        elif t==8:
            team_na='넥'
        elif t==9:
            team_na='N'
        elif t==10:
            team_na='k'    
        df=pd.DataFrame(data={'선수명':name,'팀명':team_na,'연도int':year,'연봉':sal})
        
        print(year,t,'완료')
        if year == 2000:
            sal_result = df
        else:
            sal_result = sal_result.append(df)
            sal_result = sal_result.reset_index(drop=True)
    
    

print('완료')



#%% 중복 제거     
sal_result = sal_result.drop_duplicates(['선수명', '팀명', '연도int'], keep='last')

result=result.drop_duplicates(['선수명','팀명','연도int','장타'],keep='last')

result.info()
'''
 #   Column  Non-Null Count  Dtype  
---  ------  --------------  -----  
 0   선수      8386 non-null   object 
 1   WAR     7756 non-null   float64
 2   G       7707 non-null   float64
 3   타석      7707 non-null   float64
 4   타수      7429 non-null   float64
 5   득점      7429 non-null   float64
 6   안타      7398 non-null   float64
 7   2타      7398 non-null   float64
 8   3타      7277 non-null   float64
 9   홈런      6916 non-null   float64
 10  루타      6773 non-null   float64
 11  타점      6572 non-null   float64
 12  도루      6533 non-null   float64
 13  도실      6395 non-null   float64
 14  볼넷      6278 non-null   float64
 15  사구      6145 non-null   float64
 16  고4      6076 non-null   float64
 17  삼진      6053 non-null   float64
 18  병살      5904 non-null   float64
 19  희타      5632 non-null   float64
 20  희비      5500 non-null   float64
 21  타율      4186 non-null   float64
 22  출루      4073 non-null   float64
 23  장타      4000 non-null   float64
 24  OPS     3886 non-null   float64
 25  wOBA    3986 non-null   float64
 26  wRC+    3703 non-null   float64
 27  WAR+    5042 non-null   float64
 28  생일      8386 non-null   object 
 29  선수명     8386 non-null   object 
 30  연도      8386 non-null   object 
 31  팀명      8386 non-null   object 
 32  포지션     8386 non-null   object 
 33  출생연도    8386 non-null   int64  
 34  나이      8379 non-null   float64
 '''


# result 데이터프레임과 sal_result 데이터프레임을 조인하기 위하여 sal_result에 result의 연도와 같은 형태의 숫자형 연도 컬럼 추가

sal_year=[]
for i in sal_result['연도int']:
    sal_year.append(str(int(i)))

sal_result['연도str']=sal_year

#%%

# sal_result , result 조인 하여 kbo_df 데이터프레임 생성
kbo_df = pd.merge(result, sal_result,on=['선수명','팀명','연도str','연도int'])



#%%
# 출전경기 5게임 미만인 선수들 제거
kbo_df=kbo_df.loc[kbo_df['G']>5]


# 연봉의 타입변경 'object' -> 'int'
kbo_df['연봉']=kbo_df['연봉'].str.replace(",", '')
kbo_df['연봉']=pd.to_numeric(kbo_df['연봉'])


# WAR 대비 연봉 시각화
sns.relplot(x="WAR", y="연봉", data=kbo_df)
plt.show()


# WAR대비연봉 칼럼 생성
kbo_df['WAR대비연봉']=kbo_df['연봉']/kbo_df['WAR']

#WAR대비연봉칼럼의 이상치 제거

q1 = kbo_df['WAR대비연봉'].quantile(0.25)
q3 = kbo_df['WAR대비연봉'].quantile(0.75)

# 1.5 * IQR(Q3 - Q1)
iqt = 1.5 * (q3 - q1)

# 원래 데이터 복제
y = kbo_df

# 이상치를 NA로 변환
y["WAR대비연봉"][(y["WAR대비연봉"] > (q3 + iqt)) | (y["WAR대비연봉"] < (q1 - iqt))] = None

# WAR대비연봉의 이상치 제거
kbo_df['WAR대비연봉'].dropna(how='any')

kbo_df=kbo_df.loc[kbo_df.isnull()['WAR대비연봉']==False,]

# 이상치 제거후 WAR 대비 연봉 시각화
sns.relplot(x="WAR", y="연봉", data=kbo_df)
plt.show()

#%%
#%% 소비자 물가 지수 칼럼 추가
import pandas as pd

# 소비자 물가 지수 칼럼 추가
prices=pd.read_excel('stat_402701.xls',header=2).iloc[0,36:]
# 소비자 물가 상승률 데이터에서 2018대비 2019 상승률 데이터 추출
price_increase_2019=pd.read_excel('stat_106001.xls').iloc[2,-1]
# 2018년 소비자물가지수 + 2018년 상승률
prices['2019']=prices['2018']+price_increase_2019

# 2020년도 소비자물가지수는 불필요하지만 코드상 필요에 의하여 임의의 0값을 저장
prices['2020']=0

year=[]
for i in kbo_df['연도str']:
    year.append(str(int(i)))

kbo_price=[]
for i in year:
    kbo_price.append(prices[i])

kbo_df['소비자물가지수']=kbo_price

#%% 이듬해 연봉 칼럼 추가 (이듬해연봉-label)



# kbo_df의 인덱스 reset
kbo_df = kbo_df.reset_index(drop=True)

# 이듬해 연봉 칼럼 추가
nexty_sal=[]
for i in kbo_df.index:
    try:
        a=(kbo_df[kbo_df['선수명']==kbo_df.loc[i,'선수명']]['연도int']==kbo_df.loc[i,:]['연도int']+1)
        nexty_sal.append(kbo_df[kbo_df['선수명']==kbo_df.loc[i,'선수명']][a==True]['연봉'].values[0])
    except IndexError:
        nexty_sal.append(None)
        

kbo_df['이듬해연봉']=nexty_sal




kbo_df = kbo_df.reset_index(drop=True)


#%%
# 필요없는 칼럼 제거
kbo_df=kbo_df.drop(['선수','생일','선수명'],axis=1)

# null값 제거
kbo_df = kbo_df.dropna(axis=0)


# csv형태로 저장
kbo_df.to_csv('kbo_df2.csv')

#%%


#%%
#webdriver 종료
driver.close()

print("데이터 전처리 완료")



#%%
# 모델링

#%%

#1. Dense를 이용한 딥러닝



#%% Dense를 이용한 딥러닝
from keras.models import Sequential
from keras.layers import Dense,Dropout
from sklearn.model_selection import train_test_split
from keras.callbacks import ModelCheckpoint, EarlyStopping
import os
import numpy as np
import pandas as pd
import tensorflow as tf

import matplotlib.pyplot as plt

seed = 0
np.random.seed(seed)
tf.random.set_seed(3)
df = pd.read_csv('kbo_df2.csv',index_col=0)
df.head(10)

df.info()
df_y= df['이듬해연봉']
df.columns

#중요한피쳐만 추출

corr=df.corr()
label_corr=corr['이듬해연봉']
label_corr.sort_values(ascending=False)[15::-1]
'''
장타       0.484196
OPS      0.489095
고4       0.493655
타수       0.522612
타석       0.535021
득점       0.548051
2타       0.563913
홈런       0.565589
안타       0.571786
볼넷       0.582170
WAR      0.588025
WAR+     0.588025
루타       0.609493
타점       0.626061
연봉       0.931610
이듬해연봉    1.000000
'''
df_x=df[['연봉','타점','루타','WAR+','WAR','볼넷','안타','홈런','2타','득점','타석','타수','고4','OPS','장타']]
#df_x=df.drop(['이듬해연봉'],axis=1)
'''
from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
df_x['팀명']=le.fit_transform(df['팀명'])
df_x['포지션']=le.fit_transform(df['포지션'])
'''
X = df_x.values.astype('float64')
Y = df_y.values
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.1, random_state=seed)
 
model = Sequential()
model.add(Dense(1000, input_dim=df_x.shape[1], activation='relu'))
model.add(Dense(1000,activation='relu'))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
# model.fit(X_train, Y_train, epochs=500, batch_size=500)
  
# 모델 최적화 설정
MODEL_DIR = './model/'
if not os.path.exists(MODEL_DIR):
    os.mkdir(MODEL_DIR)
 
modelpath="./model/{epoch:02d}-{val_loss:.4f}.hdf5"
checkpointer = ModelCheckpoint(filepath=modelpath, monitor='val_loss', verbose=1, save_best_only=True)
early_stopping_callback = EarlyStopping(monitor='val_loss', patience=10)
  
# 모델의 실행
history = model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=3000, batch_size=200, verbose=1, callbacks=[early_stopping_callback,checkpointer])
  
# 테스트 정확도 출력
print("\n Test Accuracy: %.4f" % (model.evaluate(X_test, Y_test)[1]))
  
# 테스트셋의 오차
y_vloss = history.history['val_loss']
  
# 학습셋의 오차
y_loss = history.history['loss']
# 그래프로 표현
x_len = np.arange(len(y_loss))
plt.plot(x_len, y_vloss, marker='.', c="red", label='Testset_loss')
plt.plot(x_len, y_loss, marker='.', c="blue", label='Trainset_loss')

# 그래프에 그리드를 주고 레이블을 표시
plt.legend(loc='upper right')
# plt.axis([0, 20, 0, 0.35])
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()





  
# 예측 값과 실제 값의 비교
Y_prediction = model.predict(X_test).flatten()
for i in range(10):
    label = Y_test[i]
    prediction = Y_prediction[i]
    print("실제가격: {:.3f}, 예상가격: {:.3f}".format(label, prediction))
print("\n Test Accuracy: %.4f" % (model.evaluate(X_test, Y_test)[1]))

#1. RMSE
from sklearn.metrics import mean_squared_error
def RMSE(y_test,Y_prediction):
    return np.sqrt(mean_squared_error(y_test, Y_prediction))
print('RMSE : ',RMSE(Y_test,Y_prediction)) 
#2. R2 score
from sklearn.metrics import r2_score
r2_y_predict = r2_score(Y_test,Y_prediction)
print('R2 score : ',r2_y_predict)
#%% 실값,예측값 그래프

pred = model.predict(X_test)
# %matplotlib inline
plt.rc('font', family='gulim') 
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111)
ax.plot(Y_test, label='실값')
ax.plot(pred, label='예측값')
ax.legend() # 범주

#%%





#2. XGBM 기계학습





#%% XGBM 기계학습
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from sklearn import datasets
from sklearn import model_selection
from sklearn import metrics
import xgboost

df= pd.read_csv('kbo_df2.csv',index_col=0)

df_y= df['이듬해연봉']

#다중공선성 제거 후 필요한 피처만 추출
df_x.corr()
'''
               연봉        타점        루타  ...        홈런        2타   소비자물가지수
연봉       1.000000  0.532258  0.506362  ...  0.479031  0.453159  0.216331
타점       0.532258  1.000000  0.951069  ...  0.883913  0.853812  0.068802
루타       0.506362  0.951069  1.000000  ...  0.825451  0.924871  0.047177
WAR      0.465408  0.847841  0.888951  ...  0.757055  0.819756  0.013657
볼넷       0.506085  0.823265  0.853210  ...  0.688263  0.778264  0.017034
안타       0.478591  0.889200  0.973465  ...  0.681742  0.917194  0.046382
홈런       0.479031  0.883913  0.825451  ...  1.000000  0.672560  0.027004
2타       0.453159  0.853812  0.924871  ...  0.672560  1.000000  0.046262
소비자물가지수  0.216331  0.068802  0.047177  ...  0.027004  0.046262  1.000000
'''
df_x=df[['연봉','타점','루타','WAR','볼넷','안타','홈런','2타','소비자물가지수']]
df_x.info()

X = df_x.values
Y = df_y.values

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
data_scaled = scaler.fit_transform(X)

from sklearn.model_selection import train_test_split
x_train , x_test, y_train , y_test = train_test_split(X,Y,
                                                      test_size=0.1,                                                     
                                                      random_state=1)



model = xgboost.XGBRegressor(learning_rate=0.1,
                             max_depth=5,
                             n_estimators=100) 
model.fit(x_train, y_train)
print(model.score(x_train,y_train))
print(model.score(x_test,y_test))

from xgboost import plot_importance
import matplotlib.pyplot as plt
fig,ax= plt.subplots(figsize=(10,12))
plot_importance(model,ax=ax)

print('\n',"교육정확도",model.score(x_train,y_train))
print("테스트정확도",model.score(x_test,y_test),'\n')

y_prediction = model.predict(x_test).flatten()
for i in range(10):
    label = y_test[i]
    prediction = y_prediction[i]
    print("실제연봉: {:.3f}, 예상연봉: {:.3f}".format(label, prediction))

pred = model.predict(x_test)
# %matplotlib inline
plt.rc('font', family='gulim') 
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111)
ax.plot(y_test, label='실값')
ax.plot(pred, label='예측값')
ax.legend() # 범주

#%%





#3. LSTM 인공신경망


# LSTM 인공신경망 딥러닝
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import LSTM, Dropout, Dense, Activation
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.callbacks import ModelCheckpoint, EarlyStopping
import os
import seaborn as sns
#데이터불러오기
data = pd.read_csv('kbo_df2.csv',index_col=0)
#x_data = data.drop(['Unnamed: 0','선수명','선수','생일','팀명','포지션','이듬해연봉','OPS','wOBA','wRC+','WAR+','출생연도'],axis=1) .values
#x_data = data[['연봉','연도','볼넷','WAR','출루','나이','타율','삼진','장타','WAR대비연봉']].astype('float64').values
#중요한피쳐만추출
#x_data=data[['연봉','타점','루타','WAR','볼넷','안타','홈런','2타','소비자물가지수']]
#x_data=data.drop(['팀명','포지션','연도str'],axis=1)
x_data=data[['연봉','타점','루타','WAR+','WAR','볼넷','안타','홈런','2타','득점','타석','타수','고4','OPS','장타']]
x_data.info()
x_data = x_data.astype('float32').values

y_data = data['이듬해연봉'].values

#데이터정규화
mean = x_data.mean(axis=0)
x_data -= mean
std = x_data.std(axis=0)
x_data /= std
mean = y_data.mean(axis=0)
y_data -= mean
std = y_data.std(axis=0)
y_data /= std
y_data=y_data.reshape(-1,1)



#데이터스플릿
x_train,x_test,y_train,y_test = train_test_split(x_data,y_data,test_size=0.2, random_state=0)
#2차배열의 데이터를 3차원으로
x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

#모델구축 인공신경망 LSTM - 선형의 데이타를 예측하기 좋다.
model = Sequential()
model.add(LSTM(32 ,return_sequences=True, input_shape=(x_data.shape[1], 1)))
model.add(LSTM(16, return_sequences=False))
model.add(Dense(1, activation='linear'))
model.compile(loss='mse', optimizer='Adam')
model.summary()  

# 모델 최적화 설정
MODEL_DIR = './model/'
if not os.path.exists(MODEL_DIR):
    os.mkdir(MODEL_DIR) 
modelpath="./model/{epoch:02d}-{val_loss:.4f}.hdf5"
mc = ModelCheckpoint(filepath=modelpath, monitor='val_loss', verbose=1, save_best_only=True)
es = EarlyStopping(monitor='val_loss', patience=50)
#모델실행
history = model.fit(x_train, y_train,validation_data=(x_test, y_test),batch_size=50,epochs=500,callbacks=[es,mc])





# 테스트셋의 오차
y_vloss = history.history['val_loss']  
# 학습셋의 오차
y_loss = history.history['loss']
# 그래프로 표현
x_len = np.arange(len(y_loss))
plt.plot(x_len, y_vloss, marker='.', c="red", label='Testset_loss')
plt.plot(x_len, y_loss, marker='.', c="blue", label='Trainset_loss')  
# 그래프에 그리드를 주고 레이블을 표시
plt.legend(loc='upper right')
# plt.axis([0, 20, 0, 0.35])
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss')
plt.show()

#검증
Y_prediction = model.predict(x_test)
# 1. RMSE
from sklearn.metrics import mean_squared_error
def RMSE(y_test,Y_prediction):
    return np.sqrt(mean_squared_error(y_test, Y_prediction))
print('RMSE : ',RMSE(y_test,Y_prediction)) 
# 2. R2 score
from sklearn.metrics import r2_score
r2_y_predict = r2_score(y_test,Y_prediction)
print('R2 score : ',r2_y_predict)
x_test.shape[0]
# 예측 값과 실제 값의 비교
for i in range(20):
    label = y_test[i]
    prediction = Y_prediction[i]
    print("실제연봉: ", int(label[0]*std+mean), "예상연봉: ", int(prediction[0]*std+mean))
    

#%% 실값,예측값 그래프

pred = model.predict(x_test)
# %matplotlib inline
plt.rc('font', family='gulim') 
fig = plt.figure(figsize=(20, 10))
ax = fig.add_subplot(111)
ax.plot(y_test, label='실값')
ax.plot(pred, label='예측값')
ax.legend() # 범주