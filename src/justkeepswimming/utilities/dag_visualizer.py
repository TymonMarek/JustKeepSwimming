"""
DAG Visualizer - A debugging tool to visualize the system execution graph.
Runs in a separate thread to avoid blocking the main game thread.
"""

import threading
import queue
import logging
import math
from typing import Dict, Set, List, Tuple, Optional
from dataclasses import dataclass

try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


# Constants
MAX_DISPLAYED_COMPONENTS = 5


@dataclass
class NodeData:
    """Data structure for a node in the DAG visualization."""

    name: str
    reads: List[str]
    writes: List[str]
    position: Tuple[int, int] = (0, 0)


@dataclass
class EdgeData:
    """Data structure for an edge in the DAG visualization."""

    from_node: str
    to_node: str


@dataclass
class GraphData:
    """Complete graph data for visualization."""

    nodes: Dict[str, NodeData]
    edges: List[EdgeData]
    layers: List[Set[str]]


class DAGVisualizer:
    """
    Visualizes the DAG graph in a separate window on a separate thread.
    Thread-safe communication via queue.
    """

    def __init__(self, title: str = "DAG Visualization"):
        self.logger = logging.getLogger("DAGVisualizer")
        self.title = title
        self.window_size = (1200, 800)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.data_queue: queue.Queue[Optional[GraphData]] = queue.Queue()
        self.current_graph: Optional[GraphData] = None

    def start(self) -> None:
        """Start the visualization thread."""
        if not PYGAME_AVAILABLE:
            self.logger.warning("pygame not available, DAG visualizer cannot start")
            return

        if self.running:
            self.logger.warning("DAG visualizer already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_visualization, daemon=True)
        self.thread.start()
        self.logger.info("DAG visualizer thread started")

    def stop(self) -> None:
        """Stop the visualization thread."""
        if not self.running:
            return

        self.running = False
        self.data_queue.put(None)  # Signal thread to stop
        if self.thread:
            self.thread.join(timeout=2.0)
        self.logger.info("DAG visualizer thread stopped")

    def update_graph(self, graph_data: GraphData) -> None:
        """Update the graph data for visualization (thread-safe)."""
        if not self.running:
            return

        try:
            # Clear old data and add new
            while True:
                try:
                    self.data_queue.get_nowait()
                except queue.Empty:
                    break
            self.data_queue.put(graph_data)
        except Exception as e:
            self.logger.error(f"Error updating graph: {e}")

    def _run_visualization(self) -> None:
        """Main visualization loop running in separate thread."""
        try:
            # Initialize pygame in this thread
            pygame.init()
            screen = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption(self.title)
            clock = pygame.time.Clock()

            # Colors
            BG_COLOR = (30, 30, 40)
            NODE_COLOR = (70, 130, 180)
            NODE_SELECTED_COLOR = (100, 160, 210)
            EDGE_COLOR = (150, 150, 150)
            TEXT_COLOR = (255, 255, 255)
            READ_COLOR = (100, 200, 100)
            WRITE_COLOR = (200, 100, 100)

            font = pygame.font.SysFont("monospace", 12)
            title_font = pygame.font.SysFont("monospace", 16, bold=True)

            selected_node: Optional[str] = None

            while self.running:
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        # Check if user clicked on a node
                        mouse_pos = pygame.mouse.get_pos()
                        selected_node = self._find_node_at_position(mouse_pos)

                # Check for new graph data
                try:
                    data = self.data_queue.get_nowait()
                    if data is None:
                        break
                    self.current_graph = data
                    self._calculate_node_positions()
                except queue.Empty:
                    pass

                # Clear screen
                screen.fill(BG_COLOR)

                # Draw title
                title_text = title_font.render("System Execution DAG", True, TEXT_COLOR)
                screen.blit(title_text, (10, 10))

                # Draw graph if available
                if self.current_graph:
                    self._draw_graph(
                        screen,
                        font,
                        NODE_COLOR,
                        NODE_SELECTED_COLOR,
                        EDGE_COLOR,
                        TEXT_COLOR,
                        READ_COLOR,
                        WRITE_COLOR,
                        selected_node,
                    )
                else:
                    no_data_text = font.render(
                        "Waiting for graph data...", True, TEXT_COLOR
                    )
                    screen.blit(no_data_text, (10, 50))

                # Draw instructions
                self._draw_instructions(screen, font, TEXT_COLOR)

                pygame.display.flip()
                clock.tick(30)  # 30 FPS

        except Exception as e:
            self.logger.error(f"Error in visualization thread: {e}", exc_info=True)
        finally:
            pygame.quit()

    def _calculate_node_positions(self) -> None:
        """Calculate positions for nodes based on their layers."""
        if not self.current_graph:
            return

        layers = self.current_graph.layers
        if not layers:
            return

        margin = 50
        vertical_spacing = 150

        for layer_idx, layer in enumerate(layers):
            y = margin + 80 + layer_idx * vertical_spacing
            nodes_in_layer = list(layer)
            layer_width = len(nodes_in_layer)

            if layer_width == 0:
                continue

            # Calculate horizontal spacing
            available_width = self.window_size[0] - 2 * margin
            horizontal_spacing = available_width / max(layer_width, 1)

            for node_idx, node_name in enumerate(nodes_in_layer):
                x = margin + node_idx * horizontal_spacing + horizontal_spacing / 2
                if node_name in self.current_graph.nodes:
                    self.current_graph.nodes[node_name].position = (int(x), int(y))

    def _draw_graph(
        self,
        screen,
        font,
        node_color,
        selected_color,
        edge_color,
        text_color,
        read_color,
        write_color,
        selected_node: Optional[str],
    ) -> None:
        """Draw the graph on the screen."""
        if not self.current_graph:
            return

        # Draw edges first (so they appear behind nodes)
        for edge in self.current_graph.edges:
            from_node = self.current_graph.nodes.get(edge.from_node)
            to_node = self.current_graph.nodes.get(edge.to_node)

            if from_node and to_node:
                pygame.draw.line(
                    screen, edge_color, from_node.position, to_node.position, 2
                )

                # Draw arrow head
                self._draw_arrow_head(
                    screen, from_node.position, to_node.position, edge_color
                )

        # Draw nodes
        node_radius = 30
        for node_name, node_data in self.current_graph.nodes.items():
            color = selected_color if node_name == selected_node else node_color

            # Draw node circle
            pygame.draw.circle(screen, color, node_data.position, node_radius)
            pygame.draw.circle(screen, text_color, node_data.position, node_radius, 2)

            # Draw node name
            name_text = font.render(node_name, True, text_color)
            text_rect = name_text.get_rect(center=node_data.position)
            screen.blit(name_text, text_rect)

            # If selected, show details
            if node_name == selected_node:
                self._draw_node_details(
                    screen, font, node_data, text_color, read_color, write_color
                )

    def _draw_arrow_head(self, screen, start_pos, end_pos, color) -> None:
        """Draw an arrow head at the end of an edge."""
        # Calculate angle
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        angle = math.atan2(dy, dx)

        # Arrow head size
        arrow_length = 15
        arrow_angle = math.pi / 6  # 30 degrees

        # Calculate arrow head points
        x1 = end_pos[0] - arrow_length * math.cos(angle - arrow_angle)
        y1 = end_pos[1] - arrow_length * math.sin(angle - arrow_angle)
        x2 = end_pos[0] - arrow_length * math.cos(angle + arrow_angle)
        y2 = end_pos[1] - arrow_length * math.sin(angle + arrow_angle)

        pygame.draw.line(screen, color, end_pos, (int(x1), int(y1)), 2)
        pygame.draw.line(screen, color, end_pos, (int(x2), int(y2)), 2)

    def _draw_node_details(
        self, screen, font, node_data: NodeData, text_color, read_color, write_color
    ) -> None:
        """Draw detailed information about a selected node."""
        detail_x = 10
        detail_y = self.window_size[1] - 200

        # Background box
        pygame.draw.rect(screen, (40, 40, 50), (detail_x - 5, detail_y - 5, 400, 190))
        pygame.draw.rect(screen, text_color, (detail_x - 5, detail_y - 5, 400, 190), 2)

        # Node name
        y_offset = detail_y
        title = font.render(f"System: {node_data.name}", True, text_color)
        screen.blit(title, (detail_x, y_offset))
        y_offset += 25

        # Reads
        reads_label = font.render("Reads:", True, read_color)
        screen.blit(reads_label, (detail_x, y_offset))
        y_offset += 20

        if node_data.reads:
            for component in node_data.reads[:MAX_DISPLAYED_COMPONENTS]:
                text = font.render(f"  - {component}", True, text_color)
                screen.blit(text, (detail_x, y_offset))
                y_offset += 18
        else:
            text = font.render("  (none)", True, text_color)
            screen.blit(text, (detail_x, y_offset))
            y_offset += 18

        # Writes
        writes_label = font.render("Writes:", True, write_color)
        screen.blit(writes_label, (detail_x, y_offset))
        y_offset += 20

        if node_data.writes:
            for component in node_data.writes[:MAX_DISPLAYED_COMPONENTS]:
                text = font.render(f"  - {component}", True, text_color)
                screen.blit(text, (detail_x, y_offset))
                y_offset += 18
        else:
            text = font.render("  (none)", True, text_color)
            screen.blit(text, (detail_x, y_offset))
            y_offset += 18

    def _draw_instructions(self, screen, font, text_color) -> None:
        """Draw usage instructions."""
        instructions = [
            "Click on a node to view details",
            "Close window or press ESC to exit",
        ]

        y = self.window_size[1] - 40
        for instruction in instructions:
            text = font.render(instruction, True, text_color)
            screen.blit(text, (self.window_size[0] - 350, y))
            y += 18

    def _find_node_at_position(self, pos: Tuple[int, int]) -> Optional[str]:
        """Find which node is at the given position."""
        if not self.current_graph:
            return None

        node_radius = 30
        for node_name, node_data in self.current_graph.nodes.items():
            dx = pos[0] - node_data.position[0]
            dy = pos[1] - node_data.position[1]
            distance_sq = dx * dx + dy * dy

            if distance_sq <= node_radius * node_radius:
                return node_name

        return None


def extract_graph_data_from_scheduler(scheduler) -> GraphData:
    """
    Extract graph data from a SystemScheduler instance.

    Args:
        scheduler: SystemScheduler instance

    Returns:
        GraphData object containing nodes, edges, and layers
    """
    from justkeepswimming.ecs.scheduler import SystemScheduler

    if not isinstance(scheduler, SystemScheduler):
        raise TypeError("scheduler must be a SystemScheduler instance")

    nodes: Dict[str, NodeData] = {}
    edges: List[EdgeData] = []

    # Extract nodes
    for system in scheduler.systems:
        node_name = type(system).__name__
        reads = [comp.__name__ for comp in system.reads]
        writes = [comp.__name__ for comp in system.writes]

        nodes[node_name] = NodeData(name=node_name, reads=reads, writes=writes)

    # Extract edges from the DAG
    for system in scheduler.systems:
        node_name = type(system).__name__
        system_node = scheduler._nodes.get(system)

        if system_node:
            for dependency in system_node.depends_on:
                dep_name = type(dependency.value).__name__
                edges.append(EdgeData(from_node=dep_name, to_node=node_name))

    # Get execution layers
    layers = []
    for layer in scheduler.execution_order():
        layer_names = {type(system).__name__ for system in layer}
        layers.append(layer_names)

    return GraphData(nodes=nodes, edges=edges, layers=layers)
