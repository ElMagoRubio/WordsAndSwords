extends CharacterBody2D

const speed = 500
const jump_height = -1500

const acceleration = 50
const friction = 70

const gravity = 150

const max_jumps = 2
var current_jump = 0

func _physics_process(delta):
	var input_dir: Vector2 = input()
	
	if input_dir != Vector2.ZERO:
		accelerate(input_dir)
		play_animation()
	else:
		add_friction()
		play_animation()
	
	player_movement()
	jump()

func input() -> Vector2:
	var input_dir = Vector2.ZERO
	
	input_dir.x = Input.get_axis("ui_left", "ui_right")
	input_dir = input_dir.normalized()
	return input_dir

func accelerate(direction):
	velocity = velocity.move_toward(speed * direction, acceleration)

func add_friction():
	velocity = velocity.move_toward(Vector2.ZERO, friction)

func player_movement():
	move_and_slide()

func jump():
	if Input.is_action_just_pressed("ui_up"):
		if current_jump < max_jumps:
			velocity.y = jump_height
			current_jump += 1
	else:
		velocity.y += gravity
	
	if is_on_floor():
		current_jump = 0

func play_animation():
	pass
