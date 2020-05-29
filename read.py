import pandas as pd
import stockapi as sapi
import regression
import pickle


df = pickle.load(open( "save.p", "rb" ))

print(df)
