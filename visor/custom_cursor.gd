extends Node2D

@onready var sprite = $Sprite2D
@export var camera: Camera3D

func _ready():
	Input.set_mouse_mode(Input.MOUSE_MODE_HIDDEN)

func _process(delta):
	global_position = get_global_mouse_position()
	print(get_mouse_world_position())

func get_mouse_world_position() -> Vector2:
	var mouse_position = get_viewport().get_mouse_position()

	var ray_origin = camera.project_ray_origin(mouse_position)
	var ray_direction = camera.project_ray_normal(mouse_position)

	# Intersección con el plano Z = -1.7
	var distance = (-1.7 - ray_origin.z) / ray_direction.z
	
	var out = ray_origin + ray_direction * distance

	return Vector2(out.x, -out.y)
