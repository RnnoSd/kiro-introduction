from dataclasses import dataclass, field


@dataclass
class CanvasConfig:
    width: int = 800
    height: int = 600


@dataclass
class PlayerConfig:
    start_x: float = 150.0
    start_y: float = 300.0
    base_speed: float = 5.0         # px/frame
    boost_speed: float = 10.0       # px/frame con BARRA ESPACIADORA
    sprite_width: int = 48
    sprite_height: int = 48
    cooldown_shoot: float = 0.5     # segundos
    cooldown_dash: float = 1.0      # segundos
    cooldown_brake: float = 5.0     # segundos
    brake_duration: float = 3.0     # segundos
    dash_distance: float = 100.0    # píxeles hacia la izquierda
    invulnerability_duration: float = 1.0  # segundos tras colisión con barra


@dataclass
class BarsConfig:
    width: int = 60
    gap_size_min: int = 150
    gap_size_max: int = 200
    spawn_distance: int = 200       # distancia mínima al borde derecho para generar nuevo par
    scroll_speed: float = 180.0     # px/s (sincronizado con Background)
    min_gap_y: int = 120
    max_gap_y: int = 480


@dataclass
class ObjectsConfig:
    size: int = 30                  # dimensión del objeto (cuadrado)
    speed_min: float = 3.0          # px/frame
    speed_max: float = 8.0          # px/frame
    penalty_points: int = 20        # penalización por Objeto_Rojo
    bonus_points: int = 100         # bonificación por Objeto_Verde


@dataclass
class ProjectileConfig:
    speed: float = 400.0            # px/s
    width: int = 20
    height: int = 6


@dataclass
class ScoreConfig:
    points_per_bar: int = 5
    life_bonus_threshold: int = 1000
    max_lives: int = 9
    initial_lives: int = 3


@dataclass
class BackgroundConfig:
    scroll_speed: float = 180.0     # px/s — debe coincidir con BarsConfig.scroll_speed


@dataclass
class GameConfig:
    canvas: CanvasConfig = field(default_factory=CanvasConfig)
    player: PlayerConfig = field(default_factory=PlayerConfig)
    bars: BarsConfig = field(default_factory=BarsConfig)
    objects: ObjectsConfig = field(default_factory=ObjectsConfig)
    projectile: ProjectileConfig = field(default_factory=ProjectileConfig)
    score: ScoreConfig = field(default_factory=ScoreConfig)
    background: BackgroundConfig = field(default_factory=BackgroundConfig)
