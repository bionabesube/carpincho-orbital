extends Control

signal fieldOfView_pressed
signal eyeTraking_pressed

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass



func _on_field_of_view_pressed() -> void:
	fieldOfView_pressed.emit()
	hide()
	get_tree().current_scene.get_node("Background2").show()


func _on_eye_traking_pressed() -> void:
	eyeTraking_pressed.emit()
	hide()
	get_tree().current_scene.get_node("Background2").show()
