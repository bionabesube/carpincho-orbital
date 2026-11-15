
extends MeshInstance3D

@export var screen_width: float = 4.2
@export var screen_height: float = 1.8
@export var distance: float = 2.0
@export_range(1.0, 60.0) var curve_angle: float = 25.0
@export var segments: int = 40

var radius: float
var half_angle: float


func _ready():
	generate_screen()


func generate_screen():
	half_angle = deg_to_rad(curve_angle)
	radius = screen_width / (2.0 * sin(half_angle))

	var st = SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)

	# Crear vértices
	for j in range(2):
		for i in range(segments + 1):
			var u = float(i) / segments
			var theta = lerp(-half_angle, half_angle, u)

			var x = radius * sin(theta)
			var z = -distance + radius * (1.0 - cos(theta))
			var y = (j - 0.5) * screen_height

			st.set_uv(Vector2(u, float(j)))
			st.add_vertex(Vector3(x, y, z))

	# Crear triángulos
	for i in range(segments):
		var a = i
		var b = i + 1
		var c = segments + 1 + i
		var d = segments + 1 + i + 1

		st.add_index(a)
		st.add_index(b)
		st.add_index(c)

		st.add_index(b)
		st.add_index(d)
		st.add_index(c)

	st.generate_normals()
	mesh = st.commit()


# Obtener una posición sobre la pantalla.
# horizontal y vertical van de -1 a 1.

func get_surface_position(
	horizontal: float,
	vertical: float,
	offset: float = 0.01
) -> Vector3:

	var theta = horizontal * half_angle

	var normal = Vector3(
		-sin(theta),
		0,
		cos(theta)
	)

	var point = Vector3(
		radius * sin(theta),
		vertical * screen_height / 2.0,
		-distance + radius * (1.0 - cos(theta))
	)

	return point + normal * offset
