#! /usr/bin/env python3
# coding: utf-8

import datetime
import os.path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from urllib import request

class vacdata():
    """Classe dealing with vaccination datas"""
    def __init__(self):
        """Initialisating by importing worlindata datas"""
        if not os.path.exists('vaccinations.csv'):
            request.urlretrieve ("https://raw.github.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv", "vaccinations.csv")
            print('Données du jour importées')
        else:
            mod_date = datetime.datetime.fromtimestamp(os.path.getmtime("vaccinations.csv"))
            if not mod_date.date() == datetime.date.today():
                request.urlretrieve ("https://raw.github.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv", "vaccinations.csv")
                print('Données du jour importées')

        self.vaccinations=pd.read_csv("vaccinations.csv")
        
    def clean(self):
        """Replace NaN by 0"""

        self.vaccinations.people_vaccinated_per_hundred = self.vaccinations.groupby(['location']).people_vaccinated_per_hundred.ffill().fillna(0)
        self.vaccinations.people_fully_vaccinated_per_hundred = self.vaccinations.groupby(['location']).people_fully_vaccinated_per_hundred.ffill().fillna(0)
        self.vaccinations.fillna(0, inplace=True)
     
    def doses_by_day(self):
        """Create columns 'number od days since start of vaccination', 'number of first doses', number of second doses'"""
        #Create a datetime type column
        self.vaccinations['dt_date'] = pd.to_datetime(self.vaccinations.date)
        for loc in self.vaccinations.location.unique():
            #get number of days since start of vaccination by country
            dates = self.vaccinations[self.vaccinations.location==loc]['dt_date']
            date1 = self.vaccinations[self.vaccinations.location==loc]['dt_date'].iloc[0]
            self.vaccinations.loc[self.vaccinations.location==loc,'days_vac'] = dates - date1

        self.vaccinations['days_vac'] = pd.to_timedelta(self.vaccinations['days_vac'],unit='d').astype('timedelta64[D]')
        
        #get number of first and second doses, clean negative values
        self.vaccinations['first_dose'] = self.vaccinations.people_vaccinated.diff()
        self.vaccinations.first_dose = np.where(self.vaccinations.first_dose < 0, 0, self.vaccinations.first_dose)
        self.vaccinations['second_dose'] = self.vaccinations.people_fully_vaccinated.diff()
        self.vaccinations.second_dose = np.where(self.vaccinations.second_dose < 0, 0, self.vaccinations.second_dose)        

        for loc in self.vaccinations.location.unique():
            #set the first day diff, by total number of the first day 
            ind_first = self.vaccinations[self.vaccinations.location==loc].index[0]
            vac_d1 = self.vaccinations[self.vaccinations.location==loc]['people_vaccinated'].iloc[0]
            self.vaccinations.loc[ind_first,'first_dose'] = vac_d1
            ind_first = self.vaccinations[self.vaccinations.location==loc].index[0]
            vac_d1 = self.vaccinations[self.vaccinations.location==loc]['people_fully_vaccinated'].iloc[0]
            self.vaccinations.loc[ind_first,'second_dose'] = vac_d1
   
    def truncate(self,loc,val):
        """Truncate absurd first and second doses values"""
        self.vaccinations.loc[self.vaccinations.location==loc,'first_dose'] = np.where(self.vaccinations[self.vaccinations.location==loc].first_dose > val, 0, self.vaccinations[self.vaccinations.location==loc].first_dose)
        self.vaccinations.loc[self.vaccinations.location==loc,'second_dose'] = np.where(self.vaccinations[self.vaccinations.location==loc].second_dose > val, 0, self.vaccinations[self.vaccinations.location==loc].second_dose)
            
    def plot_doses_by_day(self,loc):
        """Create two plots, one with nimber of first doses since beginning of vaccination, one with seconde doses"""
        #FIRST DOSES SUBGRAPH
        plt.subplot(211)
        plt.title('Vaccination quotidienne: {}'.format(loc))
        plt.xticks(np.arange(0, len(self.vaccinations[self.vaccinations.location==loc]), step=7))
#        plt.yticks(np.arange(0, self.vaccinations[self.vaccinations.location==loc].first_dose.max()+20000, step=))
        plt.xlabel('Jours écoulés')
        plt.ylabel('Premières doses')
        plt.bar(self.vaccinations[self.vaccinations.location==loc].days_vac, self.vaccinations[self.vaccinations.location==loc].first_dose)
        locs, labels = plt.yticks()  
        #SECOND DOSES SUBGRAPH
        plt.subplot(212)
        plt.bar(self.vaccinations[self.vaccinations.location==loc].days_vac, self.vaccinations[self.vaccinations.location==loc].second_dose)
        plt.xticks(np.arange(0, len(self.vaccinations[self.vaccinations.location==loc]), step=7))
#        plt.yticks(np.arange(0, self.vaccinations[self.vaccinations.location==loc].first_dose.max()+20000, step=3))
        plt.yticks(locs)
        plt.xlabel('Jours écoulés')
        plt.ylabel('Secondes doses')
        
    def plot_doses_by_date(self,loc):
        """Create two plots, one with nimber of first doses since beginning of vaccination, one with seconde doses"""
        #FIRST DOSES SUBGRAPH
        plt.subplot(211)
        plt.title('Vaccination quotidienne: {}'.format(loc))
        plt.xlabel('Mois')
        plt.ylabel('Premières doses')
        plt.bar(self.vaccinations[self.vaccinations.location==loc].dt_date, self.vaccinations[self.vaccinations.location==loc].first_dose,width=np.timedelta64(12, 'h'))
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
        plt.gcf().autofmt_xdate()
        locs_y, labels_y = plt.yticks()  
        locs_x, labels_x = plt.xticks()  
        
        #FIRST DOSES SUBGRAPH
        plt.subplot(212)
        plt.bar(self.vaccinations[self.vaccinations.location==loc].dt_date, self.vaccinations[self.vaccinations.location==loc].second_dose,width=np.timedelta64(12, 'h'))
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
        plt.gcf().autofmt_xdate()
        plt.yticks(locs_y)
        plt.xticks(locs_x)
        plt.xlabel('Mois')
        plt.ylabel('Secondes doses')
        

    def plot_per_hundred_by_date(self,loc):
        """Create a plot with two function: the percentage of people vaccinated and percentage of people fully vaccinated"""
        
        mask = self.vaccinations.location == loc
        
        plt.title('Pourcentage de personne vaccinées: {}'.format(loc))
        plt.xlabel('Mois')
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
        plt.gcf().autofmt_xdate()
        plt.plot(self.vaccinations[mask].dt_date, self.vaccinations[mask].people_vaccinated_per_hundred, self.vaccinations[mask].dt_date, self.vaccinations[mask].people_fully_vaccinated_per_hundred)
        plt.legend(['Vaccinés','Complétement Vaccinés'])
            
            
