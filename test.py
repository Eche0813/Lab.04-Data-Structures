"""
test.py
Pruebas unitarias y verificación visual para la implementación del Quadtree.
Genera las gráficas del mapa espacial, el radio de búsqueda y el vecino más cercano.
"""

import unittest
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from Quadtree import Point, BoundingBox, QuadTree


# ----------------------------------------------------------------------
# 1. PRUEBAS UNITARIAS (UNITTTEST)
# ----------------------------------------------------------------------

class TestQuadTree(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para pruebas: 1000 puntos aleatorios en plano 10,000 x 10,000."""
        random.seed(42)  # Semilla fija para reproducibilidad
        self.boundary = BoundingBox(5000, 5000, 5000, 5000)
        self.qt = QuadTree(self.boundary, capacity=4)
        
        self.points = [
            Point(random.uniform(0, 10000), random.uniform(0, 10000), data=f"P_{i}")
            for i in range(1000)
        ]
        for p in self.points:
            self.qt.insert(p)

    def test_insertion_count(self):
        """Verifica que todos los puntos dentro del área se inserten correctamente."""
        def count_points(node: QuadTree) -> int:
            if not node.divided:
                return len(node.points)
            return (count_points(node.northwest) + count_points(node.northeast) +
                    count_points(node.southwest) + count_points(node.southeast))

        self.assertEqual(count_points(self.qt), 1000)

    def test_range_search_accuracy(self):
        """Compara la Búsqueda por Radio del Quadtree contra Fuerza Bruta."""
        center = Point(5000, 5000)
        radius = 1500.0

        # Fuerza bruta
        expected = [p for p in self.points if center.distance_to(p) <= radius]
        
        # Quadtree
        result = self.qt.query_radius(center, radius)

        # Comprobar mismo número de elementos y mismos puntos
        self.assertEqual(len(result), len(expected))
        self.set_of_tuples = lambda pts: {(p.x, p.y) for p in pts}
        self.assertEqual(self.set_of_tuples(result), self.set_of_tuples(expected))

    def test_nearest_neighbor_accuracy(self):
        """Compara el Vecino Más Cercano del Quadtree contra Fuerza Bruta."""
        target = Point(3200, 7800)

        # Fuerza bruta
        expected_point = min(self.points, key=lambda p: target.distance_to(p))
        expected_dist = target.distance_to(expected_point)

        # Quadtree
        best_point, best_dist = self.qt.nearest_neighbor(target)

        self.assertIsNotNone(best_point)
        self.assertAlmostEqual(best_dist, expected_dist, places=5)
        self.assertAlmostEqual(best_point.x, expected_point.x, places=5)
        self.assertAlmostEqual(best_point.y, expected_point.y, places=5)


# ----------------------------------------------------------------------
# 2. FUNCIONES DE VISUALIZACIÓN ESPACIAL (MATPLOTLIB)
# ----------------------------------------------------------------------

def draw_quadtree_boundaries(ax, node: QuadTree):
    """Dibuja recursivamente las subdivisiones rectangulares del Quadtree."""
    box = node.boundary
    rect = patches.Rectangle(
        (box.center_x - box.half_width, box.center_y - box.half_height),
        box.half_width * 2,
        box.half_height * 2,
        linewidth=0.5,
        edgecolor='#BDC3C7',
        facecolor='none',
        linestyle='--'
    )
    ax.add_patch(rect)

    if node.divided:
        draw_quadtree_boundaries(ax, node.northwest)
        draw_quadtree_boundaries(ax, node.northeast)
        draw_quadtree_boundaries(ax, node.southwest)
        draw_quadtree_boundaries(ax, node.southeast)


def visualize_range_search(points: list[Point], qt: QuadTree, center: Point, radius: float, filename="radio_search.png"):
    """Genera y guarda la gráfica de Búsqueda por Radio con vista global y detalle (Zoom In)."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Obtener puntos dentro del radio mediante el Quadtree
    found = qt.query_radius(center, radius)
    found_set = {(p.x, p.y) for p in found}

    # Separar puntos dentro y fuera
    inside_x = [p.x for p in found]
    inside_y = [p.y for p in found]
    outside_x = [p.x for p in points if (p.x, p.y) not in found_set]
    outside_y = [p.y for p in points if (p.x, p.y) not in found_set]

    # Margen para la vista detallada con Zoom In
    zoom_margin = radius * 1.5  # Mostrar un área de 750m alrededor del centro de 500m

    # ------------------------------------------------------------------
    # PANEL IZQUIERDO: VISTA GLOBAL (MAPA COMPLETO DE 10KM X 10KM)
    # ------------------------------------------------------------------
    draw_quadtree_boundaries(ax1, qt)

    ax1.scatter(outside_x, outside_y, c='#95A5A6', s=3, alpha=0.3, label='Puntos fuera')
    ax1.scatter(inside_x, inside_y, c='#E74C3C', s=12, alpha=0.9, label=f'Puntos dentro ({len(found)})')
    ax1.scatter([center.x], [center.y], c='#2ECC71', s=80, marker='*', zorder=5, label='Centro Consulta')

    # Círculo del radio en el mapa global
    circle_global = patches.Circle((center.x, center.y), radius, color='#2ECC71', fill=True, alpha=0.2, linewidth=1.2)
    circle_border_g = patches.Circle((center.x, center.y), radius, color='#27AE60', fill=False, linewidth=1.2)
    ax1.add_patch(circle_global)
    ax1.add_patch(circle_border_g)

    # Cuadro indicador de la zona de zoom
    zoom_rect = patches.Rectangle(
        (center.x - zoom_margin, center.y - zoom_margin),
        zoom_margin * 2, zoom_margin * 2,
        linewidth=1.5, edgecolor='#2ECC71', facecolor='none', linestyle='--'
    )
    ax1.add_patch(zoom_rect)

    ax1.set_title(f"Vista Global - Plano Urbano ({len(found)} puntos en {radius}m)", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Coordenada X (metros)")
    ax1.set_ylabel("Coordenada Y (metros)")
    ax1.legend(loc='upper right')
    ax1.set_aspect('equal')

    # ------------------------------------------------------------------
    # PANEL DERECHO: VISTA DETALLADA CON ZOOM IN
    # ------------------------------------------------------------------
    draw_quadtree_boundaries(ax2, qt)

    # Filtrar puntos fuera pero dentro del área de zoom para no recargar el plot
    zoom_outside_x = [p.x for p in points if (p.x, p.y) not in found_set and abs(p.x - center.x) <= zoom_margin and abs(p.y - center.y) <= zoom_margin]
    zoom_outside_y = [p.y for p in points if (p.x, p.y) not in found_set and abs(p.x - center.x) <= zoom_margin and abs(p.y - center.y) <= zoom_margin]

    ax2.scatter(zoom_outside_x, zoom_outside_y, c='#95A5A6', s=20, alpha=0.5, label='Puntos fuera del radio')
    ax2.scatter(inside_x, inside_y, c='#E74C3C', s=30, alpha=0.9, label=f'Puntos dentro ({len(found)})')
    ax2.scatter([center.x], [center.y], c='#2ECC71', s=150, marker='*', zorder=5, label='Centro Consulta')

    # Círculo y frontera detallada
    circle_zoom = patches.Circle((center.x, center.y), radius, color='#2ECC71', fill=True, alpha=0.15, linewidth=1.8)
    circle_border_z = patches.Circle((center.x, center.y), radius, color='#27AE60', fill=False, linewidth=2, linestyle='-')
    ax2.add_patch(circle_zoom)
    ax2.add_patch(circle_border_z)

    # Ajustar límites del zoom
    ax2.set_xlim(center.x - zoom_margin, center.x + zoom_margin)
    ax2.set_ylim(center.y - zoom_margin, center.y + zoom_margin)

    ax2.set_title(f"Detalle (Zoom In) - Radio R = {radius:.0f}m", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Coordenada X (metros)")
    ax2.set_ylabel("Coordenada Y (metros)")
    ax2.legend(loc='upper right')
    ax2.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"[+] Gráfica de Radio con Zoom guardada exitosamente: {filename}")


def visualize_nearest_neighbor(points: list[Point], qt: QuadTree, target: Point, filename="nearest_neighbor.png"):
    """Genera y guarda la gráfica del vecino más cercano con vista global y recuadro de zoom."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Encontrar vecino más cercano
    nearest, dist = qt.nearest_neighbor(target)

    # ------------------------------------------------------------------
    # PANEL IZQUIERDO: VISTA GLOBAL (MAPA COMPLETO DE 10KM X 10KM)
    # ------------------------------------------------------------------
    draw_quadtree_boundaries(ax1, qt)

    px = [p.x for p in points if p != nearest]
    py = [p.y for p in points if p != nearest]
    ax1.scatter(px, py, c='#BDC3C7', s=3, alpha=0.3, label='Puntos de Entrega')

    ax1.scatter([target.x], [target.y], c='#9B59B6', s=80, marker='X', zorder=5, label='Ubicación Objetivo')
    ax1.scatter([nearest.x], [nearest.y], c='#E67E22', s=90, marker='o', zorder=5, label=f'Vecino ({dist:.2f}m)')

    # Resaltar la zona de zoom con un cuadro punteado
    zoom_margin = max(dist * 5, 200.0)  # Margen de acercamiento inteligente
    zoom_rect = patches.Rectangle(
        (target.x - zoom_margin, target.y - zoom_margin),
        zoom_margin * 2, zoom_margin * 2,
        linewidth=1.5, edgecolor='#E67E22', facecolor='none', linestyle='--'
    )
    ax1.add_patch(zoom_rect)

    ax1.set_title(f"Vista Global - Plano Urbano completo", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Coordenada X (metros)")
    ax1.set_ylabel("Coordenada Y (metros)")
    ax1.legend(loc='upper right')
    ax1.set_aspect('equal')

    # ------------------------------------------------------------------
    # PANEL DERECHO: VISTA DETALLADA CON ZOOM IN
    # ------------------------------------------------------------------
    draw_quadtree_boundaries(ax2, qt)

    # Filtrar puntos dentro del área de zoom para rendimiento visual
    in_zoom_x = [p.x for p in points if abs(p.x - target.x) <= zoom_margin and abs(p.y - target.y) <= zoom_margin and p != nearest]
    in_zoom_y = [p.y for p in points if abs(p.x - target.x) <= zoom_margin and abs(p.y - target.y) <= zoom_margin and p != nearest]
    
    ax2.scatter(in_zoom_x, in_zoom_y, c='#7F8C8D', s=25, alpha=0.6, label='Puntos vecinos')
    ax2.scatter([target.x], [target.y], c='#9B59B6', s=140, marker='X', zorder=5, label='Objetivo')
    ax2.scatter([nearest.x], [nearest.y], c='#E67E22', s=150, marker='o', zorder=5, label=f'Vecino Más Cercano ({dist:.2f}m)')

    # Línea de conexión y círculo de distancia mínima
    ax2.plot([target.x, nearest.x], [target.y, nearest.y], color='#E67E22', linestyle='--', linewidth=2)
    circle = patches.Circle((target.x, target.y), dist, color='#9B59B6', fill=False, linewidth=1.5, linestyle=':')
    ax2.add_patch(circle)

    # Establecer límites ajustados para el zoom
    ax2.set_xlim(target.x - zoom_margin, target.x + zoom_margin)
    ax2.set_ylim(target.y - zoom_margin, target.y + zoom_margin)

    ax2.set_title(f"Detalle (Zoom In) - Distancia: {dist:.2f}m", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Coordenada X (metros)")
    ax2.set_ylabel("Coordenada Y (metros)")
    ax2.legend(loc='upper right')
    ax2.set_aspect('equal')

    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"[+] Gráfica con Zoom guardada exitosamente: {filename}")


# ----------------------------------------------------------------------
# 3. EJECUCIÓN PRINCIPAL
# ----------------------------------------------------------------------

if __name__ == '__main__':
    print("=== EJECUTANDO PRUEBAS UNITARIAS ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQuadTree)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)

    if test_result.wasSuccessful():
        print("\n=== GENERANDO VISUALIZACIONES ESPACIALES ===")
        random.seed(101)
        
        # Generar 10.000 puntos de prueba en un área urbana de 10,000m x 10,000m (10km x 10km)
        NUM_POINTS = 10000
        CITY_SIZE = 10000.0  # metros
        
        boundary = BoundingBox(CITY_SIZE / 2, CITY_SIZE / 2, CITY_SIZE / 2, CITY_SIZE / 2)
        quadtree = QuadTree(boundary, capacity=8)

        delivery_points = [
            Point(random.uniform(0, CITY_SIZE), random.uniform(0, CITY_SIZE), data=f"Punto_{i}")
            for i in range(NUM_POINTS)
        ]

        for p in delivery_points:
            quadtree.insert(p)

        # 1. Visualización de Búsqueda por Radio (500m)
        center_query = Point(5000.0, 5000.0)
        search_radius = 500.0  # 500 metros
        visualize_range_search(delivery_points, quadtree, center_query, search_radius)

        # 2. Visualización de Vecino Más Cercano
        target_query = Point(3500.0, 7200.0)
        visualize_nearest_neighbor(delivery_points, quadtree, target_query)