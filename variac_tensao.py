# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 09:30:27 2021

@author: luisf
"""
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

#importando as tensões da fase A
Va_no_pv = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VA12.csv", header=None, delim_whitespace=True, dtype=float))
Va_pv1 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VA12_pv1.csv", header=None, dtype=float))
Va_pv2 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VA12_pv2.csv", header=None, dtype=float))
Va_pv3 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VA12_pv3.csv", header=None, dtype=float))

#importando as tensões da fase B
Vb_no_pv = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VB12.csv", header=None, dtype=float))
Vb_pv1 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VB12_pv1.csv", header=None, dtype=float))
Vb_pv2 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VB12_pv2.csv", header=None, dtype=float))
Vb_pv3 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VB12_pv3.csv", header=None, dtype=float))

#importando as tensões da fase C
Vc_no_pv = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VC12.csv", header=None, dtype=float))
Vc_pv1 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VC12_pv1.csv", header=None, dtype=float))
Vc_pv2 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VC12_pv2.csv", header=None, dtype=float))
Vc_pv3 = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\VC12_pv3.csv", header=None, dtype=float))

#distancias
da = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\DA12.csv", header=None, dtype=float))
db = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\DB12.csv", header=None, dtype=float))
dc = pd.DataFrame.to_numpy(pd.read_csv(r"C:\Users\luisf\OneDrive\Documentos\IC\123Bus\DC12.csv", header=None, dtype=float)) 

#calculando as variações
print(f'A máxima tensão sem pv é: {np.max(Va_no_pv)} pu')

#fase A
A1 = np.max(Va_pv1) - np.max(Va_no_pv) #20%

A2 = np.max(Va_pv2) - np.max(Va_no_pv) #40%

A3 = np.max(Va_pv3) - np.max(Va_no_pv) #60%
A = [A1,A2,A3]
DA = [20, 40, 60]
#fase B
B1 = np.max(Vb_pv1) - np.max(Vb_no_pv) #20%

B2 = np.max(Vb_pv2) - np.max(Vb_no_pv) #40%

B3 = np.max(Vb_pv3) - np.max(Vb_no_pv) #60%
B = [B1,B2,B3]
DB = [20, 40, 60]

#fase A
C1 = np.max(Vc_pv1) - np.max(Vc_no_pv) #20%

C2 = np.max(Vc_pv2) - np.max(Vc_no_pv)#40%

C3 = np.max(Vc_pv3) - np.max(Vc_no_pv) #60%
C = [C1,C2,C3]
DC = [20, 40, 60]

#Y = [A1,A2,A3,B1,B2,B3,C1,C2,C3]
#X = [DA,DB,DC]

plt.figure()
plt.plot(DA,A,'^',ms='8',label='Fase A')
plt.plot(DB,B,'s',ms='8',label='Fase B')
plt.plot(DC,C,'o',ms='8',label='Fase C')
plt.title('Diferença máxima de tensão nas três fases - 12 Horas')
plt.xlabel('Cargas com PV [%]')
plt.ylabel(r'$\Delta$V  [pu]')
plt.legend(loc='best')
