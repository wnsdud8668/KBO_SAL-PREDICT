# KBO_SAL-PREDICT
KBO 선수 정보를 바탕으로 이듬해 연봉을 예측하는 프로젝트 입니다.

### 데이터 추출
 * SELENIUM을 활용하여 STATIZ(야구 통계 사이트)의 정보 웹크롤링

### 데이터 전처리
 * IQR을 활용하여 이상치 제거
 * 중복 값, NULL 값 제거

### 데이터 모델링
 * Dense(딥러닝) - RMSE :  7914.50 , R2 score :  0.8572

 * XGBMRegressor(머신러닝) - 예측 정확도 : 0.9241

 * LSTM(딥러닝) - RMSE :  0.2889, R2 score : 0.9426
