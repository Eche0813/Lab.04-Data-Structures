# Sistema de Logística Urbana: Quadtree 2D vs. Fuerza Bruta

Este repositorio contiene la solución completa para el **Laboratorio 4: Estructuras de Datos Espaciales**. El objetivo principal es resolver consultas de proximidad espacial en una red de logística urbana con **10.000 puntos de entrega** utilizando un **Quadtree 2D implementado desde cero**, comparando su rendimiento contra un enfoque de **Fuerza Bruta**.

---

## Tabla de Contenidos
- [Descripción del Problema](#-descripción-del-problema)
- [Arquitectura de Archivos](#-arquitectura-de-archivos)
- [Requisitos e Instalación](#-requisitos-e-instalación)
- [Guía de Ejecución](#-guía-de-ejecución)
- [Visualizaciones Espaciales](#-visualizaciones-espaciales)
- [Análisis Comparativo y Resultados](#-análisis-comparativo-y-resultados)
- [Conclusión y Preguntas del Laboratorio](#-conclusión-y-preguntas-del-laboratorio)

---

## Descripción del Problema

Un sistema de logística urbana gestiona $N = 10.000$ puntos de entrega distribuidos en un plano de $10\text{ km} \times 10\text{ km}$ ($10.000\text{ m} \times 10.000\text{ m}$). El sistema necesita responder eficientemente a dos tipos de consultas en tiempo real:

1. **Búsqueda por Radio (Range Search):** Determinar qué puntos de entrega se encuentran dentro de un radio de $500\text{ metros}$ desde un punto dado.
2. **Vecino Más Cercano (Nearest Neighbor):** Identificar el punto de entrega más cercano a una ubicación de consulta.

---

## Arquitectura de Archivos

```text
.
├── Quadtree.py                  # Estructura de datos base (Point, BoundingBox, QuadTree)
├── test.py                      # Pruebas unitarias (unittest) y generación de visualizaciones
├── analisis.py                  # Benchmarking de tiempos O(N) vs O(log N)
├── radio_search.png             # Visualización espacial del radio de 500m
├── nearest_neighbor.png         # Visualización espacial del vecino más cercano
├── performance_benchmark.png    # Gráfica de comparación de rendimiento (escala log-log)
└── README.md                    # Documentación del proyecto

```

## Requisitos e instalación
El proyecto está escrito en Python 3 y no requiere librerías externas de estructuras de datos (como scipy o rtree). Únicamente se utiliza matplotlib para la generación de gráficas visuales.

### Configuración del entorno virtual

```bash

# Crear entorno virtual
python -m venv venv

# Activar el entorno (Linux/macOS)
source venv/bin/activate

# Activar el entorno (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install matplotlib

```

## Guía de ejecución
1. **Pruebas Unitarias y Visualización Espacial**

Para correr la suite de pruebas unittest y generar las gráficas de verificación espacial (radio_search.png y nearest_neighbor.png):

```bash

python test.py

```
2. **Benchmark de Rendimiento y Análisis** 

Para ejecutar el experimento de tiempos comparando Quadtree contra Fuerza Bruta con distintos tamaños de $N$ ($10$ a $100.000$ puntos):

```bash

python analisis.py

```

## Visualizaciones espaciales

**1. Búsqueda por radio** : La figura muestra la división del espacio mediante la retícula del Quadtree, el centro de la consulta ($*$), el círculo con radio de $500\text{ m}$ y los puntos contenidos resaltados en rojo.

**2. Vecino más cercano:** La figura identifica el punto objetivo de consulta ($X$), la conexión hacia el vecino más cercano encontrado y el círculo de radio mínimo equivalente a dicha distancia.

## Análisis comparativo y resultados

Se evaluaron los tiempos de consulta promedio (en milisegundos) variando el número de puntos $N \in [10, 100000]$.

| Operación | Fuerza Bruta O(N) | QuadTree O(log N) | Aceleración (Speedup) |
| :--- | :---: | :---: | :---: |
| **Búsqueda por Radio (500m)** | 2.08 ms | 0.16 ms | **12.73x más rápido** |
| **Vecino Más Cercano** | 3.52 ms | 0.05 ms | **62.57x más rápido** |

* **Punto de Inflexión:** N ≈ 50 puntos.

## Conclusión y preguntas del laboratorio

### ¿Para qué tamaño de datos el Árbol-Quadtree comienza a ser más rápido que "Fuerza Bruta"?

* Punto de Inflexión (Break-even point): Ocurre tempranamente alrededor de $N \approx 50$ puntos.
* Explicación Técnica:
* Para conjuntos de datos muy pequeños ($N < 50$), la Fuerza Bruta es competitiva debido a la simplicidad del bucle contiguo en memoria y la ausencia de llamadas recursivas en la pila.
* Cuando $N \ge 50$, la complejidad algorítmica $O(\log N)$ del Quadtree comienza a superar con claridad el comportamiento lineal $O(N)$ de la Fuerza Bruta.
* A medida que $N$ escala a $10.000$ y $100.000$ puntos, el Quadtree demuestra una eficiencia abrumadora, reduciendo las consultas de vecino más cercano de $33.91\text{ ms}$ a solo $0.07\text{ ms}$ ($>430\times$ de velocidad).
--- 
## Uso de IA generativa
```text

Afirmo haber usado la IA de google en su modelo Gemini-3.6-flash única y exclusivamente para:
- Afianzar conceptos de creación de gràficas con matplotlib.
- Acompañamiento y revisión de código en la creación del Quadtree desde 0 sin librerías externas.
- Comprensión de codificación de mediciones de tiempos mediante la librería time.

```