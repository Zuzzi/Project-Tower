import pygame as pg
from settings import *
from utility import *
import random
vector = pg.math.Vector2

	
class Background_first_layer(pg.sprite.Sprite):
	def __init__(self, game, tile, col, row):
		self._layer = 0
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		if tile == "R":
			self.image = game.spritesheet.get_image(1280, 384, TILESIZE, TILESIZE)
		else:
			self.image = game.spritesheet.get_image(1216, 384, TILESIZE, TILESIZE)
		self.game = game
		self.rect = self.image.get_rect()
		self.col = col
		self.row = row
		self.rect.x = col * TILESIZE
		self.rect.y = row * TILESIZE
	
		
class Background_second_layer(pg.sprite.Sprite):
	def __init__(self, game, tile, col, row):
		self._layer = 1
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		if tile == "T":
			self.image = game.spritesheet.get_image(960, 320, TILESIZE, TILESIZE)
		elif tile == "t":
			self.image = game.spritesheet.get_image(1024, 320, TILESIZE, TILESIZE)
		elif tile == "p":
			self.image = game.spritesheet.get_image(1088, 320, TILESIZE, TILESIZE)
		elif tile == "P":
			self.image = game.spritesheet.get_image(1216, 320, TILESIZE, TILESIZE)
		elif tile == "s":
			self.image = game.spritesheet.get_image(1280, 320, TILESIZE, TILESIZE)
		elif tile == "S":
			self.image = game.spritesheet.get_image(1344, 320, TILESIZE, TILESIZE)
		self.game = game
		self.rect = self.image.get_rect()
		self.col = col
		self.row = row
		self.rect.x = col * TILESIZE
		self.rect.y = row * TILESIZE
		
		
class Mob(pg.sprite.Sprite):
	def __init__(self, game, x, y):
		self.layer = 1
		self.groups = game.all_sprites, game.mobs
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = game.mob_img
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.vel = MOB_VEL
		self.rotated_right = False
		self.tollerance = random.randrange(10,30)
		self.radius = 5
		
	def update(self):
		if  320 + self.tollerance<=self.rect.y<=448 and 192<=self.rect.x<=576 + self.tollerance:    #go right
			self.rect.x += self.vel * self.game.dt
			if not self.rotated_right:
				self.image = pg.transform.rotate(self.image,90)
				self.rotated_right = True
		else:
			self.rect.y += self.vel * self.game.dt
			if self.rotated_right:
				self.image = pg.transform.rotate(self.image,-90)
				self.rotated_right = False
		if self.rect.y > HEIGHT:    #GAME OVER!
			self.kill()
			self.game.playing = False
			pg.mixer.music.fadeout(500)
			
			
			
class Grass_animation(pg.sprite.Sprite):
	def __init__(self, game, col, row):
		self.layer = 2
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = self.game.grass_animation
		self.rect = self.image.get_rect()
		self.rect.x = col * TILESIZE
		self.rect.y = row * TILESIZE
		self.col = col
		self.row = row
		
	def update(self):
		if self.game.mouse_col != self.col or self.game.mouse_row != self.row:
			self.kill() 


class Gun(pg.sprite.Sprite):
	def __init__(self, game, type, x, y):
		self.layer = 3
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.type = type
		self.image = self.get_original_image()
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.rot = 0
		self.fixed_pos = vector(x + TILESIZE/2, y + TILESIZE/2 )
		self.last_shot = 0
	
	def update(self):
		self.rot_speed = 0
		self.shoot()
		self.rot = (self.rot + self.rot_speed * self.game.dt)%360
		self.image = pg.transform.rotate(self.get_original_image(), self.rot)
		self.rect = self.image.get_rect()
		self.rect.center = self.fixed_pos
		for mob in self.game.mobs:
			if self.is_in_range(mob):
				mob_pos = vector(mob.rect.x, mob.rect.y) * TILESIZE
				gun_pos = vector(self.rect.x, self.rect.y) * TILESIZE
				self.rot = (mob_pos - gun_pos).angle_to(vector(1,0)) #look at the mob
				self.rect = self.image.get_rect()
				self.rect.center = self.fixed_pos	
	
	def get_original_image(self):
		if self.type == "machinegun":
			image = self.game.machinegun_img
		elif self.type == "double_machinegun":
			image = self.game.double_machinegun_img
		elif self.type == "rocket_louncher":
			image = self.game.rocket_louncher_img
		return image
	
	def shoot(self):
		now = pg.time.get_ticks()
		if now - self.last_shot > BULLET_RATE and self.type != "rocket_louncher":
			self.last_shot = now
			dir = vector(1, 0).rotate(-self.rot)
			if self.type == "machinegun":
				pos = self.fixed_pos + BARREL_OFFSET.rotate(-self.rot)
				Bullet(self.game,pos, dir)
				Flame(self.game,pos, self.rot)
				self.game.machinegun_sound.play()
			elif self.type == "double_machinegun":
				pos1 = self.fixed_pos + BARREL_1_OFFSET.rotate(-self.rot)
				pos2 = self.fixed_pos + BARREL_2_OFFSET.rotate(-self.rot)
				Bullet(self.game, pos1, dir)
				Bullet(self.game, pos2, dir)
				Flame(self.game, pos1, self.rot)
				Flame(self.game, pos2, self.rot)
				self.game.d_machinegun_sound.play()
		elif now - self.last_shot > ROCKET_RATE and self.type == "rocket_louncher":
			self.last_shot = now
			dir = vector(1,0).rotate(-self.rot)
			pos = self.fixed_pos + BARREL_OFFSET.rotate(-self.rot)
			Rocket(self.game, pos, dir, self.rot)
			Flame(self.game, pos, self.rot)
			self.game.r_louncher_sound.play()
	
	def is_in_range(self, mob):
		if self.type == "machinegun" or self.type == "double_machinegun":
			if abs(self.rect.x - mob.rect.x) < BULLET_RANGE and abs(self.rect.y - mob.rect.y) < BULLET_RANGE:
				return True
		if self.type == "rocket_louncher":
			if abs(self.rect.x - mob.rect.x) < ROCKET_RANGE and abs(self.rect.y - mob.rect.y) < ROCKET_RANGE:
				return True
		return False
					

class Button(pg.sprite.Sprite):
	def __init__(self, game, gun, x, y, checked, price):
		self.layer = 2
		self.groups = game.buttons, game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = game.button_unchecked_img
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.rect.x = self.x
		self.rect.y = self.y
		self.checked = checked
		self.gun = gun
		self.price = price
	
	def update(self):
		if self.checked:
			self.image = self.game.button_checked_img
		else:
			self.image = self.game.button_unchecked_img
		self.rect = self.image.get_rect()
		self.rect.x = self.x
		self.rect.y = self.y

		
class Bullet(pg.sprite.Sprite):
	def __init__(self, game, pos, dir):
		self.layer = 3
		self.groups = game.all_sprites, game.bullets
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = game.bullet_img
		self.rect = self.image.get_rect()
		self.pos = pos  
		self.rect.center = pos
		spread = random.uniform(-GUN_SPREAD, GUN_SPREAD)  # REAL random number, it regulates accuracy
		self.vel = dir.rotate(spread) * BULLET_SPEED
		self.spawn_time = pg.time.get_ticks()
		self.radius = 5
		
	def update(self):
		self.pos += self.vel * self.game.dt
		self.rect.center = self.pos
		if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
			self.kill()
		if self.pos.x > WIDTH - 10 or self.pos.x < 0 or self.pos.y > HEIGHT or self.pos.y < 0: #bullet offscreen
			self.kill()
		if pg.sprite.spritecollide(self, self.game.mobs, True, pg.sprite.collide_circle):
			self.kill()
			self.game.kills += 1
			self.game.info_panel.updated_kills = True


class Flame(pg.sprite.Sprite):
	def __init__(self, game, pos, rot):
		self.layer = 4
		self.groups = game.all_sprites
		pg.sprite.Sprite.__init__(self, self.groups)
		self.image = pg.transform.rotate(game.flame_img, rot)
		self.rect = self.image.get_rect()
		self.rect.center = pos
		self.spawn_time = pg.time.get_ticks()
	
	def update(self):
		if pg.time.get_ticks() - self.spawn_time > 50:
			self.kill() 	
		

class Rocket(pg.sprite.Sprite):
	def __init__(self, game, pos, dir, rot):
		self.layer = 3
		self.groups = game.all_sprites, game.bullets
		pg.sprite.Sprite.__init__(self, self.groups)
		self.game = game
		self.image = pg.transform.rotate(game.rocket_img, rot - 90)
		self.rect = self.image.get_rect()
		self.pos = pos  
		self.rect.center = pos
		self.vel =  dir * ROCKET_SPEED
		self.spawn_time = pg.time.get_ticks()
		self.radius = 20
		
	def update(self):
		self.pos += self.vel * self.game.dt
		self.rect.center = self.pos
		if pg.time.get_ticks() - self.spawn_time > ROCKET_LIFETIME:
			self.kill()
		if self.pos.x > WIDTH - 15 or self.pos.x < 0 or self.pos.y > HEIGHT or self.pos.y < 0: 
			self.kill()
		if pg.sprite.spritecollide(self, self.game.mobs, True, pg.sprite.collide_circle):
			Explosion(self.game, self.rect.center)
			self.game.explosion_sound.play()
			self.kill()
			

class Explosion (pg.sprite.Sprite):
	def __init__(self, game, center):
		self.layer = 3
		self.groups = game.all_sprites, game.explosions
		pg.sprite.Sprite.__init__(self, self.groups)
		self.image = game.explosion_animation[0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pg.time.get_ticks()
		self.game = game
		self.radius = 45
		
	def update(self):
		now = pg.time.get_ticks()
		if now - self.last_update > FPS:
			self.last_update = now
			self.frame += 1
			if self.frame == len(self.game.explosion_animation):
				self.kill()
			else:
				center = self.rect.center
				self.image = self.game.explosion_animation[self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center
		hits = pg.sprite.spritecollide(self, self.game.mobs, True, pg.sprite.collide_circle)
		for hit in hits:
			hit.kill()
			self.game.kills += 1
			self.game.info_panel.updated_kills = True
