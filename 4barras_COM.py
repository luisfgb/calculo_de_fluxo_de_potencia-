# -*- coding: utf-8 -*-
"""
Created on Mon May 17 09:46:26 2021

@author: luisf
"""

'Alguns resultados para o circuito 4 barras IEEE - Shape Comercial'
import numpy as np
import matplotlib.pyplot as plt
import dss
dss_engine = dss.DSS

#Compilação do circuito em estudo
dss_engine.Text.Command = r'compile "C:\Users\luisf\OneDrive\Documentos\OpenDSS\IEEE4_python_Com\4bus_Com_python.dss"'


# Obtendo algumas informações sobre as fontes
print('-'*30)
print('Fontes:')
for source in dss_engine.ActiveCircuit.Vsources:
    print(f'Nome: {source.Name}')
    print(f'kV: {source.BasekV}')
    print(f'Frequência: {source.Frequency}')
    print(f'Fases: {source.Phases}')

# Obtendo algumas informações sobre as barras
print('-'*30)
print('Barras:')
for bus in dss_engine.ActiveCircuit.Buses:
    print(f'Nome: {bus.Name}')
    print(f'kV: {(bus.kVBase)*np.sqrt(3)}')
        
# Obtendo algumas informações sobre as cargas
print('-'*30)
print('Cargas:')
for load in dss_engine.ActiveCircuit.Loads:
    loadpot = load.kW
    print(f'Nome: {load.Name}')
    print(f'Potência: {load.kW}')
    print(f'Fator de Potência: {load.PF}')

# Obtendo algumas informações sobre o transformador
print('-'*30)
print('Transformadores:')
for trs in dss_engine.ActiveCircuit.Transformers:
    print(f'Nome: {trs.Name}')
    print(f'Kv: {trs.kV}')
    print(f'kVA: {trs.kva}')

# Obtendo algumas informações sobre o PV
print('-'*30)
print('Sistema FV: ')
for pv in dss_engine.ActiveCircuit.PVSystems:
    print(f'Potência Nominal: {pv.kVArated}')
    print(f'Potência Ativa: {pv.Pmpp}')
    print(f'Potência Reativa: {pv.kvar}')
    print(f'Fator de Potência: {pv.PF}\n')

#PERFIL DE CARGA COMERCIAL
print('-'*30)
print('Análise do Load Shape')
horas = []
potShape = []
for lds in dss_engine.ActiveCircuit.LoadShapes:
    if lds.Name == 'comercial':
        print(f'Load Shape {lds.Name}')
        for i in range(lds.Npts):
            potShape.append(lds.Pmult[i])
            horas.append(i)
        for j in range(lds.Npts):
            potShape[j] = potShape[j]*loadpot
print(f'Valores de consumo por hora da carga [kW] :\n {potShape}')


#RESOLVENDO O CICRCUITO PARA AS 24 HORAS DO DIA
print('\n')
print('-'*30)
print('Resolvendo o circuito para 24 horas do dia')
#potencia do pv
pv_power = []

#perdas
line_loss = []
transf_loss = []
load_loss = []
twelve_line_loss = []
four_line_loss = []
twelve_load_loss = []
four_load_loss = []

#tensoes de sequencia
Vseqn2 = []
Vseqn3 = []
Vseqn4 = []

#fator de desequilibrio
FDn2 = np.zeros(len(horas))
FDn3 = np.zeros(len(horas))
FDn4 = np.zeros(len(horas))

#loop de solucao do circuito
for i in range(len(horas)):
    dss_engine.Text.Command = 'set number = 1'
    dss_engine.ActiveCircuit.Solution.Solve()
    
    for pv in dss_engine.ActiveCircuit.PVSystems:
        pv_power.append(pv.kW/3)
    
    for em in dss_engine.ActiveCircuit.Meters:
        regs = em.RegisterNames
        loss = em.RegisterValues
        for k in range(len(regs)):
            if regs[k] == 'Line Losses':
                line_loss.append(loss[k])
            elif regs[k] == 'Transformer Losses':
                transf_loss.append(loss[k])
            elif regs[k] == 'Load Losses kWh':
                load_loss.append(loss[k])
            elif regs[k] == '12.5 kV Line Loss':
                twelve_line_loss.append(loss[k])
            elif regs[k] == '4.16 kV Line Loss':
                four_line_loss.append(loss[k])
            elif regs[k] == '12.5 kV Load Loss':
                twelve_load_loss.append(loss[k])
            elif regs[k] == '4.16 kV Load Loss':
                four_load_loss.append(loss[k])
    for bus in dss_engine.ActiveCircuit.Buses:
        #Tensões de sequência são V0, V+ e V-
        if bus.Name == 'n2':
            Vseqn2.append(bus.SeqVoltages)
        elif bus.Name == 'n3':
            Vseqn3.append(bus.SeqVoltages)
        elif bus.Name == 'n4':
            Vseqn4.append(bus.SeqVoltages)
    #Fator de desequilibrio - (V- / V+)*100%        
    FDn2[i] = (Vseqn2[i][2]/Vseqn2[i][1])*100        
    FDn3[i] = (Vseqn3[i][2]/Vseqn3[i][1])*100 
    FDn4[i] = (Vseqn4[i][2]/Vseqn4[i][1])*100 

print(len(pv_power))
#Comparação entre load shape e geração do PV
plt.figure(figsize=(10,8))
plt.plot(horas,potShape, color='b',label = 'Consumo da carga')
plt.plot(horas,pv_power, color = 'r',label = 'Potência Gerada pelo PV')
plt.legend(loc='best')
plt.xlabel('Horas do dia')
plt.ylabel('kW')
plt.title('Load Shape e Geração do PV',fontsize = 15)
plt.grid()
plt.show()

#Perdas por patamar de hora do dia
#perdas não acumuladas 
load_loss_NAC = []
line_loss_NAC = []
transf_loss_NAC = []
for i in range(len(load_loss)):
    if i == 0:
        load_loss_NAC.append(load_loss[i])
        line_loss_NAC.append(line_loss[i])
        transf_loss_NAC.append(transf_loss[i])
    else:
        load_loss_NAC.append(load_loss[i] - load_loss[i-1])
        line_loss_NAC.append(line_loss[i] - line_loss[i-1])
        transf_loss_NAC.append(transf_loss[i] - transf_loss[i-1])

plt.figure(figsize=(10,8))
plt.plot(horas,line_loss_NAC, color='b',label = 'Perdas na Linha')
plt.plot(horas,transf_loss_NAC, color='r',label = 'Perdas no Transformador')
plt.plot(horas,load_loss_NAC, color='#0bfc03',label = 'Perdas na Carga')
plt.legend(loc='best')
plt.xlabel('Horas do dia')
plt.ylabel('kWh')
plt.title('Perdas para cada hora do dia - Load Shape Comercial',fontsize = 15)
plt.grid()
plt.show()
print('\n')
print('-'*50)
print('Fatores de desequilibrio para barra N2\n')
for i in range(len(horas)):
    print(f'Hora {horas[i]}: {np.round(FDn2[i],3)} %')
print('\n')
print('-'*50)
print('Fatores de desequilibrio para barra N3\n')
for i in range(len(horas)):
    print(f'Hora {horas[i]}: {np.round(FDn3[i],3)} %')
print('\n')
print('-'*50)
print('Fatores de desequilibrio para barra N4\n')
for i in range(len(horas)):
    print(f'Hora {horas[i]}: {np.round(FDn4[i],3)} %')


 
