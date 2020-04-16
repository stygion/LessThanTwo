import matplotlib.pyplot as plt
import numpy as np
import math

quellen = ['Windkraft', 'Biomasse', 'Photovoltaik', 'Wasserkraft', 'Hausmüll']
TWh = [107, 46, 40, 20, 6]
title = 'Energiequellen bei der Stromerzeugung'
plt.barh(quellen, TWh)
plt.ylabel('Erzeugte Energie (TWh)')
plt.title('Eneuerbare Energien bei der Stromerzeugung')
plt.show()
