# El Precio de la Incertidumbre — código de ejercicios

Repositorio **oficial de código** del libro **_El Precio de la Incertidumbre:
Valuación de opciones con Python_** (Liber Jaime Merlos). Aquí vive, listo para correr,
el código de los ejemplos del libro: el módulo `opciones.py` y un script por capítulo.

> Este repo contiene **solo el código de los ejercicios**. El **manuscrito del libro no
> se publica aquí** ni en ningún repo público.

## Instalación rápida
```bash
pip install -r requirements.txt
```
Solo necesitas `numpy` (y `matplotlib` para las gráficas).

## Uso (idéntico a los fragmentos del libro)
```python
from opciones import BlackScholes, BinomialTree

# Call europea por Black-Scholes
BlackScholes(S=100, K=100, r=0.05, sigma=0.20, T=1, tipo="call").price()

# Opción americana por árbol binomial (CRR)
BinomialTree(100, 100, 0.05, 0.20, 1, N=1000, tipo="put", americana=True).price()
```
Verifica que todo funciona:
```bash
python opciones.py        # corre los auto-tests (paridad, convergencia, etc.)
python ejemplos/cap04_binomial.py
```

## Correr en la nube (sin instalar nada)
En [Google Colab](https://colab.research.google.com): *File → Open notebook → GitHub*,
busca `libjai/precio-de-la-incertidumbre` y abre el ejemplo; o en una celda:
```python
!git clone https://github.com/libjai/precio-de-la-incertidumbre.git
%cd precio-de-la-incertidumbre
```

## Estructura
```
precio-de-la-incertidumbre/
├── opciones.py        # módulo: BlackScholes, BinomialTree, MonteCarlo, LongstaffSchwartz,
│                      # precio_asiatica, precio_barrera
├── ejemplos/          # un script por capítulo, reproducible
│   ├── cap04_binomial.py          ├── cap09_longstaff_schwartz.py
│   ├── cap05_black_scholes.py     ├── cap10_cotas.py
│   ├── cap06_griegas.py           ├── cap11_caso_mexico.py
│   ├── cap07_montecarlo.py        ├── cap12_exoticas.py
│   ├── cap08_americanas.py        └── cap13_opciones_reales.py
├── apps/              # dashboards interactivos (streamlit run apps/<app>.py)
│   ├── dashboard_griegas.py       # explorador de griegas (Cap. 6)
│   └── dashboard_valuacion.py     # tres motores + sensibilidad σ×r (Cap. 11)
├── requirements.txt
└── LICENSE            # MIT (puedes reutilizar el código citando la fuente)
```

## Dashboards interactivos
```bash
pip install streamlit
streamlit run apps/dashboard_griegas.py
streamlit run apps/dashboard_valuacion.py
```

## Cómo se relaciona con el libro
El libro muestra **conceptos, fragmentos breves y resultados**; el **código completo y
reproducible** vive aquí. Cada capítulo del libro remite al script correspondiente.

## Licencia y aviso
Código bajo licencia **MIT**. Material **educativo**; no es asesoría de inversión.

Autor: Liber Jaime Merlos · GitHub: [@libjai](https://github.com/libjai)
