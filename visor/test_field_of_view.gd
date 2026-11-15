extends Control

@export var target_scene: PackedScene
@export var velocidad: float = 100.0

var target: MeshInstance3D

func start() -> void:
	var timer = Timer.new()
	add_child(timer)

	timer.wait_time = 1.0
	timer.one_shot = true
	timer.timeout.connect(spawn_target)
	timer.start()


func spawn_target() -> void:
	target = target_scene.instantiate()
	add_child(target)

	target.global_position = Vector3(2.0, 0.0, -1.0)

func _process(delta: float) -> void:
	if target != null:
		var centro = Vector3(0, 0, 0)

		target.position = target.position.move_toward(
			centro,
			velocidad * delta
		)
