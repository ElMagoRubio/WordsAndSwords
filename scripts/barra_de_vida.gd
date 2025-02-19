extends Node2D

const MAX_PUNTOS_VIDA = 8

@onready var sprite_barra_vida = $Estados
@onready var puntos_vida

signal golpe(puntos_vida)

func _ready():
	puntos_vida = MAX_PUNTOS_VIDA


func _process(delta):
	sprite_barra_vida.play("hp_" + str(puntos_vida))


func recibe_golpe():
	if puntos_vida > 0:
		puntos_vida -= 1
	else:
		puntos_vida = MAX_PUNTOS_VIDA
	emit_signal("golpe", puntos_vida)



