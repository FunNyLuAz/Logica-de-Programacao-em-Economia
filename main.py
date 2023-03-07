import numpy as np
import json

import matplotlib.pyplot as pyplot
import matplotlib.widgets as widgets
import matplotlib.lines as lines

# Classes
class Line:
  def __init__(self, a=0, b=0):
    self.a = a
    self.b = b
  
  def solve(self, x): # Retorna y para um dado valor de x
    return x * self.a + self.b

  @staticmethod
  def intersect_lines(line1, line2): # Retorna o ponto de intersecção de duas linhas
    if (line1.a - line2.a) != 0:
      x = (line2.b - line1.b) / (line1.a - line2.a)
      y = line1.solve(x)
      return (x, y)
    else:
      return None

  @staticmethod
  def reverse_line(line): # Inverte a linha
    return Line(1 / line.a, -line.b / line.a)

# Functions
@staticmethod
def import_json(name): # Importa um json como um objeto
  with open(f"{name}.json", "r", encoding="utf") as file:
    config = json.load(file)
  return config

@staticmethod
def get_offset(val, offset_ratio):  # Determina o offset em unidades absolutas para uma dada porcentagem de um valor
  return abs(val) * offset_ratio

@staticmethod
def add_offset(val, offset): # Adiciona um offset a um dado valor
  return val + offset

@staticmethod
def equilibrio(o, d): # Retorna o ponto de equilíbrio para a oferta e para a demanda
  point = Line.intersect_lines(o, d)
  return (point[1], point[0])

@staticmethod
def cria_grafico(o, d, eq, offset_ratio=0): # Cria um gráfico para a oferta e para a demanda com um dado offset
  if eq[0] < 0: # Detecta quantidades negativas e retorna um erro (existe preços negativos, então, para eles, não há erro)
    print("\nErro! Não existe quantidade negativa!")
    exit()

  fig, ax = pyplot.subplots(figsize=(CONFIG["window"]["width"], CONFIG["window"]["height"]))

  fig.canvas.manager.set_window_title(CONFIG["window"]["window_title"])

  ax.set_title(CONFIG["graph"]["graph_title"])
  ax.set_xlabel(CONFIG["graph"]["xlabel"])
  ax.set_ylabel(CONFIG["graph"]["ylabel"])

  o = Line.reverse_line(o)  # Inverte a função de oferta
  d = Line.reverse_line(d)  # Inverte a função de demanda

  init = [eq[0] / 2, 3 * eq[0] / 2]

  x = np.linspace(min(init), max(init))  # Define as fronteiras no eixo x
  yo = np.linspace(o.solve(min(init)), o.solve(max(init))) # Define as fronteiras no eixo y de oferta
  yd = np.linspace(d.solve(min(init)), d.solve(max(init))) # Define as fronteiras no eixo y de demanda

  def func(x, a, b): # Função para resolver uma função afim ax + b
    return x * a + b

  # Determina os offsets unitários para os eixos
  xoff = get_offset(x.min(), offset_ratio)
  yoff = get_offset(min([yo.min(), yd.min()]), offset_ratio)

  # Define os limites das fronteiras do gráfico
  axis_lim = [add_offset(x.min(), -xoff), add_offset(x.max(), xoff), add_offset(min([yo.min(), yd.min()]), -yoff), add_offset(max([yo.max(), yd.max()]), yoff)]
  ax.axis(axis_lim)

  # Define se haverá uma grade
  ax.grid(CONFIG["graph"]["has_grid"])

  # Coloca curvas de demanda e de oferta no gráfico
  oline = lines.Line2D(x, yo, color=CONFIG["o"]["color"], zorder=CONFIG["o"]["zorder"], label=CONFIG["o"]["label"])  # Oferta
  dline = lines.Line2D(x, yd, color=CONFIG["d"]["color"], zorder=CONFIG["d"]["zorder"], label=CONFIG["d"]["label"])  # Demanda
  ax.add_artist(oline)
  ax.add_artist(dline)

  # Coloca ponto no gráfico
  eqpoint = lines.Line2D([eq[0]], [eq[1]], marker="o", color=CONFIG["eq"]["color"], zorder=CONFIG["eq"]["zorder"], label=CONFIG["eq"]["label"])  # Equilíbrio
  ax.add_artist(eqpoint)

  # Define as funções em caso de atualização nos Sliders de demanda e de oferta
  def update_o(val):
    nonlocal o, eq
    o = Line(o.a, val)
    oline.set_ydata(np.linspace(func(x.min(), o.a, o.b), func(x.max(), o.a, o.b)))
    eq = equilibrio(Line.reverse_line(o), Line.reverse_line(d))
    eqpoint.set_data([eq[0]], [eq[1]])
  def update_d(val):
    nonlocal d, eq
    d = Line(d.a, val)
    dline.set_ydata(np.linspace(func(x.min(), d.a, d.b), func(x.max(), d.a, d.b)))
    eq = equilibrio(Line.reverse_line(o), Line.reverse_line(d))
    eqpoint.set_data([eq[0]], [eq[1]])

  # Define os Sliders para os gráficos de demanda e de oferta
  pyplot.subplots_adjust(bottom=CONFIG["graph"]["bottom_adjust"])

  obslider_val = (o.b / 2, 3 * o.b / 2)
  ax_obslider = pyplot.axes([CONFIG["o"]["slider"]["x"], CONFIG["o"]["slider"]["y"], CONFIG["o"]["slider"]["width"], CONFIG["o"]["slider"]["height"]])
  obslider = widgets.Slider(ax_obslider, CONFIG["o"]["slider"]["label"], valmin=min(obslider_val), valmax=max(obslider_val), valinit=o.b)
  obslider.on_changed(update_o)

  dbslider_val = (d.b / 2, 3 * d.b / 2)
  ax_dbslider = pyplot.axes([CONFIG["d"]["slider"]["x"], CONFIG["d"]["slider"]["y"], CONFIG["d"]["slider"]["width"], CONFIG["d"]["slider"]["height"]])
  dbslider = widgets.Slider(ax_dbslider, CONFIG["d"]["slider"]["label"], valmin=min(dbslider_val), valmax=max(dbslider_val), valinit=d.b)
  dbslider.on_changed(update_d)

  if CONFIG["graph"]["has_legend"]:
    ax.legend() # Constrói a legenda

  pyplot.show() # Constrói a janela com o que foi dado

# Head
CONFIG = import_json("config") # Importa as configurações do programa
headers = import_json("headers") # Importa os dados iniciais para o programa

# Body
o = Line(headers["o"]["a"], headers["o"]["b"]) # Pega as constantes da reta de oferta
d = Line(headers["d"]["a"], headers["d"]["b"]) # Pega as constantes da reta de demanda

offset_ratio = headers["offset_ratio"]  # Pega o percentual de offset

cria_grafico(o, d, equilibrio(o, d), offset_ratio)

# Variáveis para variação da demanda:
#   1. Renda.
#   2. Preço dos bens relacionados: bens substitutos X bens complementares.
#   3. Gostos.
#   4. Expectativas.
#   5. Número de compradores.

#  Variáveis para variação da oferta:
#   1. Preço dos insumos.
#   2. Tecnologia.
#   3. Expectativas.
#   4. Número de vendedores.
