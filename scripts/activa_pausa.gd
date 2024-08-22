extends Control

@onready var menuContenedor = $MenuContenedor

func _ready():
	menuContenedor.visible = false

func _on_ajustes_pressed():
	menuContenedor.visible = not menuContenedor.visible
