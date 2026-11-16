@tool
extends Node3D

signal new_target_position(position: Vector2, traking: bool)
signal end_test_eye_traking()
signal FOV_found(fov: float)

@export var target_scene: PackedScene
var target_speed: float = 0.25
var target = null
var limited = false
var target_count = 0
@export var ancho: float = 4.2
@export var alto: float = 1.8
@export var curvatura: float = 0.30
@export var radio_esquinas: float = 0.10
@export var grosor_borde: float = 0.005

var material_fondo: StandardMaterial3D
var textura_original: Texture2D
var rng = RandomNumberGenerator.new()

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

		var puntos = [
			Vector2.ZERO,
			interior[i],
			interior[siguiente]
		]

		for p in puntos:
			var uv = Vector2(
				p.x / ancho + 0.5,
				p.y / alto + 0.5
			)
			superficie.set_uv(uv)
			superficie.add_vertex(punto_3d(p))

	material_fondo = StandardMaterial3D.new()
	material_fondo.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material_fondo.albedo_color = Color.WHITE
	textura_original = load("res://images/fondo.png")
	material_fondo.albedo_texture = textura_original

	var panel = MeshInstance3D.new()
	panel.mesh = superficie.commit()
	panel.material_override = material_fondo
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

func cambiar_fondo() -> void:
	if material_fondo.albedo_texture != null:
		material_fondo.albedo_texture = null
		material_fondo.albedo_color = Color.BLACK
	else:
		material_fondo.albedo_texture = textura_original
		material_fondo.albedo_color = Color.WHITE

func _process(delta: float) -> void:
	if limited:
		if target != null:
			if target.position.x < 0:
				target.queue_free()
				target = null

func _on_main_menu_field_of_view_pressed() -> void:
	cambiar_fondo()
	
	target = target_scene.instantiate()
	limited = true
	
	add_child(target)
	
	target.position = Vector3(1.45, 0, -0.3)
	
	target.set_up(
		Vector2(-1, 0),
		target_speed
	)


func _on_main_menu_eye_traking_pressed() -> void:
	cambiar_fondo()
	limited = false
	spawn_still_target()

func spawn_still_target() -> void:
	var position_x = rng.randf_range(-1.45, 1.45)
	var position_y = rng.randf_range(-0.7, 0.7)
	var position_z = -0.3
	new_target_position.emit(Vector2(position_x, position_y), true)
	
	target = target_scene.instantiate()
	
	add_child(target)
	
	target.position = Vector3(position_x, position_y, position_z)
	#target.position = Vector3(1.5, 0, -0.3)
	
	target.set_up(
		Vector2(0, 0),
		0.0
	)
	


func _on_test_field_of_view_space_pressed() -> void:
	cambiar_fondo()
	print("Yuliana aca screen.gd")
	print("Patita tu nana aca")
	if target != null:
		print(target.position.x)
		var FOV_angle = rad_to_deg(atan(target.position.x / 2))
		FOV_found.emit(FOV_angle)
		target.queue_free()
		target = null
	limited = false


func _on_custom_cursor_target_found() -> void:
	new_target_position.emit(Vector2(0, 0), false)
	target.queue_free()
	target_count += 1
	if target_count < 10:
		spawn_still_target()
	else:
		target_count = 0
		end_test_eye_traking.emit()
		


func _on_end_test_eye_traking() -> void:
	cambiar_fondo()
