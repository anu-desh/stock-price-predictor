from os import name
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Loading data
df = pd.read_csv('AAPL.csv')
df["date"]=pd.to_datetime(df.date,format="%Y-%m-%d").dt.date
df.index=df['date']

new_dataset=pd.DataFrame(index=range(0,len(df)),columns=['Date','Close'])
for i in range(0,len(df)):
    new_dataset["Date"][i]=df['date'][i]
    new_dataset["Close"][i]=df["close"][i]
new_dataset.index = new_dataset.Date
new_dataset.drop("Date",axis=1,inplace=True)

# splitting dataset into train and test data
final_dataset=new_dataset.values
n = len(new_dataset)
train_data=final_dataset[0:int(n*.60),:]
test_data=final_dataset[int(n*.60):,:]

# Applying MinMax scaler
scaler=MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(final_dataset)

# train data
x_train_data,y_train_data=[],[]
time_step = 60
for i in range(time_step,len(train_data)):
    x_train_data.append(scaled_data[i-time_step:i,0])
    y_train_data.append(scaled_data[i,0])
x_train_data,y_train_data=np.array(x_train_data),np.array(y_train_data)

x_train_data=np.reshape(x_train_data,(x_train_data.shape[0],x_train_data.shape[1],1))

# test data
inputs_data=new_dataset[len(new_dataset)-len(test_data)-time_step:].values
inputs_data=inputs_data.reshape(-1,1)
inputs_data=scaler.transform(inputs_data)

X_test,Y_test=[],[]
for i in range(time_step,inputs_data.shape[0]):
    X_test.append(inputs_data[i-time_step:i,0])
    Y_test.append(inputs_data[i,0],)
X_test,Y_test = np.array(X_test),np.array(Y_test)

X_test=np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))

model=load_model("improved_model.h5")

train_predict = model.predict(x_train_data)
train_predict = scaler.inverse_transform(train_predict)
y_pred = model.predict(X_test)
y_pred = scaler.inverse_transform(y_pred)

train_data = new_dataset[60:int(n*0.60)]
test_data = new_dataset[int(n*0.60):]
print(len(test_data),len(y_pred))
train_data['predictions'] = train_predict
test_data['predictions'] = y_pred

days = 30
for i in range(days):

    new_input = new_dataset.values[-time_step:]
    new_input = scaler.fit_transform(new_input)
    new_input = np.array(new_input)
    new_input = new_input.reshape(1,-1)
    new_input = np.reshape(new_input,(1,time_step,1))

    new_pred = model.predict(new_input)
    new_pred = scaler.inverse_transform(new_pred)

    date = new_dataset.index[-1]+pd.to_timedelta(1,unit='d')
    new_dataset = new_dataset.append(pd.DataFrame({"Close":new_pred[0][0]},index=[date]))

predicted_plot = new_dataset[-days:]

app = dash.Dash()
server = app.server

app.layout = html.Div([

    html.H1("Stock Price Analysis Dashboard", style={"textAlign": "center"}),		
				html.H2("Actual closing price",style={"textAlign": "center"}),
				dcc.Graph(
					id="Actual Data",
					figure={
						"data":[
							go.Scatter(
                                name = "actual data",
								x=test_data.index,
								y=test_data["Close"],
								mode='lines'
							),

						],
						"layout":go.Layout(
							xaxis={'title':'Date'},
							yaxis={'title':'Closing Rate'}
						)
					}

				),
                html.H2("LSTM Predicted closing price",style={"textAlign": "center"}),
				dcc.Graph(
					id="Predicted Data",
					figure={
						"data":[
							# go.Scatter(
							# 	x=train_data.index,
							# 	y=train_data["predictions"],
							# 	mode='lines'
							# ),
                            go.Scatter(
                                name = "test prediction",
								x=test_data.index,
								y=test_data["predictions"],
								mode='lines'
							),
                            go.Scatter(
                                name = "future prediction",
								x=predicted_plot.index,
								y=predicted_plot["Close"],
								mode='lines'
							),
						],
						"layout":go.Layout(
							xaxis={'title':'Date'},
							yaxis={'title':'Closing Rate'}
						)
					}

				)				
        
])

if __name__=='__main__':
	app.run_server(debug=True)