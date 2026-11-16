extends Node2D

@onready var sprite = $Sprite2D
@export var camera: Camera3D
@export var detection_radius: float = 0.08
var target_position: Vector2 = Vector2(0, 0)
var target_traking: bool = false

signal target_found()

func _ready():
	Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)

func _process(delta):
	global_position = get_global_mouse_position()
	
	if target_traking:
		var world_position = get_mouse_world_position()
		var distance = Vector2(
			world_position.x - target_position.x,
			world_position.y - target_position.y
		).length()
		if distance < detection_radius:
			target_found.emit()
		

func get_mouse_world_position() -> Vector2:
	var mouse_position = get_viewport().get_mouse_position()

	var ray_origin = camera.project_ray_origin(mouse_position)
	var ray_direction = camera.project_ray_normal(mouse_position)

	# Intersección con el plano Z = -1.7
	var distance = (-1.7 - ray_origin.z) / ray_direction.z
	
	var out = ray_origin + ray_direction * distance

	return Vector2(out.x, -out.y)




func _on_screen_new_target_position(position: Vector2, traking: bool) -> void:
	target_position = position
	target_traking = traking
