extends Control


func _on_boton_volver_pressed():
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_boton_volumen_pressed():
	get_tree().change_scene_to_file("res://scenes/menu_audio.tscn")


func _on_boton_resolucion_pressed():
	pass
