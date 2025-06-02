extends Node2D

func _ready():
	var text = Global.nombre_jugador + " se ha rendido.[center]"
	$CajaTexto1/Texto.text = "[center]" + text + "[/center]"
