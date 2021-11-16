# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 21:35:03 2021

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
cargas_FV = int(round(0.2*num_cargas))
cargas_ind = int(round(0.05*cargas_FV))
cargas_com = int(round(0.1*cargas_FV))
cargas_res = int(round(0.85*cargas_FV))
print(f'\nO sistema tem {num_cargas} cargas')
print(f'O número de cargas em que um sistema FV será conectado é {cargas_FV}')
print(f'{cargas_ind} cargas com Load Shape Industrial')
print(f'{cargas_com} cargas com Load Shape Comercial')
print(f'{cargas_res} cargas com Load Shape Residencial\n')

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
'''
eres = [0.544181,0.503066,0.473728,0.457491,0.454773,0.46662,0.489477,0.508223,0.508223,0.570523,0.590941,0.598676,0.605505,0.595052,0.595679,0.599791,0.628153,0.741045,0.770035,0.747247,0.718397,0.678537,0.618537,0.546202]
ecom = [0.40136901,0.38850789,0.37480289,0.36073353,0.36069369,0.3739083,0.43381697,0.54524834,0.64652918,0.71303683,0.74277494,0.75406056,0.7596092,0.76595754,0.770035,0.76087974,0.7423099,0.66241452,0.52092704,0.43910557,0.45288446,0.50072302,0.51768985,0.47370977]
eind = [0.5765252,0.5765252,0.58172294,0.57221301,0.57032642,0.59219542,0.64043811,0.69988481,0.74550939,0.76402873,0.76526078,0.76579981,0.76953448,0.770035,0.7611796,0.74254475,0.71767262,0.69326251,0.67624474,0.66869839,0.66619578,0.66099804,0.64594386,0.61633601]
'''
eres = pd.DataFrame.to_numpy(pd.read_csv('loadshapeR.csv', header=None,dtype='float'))
ecom = pd.DataFrame.to_numpy(pd.read_csv('loadshapeCOM.csv', header=None,dtype='float'))
eind = pd.DataFrame.to_numpy(pd.read_csv('loadshapeIND.csv', header=None,dtype='float'))

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
pv_loads = ['s48', 's64b', 's76c', 's17c', 's19a', 's22b', 's32c', 's34c', 's39b', 's46a', 's77b', 's83c', 's86b', 's94a', 's96b', 's102c', 's111a', 's49a']
load_power_bus = {}
for load in dss_engine.ActiveCircuit.Loads:
    load_power_bus[load.Name.lower()] = (load.kW , dss_engine.ActiveCircuit.ActiveCktElement.BusNames[0], ld.kV)
load_data = []
pv_kw = []

for i in range(len(pv_loads)):
    load_data.append(load_power_bus[pv_loads[i]])
    if i == 0:
        pv_kw.append(pv_power(eind,horas,load_data[i][0]))
    elif (i > 0) and (i < 3):
        pv_kw.append(pv_power(ecom,horas,load_data[i][0]))
    else:
        pv_kw.append(pv_power(eres,horas,load_data[i][0]))

#criando os Pv's
dss_engine.Text.Command = f'New PVSystem.Pv_ind phases=3 bus1={load_data[0][1]} kv={load_data[0][2]} kva={pv_kw[0]} irrad=0.98 pmpp={pv_kw[0]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com1 phases=1 bus1={load_data[1][1]} kv={load_data[1][2]} kva={pv_kw[1]} irrad=0.98 pmpp={pv_kw[1]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_com2 phases=1 bus1={load_data[2][1]} kv={load_data[2][2]} kva={pv_kw[2]} irrad=0.98 pmpp={pv_kw[2]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res1 phases=1 bus1={load_data[3][1]} kv={load_data[3][2]} kva={pv_kw[3]} irrad=0.98 pmpp={pv_kw[3]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res2 phases=1 bus1={load_data[4][1]} kv={load_data[4][2]} kva={pv_kw[4]} irrad=0.98 pmpp={pv_kw[4]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res3 phases=1 bus1={load_data[5][1]} kv={load_data[5][2]} kva={pv_kw[5]} irrad=0.98 pmpp={pv_kw[5]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res4 phases=1 bus1={load_data[6][1]} kv={load_data[6][2]} kva={pv_kw[6]} irrad=0.98 pmpp={pv_kw[6]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res5 phases=1 bus1={load_data[7][1]} kv={load_data[7][2]} kva={pv_kw[7]} irrad=0.98 pmpp={pv_kw[7]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res6 phases=1 bus1={load_data[8][1]} kv={load_data[8][2]} kva={pv_kw[8]} irrad=0.98 pmpp={pv_kw[8]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res7 phases=1 bus1={load_data[9][1]} kv={load_data[9][2]} kva={pv_kw[9]} irrad=0.98 pmpp={pv_kw[9]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res8 phases=1 bus1={load_data[10][1]} kv={load_data[10][2]} kva={pv_kw[10]} irrad=0.98 pmpp={pv_kw[10]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res9 phases=1 bus1={load_data[11][1]} kv={load_data[11][2]} kva={pv_kw[11]} irrad=0.98 pmpp={pv_kw[11]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res10 phases=1 bus1={load_data[12][1]} kv={load_data[12][2]} kva={pv_kw[12]} irrad=0.98 pmpp={pv_kw[12]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res11 phases=1 bus1={load_data[13][1]} kv={load_data[13][2]} kva={pv_kw[13]} irrad=0.98 pmpp={pv_kw[13]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res12 phases=1 bus1={load_data[14][1]} kv={load_data[14][2]} kva={pv_kw[14]} irrad=0.98 pmpp={pv_kw[14]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res13 phases=1 bus1={load_data[15][1]} kv={load_data[15][2]} kva={pv_kw[15]} irrad=0.98 pmpp={pv_kw[15]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res14 phases=1 bus1={load_data[16][1]} kv={load_data[16][2]} kva={pv_kw[16]} irrad=0.98 pmpp={pv_kw[16]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'
dss_engine.Text.Command = f'New PVSystem.Pv_res15 phases=1 bus1={load_data[17][1]} kv={load_data[17][2]} kva={pv_kw[17]} irrad=0.98 pmpp={pv_kw[17]} temperature=25 pf=1 %cutin=0.1 %cutout=0.1 effcurve=MyEff P-tCurve=myPvst Daily=MyIrrad tdaily=MyTemp'

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

Va_12.to_csv("VA12_pv1.csv",header= None ,index=None)
Vb_12.to_csv("VB12_pv1.csv",header= None ,index=None)
Vc_12.to_csv("VC12_pv1.csv",header= None ,index=None)

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
plt.title('Perfil de Tensão - PV')

data = [Va, Vb, Vc] 
#perfil de tensao boxplot
plt.figure(figsize=(12,8))
plt.boxplot(data, vert=True, labels=('VA','VB','VC'))
plt.title('Perfil de Tensão - Box Plot - PV')
plt.ylabel('V [pu]')
plt.xlabel('Tensões por Fase')

#plotando perdas
plt.figure()
plt.plot(horas,transf_loss_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas nos Transformadores - Com PV')

#plotando perdas
plt.figure()
plt.plot(horas,line_loss_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas na Linha - Com PV')

#plotando perdas
plt.figure()
plt.plot(horas,load_loss_pv, color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas sob Carga - Com PV')

#plotando perdas
plt.figure()
plt.plot(horas,no_load_loss_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas No Load - Com PV')  

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
plt.title('Perdas nos Transformadores Não acumulado')

#plotando perdas
plt.figure()
plt.plot(horas,line_loss_NAC_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas na Linha Não acumulado')

#plotando perdas
plt.figure()
plt.plot(horas,load_loss_NAC_pv, color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas sob Carga Não acumulado')

#plotando perdas
plt.figure()
plt.plot(horas,no_load_loss_NAC_pv,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas No Load Não acumulado')

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
plt.title('Energia injetada na rede ao longo do dia - PV (20%)')