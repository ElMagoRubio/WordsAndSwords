extends CharacterBody2D

const MAX_VELOCIDAD = 400
const ACELERACION_SALTO = 650
const ACELERACION_SALTO_BAJO = 400
const GRAVEDAD = 1300
const MAX_SALTOS = 2

@onready var animaciones = $Animaciones
@onready var timer_atk_descendente = $AtaqueDescendente
@onready var timer_atk_frontal = $AtaqueFrontal
@onready var timer_atk_ascendente = $AtaqueAscendente
@onready var timer_atk_aereo_descendente = $AtaqueAereoDescendente
@onready var timer_atk_aereo_descendente_suelo = $AtaqueAereoDescendenteSuelo
@onready var timer_atk_aereo_frontal = $AtaqueAereoFrontal
@onready var timer_atk_aereo_ascendente = $AtaqueAereoAscendente
@onready var timer_golpe = $Golpe
@onready var timer_muerte = $Muerte

@onready var esta_atacando = false
@onready var esta_deshabilitado = false
@onready var num_saltos = 0

func _ready():
	inicializa_timer(timer_atk_descendente, "attack_down")
	inicializa_timer(timer_atk_frontal, "attack_front")
	inicializa_timer(timer_atk_ascendente, "attack_up")
	inicializa_timer(timer_atk_aereo_descendente, "attack_down_air")
	inicializa_timer(timer_atk_aereo_descendente_suelo, "attack_down_air_fall")
	inicializa_timer(timer_atk_aereo_frontal, "attack_front_air")
	inicializa_timer(timer_atk_aereo_ascendente, "attack_up_air")
	inicializa_timer(timer_golpe, "hit")
	inicializa_timer(timer_muerte, "death")
	
	animaciones.play("idle")

func _physics_process(delta):
	var direccion = Input.get_axis("ui_move_left", "ui_move_right")
	
	if !esta_deshabilitado:
	#Si el PJ está en el suelo
		if is_on_floor():
			if not esta_atacando:
				num_saltos = 0
				#Calculamos direccion de movimiento
				if (animaciones.animation == "fall"):
					animaciones.play("landing")
				if direccion: 
					if direccion == 1:
						animaciones.flip_h = false
						animaciones.play("run")
						velocity.x = direccion * MAX_VELOCIDAD
					else:
						animaciones.flip_h = true
						animaciones.play("run")
						velocity.x = direccion * MAX_VELOCIDAD
				else:
					animaciones.play("idle")
					velocity.x = 0
				
				#Calculamos los ataques
				if animaciones.flip_h == false:
					if Input.is_action_pressed("ui_left_atk_direction"):
						jugador_bloqueo()
					elif Input.is_action_just_pressed("ui_right_atk_direction"):
						jugador_ataque_frontal()
					elif Input.is_action_just_pressed("ui_upward_atk_direction"):
						jugador_ataque_ascendente()
					elif Input.is_action_just_pressed("ui_downward_atk_direction"):
						jugador_ataque_descendente()
				else:
					if Input.is_action_pressed("ui_right_atk_direction"):
						jugador_bloqueo()
					elif Input.is_action_just_pressed("ui_left_atk_direction"):
						jugador_ataque_frontal()
					elif Input.is_action_just_pressed("ui_upward_atk_direction"):
						jugador_ataque_ascendente()
					elif Input.is_action_just_pressed("ui_downward_atk_direction"):
						jugador_ataque_descendente()
				if Input.is_action_pressed("ui_move_down"):
					if Input.is_action_just_pressed("ui_jump"):
						num_saltos += 1
						animaciones.play("low_jump")
					else:
						animaciones.play("down")
				else:
					if Input.is_action_just_pressed("ui_jump"):
						num_saltos += 1
						animaciones.play("jump")
						velocity = velocity.limit_length(ACELERACION_SALTO)
						velocity.y -= ACELERACION_SALTO
			else:
				if (animaciones.animation == "attack_down_air"):
					jugador_ataque_aereo_descendente_suelo()
				velocity.x = 0
		
		#Si el PJ no está en el suelo
		elif not is_on_floor():
			if direccion: 
				if direccion == 1:
					animaciones.flip_h = false
					velocity.x = direccion * MAX_VELOCIDAD
				else:
					animaciones.flip_h = true
					velocity.x = direccion * MAX_VELOCIDAD
			else:
					velocity.x = 0
			if not esta_atacando:
				if (num_saltos < MAX_SALTOS):
					if Input.is_action_just_pressed("ui_jump"):
						num_saltos += 1
						animaciones.play("roll")
						velocity.y -= ACELERACION_SALTO_BAJO
						velocity = velocity.limit_length(ACELERACION_SALTO_BAJO)
					elif animaciones.flip_h == false:
						if Input.is_action_pressed("ui_left_atk_direction"):
							jugador_bloqueo()
						elif Input.is_action_just_pressed("ui_right_atk_direction"):
							jugador_ataque_aereo_frontal()
						elif Input.is_action_just_pressed("ui_upward_atk_direction"):
							jugador_ataque_aereo_ascendente()
						elif Input.is_action_just_pressed("ui_downward_atk_direction"):
							velocity.y = 0
							jugador_ataque_aereo_descendente()
					elif animaciones.flip_h == true:
						if Input.is_action_just_pressed("ui_left_atk_direction"):
							jugador_ataque_aereo_frontal()
						elif Input.is_action_pressed("ui_right_atk_direction"):
							jugador_bloqueo()
						elif Input.is_action_just_pressed("ui_upward_atk_direction"):
							jugador_ataque_aereo_ascendente()
						elif Input.is_action_just_pressed("ui_downward_atk_direction"):
							velocity.y = 0
							jugador_ataque_aereo_descendente()
				elif num_saltos == 0:
					animaciones.play("fall")
				
			velocity.y += GRAVEDAD * delta
	
	
	move_and_slide()

func inicializa_timer(timer : Timer, nombre_animacion : StringName):
	timer.one_shot = true
	var wait_time_aux = 0
	var fps = animaciones.sprite_frames.get_animation_speed(nombre_animacion)
	print("Animation speed: " + str(fps))
	for frame in animaciones.sprite_frames.get_frame_count(nombre_animacion):
		wait_time_aux += 1 / fps * animaciones.sprite_frames.get_frame_duration(nombre_animacion, frame)
	
	print("wait time for " + timer.name + " timer: " + str(wait_time_aux))
	timer.wait_time = wait_time_aux
	print("CHECKSUM: wait time for " + timer.name + " timer: " + str(timer.wait_time))


func jugador_bloqueo():
	animaciones.play("block")


func jugador_ataque_descendente():
	print("Ataque descendente comienza")
	animaciones.play("attack_down")
	esta_atacando = true
	timer_atk_descendente.start()


func jugador_ataque_frontal():
	print("Ataque frontal comienza")
	animaciones.play("attack_front")
	esta_atacando = true
	timer_atk_frontal.start()


func jugador_ataque_ascendente():
	print("Ataque ascendente comienza")
	animaciones.play("attack_up")
	esta_atacando = true
	timer_atk_ascendente.start()
	

func jugador_ataque_aereo_descendente():
	print("Ataque descendente aereo comienza")
	animaciones.play("attack_down_air")
	esta_atacando = true
	timer_atk_aereo_descendente.start()

func jugador_ataque_aereo_descendente_suelo():
	print("Ataque descendente aereo en suelo comienza")
	animaciones.play("attack_down_air_fall")
	esta_atacando = true
	timer_atk_aereo_descendente_suelo.start()


func jugador_ataque_aereo_frontal():
	print("Ataque frontal aereo comienza")
	animaciones.play("attack_front_air")
	esta_atacando = true
	timer_atk_aereo_frontal.start()


func jugador_ataque_aereo_ascendente():
	print("Ataque ascendente comienza")
	animaciones.play("attack_up_air")
	esta_atacando = true
	timer_atk_aereo_ascendente.start()


func jugador_golpeado():
	print("Jugador ha sido golpeado")
	animaciones.play("hit")
	esta_deshabilitado = true
	timer_golpe.start()


func jugador_muere():
	print("Jugador ha muerto")
	animaciones.play("death")
	esta_deshabilitado = true
	timer_muerte.start()


func _on_ataque_descendente_timeout():
	esta_atacando = false
	print("ataque descendente over")


func _on_ataque_frontal_timeout():
	esta_atacando = false
	print("ataque frontal over")


func _on_ataque_ascendente_timeout():
	esta_atacando = false
	print("ataque ascendente over")


func _on_ataque_aereo_descendente_timeout():
	print("ataque descendente aereo over")
	


func _on_ataque_aereo_descendente_suelo_timeout():
	esta_atacando = false
	print("ataque descendente aereo en suelo over")
	animaciones.play("fall")


func _on_ataque_aereo_frontal_timeout():
	esta_atacando = false
	print("ataque frontal aereo over")
	animaciones.play("fall")


func _on_ataque_aereo_ascendente_timeout():
	esta_atacando = false
	print("ataque ascendente aereo over")
	animaciones.play("fall")

func _on_golpe_timeout():
	esta_deshabilitado = false
	print("Jugador se ha recuperado del golpe")

func _on_muerte_timeout():
	print("Jugador se ha recuperado del golpe")

func _on_recibe_golpe(puntos_vida):
	if puntos_vida > 0:
		jugador_golpeado()
	else:
		jugador_muere()
