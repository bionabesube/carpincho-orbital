extends MeshInstance3D

var direction: Vector2
var speed: float = 1.0

func set_up(
	new_direction: Vector2,
	new_speed: float,
):
	direction = new_direction.normalized()
	speed = new_speed

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	# Movimiento y aceleración
	position += Vector3(
		direction.x,
		direction.y,
		0
	) * speed * delta
