extends MeshInstance3D

var direction: Vector2
var area_size: Vector2
var speed: float = 1.0
var capsule: CapsuleMesh


func setup(
	new_direction: Vector2,
	new_area_size: Vector2,
	new_speed: float,
	new_rotation: float
):
	direction = new_direction.normalized()
	area_size = new_area_size
	speed = new_speed

	# Aplicar rotación inicial
	rotation_degrees.z = rad_to_deg(new_rotation) + 90

	# Obtener la cápsula existente
	capsule = mesh.duplicate() as CapsuleMesh
	mesh = capsule

func _process(delta):
	# Distancia al centro
	var distance = Vector2(position.x, position.y).length() + 1.0

	# Movimiento y aceleración
	position += Vector3(
		direction.x,
		direction.y,
		0
	) * speed * distance * delta

	# Aumentar altura de la cápsula
	if capsule:
		capsule.height = 0.1 * distance

	# Comprobar si salió del área
	if (
		abs(position.x) > area_size.x / 2.0
		or abs(position.y) > area_size.y / 2.0
	):
		queue_free()
