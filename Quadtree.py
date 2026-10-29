"""
Quadtree.py
Estructura de datos Quadtree 2D para consultas espaciales en logística urbana.
Desarrollado desde cero sin librerías externas de estructuras de datos.
"""

import math


class Point:
    """Representa un punto de entrega en un plano bidimensional (x, y)."""
    
    def __init__(self, x: float, y: float, data=None):
        self.x = float(x)
        self.y = float(y)
        self.data = data  # Información adicional opcional (ID de entrega, dirección, etc.)

    def distance_to(self, other: 'Point') -> float:
        """Calcula la distancia euclidiana hacia otro punto."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def distance_sq_to(self, other: 'Point') -> float:
        """Calcula el cuadrado de la distancia euclidiana (optimización computacional)."""
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def __repr__(self):
        return f"Point({self.x:.2f}, {self.y:.2f})"


class BoundingBox:
    """
    Representa una región rectangular alineada con los ejes (AABB - Axis-Aligned Bounding Box).
    Definida por su centro (x, y) y sus medias extensiones (half_width, half_height).
    """

    def __init__(self, center_x: float, center_y: float, half_width: float, half_height: float):
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.half_width = float(half_width)
        self.half_height = float(half_height)

    def contains_point(self, point: Point) -> bool:
        """Verifica si un punto se encuentra dentro de los límites del rectángulo."""
        return (
            (self.center_x - self.half_width <= point.x <= self.center_x + self.half_width) and
            (self.center_y - self.half_height <= point.y <= self.center_y + self.half_height)
        )

    def intersects_box(self, other: 'BoundingBox') -> bool:
        """Verifica si este rectángulo colisiona o se solapa con otro BoundingBox."""
        return not (
            other.center_x - other.half_width > self.center_x + self.half_width or
            other.center_x + other.half_width < self.center_x - self.half_width or
            other.center_y - other.half_height > self.center_y + self.half_height or
            other.center_y + other.half_height < self.center_y - self.half_height
        )

    def intersects_circle(self, center: Point, radius: float) -> bool:
        """
        Verifica si este rectángulo interseca con un círculo de centro y radio dados.
        Crucial para podar ramas en la búsqueda por radio (Range Search).
        """
        # Encontrar el punto más cercano del rectángulo al centro del círculo
        closest_x = max(self.center_x - self.half_width, min(center.x, self.center_x + self.half_width))
        closest_y = max(self.center_y - self.half_height, min(center.y, self.center_y + self.half_height))

        # Distancia desde el punto más cercano al centro del círculo
        distance_x = center.x - closest_x
        distance_y = center.y - closest_y

        return (distance_x ** 2 + distance_y ** 2) <= (radius ** 2)


class QuadTree:
    """
    Estructura de Árbol Quadtree para particionamiento espacial 2D.
    """

    def __init__(self, boundary: BoundingBox, capacity: int = 4):
        self.boundary = boundary
        self.capacity = capacity  # Capacidad máxima de puntos antes de subdividir
        self.points: list[Point] = []
        self.divided = False

        # Referencias a los cuatro cuadrantes hijos
        self.northwest: 'QuadTree' = None
        self.northeast: 'QuadTree' = None
        self.southwest: 'QuadTree' = None
        self.southeast: 'QuadTree' = None

    def subdivide(self):
        """Divide el nodo actual en 4 cuadrantes (NW, NE, SW, SE)."""
        x = self.boundary.center_x
        y = self.boundary.center_y
        hw = self.boundary.half_width / 2.0
        hh = self.boundary.half_height / 2.0

        self.northwest = QuadTree(BoundingBox(x - hw, y + hh, hw, hh), self.capacity)
        self.northeast = QuadTree(BoundingBox(x + hw, y + hh, hw, hh), self.capacity)
        self.southwest = QuadTree(BoundingBox(x - hw, y - hh, hw, hh), self.capacity)
        self.southeast = QuadTree(BoundingBox(x + hw, y - hh, hw, hh), self.capacity)

        self.divided = True

    def insert(self, point: Point) -> bool:
        """
        Inserta un punto en el Quadtree de forma recursiva.
        Retorna True si fue insertado, False si está fuera del límite.
        """
        if not self.boundary.contains_point(point):
            return False

        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True

        if not self.divided:
            self.subdivide()
            # Reorganizar los puntos existentes en el nodo actual hacia los hijos
            existing_points = self.points
            self.points = []
            for p in existing_points:
                self._insert_into_children(p)

        return self._insert_into_children(point)

    def _insert_into_children(self, point: Point) -> bool:
        """Intenta insertar el punto en cualquiera de los 4 sub-cuadrantes."""
        return (
            self.northwest.insert(point) or
            self.northeast.insert(point) or
            self.southwest.insert(point) or
            self.southeast.insert(point)
        )

    def query_radius(self, center: Point, radius: float, found_points: list[Point] = None) -> list[Point]:
        """
        Búsqueda por Radio (Range Search).
        Retorna todos los puntos dentro del radio 'radius' centrado en 'center'.
        """
        if found_points is None:
            found_points = []

        # Poda: Si el cuadrante no interseca con el círculo de búsqueda, se descarta todo el subárbol
        if not self.boundary.intersects_circle(center, radius):
            return found_points

        # Si el nodo es una hoja, revisar sus puntos
        if not self.divided:
            radius_sq = radius ** 2
            for p in self.points:
                if center.distance_sq_to(p) <= radius_sq:
                    found_points.append(p)
        else:
            # Recorrer los hijos recursivamente
            self.northwest.query_radius(center, radius, found_points)
            self.northeast.query_radius(center, radius, found_points)
            self.southwest.query_radius(center, radius, found_points)
            self.southeast.query_radius(center, radius, found_points)

        return found_points

    def nearest_neighbor(self, target: Point, best_candidate: tuple[Point, float] = (None, float('inf'))) -> tuple[Point, float]:
        """
        Encuentra el punto más cercano (Nearest Neighbor) al punto objetivo.
        Retorna una tupla (Punto_Mas_Cercano, Distancia_Minima).
        Aplica poda inteligente 'Branch and Bound'.
        """
        best_point, best_dist = best_candidate

        # Poda: Si la región rectangular está más lejos que la mejor distancia encontrada, omitir
        if not self.boundary.intersects_circle(target, best_dist):
            return best_point, best_dist

        # Si estamos en un nodo hoja, evaluar los puntos guardados
        if not self.divided:
            for p in self.points:
                d = target.distance_to(p)
                if d < best_dist:
                    best_dist = d
                    best_point = p
            return best_point, best_dist

        # Ordenar el recorrido de hijos priorizando el más cercano al objetivo
        children = [self.northwest, self.northeast, self.southwest, self.southeast]
        
        # Calcular distancia del objetivo al centro de cada sub-cuadrante para visitar primero los más prometedores
        children.sort(key=lambda child: (child.boundary.center_x - target.x)**2 + (child.boundary.center_y - target.y)**2)

        for child in children:
            best_point, best_dist = child.nearest_neighbor(target, (best_point, best_dist))

        return best_point, best_dist