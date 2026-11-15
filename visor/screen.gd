@tool
extends Node3D

@export var ancho: float = 4.2
@export var alto: float = 1.8
@export var curvatura: float = 0.30
@export var radio_esquinas: float = 0.10
@export var grosor_borde: float = 0.005

func _ready() -> void:
	crear_pantalla()

func profundidad(x: float) -> float:
	return -curvatura * pow(x / (ancho / 2.0), 2)

func contorno(w: float, h: float, r: float) -> Array:
	var puntos: Array = []
	var centros = [
		Vector2(w/2-r, h/2-r),
		Vector2(-w/2+r, h/2-r),
		Vector2(-w/2+r, -h/2+r),
		Vector2(w/2-r, -h/2+r)
	]
	for esquina in range(4):
		for i in range(13):
			var angulo = deg_to_rad(90.0 * esquina + 90.0 * i / 12.0)
			var p = centros[esquina] + Vector2(
				cos(angulo), sin(angulo)) * r
			puntos.append(p)
	return puntos

func punto_3d(p: Vector2, z_extra: float = 0.0) -> Vector3:
	return Vector3(p.x, p.y, profundidad(p.x) + z_extra)

func crear_pantalla() -> void:
	var interior = contorno(
		ancho - grosor_borde * 2.0,
		alto - grosor_borde * 2.0,
		radio_esquinas - grosor_borde
	)
	var exterior = contorno(ancho, alto, radio_esquinas)

	var superficie = SurfaceTool.new()
	superficie.begin(Mesh.PRIMITIVE_TRIANGLES)

	for i in range(interior.size()):
		var siguiente = (i + 1) % interior.size()
		superficie.add_vertex(Vector3.ZERO)
		superficie.add_vertex(punto_3d(interior[i]))
		superficie.add_vertex(punto_3d(interior[siguiente]))

	var material = StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color("0f0d13ff")
	material.cull_mode = BaseMaterial3D.CULL_DISABLED

	var panel = MeshInstance3D.new()
	panel.mesh = superficie.commit()
	panel.material_override = material
	add_child(panel)

	var borde = SurfaceTool.new()
	borde.begin(Mesh.PRIMITIVE_TRIANGLES)

	for i in range(exterior.size()):
		var j = (i + 1) % exterior.size()
		var a = punto_3d(exterior[i], 0.005)
		var b = punto_3d(exterior[j], 0.005)
		var c = punto_3d(interior[i], 0.005)
		var d = punto_3d(interior[j], 0.005)

		for p in [a, c, b, b, c, d]:
			borde.add_vertex(p)

	var luz = StandardMaterial3D.new()
	luz.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	luz.albedo_color = Color("e39cffff")
	luz.emission_enabled = true
	luz.emission = Color(0.89, 0.612, 1.0, 1.0)
	luz.emission_energy_multiplier = 3.0
	luz.cull_mode = BaseMaterial3D.CULL_DISABLED

	var marco = MeshInstance3D.new()
	marco.mesh = borde.commit()
	marco.material_override = luz
	add_child(marco)
