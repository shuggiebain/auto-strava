# Strava_Performance_Analysis
A python library that automates the STRAVA Oauth process using automatic Facebook login through selenium, extracts athlete activity data and generates basic visualizations. 

Reference for Strava API authentication process: 
https://developers.strava.com/docs/authentication/

Pre-requisites: 
- Register Client application on Strava 
- Gather App credentials from Strava
- Update Project config file in this repo with your credentials
- Selenium - executable chrome driver file downloaded and stored locally - pass path to executable in config file 

Visualization Samples: 

- ![monthly_mileage](https://github.com/nahar-senior/strava-performance-analysis/blob/master/visualizations/monthly_mileage.jpg?raw=true)

- ![runs_breakdown](https://github.com/nahar-senior/strava-performance-analysis/blob/master/visualizations/runs_breakdown.jpg?raw=true)

- ![speed_over_distance](https://github.com/nahar-senior/strava-performance-analysis/blob/master/visualizations/speed_over_distance.jpg?raw=true)

- ![time_over_distance](https://github.com/nahar-senior/strava-performance-analysis/blob/master/visualizations/time_over_distance.jpg?raw=true)

#TODO 
1. Heart rate zones visualizations
2. GPS coordinates visualizations
3. Marathon / Half-Marathon time predicter using a regression model 
4. Add params for additional login methods eg email, google etc. 
