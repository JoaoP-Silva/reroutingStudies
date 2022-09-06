import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from paths import GRAPHS
import xml.etree.ElementTree as ET
from datetime import datetime
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
GreenbergUnderwood_DSP = pd.DataFrame(columns = df_columns)
GreenbergUnderwood_RkSP = pd.DataFrame(columns = df_columns)
GreenbergUnderwood_EBkSP = pd.DataFrame(columns = df_columns)

def genGraphTravelTime():
    labels = ['Greenshield - DSP', 'Drake - DSP', 'Greenberg - DSP', 'G/U - DSP']
    values = [Greenshield_DSP.duration, Drake_DSP.duration, Greenberg_DSP.duration, GreenbergUnderwood_DSP.duration]

    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_xlabel('Model')
    ax.set_xticklabels(labels)

    ax.set_ylabel('Travel Time')
    fig.savefig("%s/DSP_TravelTime.png"%(GRAPHS))

    labels = ['Greenshield - RkSP', 'Drake - RkSP', 'Greenberg - RkSP', 'G/U - RkSP']
    values = [Greenshield_RkSP.duration, Drake_RkSP.duration, Greenberg_RkSP.duration, GreenbergUnderwood_RkSP.duration]

    fig, ax = plt.subplots()
    ax.boxplot(values)
    ax.set_xlabel('Model')
    ax.set_xticklabels(labels)

    ax.set_ylabel('Travel Time')
    plt.savefig("%s/RkSP_TravelTime.png"%(GRAPHS))

    labels = ['Greenshield - EBkSP', 'Drake - EBkSP', 'Greenberg - EBkSP', 'G/U - EBkSP']
    values = [Greenshield_EBkSP.duration, Drake_EBkSP.duration, Greenberg_EBkSP.duration, GreenbergUnderwood_EBkSP.duration]

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

def genConfInterval_hist(data_list, metric):
    Greenshield = data_list[0]
    Drake = data_list[1]
    Greenberg = data_list[2]
    GU = data_list[3]

    f = open("%s/Percentile_%s.txt"%(GRAPHS, metric),"a")
    mean_Greenshield = np.mean(Greenshield)
    mean_Drake = np.mean(Drake)
    mean_Greenberg = np.mean(Greenberg)
    mean_GU = np.mean(GU)
    IC_Greenshield = "[%f, %f]"%(np.percentile(Greenshield, 2.5), np.percentile(Greenshield, 97.5))
    IC_Drake = "[%f, %f]"%(np.percentile(Drake, 2.5), np.percentile(Drake, 97.5))
    IC_Greenberg = "[%f, %f]"%(np.percentile(Greenberg, 2.5), np.percentile(Greenberg, 97.5))
    IC_GU = "[%f, %f]"%(np.percentile(GU, 2.5), np.percentile(GU, 97.5))
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    IC_info = "Data info generated at %s\nGreenshield = %s\nDrake = %s\nGreenberg = %s\nGU = %s\n"%(dt_string, IC_Greenshield, IC_Drake, IC_Greenberg, IC_GU)
    f.write(IC_info)
    plt.hist(Greenshield, bins=30, edgecolor='k', label = 'Greenshield')
    plt.hist(Drake, bins=30, edgecolor='b', label = 'Drake')
    plt.hist(Greenberg, bins=30, edgecolor='grey', label = 'Greenberg')
    plt.hist(GU, bins=30, edgecolor='black', label = 'G/U')
    plt.xlabel('%s'%(metric))
    plt.ylabel('Amostras')
    plt.legend(loc='upper right')
    plt.savefig("%s/EBkSP_%s_ConfidenceInterval.png"%(GRAPHS, metric))
    print("Writting means on the file")
    f = open("%s/Percentile_%s.txt"%(GRAPHS, metric), "a")
    text = "Greenshield %s mean = %s\nDrake %s mean = %s\nGreenberg %s mean = %s\nGU %s mean = %s\n"%(metric, np.mean(Greenshield), metric, np.mean(Drake), metric, np.mean(Greenberg), metric, np.mean(GU))
    f.write(text)

def genConfInterval_bar(data_list, metric):
    Greenshield = data_list[0]
    Drake = data_list[1]
    Greenberg = data_list[2]
    GU = data_list[3]

    f = open("%s/Percentile_%s.txt"%(GRAPHS, metric),"a")
    mean_Greenshield = np.mean(Greenshield)
    mean_Drake = np.mean(Drake)
    mean_Greenberg = np.mean(Greenberg)
    mean_GU = np.mean(GU)
    IC_Greenshield = "[%f, %f]"%(np.percentile(Greenshield, 2.5), np.percentile(Greenshield, 97.5))
    IC_Drake = "[%f, %f]"%(np.percentile(Drake, 2.5), np.percentile(Drake, 97.5))
    IC_Greenberg = "[%f, %f]"%(np.percentile(Greenberg, 2.5), np.percentile(Greenberg, 97.5))
    IC_GU = "[%f, %f]"%(np.percentile(GU, 2.5), np.percentile(GU, 97.5))
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    IC_info = "Data info generated at %s\nGreenshield = %s\nDrake = %s\nGreenberg = %s\nGU = %s\n"%(dt_string, IC_Greenshield, IC_Drake, IC_Greenberg, IC_GU)
    f.write(IC_info)
    plt.hist(Greenshield, bins=30, edgecolor='k', label = 'Greenshield')
    plt.hist(Drake, bins=30, edgecolor='b', label = 'Drake')
    plt.hist(Greenberg, bins=30, edgecolor='grey', label = 'Greenberg')
    plt.hist(GU, bins=30, edgecolor='black', label = 'G/U')
    plt.xlabel('%s'%(metric))
    plt.ylabel('Amostras')
    plt.legend(loc='upper right')
    plt.savefig("%s/EBkSP_%s_ConfidenceInterval.png"%(GRAPHS, metric))
    print("Writting means on the file")
    f = open("%s/Percentile_%s.txt"%(GRAPHS, metric), "a")
    text = "Greenshield %s mean = %s\nDrake %s mean = %s\nGreenberg %s mean = %s\nGU %s mean = %s\n"%(metric, np.mean(Greenshield), metric, np.mean(Drake), metric, np.mean(Greenberg), metric, np.mean(GU))
    f.write(text)

def bootstrap_in(data_list, N):
    Greenshield = pd.Series(data_list[0])
    Drake = pd.Series(data_list[1])
    Greenberg = pd.Series(data_list[2])
    GU = pd.Series(data_list[3])

    size_Greenshield = len(Greenshield)
    size_Drake = len(Drake)
    size_Greenberg = len(Greenberg)
    size_GU = len(GU)
    values_Greenshield = np.zeros(N)
    values_Drake = np.zeros(N)
    values_Greenberg = np.zeros(N)
    values_GU = np.zeros(N)
    for i in range(N):
        sample_Greenshield = Greenshield.sample(size_Greenshield, replace = True)
        sample_Drake = Drake.sample(size_Drake, replace = True)
        sample_Greenberg = Greenberg.sample(size_Greenberg, replace = True)
        sample_GU = GU.sample(size_GU, replace = True)
        values_Greenshield[i] = sample_Greenshield.mean()
        values_Drake[i] = sample_Drake.mean()
        values_Greenberg[i] = sample_Greenberg.mean()
        values_GU[i] = sample_GU.mean()

    data_list[0] = values_Greenshield
    data_list[1] = values_Drake
    data_list[2] = values_Greenberg
    data_list[3] = values_GU
    print("Bootstrap done")

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

        print("Greenberg-Underwood\n")
        new_path = ("Logarithm_models/Greenberg-Underwood/")
        df = xmlToDataframe("%sOutputs_DSP/reroute_DSP_%d.xml"%(new_path, i))
        GreenbergUnderwood_DSP = GreenbergUnderwood_DSP.append(df)
        df = xmlToDataframe("%sOutputs_RkSP/reroute_RkSP_%d.xml"%(new_path, i))
        GreenbergUnderwood_RkSP = GreenbergUnderwood_RkSP.append(df)
        df = xmlToDataframe("%sOutputs_EBkSP/reroute_EBkSP_%d.xml"%(new_path, i))
        GreenbergUnderwood_EBkSP = GreenbergUnderwood_EBkSP.append(df)

        i = i + 1

    Greenshield_traveltime = Greenshield_EBkSP.duration
    Drake_traveltime = Drake_EBkSP.duration
    Greenberg_traveltime = Greenberg_EBkSP.duration
    GU_traveltime = GreenbergUnderwood_EBkSP.duration
    
    Greenshield_reroute_n = Greenshield_EBkSP.rerouteNo
    Drake_reroute_n = Drake_EBkSP.rerouteNo
    Greenberg_reroute_n = Greenberg_EBkSP.rerouteNo
    GU_reroute_n = GreenbergUnderwood_EBkSP.rerouteNo

    Greenshield_CO2 = Greenshield_EBkSP.CO2_abs
    Drake_CO2 = Drake_EBkSP.CO2_abs
    Greenberg_CO2 = Greenberg_EBkSP.CO2_abs
    GU_CO2 = GreenbergUnderwood_EBkSP.CO2_abs

    Greenshield_length = Greenshield_EBkSP.routeLength
    Drake_length = Drake_EBkSP.routeLength
    Greenberg_length = Greenberg_EBkSP.routeLength
    GU_length = GreenbergUnderwood_EBkSP.routeLength

    traveltime_l = [Greenshield_traveltime, Drake_traveltime, Greenberg_traveltime, GU_traveltime]
    reroute_n_l = [Greenshield_reroute_n, Drake_reroute_n, Greenberg_reroute_n, GU_reroute_n]
    CO2_l = [Greenshield_CO2, Drake_CO2, Greenberg_CO2, GU_CO2]
    length_l = [Greenshield_length, Drake_length, Greenberg_length, GU_length]

    metricList = [traveltime_l, reroute_n_l, CO2_l, length_l]
    print("Select metric\n1: traveltime\t2: reroute_n\t3: C02\t 4: routeLength")
    m_i = int(input()) - 1
    metrics = ["traveltime", "reroute_n", "C02", "routeLength"]
    metric = metrics[m_i]

    print("Applying bootstrap into data")
    bootstrap_in(metricList[m_i], 10000)

    print("Generating confidence interval")
    genConfInterval_bar(metricList[m_i], metric)
    print("Saved all graphics in the respective directory")

