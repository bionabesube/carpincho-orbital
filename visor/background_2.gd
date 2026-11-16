extends MeshInstance3D


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_test_field_of_view_space_pressed() -> void:
	hide()


func _on_main_menu_eye_traking_pressed() -> void:
	show()


func _on_main_menu_field_of_view_pressed() -> void:
	show()
