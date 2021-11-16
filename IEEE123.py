# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 13:36:44 2021

@author: luisf
"""

#IEEE 123 - Barras
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import dss
dss_engine = dss.DSS

#Compilando o circuito estudado
dss_engine.Text.Command = r'compile "C:\Users\luisf\OneDrive\Documentos\IC\123Bus\IEEE123Master.dss"'
 
#Plotando o circuito'
dss_engine.Text.Command = 'Buscoords BusCoords.dat'

#Energy meter para contabilizar as perdas'
dss_engine.Text.Command = 'new energymeter.medidorSource element=transformer.reg1a terminal=1'

    
coord_bus = {}
load_conn = {}
#dss_engine.ActiveCircuit.ActiveCktElement()
for bus in dss_engine.ActiveCircuit.Buses:  
    load_conn[bus.Name.lower()] = bus.LoadList
    coord_bus[bus.Name.lower()] = (bus.x,bus.y)
source = coord_bus['150']

coord_line = []
for line in dss_engine.ActiveCircuit.Lines:
    b1_x, b1_y = coord_bus[line.Bus1.lower().partition('.')[0]]
    b2_x, b2_y = coord_bus[line.Bus2.lower().partition('.')[0]]
    coord_line.append([(b1_x,b2_x),(b1_y,b2_y)])

#reguladores
reg1 = coord_bus['150r']
reg2 = coord_bus['9']
reg3 = coord_bus['25r']
reg4 = coord_bus['160']

#Capacitores
c83 = coord_bus['83']
c88 = coord_bus['88']
c90 = coord_bus['90']
c92 = coord_bus['92']

plt.figure(figsize = (16,9))
for i in range(len(coord_line)-2):
    plt.plot(coord_line[i][0],coord_line[i][1], color ='b',marker = '.') 
#inicio do circuito
plt.plot(source[0],source[1], '^',color = 'blue', ms = 10,label='Alimentador')
plt.annotate('Source', xy = (source[0],source[1]), xytext = ((source[0]-100),(source[1] + 100)))
#reguladores
#plt.plot(reg1[0],reg1[1],'s',color = 'blue', ms = 15) MESMO LOCAL DA FONTE
plt.plot(reg2[0],reg2[1],'s',color = 'blue', ms = 10, label='Reguladores')
plt.annotate('Reg 2', xy = (reg2[0],reg2[1]),xytext = (reg2[0] + 50,reg2[1]))
plt.plot(reg3[0],reg3[1],'s',color = 'blue', ms = 10)
plt.annotate('Reg 3', xy = (reg3[0],reg3[1]), xytext = (reg3[0] + 50,reg3[1]-20))
plt.plot(reg4[0],reg4[1],'s',color = 'blue', ms = 10)
plt.annotate('Reg 4', xy = (reg4[0],reg4[1]), xytext = (reg4[0],reg4[1]+80))
#capacitores
plt.plot(c83[0],c83[1],'d',color = 'blue', ms = 10, label = 'Banco de Capacitores')
plt.annotate('C83', xy = (c83[0],c83[1]), xytext = (c83[0]+40,c83[1]))
plt.plot(c88[0],c88[1],'d',color = 'blue', ms = 10)
plt.annotate('C88', xy = (c88[0],c88[1]), xytext = (c88[0]-50,c88[1]+80))
plt.plot(c90[0],c90[1],'d',color = 'blue', ms = 10)
plt.annotate('C90', xy = (c90[0],c90[1]), xytext = (c90[0]+40,c90[1]))
plt.plot(c92[0],c92[1],'d',color = 'blue', ms = 10)
plt.annotate('C92', xy = (c92[0],c92[1]), xytext = (c92[0]+40,c92[1]))
plt.legend(loc='best')
#eixos
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Circuito IEEE 123Bus')

horas = np.linspace(0,23,24)

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

#perdas
line_loss = []
transf_loss = []
load_loss = []
no_load_loss = []

#energia injetada
energy = []

dss_engine.Text.Command = 'set mode=daily'
dss_engine.Text.Command = 'set stepsize=1h'

#loop de solucao do circuito
print('\nAnálise sem PV system\n')
for i in range(len(horas)):
    dss_engine.Text.Command = 'set number = 1'
    dss_engine.ActiveCircuit.Solution.Solve()
    
    for em in dss_engine.ActiveCircuit.Meters:
        loss = em.RegisterValues
        line_loss.append(loss[ll])
        transf_loss.append(loss[tl])
        load_loss.append(loss[ldl])
        no_load_loss.append(loss[nll])
        energy.append(loss[eng])
                
    #monitorando as tensões maxima e minima 
    vpu = dss_engine.ActiveCircuit.AllBusVmagPu
    vmax = np.round(np.max(vpu),2)
    if vmax > 1.05:
        print('Há Sobretensão!')
    print('-'*50)
    print(f'A tensão máxima no instante {i} é {vmax}')
    vmin = np.round(np.min(vpu),2)
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
        Da_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeDistancesByPhase(1))
        Vb_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(2))
        Db_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeDistancesByPhase(2))
        Vc_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeVmagPUByPhase(3))
        Dc_12 = pd.DataFrame(dss_engine.ActiveCircuit.AllNodeDistancesByPhase(3)) 

Va_12.to_csv("VA12.csv", header= None ,index= None)
Da_12.to_csv("DA12.csv", header= None, index= None)
Vb_12.to_csv("VB12.csv", header= None ,index= None)
Db_12.to_csv("DB12.csv", header= None, index= None)
Vc_12.to_csv("VC12.csv", header= None ,index= None)
Dc_12.to_csv("DC12.csv", header= None, index= None)

print('\n')
print('Perdas nos Transformadores:\n')
print(f'{transf_loss}\n')
print('Perdas na Linha:\n')
print(f'{line_loss}\n')
print('Perdas sob Carga:\n')
print(f'{load_loss}\n')
print('Perdas no Load:\n')
print(f'{no_load_loss}\n')

#perfil de tensao
plt.figure(figsize=(12,8))
plt.plot(Da,Va,'D',color = 'blue', label ='Va')
plt.plot(Db,Vb,'D',color = 'red', label = 'Vb')
plt.plot(Dc,Vc,'D',color = 'green', label = 'Vc')
plt.legend(loc ='best')
plt.xlabel('Distância do Energy Meter')
plt.ylabel('V [pu]')
plt.title('Perfil de Tensão')

data = [Va, Vb, Vc] 
#perfil de tensao boxplot
plt.figure(figsize=(12,8))
plt.boxplot(data, vert=True, labels=('VA','VB','VC'))
plt.title('Perfil de Tensão - Box Plot')
plt.ylabel('V [pu]')
plt.xlabel('Tensões por Fase')


#plotando perdas
plt.figure()
plt.plot(horas,transf_loss,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas nos Transformadores')

#plotando perdas
plt.figure()
plt.plot(horas,line_loss,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas na Linha')

#plotando perdas
plt.figure()
plt.plot(horas,load_loss, color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas sob Carga')

#plotando perdas
plt.figure()
plt.plot(horas,no_load_loss,color='red')
plt.xlabel('Horas')
plt.ylabel('kWh')
plt.title('Perdas No Load')


#NÃO ACUMULADAS
load_loss_NAC = []
no_load_loss_NAC = []
line_loss_NAC = []
transf_loss_NAC = []
for i in range(len(horas)):
    if i == 0:
        load_loss_NAC.append(load_loss[i])
        line_loss_NAC.append(line_loss[i])
        transf_loss_NAC.append(transf_loss[i])
        no_load_loss_NAC.append(no_load_loss[i])
    else:
        load_loss_NAC.append(load_loss[i] - load_loss[i-1])
        line_loss_NAC.append(line_loss[i] - line_loss[i-1])
        transf_loss_NAC.append(transf_loss[i] - transf_loss[i-1])
        no_load_loss_NAC.append(no_load_loss[i] - no_load_loss[i-1])
        
print('\n')
print('Perdas nos Transformadores não acumuladas:\n')
print(f'{transf_loss_NAC}\n')
print('Perdas na Linha não acumuladas:\n')
print(f'{line_loss_NAC}\n')
print('Perdas sob Carga não acumuladas:\n')
print(f'{load_loss_NAC}\n')


#plotando perdas
plt.figure()
plt.plot(horas,transf_loss_NAC,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas nos Transformadores Não acumulado')

#plotando perdas
plt.figure()
plt.plot(horas,line_loss_NAC,color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas na Linha Não acumulado')

#plotando perdas
plt.figure()
plt.plot(horas,load_loss_NAC, color='red')
plt.xlabel('Horas')
plt.ylabel('kW')
plt.title('Perdas sob Carga Não acumulado')

#plotando perdas
plt.figure()
plt.plot(horas,no_load_loss_NAC,color='red')
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
plt.title('Energia injetada na rede ao longo do dia - Sem PV')
