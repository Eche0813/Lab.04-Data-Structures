"""
analisis.py
Métricas de rendimiento, benchmarks de tiempo y discusión de resultados.
Compara el tiempo de respuesta del Quadtree vs. Fuerza Bruta para identificar
el punto de inflexión (break-even point) donde la estructura espacial supera al recorrido lineal.
"""

import time
import random
import math
import matplotlib.pyplot as plt
from Quadtree import Point, BoundingBox, QuadTree


# ----------------------------------------------------------------------
# 1. IMPLEMENTACIONES DE FUERZA BRUTA (BASELINE)
# ----------------------------------------------------------------------

def brute_force_range_search(points: list[Point], center: Point, radius: float) -> list[Point]:
    """Búsqueda lineal O(N) de puntos dentro de un radio."""
    radius_sq = radius ** 2
    return [p for p in points if center.distance_sq_to(p) <= radius_sq]


def brute_force_nearest_neighbor(points: list[Point], target: Point) -> tuple[Point, float]:
    """Búsqueda lineal O(N) del punto más cercano."""
    best_point = None
    best_dist = float('inf')
    for p in points:
        d = target.distance_to(p)
        if d < best_dist:
            best_dist = d
            best_point = p
    return best_point, best_dist


# ----------------------------------------------------------------------
# 2. SUITE DE BENCHMARKS Y MEDICIÓN DE TIEMPOS
# ----------------------------------------------------------------------

def run_benchmarks():
    """Ejecuta experimentos variando el tamaño del dataset (N) para ambas operaciones."""
    random.seed(2026)  # Semilla fija para consistencia en los experimentos

    # Tamaños de datos N a evaluar
    sizes = [10, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]
    CITY_SIZE = 10000.0  # Plano de 10km x 10km
    RADIUS = 500.0       # Radio de 500 metros
    NUM_QUERIES = 200    # Promediar sobre múltiples consultas para estabilidad estadística

    # Listas para almacenar tiempos acumulados (en milisegundos)
    times_bf_radius = []
    times_qt_radius = []
    times_qt_build = []

    times_bf_nn = []
    times_qt_nn = []

    print(f"{'N Puntos':<10} | {'Const. QT (ms)':<15} | {'FB Radio (ms)':<15} | {'QT Radio (ms)':<15} | {'FB Vecino (ms)':<15} | {'QT Vecino (ms)':<15}")
    print("-" * 95)

    for N in sizes:
        # Generación de dataset
        points = [
            Point(random.uniform(0, CITY_SIZE), random.uniform(0, CITY_SIZE))
            for _ in range(N)
        ]

        # Puntos de consulta aleatorios para el experimento
        query_points = [
            Point(random.uniform(0, CITY_SIZE), random.uniform(0, CITY_SIZE))
            for _ in range(NUM_QUERIES)
        ]

        # 1. Medir construcción del Quadtree
        t_start = time.perf_counter()
        boundary = BoundingBox(CITY_SIZE / 2, CITY_SIZE / 2, CITY_SIZE / 2, CITY_SIZE / 2)
        qt = QuadTree(boundary, capacity=8)
        for p in points:
            qt.insert(p)
        t_build = (time.perf_counter() - t_start) * 1000.0 / NUM_QUERIES  # Tiempo promedio por consulta
        times_qt_build.append(t_build)

        # 2. Medir Búsqueda por Radio: Fuerza Bruta vs Quadtree
        t_start = time.perf_counter()
        for q in query_points:
            _ = brute_force_range_search(points, q, RADIUS)
        t_bf_r = (time.perf_counter() - t_start) * 1000.0 / NUM_QUERIES
        times_bf_radius.append(t_bf_r)

        t_start = time.perf_counter()
        for q in query_points:
            _ = qt.query_radius(q, RADIUS)
        t_qt_r = (time.perf_counter() - t_start) * 1000.0 / NUM_QUERIES
        times_qt_radius.append(t_qt_r)

        # 3. Medir Vecino Más Cercano: Fuerza Bruta vs Quadtree
        t_start = time.perf_counter()
        for q in query_points:
            _ = brute_force_nearest_neighbor(points, q)
        t_bf_nn = (time.perf_counter() - t_start) * 1000.0 / NUM_QUERIES
        times_bf_nn.append(t_bf_nn)

        t_start = time.perf_counter()
        for q in query_points:
            _ = qt.nearest_neighbor(q)
        t_qt_nn = (time.perf_counter() - t_start) * 1000.0 / NUM_QUERIES
        times_qt_nn.append(t_qt_nn)

        print(f"{N:<10} | {t_build:<15.4f} | {t_bf_r:<15.4f} | {t_qt_r:<15.4f} | {t_bf_nn:<15.4f} | {t_qt_nn:<15.4f}")

    return {
        'sizes': sizes,
        'bf_radius': times_bf_radius,
        'qt_radius': times_qt_radius,
        'bf_nn': times_bf_nn,
        'qt_nn': times_qt_nn,
        'qt_build': times_qt_build
    }


# ----------------------------------------------------------------------
# 3. GENERACIÓN DE GRÁFICAS Y ANÁLISIS DEL PUNTO DE INFLEXIÓN
# ----------------------------------------------------------------------

def plot_performance_results(data: dict, filename="performance_benchmark.png"):
    """Genera las gráficas comparativas de rendimiento en escala logarítmica."""
    sizes = data['sizes']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # --- Gráfica 1: Búsqueda por Radio ---
    ax1.plot(sizes, data['bf_radius'], 'o-', label='Fuerza Bruta O(N)', color='#E74C3C', linewidth=2)
    ax1.plot(sizes, data['qt_radius'], 's-', label='QuadTree O(log N)', color='#2ECC71', linewidth=2)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title("Rendimiento: Búsqueda por Radio (500m)", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Número de Puntos (N)")
    ax1.set_ylabel("Tiempo de Consulta por Operación (ms)")
    ax1.grid(True, which="both", linestyle="--", alpha=0.5)
    ax1.legend()

    # --- Gráfica 2: Vecino Más Cercano ---
    ax2.plot(sizes, data['bf_nn'], 'o-', label='Fuerza Bruta O(N)', color='#E74C3C', linewidth=2)
    ax2.plot(sizes, data['qt_nn'], 's-', label='QuadTree O(log N)', color='#3498DB', linewidth=2)
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title("Rendimiento: Vecino Más Cercano", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Número de Puntos (N)")
    ax2.set_ylabel("Tiempo de Consulta por Operación (ms)")
    ax2.grid(True, which="both", linestyle="--", alpha=0.5)
    ax2.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"\n[+] Gráfica de rendimiento guardada exitosamente: {filename}")


def print_conclusions(data: dict):
    """Analiza los resultados e identifica numéricamente el punto de inflexión."""
    sizes = data['sizes']
    bf_r = data['bf_radius']
    qt_r = data['qt_radius']

    break_even_n = None
    for i in range(len(sizes)):
        if qt_r[i] < bf_r[i]:
            break_even_n = sizes[i]
            break

    print("\n" + "=" * 80)
    print("ANÁLISIS COMPARATIVO DE RESULTADOS Y DISCUSIÓN")
    print("=" * 80)
    
    if break_even_n:
        print(f"\n1. PUNTO DE INFLEXIÓN (Break-even point):")
        print(f"   - El Quadtree comienza a ser más rápido que la Fuerza Bruta a partir de aproximadamente N ≈ {break_even_n} puntos.")
        print(f"   - Para conjuntos de datos pequeños (N < {break_even_n}), el overhead de la recursión y el recorrido del árbol")
        print(f"     hace que la fuerza bruta sea comparativamente competitiva o ligeramente más rápida.")
    
    print(f"\n2. ESCALABILIDAD CON N = 10,000 PUNTOS (Caso de estudio del laboratorio):")
    idx_10k = sizes.index(10000)
    speedup_r = bf_r[idx_10k] / qt_r[idx_10k] if qt_r[idx_10k] > 0 else 0
    speedup_nn = data['bf_nn'][idx_10k] / data['qt_nn'][idx_10k] if data['qt_nn'][idx_10k] > 0 else 0
    
    print(f"   - Búsqueda por Radio (500m): QuadTree es {speedup_r:.2f}x más rápido que Fuerza Bruta.")
    print(f"   - Vecino Más Cercano:        QuadTree es {speedup_nn:.2f}x más rápido que Fuerza Bruta.")

    print("\n3. COMPLEJIDAD COMPUTACIONAL:")
    print("   - Fuerza Bruta: O(N) por consulta.")
    print("   - Quadtree:     O(log N) promedio por consulta | Construcción: O(N log N).")
    print("   - En sistemas de logística real con miles de consultas por segundo sobre un mapa estático,")
    print("     el costo de construcción O(N log N) se amortiza casi instantáneamente.")
    print("=" * 80)


if __name__ == '__main__':
    print("=== INICIANDO BENCHMARK DE RENDIMIENTO (QUADTREE VS FUERZA BRUTA) ===")
    results = run_benchmarks()
    plot_performance_results(results)
    print_conclusions(results)