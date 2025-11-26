extends Control

@onready var logo = $Logo
@onready var menuPrincipal = $MenuPrincipal
@onready var menuContenedor = $MenuContenedor
@onready var textAjustes = $MenuContenedor/TextPausa

func _ready():
	logo.visible = true
	menuPrincipal.visible = true
	menuContenedor.visible = false
	textAjustes.visible = false

func _on_boton_jugar_pressed():
	get_tree().change_scene_to_file("res://scenes/menu_seleccion_pj.tscn")

func _on_boton_ajustes_pressed():
	print("Ajustes pulsado")
	logo.visible = false
	menuPrincipal.visible = false
	menuContenedor.visible = true
	textAjustes.visible = true

func _on_boton_salir_pressed():
	get_tree().quit()
