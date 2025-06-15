extends Node2D
@onready var text = ""

func _ready():
	print(Global.rendicion_jugador)
	print (Global.combate)
	
	if Global.rendicion_jugador == true:
		text = "El jugador se ha rendido.[center]"
	elif Global.combate == true:
		text = "El jugador y " + Global.nombre_jugador + " se enfrentarán en combate[center]"
	else:
		text = Global.nombre_jugador + " se ha rendido.[center]"
		
	$CajaTexto1/Texto.text = "[center]" + text + "[/center]"


func _on_boton_salir_pressed():
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
