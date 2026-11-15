extends MeshInstance3D

@export var star_scene: PackedScene

@export var spawn_interval: float = 0.01
@export var star_speed: float = 2.0

# Dimensiones del fondo (ancho y alto)
@export var area_size: Vector2 = Vector2(30.0, 20.0)

var rng = RandomNumberGenerator.new()


func _ready():
	rng.randomize()

	# Crear temporizador
	var timer = Timer.new()
	add_child(timer)

	timer.wait_time = spawn_interval
	timer.timeout.connect(spawn_stars)
	timer.autostart = true
	timer.start()

func spawn_stars():
	spawn_star()
	spawn_star()

func spawn_star():
	# Instanciar estrella
	var star = star_scene.instantiate()
	
	add_child(star)

	# Posición inicial: centro del fondo
	star.position = Vector3.ZERO

	# Dirección aleatoria
	var angle = rng.randf_range(0.0, TAU)
	
	var direction = Vector2(
		cos(angle),
		sin(angle)
	)

	# Configurar estrella
	star.setup(
		direction,
		area_size,
		star_speed,
		angle
	)
