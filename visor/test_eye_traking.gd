extends Control

var count = 0

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_main_menu_eye_traking_pressed() -> void:
	show()
	$Label.set_text("0/10")


func _on_screen_end_test_eye_traking() -> void:
	hide()


func _on_custom_cursor_target_found() -> void:
	count += 1
	if count < 10:
		$Label.set_text(str(count)+"/10")
	else:
		count = 0
		
