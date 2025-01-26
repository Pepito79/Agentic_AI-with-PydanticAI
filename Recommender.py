#!/usr/bin/env python3
import pandas as pd 

mv = pd.read_csv("./tmdb_5000_movies.csv")
mv_credit=pd.read_csv("./tmdb_5000_credits.csv")

mv=mv.merge(mv_credit,on='title')
print(mv.shape)
