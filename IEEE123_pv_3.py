# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 09:00:27 2021

@author: luisf
"""

#IEEE 123 - Barras
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import dss
dss_engine = dss.DSS

dss_engine.Text.Command = r'compile "C:\Users\luisf\OneDrive\Documentos\IC\123Bus\IEEE123Master.dss"'

#Plotando o circuito'
dss_engine.Text.Command = 'Buscoords BusCoords.dat'

#Energy meter para contabilizar as perdas'
dss_engine.Text.Command = 'new energymeter.medidorSource element=transformer.reg1a terminal=1'

horas = np.linspace(0,23,24)

#cargas
num_cargas = dss_engine.ActiveCircuit.Loads.Count
cargas_FV = int(round(0.6*num_cargas))
cargas_ind = int(round(0.05*cargas_FV))
cargas_com = int(round(0.1*cargas_FV))
cargas_res = int(round(0.85*cargas_FV))
print(f'\nO sistema tem {num_cargas} cargas')
print(f'O número de cargas em que um sistema FV será conectado é {cargas_FV+1}')
print(f'{cargas_ind} cargas com Load Shape Industrial')
print(f'{cargas_com} cargas com Load Shape Comercial')
print(f'{cargas_res} cargas com Load Shape Residencial\n')


eres = pd.DataFrame.to_numpy(pd.read_csv('loadshapeR.csv', header=None,dtype='float'))
ecom = pd.DataFrame.to_numpy(pd.read_csv('loadshapeCOM.csv', header=None,dtype='float'))
eind = pd.DataFrame.to_numpy(pd.read_csv('loadshapeIND.csv', header=None,dtype='float'))


dss_engine.Text.Command = 'New loadshape.residencial npts=24 interval=1 mult=(file=loadshapeR.csv)'
dss_engine.Text.Command = 'New loadshape.comercial npts=24 interval=1 mult=(file=loadshapeCOM.csv)'
dss_engine.Text.Command = 'New loadshape.industrial npts=24 interval=1 mult=(file=loadshapeIND.csv)'

meter_names = dss_engine.ActiveCircuit.Meters.RegisterNames
ll = meter_names.index('Line Losses')
tl = meter_names.index('Transformer Losses')
ldl = meter_names.index('Load Losses kWh')
nll = meter_names.index('No Load Losses kWh')
eng = meter_names.index('kWh')

for ld in dss_engine.ActiveCircuit.Loads:
    if ld.kW >= 100:
        ld.daily = 'industrial'
    elif (ld.kW >= 60) and (ld.kW < 100):
        ld.daily = 'comercial'
    else:
        ld.daily = 'residencial'

#função para dimensionar o PV system
def pv_power(daily,horas,load_power):
    Daily = np.zeros(len(daily))
    #multiplicação pela potencia da carga
    for i in range(len(daily)):
        Daily[i] = daily[i]*load_power
    #consumo diario em kW
    Edaily = np.trapz(Daily,horas)
    HSP = 4.68
    #demanda em kWp
    demanda = Edaily/HSP
    return demanda

#elaborando pv systems
#curva potência por temperatura
dss_engine.Text.Command = 'New XYcurve.MyPvst npts=4 xarray=[0 25 75 100] yarray=[1.2 1 0.8 0.6]'
#curva eficiencia inversor
dss_engine.Text.Command = 'New XYcurve.MyEff npts=4 xarray=[0.1 0.2 0.4 1] yarray=[0.86 0.9 0.93 0.97]'
#curva de irradiação
dss_engine.Text.Command = 'New loadshape.MyIrrad npts=24 interval=1 mult=[0 0 0 0 0 0 .1 .2 .3  .5  .8  .9  1.0  1.0  .99  .9  .7  .4  .1 0  0  0  0  0]'
#temperatura diaria no painel
dss_engine.Text.Command = 'New Tshape.MyTemp npts=24 interval=1 temp=[25 25 25 25 25 25 25 25 25 25 25 25 25 25 25 25 25 25  25 25 25 25 25 25]'

#cargas
pv_loads = ['s47','s48','s76a','s49b', 's64b','s66c', 's76c','s65c','s76b', 's17c', 's19a', 's22b', 's32c', 's34c', 's39b', 's46a', 's77b', 's83c', 's86b', 's94a', 's96b', 's102c', 's111a', 's49a','s10a','s12b','s20a','s31c','s38b','s41c','s42a','s45a','s49c','s51a','s53a','s55a','s56b','s58b','s60a','s63a','s65a','s68a','s70a','s79a', 's5c','s10a','s12b','s24c','s7a','s11a','s100c','s112a','s103c','s88a','s104c','s109a']
load_power_bus = {}
for load in dss_engine.ActiveCircuit.Loads:
    load_power_bus[load.Name.lower()] = (load.kW , dss_engine.ActiveCircuit.ActiveCktElement.BusNames[0], ld.kV)
load_data = []
pv_kw = []

for i in range(len(pv_loads)):
    load_data.append(load_power_bus[pv_loads[i]])
    if i <= 2:
        pv_kw.append(pv_power(eind,horas,load_data[i][0]))
    elif (i >= 3) and (i <= 8):
        pv_kw.append(pv_power(ecom,horas,load_data[i][0]))
    else:
        pv_kw.append(pv_power(eres,horas,load_data[i][0]))

#criando os Pv's
dss_engine.Text.Command = f'New PVSystem.Pv_ind1 phases=3 bus1={load_data[0][1]} kv={load_data[0][2]} kva={pv_kw[0]} irrad=0.98 pmpp={pv_kw[0]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_ind2 phases=3 bus1={load_data[1][1]} kv={load_data[1][2]} kva={pv_kw[1]} irrad=0.98 pmpp={pv_kw[1]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_ind3 phases=1 bus1={load_data[2][1]} kv={load_data[2][2]} kva={pv_kw[2]} irrad=0.98 pmpp={pv_kw[2]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com1 phases=1 bus1={load_data[3][1]} kv={load_data[3][2]} kva={pv_kw[3]} irrad=0.98 pmpp={pv_kw[3]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com2 phases=1 bus1={load_data[4][1]} kv={load_data[4][2]} kva={pv_kw[4]} irrad=0.98 pmpp={pv_kw[4]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com3 phases=1 bus1={load_data[5][1]} kv={load_data[5][2]} kva={pv_kw[5]} irrad=0.98 pmpp={pv_kw[5]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com4 phases=1 bus1={load_data[6][1]} kv={load_data[6][2]} kva={pv_kw[6]} irrad=0.98 pmpp={pv_kw[6]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com5 phases=1 bus1={load_data[7][1]} kv={load_data[7][2]} kva={pv_kw[7]} irrad=0.98 pmpp={pv_kw[7]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com6 phases=1 bus1={load_data[8][1]} kv={load_data[8][2]} kva={pv_kw[8]} irrad=0.98 pmpp={pv_kw[8]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res1 phases=1 bus1={load_data[9][1]} kv={load_data[9][2]} kva={pv_kw[9]} irrad=0.98 pmpp={pv_kw[9]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res2 phases=1 bus1={load_data[10][1]} kv={load_data[10][2]} kva={pv_kw[10]} irrad=0.98 pmpp={pv_kw[10]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res3 phases=1 bus1={load_data[11][1]} kv={load_data[11][2]} kva={pv_kw[11]} irrad=0.98 pmpp={pv_kw[11]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res4 phases=1 bus1={load_data[12][1]} kv={load_data[12][2]} kva={pv_kw[12]} irrad=0.98 pmpp={pv_kw[12]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res5 phases=1 bus1={load_data[13][1]} kv={load_data[13][2]} kva={pv_kw[13]} irrad=0.98 pmpp={pv_kw[13]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res6 phases=1 bus1={load_data[14][1]} kv={load_data[14][2]} kva={pv_kw[14]} irrad=0.98 pmpp={pv_kw[14]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res7 phases=1 bus1={load_data[15][1]} kv={load_data[15][2]} kva={pv_kw[15]} irrad=0.98 pmpp={pv_kw[15]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res8 phases=1 bus1={load_data[16][1]} kv={load_data[16][2]} kva={pv_kw[16]} irrad=0.98 pmpp={pv_kw[16]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res9 phases=1 bus1={load_data[17][1]} kv={load_data[17][2]} kva={pv_kw[17]} irrad=0.98 pmpp={pv_kw[17]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res10 phases=1 bus1={load_data[18][1]} kv={load_data[18][2]} kva={pv_kw[18]} irrad=0.98 pmpp={pv_kw[18]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res11 phases=1 bus1={load_data[19][1]} kv={load_data[19][2]} kva={pv_kw[19]} irrad=0.98 pmpp={pv_kw[19]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res12 phases=1 bus1={load_data[20][1]} kv={load_data[20][2]} kva={pv_kw[20]} irrad=0.98 pmpp={pv_kw[20]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res13 phases=1 bus1={load_data[21][1]} kv={load_data[21][2]} kva={pv_kw[21]} irrad=0.98 pmpp={pv_kw[21]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res14 phases=1 bus1={load_data[22][1]} kv={load_data[22][2]} kva={pv_kw[22]} irrad=0.98 pmpp={pv_kw[22]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res15 phases=1 bus1={load_data[23][1]} kv={load_data[23][2]} kva={pv_kw[23]} irrad=0.98 pmpp={pv_kw[23]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res16 phases=1 bus1={load_data[24][1]} kv={load_data[24][2]} kva={pv_kw[24]} irrad=0.98 pmpp={pv_kw[24]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res17 phases=1 bus1={load_data[25][1]} kv={load_data[25][2]} kva={pv_kw[25]} irrad=0.98 pmpp={pv_kw[25]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res18 phases=1 bus1={load_data[26][1]} kv={load_data[26][2]} kva={pv_kw[26]} irrad=0.98 pmpp={pv_kw[26]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res19 phases=1 bus1={load_data[27][1]} kv={load_data[27][2]} kva={pv_kw[27]} irrad=0.98 pmpp={pv_kw[27]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res20 phases=1 bus1={load_data[28][1]} kv={load_data[28][2]} kva={pv_kw[28]} irrad=0.98 pmpp={pv_kw[28]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res21 phases=1 bus1={load_data[29][1]} kv={load_data[29][2]} kva={pv_kw[29]} irrad=0.98 pmpp={pv_kw[29]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res22 phases=1 bus1={load_data[30][1]} kv={load_data[30][2]} kva={pv_kw[30]} irrad=0.98 pmpp={pv_kw[30]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res23 phases=1 bus1={load_data[31][1]} kv={load_data[31][2]} kva={pv_kw[31]} irrad=0.98 pmpp={pv_kw[31]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res24 phases=1 bus1={load_data[32][1]} kv={load_data[32][2]} kva={pv_kw[32]} irrad=0.98 pmpp={pv_kw[32]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res25 phases=1 bus1={load_data[33][1]} kv={load_data[33][2]} kva={pv_kw[33]} irrad=0.98 pmpp={pv_kw[33]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res26 phases=1 bus1={load_data[34][1]} kv={load_data[34][2]} kva={pv_kw[34]} irrad=0.98 pmpp={pv_kw[34]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res27 phases=1 bus1={load_data[35][1]} kv={load_data[35][2]} kva={pv_kw[35]} irrad=0.98 pmpp={pv_kw[35]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res28 phases=1 bus1={load_data[36][1]} kv={load_data[36][2]} kva={pv_kw[36]} irrad=0.98 pmpp={pv_kw[36]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res29 phases=1 bus1={load_data[37][1]} kv={load_data[37][2]} kva={pv_kw[37]} irrad=0.98 pmpp={pv_kw[37]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res30 phases=1 bus1={load_data[38][1]} kv={load_data[38][2]} kva={pv_kw[38]} irrad=0.98 pmpp={pv_kw[38]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res31 phases=1 bus1={load_data[39][1]} kv={load_data[39][2]} kva={pv_kw[39]} irrad=0.98 pmpp={pv_kw[39]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res32 phases=1 bus1={load_data[40][1]} kv={load_data[40][2]} kva={pv_kw[40]} irrad=0.98 pmpp={pv_kw[40]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res33 phases=1 bus1={load_data[41][1]} kv={load_data[41][2]} kva={pv_kw[41]} irrad=0.98 pmpp={pv_kw[41]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res34 phases=1 bus1={load_data[42][1]} kv={load_data[42][2]} kva={pv_kw[42]} irrad=0.98 pmpp={pv_kw[42]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res35 phases=1 bus1={load_data[43][1]} kv={load_data[43][2]} kva={pv_kw[43]} irrad=0.98 pmpp={pv_kw[43]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res36 phases=1 bus1={load_data[44][1]} kv={load_data[44][2]} kva={pv_kw[44]} irrad=0.98 pmpp={pv_kw[44]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res37 phases=1 bus1={load_data[45][1]} kv={load_data[45][2]} kva={pv_kw[45]} irrad=0.98 pmpp={pv_kw[45]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res38 phases=1 bus1={load_data[46][1]} kv={load_data[46][2]} kva={pv_kw[46]} irrad=0.98 pmpp={pv_kw[46]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res39 phases=1 bus1={load_data[47][1]} kv={load_data[47][2]} kva={pv_kw[47]} irrad=0.98 pmpp={pv_kw[47]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res40 phases=1 bus1={load_data[48][1]} kv={load_data[48][2]} kva={pv_kw[48]} irrad=0.98 pmpp={pv_kw[48]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res41 phases=1 bus1={load_data[49][1]} kv={load_data[49][2]} kva={pv_kw[49]} irrad=0.98 pmpp={pv_kw[49]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res42 phases=1 bus1={load_data[50][1]} kv={load_data[50][2]} kva={pv_kw[50]} irrad=0.98 pmpp={pv_kw[50]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res43 phases=1 bus1={load_data[51][1]} kv={load_data[51][2]} kva={pv_kw[51]} irrad=0.98 pmpp={pv_kw[51]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res44 phases=1 bus1={load_data[52][1]} kv={load_data[52][2]} kva={pv_kw[52]} irrad=0.98 pmpp={pv_kw[52]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res45 phases=1 bus1={load_data[53][1]} kv={load_data[53][2]} kva={pv_kw[53]} irrad=0.98 pmpp={pv_kw[53]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res46 phases=1 bus1={load_data[54][1]} kv={load_data[54][2]} kva={pv_kw[54]} irrad=0.98 pmpp={pv_kw[54]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res47 phases=1 bus1={load_data[55][1]} kv={load_data[55][2]} kva={pv_kw[55]} irrad=0.98 pmpp={pv_kw[55]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'

line_loss_pv = []
transf_loss_pv = []
load_loss_pv = []
no_load_loss_pv = []

#energia injetada
energy = []

dss_engine.Text.Command = 'set mode=daily'
dss_engine.Text.Command = 'set stepsize=1h'
print('Análise com PV system\n')
for i in range(len(horas)):
    dss_engine.Text.Command = 'set number = 1'
    dss_engine.ActiveCircuit.Solution.Solve()

    for em in dss_engine.ActiveCircuit.Meters:
        loss = em.RegisterValues
        line_loss_pv.append(loss[ll])
        transf_loss_pv.append(loss[tl])
        load_loss_pv.append(loss[ldl])
        no_load_loss_pv.append(loss[nll])
        energy.append(loss[eng])
        
    #monitorando as tensões maxima e minima 
    vpu_pv = dss_engine.ActiveCircuit.AllBusVmagPu
    vmax = np.round(np.max(vpu_pv),2)
    if vmax > 1.05:
        print('Há Sobretensão!')
    print('-'*50)
    print(f'A tensão máxima no instante {i} é {vmax}')
    vmin = np.round(np.min(vpu_pv),2)
    if vmin < 0.93:
        print('Há Subtensão!')
    print(f'A tensão mínima no instante {i} é {vmin}')
        
    #perfil de tensão
    Va = dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(1)
    Da = dss_engine.ActiveCircuit.AllNodeDistancesByPhase(1)
    Vb = dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(2)
    Db = dss_engine.ActiveCircuit.AllNodeDistancesByPhase(2)
    Vc = dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(3)
    Dc = dss_engine.ActiveCircuit.AllNodeDistancesByPhase(3)
    
    if i == 12:
        Va_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(1))
        Da_12 = dss_engine.ActiveCircuit.AllNodeDistancesByPhase(1)
        Vb_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(2))
        Db_12 = dss_engine.ActiveCircuit.AllNodeDistancesByPhase(2)
        Vc_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(3))
        Dc_12 = dss_engine.ActiveCircuit.AllNodeDistancesByPhase(3) 

Va_12.to_csv("VA12_pv3.csv",header= None ,index=None)
Vb_12.to_csv("VB12_pv3.csv",header= None ,index=None)
Vc_12.to_csv("VC12_pv3.csv",header= None ,index=None)

print('\n')
print('Perdas nos Transformadores:\n')
print(f'{transf_loss_pv}\n')
print('Perdas na Linha:\n')
print(f'{line_loss_pv}\n')
print('Perdas sob Carga:\n')
print(f'{load_loss_pv}\n')
print('Perdas no Load:\n')
print(f'{no_load_loss_pv}\n')

#perfil de tensao
plt.figure(figsize=(12,8))
plt.plot(Da,Va,'D',color = 'blue', label ='Va')
plt.plot(Db,Vb,'D',color = 'red', label = 'Vb')
plt.plot(Dc,Vc,'D',color = 'green', label = 'Vc')
plt.legend(loc ='best')
plt.xlabel('Distância do Energy Meter')
plt.ylabel('V [pu]')
plt.title('Perfil de Tensão - PV (60%)')

data = [Va, Vb, Vc] 
#perfil de tensao boxplot
plt.figure(figsize=(12,8))
plt.boxplot(data, vert=True, labels=('VA','VB','VC'))
plt.title('Perfil de Tensão - Box Plot - PV (60%)')
plt.ylabel('V [pu]')
plt.xlabel('Tensões por Fase')

#plotando perdas
plt.figure()
plt.plot(horas,transf_loss_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas nos Transformadores - PV (60%)')

#plotando perdas
plt.figure()
plt.plot(horas,line_loss_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas na Linha - PV (60%)')

#plotando perdas
plt.figure()
plt.plot(horas,load_loss_pv, color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas sob Carga - PV (60%)')

#plotando perdas
plt.figure()
plt.plot(horas,no_load_loss_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas No Load - PV (60%)')  

#NÃO ACUMULADAS
load_loss_NAC_pv = []
no_load_loss_NAC_pv = []
line_loss_NAC_pv = []
transf_loss_NAC_pv = []
for i in range(len(horas)):
    if i == 0:
        load_loss_NAC_pv.append(load_loss_pv[i])
        line_loss_NAC_pv.append(line_loss_pv[i])
        transf_loss_NAC_pv.append(transf_loss_pv[i])
        no_load_loss_NAC_pv.append(no_load_loss_pv[i])
    else:
        load_loss_NAC_pv.append(load_loss_pv[i] - load_loss_pv[i-1])
        line_loss_NAC_pv.append(line_loss_pv[i] - line_loss_pv[i-1])
        transf_loss_NAC_pv.append(transf_loss_pv[i] - transf_loss_pv[i-1])
        no_load_loss_NAC_pv.append(no_load_loss_pv[i] - no_load_loss_pv[i-1])

print('\n')
print('Perdas nos Transformadores não acumuladas:\n')
print(f'{transf_loss_NAC_pv}\n')
print('Perdas na Linha não acumuladas:\n')
print(f'{line_loss_NAC_pv}\n')
print('Perdas sob Carga não acumuladas:\n')
print(f'{load_loss_NAC_pv}\n')


#plotando perdas
plt.figure()
plt.plot(horas,transf_loss_NAC_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas nos Transformadores Não acumulado - PV (60%)')

#plotando perdas
plt.figure()
plt.plot(horas,line_loss_NAC_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas na Linha Não acumulado - PV (60%)')

#plotando perdas
plt.figure()
plt.plot(horas,load_loss_NAC_pv, color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas sob Carga Não acumulado - PV (60%)')

#plotando perdas
plt.figure()
plt.plot(horas,no_load_loss_NAC_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas No Load Não acumulado - PV (60%)')


#energia injetada na rede ao longo do dia
energy_NAC = []
for i in range(len(energy)):
    if i == 0:
        energy_NAC.append(energy[i])
    else:
        energy_NAC.append(energy[i]-energy[i-1])
        
plt.figure(figsize=(12,8))
plt.plot(horas,energy_NAC,color='m')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Energia injetada na rede ao longo do dia - PV (60%)')
