# El Precio de la Incertidumbre — código de ejercicios

Repositorio **oficial de código** del libro **_El Precio de la Incertidumbre.
Valuación avanzada de opciones con Python: teoría, simulación y machine learning_**
(Liber Jaime Merlos). Aquí vive, listo para correr,
el código de los ejemplos del libro: el módulo `opciones.py`, un script por capítulo y
los dashboards interactivos.

> Este repo contiene **solo el código de los ejercicios**. El **manuscrito del libro no
> se publica aquí** ni en ningún repo público.

## Instalación rápida
```bash
pip install -r requirements.txt
```
Solo necesitas `numpy` (y `matplotlib` para las gráficas). `streamlit` y `pandas` son
opcionales, para los dashboards.

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
├── apps/              # dashboards interactivos del libro (Streamlit)
│   ├── app.py                     # hub: portada + navegación entre dashboards
│   ├── dashboard_griegas.py       # P&L con cono ±1σ, escaleras de griegas, cadena (Cap. 6)
│   ├── dashboard_valuacion.py     # tres motores, frontera de ejercicio, convergencia, sonrisa (Cap. 11)
│   ├── componentes.py             # marca del libro, selector de tema, paneles
│   ├── graficos.py                # cálculos y figuras (matplotlib puro)
│   └── tema.py                    # paleta validada, modo claro/oscuro
├── .streamlit/config.toml         # tema visual (oscuro por defecto)
├── requirements.txt
└── LICENSE            # MIT (puedes reutilizar el código citando la fuente)
```

## Dashboards interactivos
```bash
pip install streamlit pandas
streamlit run apps/app.py                  # hub con los dos dashboards
streamlit run apps/dashboard_griegas.py    # o cada uno por separado
streamlit run apps/dashboard_valuacion.py
```
Los dashboards son la versión interactiva de las tablas y figuras del libro, con las
vistas que usan las mesas de opciones: P&L con cono de ±1σ, escaleras de griegas por
vencimiento, cadena de opciones, frontera de ejercicio óptimo, convergencia de los tres
motores y sonrisa de volatilidad a partir de cotizaciones editables. Mismos motores de
`opciones.py`, mismos parámetros que se declaran en cada capítulo.

Convenciones de mercado: volatilidad y tasa en % anual; vega y rho por 1 punto porcentual;
theta por día calendario. Las cifras se muestran **por acción** (como se cotiza la prima),
**por contrato de 100 acciones** (tamaño del contrato de opción sobre acciones en MexDer) y
**por posición** (número de contratos que eliges). Cada gráfico lleva un recuadro "Cómo leer"
y la barra lateral incluye un glosario para quien empieza.

Abren en modo oscuro (superficie casi negra, acento ámbar); el selector de la barra
lateral cambia a modo claro. La paleta está validada para daltonismo
(protanopia/deuteranopia) y contraste.

## Cómo se relaciona con el libro
El libro muestra **conceptos, fragmentos breves y resultados**; el **código completo y
reproducible** vive aquí. Cada capítulo del libro remite al script correspondiente y
cada dashboard indica el capítulo que lo explica.

## Licencia y aviso
Código bajo licencia **MIT**. Material **educativo**; no es asesoría de inversión.

Autor: Liber Jaime Merlos · GitHub: [@libjai](https://github.com/libjai)
