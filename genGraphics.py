import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from paths import GRAPHS
import xml.etree.ElementTree as ET

#Defining all dataframes
df_columns = ['id', 'duration', 'routeLength' , 'rerouteNo', 'CO_abs', 'CO2_abs', 'HC_abs', 'PMx_abs', 'NOx_abs', 'fuel_abs']
Greenshield_DSP = pd.DataFrame(columns = df_columns)
Greenshield_RkSP = pd.DataFrame(columns = df_columns)
Greenshield_EBkSP = pd.DataFrame(columns = df_columns)
Other_DSP = pd.DataFrame(columns = df_columns)
Other_RkSP = pd.DataFrame(columns = df_columns)
Other_EBkSP = pd.DataFrame(columns = df_columns)
Drake_DSP = pd.DataFrame(columns = df_columns)
Drake_RkSP = pd.DataFrame(columns = df_columns)
Drake_EBkSP = pd.DataFrame(columns = df_columns)
Greenberg_DSP = pd.DataFrame(columns = df_columns)
Greenberg_RkSP = pd.DataFrame(columns = df_columns)
Greenberg_EBkSP = pd.DataFrame(columns = df_columns)
Underwood_DSP = pd.DataFrame(columns = df_columns)
Underwood_RkSP = pd.DataFrame(columns = df_columns)
Underwood_EBkSP = pd.DataFrame(columns = df_columns)

def genGraphTravelTime():
    labels = ['Greenshield - DSP', 'Drake - DSP', 'Greenberg - DSP', 'Underwood - DSP']
    values = [Greenshield_DSP.duration, Drake_DSP.duration, Greenberg_DSP.duration, Underwood_DSP.duration]

    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_xlabel('Model')
    ax.set_xticklabels(labels)

    ax.set_ylabel('Travel Time')
    fig.savefig("%s/DSP_TravelTime.png"%(GRAPHS))

    labels = ['Greenshield - RkSP', 'Drake - RkSP', 'Greenberg - RkSP', 'Underwood - RkSP']
    values = [Greenshield_RkSP.duration, Drake_RkSP.duration, Greenberg_RkSP.duration, Underwood_RkSP.duration]

    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_xlabel('Model')
    ax.set_xticklabels(labels)

    ax.set_ylabel('Travel Time')
    plt.savefig("%s/RkSP_TravelTime.png"%(GRAPHS))

    labels = ['Greenshield - EBkSP', 'Drake - EBkSP', 'Greenberg - EBkSP', 'Underwood - EBkSP']
    values = [Greenshield_EBkSP.duration, Drake_EBkSP.duration, Greenberg_EBkSP.duration, Underwood_EBkSP.duration]

    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_xlabel('Model')
    ax.set_xticklabels(labels)

    ax.set_ylabel('Travel Time')
    plt.savefig("%s/EBkSP_TravelTime.png"%(GRAPHS))


def xmlToDataframe(path):
  prstree = ET.parse(path)
  root = prstree.getroot()

  rows = []
    
  for tripinfo in root.iter('tripinfo'):
      id = tripinfo.attrib.get('id')
      duration = float(tripinfo.attrib.get('duration'))
      routeLength = float(tripinfo.attrib.get('routeLength'))
      rerouteNo = int(tripinfo.attrib.get('rerouteNo'))
      CO_abs = float(tripinfo.find('emissions').attrib.get('CO_abs'))
      CO2_abs = float(tripinfo.find('emissions').attrib.get('CO2_abs'))
      HC_abs = float(tripinfo.find('emissions').attrib.get('HC_abs'))
      PMx_abs = float(tripinfo.find('emissions').attrib.get('PMx_abs'))
      NOx_abs = float(tripinfo.find('emissions').attrib.get('NOx_abs'))
      fuel_abs = float(tripinfo.find('emissions').attrib.get('fuel_abs'))

      rows.append([id, duration, routeLength, rerouteNo, CO_abs, CO2_abs, HC_abs, PMx_abs, NOx_abs, fuel_abs])
    
  return pd.DataFrame(rows, columns=['id', 'duration', 'routeLength' , 'rerouteNo', 'CO_abs', 'CO2_abs', 'HC_abs', 'PMx_abs', 'NOx_abs', 'fuel_abs'])


def genDf(path, DSP_df, RkSP_df, EBkSP_df, seed):
    df = xmlToDataframe("%sOutputs_DSP/reroute_DSP_%d.xml"%(path, seed))
    DSP_df = DSP_df.append(df)
    #print(DSP_df.head())
    df = xmlToDataframe("%sOutputs_RkSP/reroute_RkSP_%d.xml"%(path, seed))
    RkSP_df = RkSP_df.append(df)
    df = xmlToDataframe("%sOutputs_EBkSP/reroute_EBkSP_%d.xml"%(path, seed))
    EBkSP_df = EBkSP_df.append(df)


if __name__ == '__main__':

    print("Type the number of seeds\n")
    seeds = int(input())
    i = 0
    root = os.getcwd()

    while(i < seeds):

        print("Processing the linear models\n")
        print("Greenshield\n")
        new_path = ("Linear_models/Greenshield/")
        df = xmlToDataframe("%sOutputs_DSP/reroute_DSP_%d.xml"%(new_path, i))
        Greenshield_DSP = Greenshield_DSP.append(df)
        #print(DSP_df.head())
        df = xmlToDataframe("%sOutputs_RkSP/reroute_RkSP_%d.xml"%(new_path, i))
        Greenshield_RkSP = Greenshield_RkSP.append(df)
        df = xmlToDataframe("%sOutputs_EBkSP/reroute_EBkSP_%d.xml"%(new_path, i))
        Greenshield_EBkSP = Greenshield_EBkSP.append(df)

        #print("Other\n")
        #new_path = ("%s/Linear_models/Other/"%(root))
        #genDf(new_path, Other_DSP, Other_RkSP, Other_EBkSP, i)

        print("Processing the logarithm models\n")
        print("Drake\n")
        new_path = ("Logarithm_models/Drake/")
        df = xmlToDataframe("%sOutputs_DSP/reroute_DSP_%d.xml"%(new_path, i))
        Drake_DSP = Drake_DSP.append(df)
        df = xmlToDataframe("%sOutputs_RkSP/reroute_RkSP_%d.xml"%(new_path, i))
        Drake_RkSP = Drake_RkSP.append(df)
        df = xmlToDataframe("%sOutputs_EBkSP/reroute_EBkSP_%d.xml"%(new_path, i))
        Drake_EBkSP = Drake_EBkSP.append(df)

        print("Greenberg\n")
        new_path = ("Logarithm_models/Greenberg/")
        df = xmlToDataframe("%sOutputs_DSP/reroute_DSP_%d.xml"%(new_path, i))
        Greenberg_DSP = Greenberg_DSP.append(df)
        df = xmlToDataframe("%sOutputs_RkSP/reroute_RkSP_%d.xml"%(new_path, i))
        Greenberg_RkSP = Greenberg_RkSP.append(df)
        df = xmlToDataframe("%sOutputs_EBkSP/reroute_EBkSP_%d.xml"%(new_path, i))
        Greenberg_EBkSP = Greenberg_EBkSP.append(df)

        print("Underwood\n")
        new_path = ("Logarithm_models/Underwood/")
        df = xmlToDataframe("%sOutputs_DSP/reroute_DSP_%d.xml"%(new_path, i))
        Underwood_DSP = Underwood_DSP.append(df)
        df = xmlToDataframe("%sOutputs_RkSP/reroute_RkSP_%d.xml"%(new_path, i))
        Underwood_RkSP = Underwood_RkSP.append(df)
        df = xmlToDataframe("%sOutputs_EBkSP/reroute_EBkSP_%d.xml"%(new_path, i))
        Underwood_EBkSP = Underwood_EBkSP.append(df)

        i = i + 1

    genGraphTravelTime()
    print("Saved all graphics in the respective directory")

