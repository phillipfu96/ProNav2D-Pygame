import math
import random

import Setup
import pygame

MAX_FPS = Setup.MAX_FPS

pygame.init()
win = pygame.display.set_mode((Setup.WINDOW_WIDTH, Setup.WINDOW_HEIGHT), pygame.DOUBLEBUF, 16)
clock = pygame.time.Clock()

acc = 0

missileVector = pygame.math.Vector2(.8, 0)
mpos = 200, 200
mshape = [(-0.5, -0.866), (-0.5, 0.866), (2.0, 0.0)]

run = True
uv = pygame.Vector2(0, 100)
gain = 0
MVP2 = pygame.math.Vector2((0, 0))

red = (255, 0, 0)  # rgb color
yellow = (10, 250, 10)
white = (255, 255, 255)
grey = (200, 200, 200)


def recolor(color_elm, alpha):
    if color_elm >= 0:
        return 0
    else:
        return color_elm - alpha


def rotate_triangle(center, scale, mouse_pos):
    vMouse = pygame.math.Vector2(mouse_pos)
    vCenter = pygame.math.Vector2(center)
    angle = pygame.math.Vector2().angle_to(vMouse - vCenter)

    points = [(-0.5, -0.866), (-0.5, 0.866), (2.0, 0.0)]
    rotated_point = [pygame.math.Vector2(p).rotate(angle) for p in points]

    triangle_points = [(vCenter + p * scale) for p in rotated_point]
    return triangle_points


def VectorSlope(Vector2D):
    return math.atan2(Vector2D[1], Vector2D[0])


class Bullet:
    def __init__(self, location, speed, angle):
        self.center = location
        self.speed = speed * 3
        self.angle = angle
        self.velocity = pygame.math.Vector2((self.speed, 0))
        self.velocity = self.velocity.rotate(self.angle + random.randint(-7, 7))
        self.lifetime = 10 + random.randint(-1, 6)

    def update(self):
        self.center += self.velocity
        self.lifetime -= .1


class TargetClass:
    def __init__(self, location):
        self.center = location
        self.vel_vector = pygame.Vector2((.5, .5))
        self.perpendicular_velocity = pygame.Vector2((-self.vel_vector[1], self.vel_vector[0]))
        self.pos = self.center
        self.heading = math.atan2(self.center[1], self.center[0])

    def rotate(self, angle):
        self.vel_vector.rotate_ip(angle)

    def getpos(self):
        return self.pos

    def getheading(self):
        return math.degrees(math.atan2(self.vel_vector[1], self.vel_vector[0]))

    def update(self, alpha):
        self.vel_vector.rotate(6)
        self.center = self.center + self.vel_vector
        self.pos = self.center
        self.heading = math.atan2(self.center[1], self.center[0])


class MissileClass:
    def __init__(self, location, angle):
        self.center = location
        self.vel_vector = pygame.Vector2((.8, 0))
        self.vel_vector = self.vel_vector.rotate(angle)
        self.pos = self.center
        self.heading = math.atan2(self.vel_vector[1], self.vel_vector[0])
        self.perpendicular = self.vel_vector.rotate(90)

    def steer(self, Normal_acceleration):
        self.perpendicular.scale_to_length(Normal_acceleration)
        self.vel_vector += self.perpendicular

    def update(self):
        self.perpendicular = self.vel_vector.rotate(90)
        self.center = self.center + self.vel_vector


class ClassSmoke:
    def __init__(self, location):
        self.center = location
        self.life = 1
        self.x = self.center[0]
        self.y = self.center[1]
        self.color = random.choice([white, grey])

    def newcolor(self):
        alpha = 2
        r, g, b = self.color

        if r < alpha:
            r = 0
        else:
            r -= alpha

        if g < alpha:
            g = 0
        else:
            g -= alpha

        if b < alpha:
            b = 0
        else:
            b -= alpha

        if (r and g and b) == 0:
            self.life = 0

        self.color = (r, g, b)

    def update(self):
        self.x += random.randint(-10, 10) * .08
        self.y += random.randint(-10, 10) * .08
        self.center = self.x, self.y
        self.life += 1
        self.newcolor()


class FireParticle:
    def __init__(self, position):
        self.agespeed = 2
        self.center = position
        self.x = self.center[0]
        self.y = self.center[1]
        self.alpha = random.randint(-20, 20)
        self.color = (230 + self.alpha, 120 + self.alpha, 0 + self.alpha)
        self.age = 0

    def darken(self):
        self.new_color = []
        for c in self.color:
            nc = c - self.agespeed
            if nc <= 0:
                nc = 0
            self.new_color.append(nc)
        self.color = self.new_color

    def update(self):
        self.darken()
        self.x += random.randint(-1, 1) * self.age * 0.02
        self.y += random.randint(-1, 1) * self.age * 0.02
        self.center = self.x, self.y
        self.age += 1


class ChaffParticle:
    def __init__(self, location, angle):
        self.control = 0
        self.center = location
        self.speed = 1
        self.angle = angle
        self.velocity = pygame.math.Vector2((self.speed, 0))
        self.velocity.scale_to_length(self.speed)
        self.velocity = self.velocity.rotate(self.angle)
        self.life = 20
        self.size = 1
        self.color = (30, random.randint(100, 190), 20)

    def newcolor(self):
        alpha = 250
        r, g, b = self.color

        if r > alpha:
            r = 100
        else:
            r += 1

        if g > alpha:
            g = 255
        else:
            g += 1

        if b > alpha:
            b = 100
        else:
            b += 1

        if (r and g and b) == 255:
            self.life = 0
        self.color = (r, g, b)

    def update(self):
        self.newcolor()
        self.velocity.scale_to_length(self.life * .02)
        self.center += self.velocity
        self.life -= 0.05
        self.size += .03


class ClassExplosion:
    def __init__(self, location):
        self.center = location
        self.life = 1
        self.x = self.center[0]
        self.y = self.center[1]
        self.angle = random.randint(0, 360)
        self.launch = pygame.Vector2((0, 0))
        self.speed = random.randint(40, 100) / 300

    def update(self):
        self.launch.from_polar((random.randint(1, 10), self.angle))
        self.x += self.speed * self.launch[0]
        self.y += self.speed * self.launch[1]
        self.center = self.x, self.y
        self.life += 1
        self.speed -= .004


explodeparts = []


def explode(explosionpos):
    for i in range(30):
        explodeparts.append(ClassExplosion(explosionpos))


exploding = False
target1 = TargetClass((500, 500))
missile1 = MissileClass((200, 200), 0)
smokeMissile = []
fire = []

for i in range(30):
    fire.append(FireParticle(missile1.center))
for i in range(100):
    smokeMissile.append(ClassSmoke(target1.center))

bullets = []


def shoot():
    bullets.append(Bullet((0, 0) + targpos, 1, math.degrees(VectorSlope(target1.vel_vector))))


canshoot = True
chaffs = []
log = []


def chaff():
    for i in range(10):
        chaffs.append(ChaffParticle((0, 0) + targpos, math.degrees(VectorSlope(target1.vel_vector))))


while run:
    pygame.display.set_caption("FPS: " + str(round(clock.get_fps(), 1)))
    clock.tick(MAX_FPS)
    targpos = target1.center
    targheading = target1.heading
    log.append(clock.get_time())
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        acc -= .025

    if keys[pygame.K_RIGHT]:
        acc += .025

    if keys[pygame.K_UP]:
        gain += .05

    if keys[pygame.K_SPACE]:
        if pygame.time.get_ticks() % 9 == 0:
            shoot()
    if keys[pygame.K_c]:
        if pygame.time.get_ticks() % 9 == 0:
            chaff()

    # target
    gain = gain - gain * .1
    OldTargetPos = target1.center
    target1.rotate(acc)
    acc = acc - (acc * 0.01)
    target1.update(0)
    NewTargetPos = target1.center

    dp = (NewTargetPos + target1.vel_vector) * 20

    dpx = (dp.x, 0)
    dpy = (0, dp.y)
    perp = pygame.Vector2(target1.vel_vector)
    perp.rotate_ip(90)

    perp.scale_to_length(acc * 10)

    # missile
    OldMissilePos2 = missile1.center
    missile1.update()
    NewMissilePos2 = missile1.center

    Old_LOS = pygame.Vector2(OldTargetPos) - OldMissilePos2
    New_LOS = NewTargetPos - NewMissilePos2
    old_Slope = math.atan2(Old_LOS[1], Old_LOS[0])
    new_Slope = math.atan2(New_LOS[1], New_LOS[0])
    LOS_rate = new_Slope - old_Slope
    Acc = LOS_rate * 3
    if abs(Acc) > 1:
        print(old_Slope, new_Slope, LOS_rate)
        LOS_rate = abs(new_Slope) - abs(old_Slope)
        Acc = LOS_rate * 3
    missile1.steer(Acc)

    dmp = missile1.vel_vector
    dmpX = (dmp.x, 0)
    dmpY = (0, dmp.y)

    MVP2 = pygame.Vector2(missile1.vel_vector)
    MVP2.rotate_ip(90)
    MVP2.scale_to_length(Acc)

    # check explosion
    # print(-VectorSlope(dmp) + new_Slope, new_Slope+VectorSlope(dmp))
    if New_LOS.magnitude() < 2:
        exploding = True
        for i in range(10):
            explode(missile1.center)
        missile1.center = pygame.Vector2(random.randint(100, 900), random.randint(100, 900))
        missile1.vel_vector = missile1.vel_vector.rotate(math.degrees(VectorSlope(target1.vel_vector)))
        # i dont know why this won't work

    # chaffs loop:
    for f in chaffs:
        f.update()
        if f.life <= 0:
            chaffs.remove(f)
        pygame.draw.circle(win, f.color, f.center, f.size)

    # bullet loop
    for b in bullets:
        b.update()
        if (b.center - missile1.center).magnitude() < 4:
            exploding = True
            for i in range(10):
                explode(missile1.center)
            missile1.center = pygame.Vector2(random.randint(100, 900), random.randint(100, 900))
        if b.lifetime <= 0:
            bullets.remove(b)
        pygame.draw.circle(win, (255, 100, 90), b.center, 2, 4)

    # fire loop
    fire.append(FireParticle(missile1.center))
    for f in fire:
        f.update()
        if f.color[0] == 0:
            fire.remove(f)
        else:
            pygame.draw.circle(win, f.color, f.center, f.age / 8)
    # smoke loop
    smokeMissile.append(ClassSmoke(target1.center))
    for i in smokeMissile:
        i.update()
        if i.life > 100:
            smokeMissile.remove(i)
        else:
            pygame.draw.circle(win, i.color, (i.center[0], i.center[1]), i.life * .09)
    # explosion loop
    if exploding:
        for i in explodeparts:
            i.update()
            if i.life > 100 + random.randint(-50, 50):
                explodeparts.remove(i)
            else:
                pygame.draw.rect(win, random.choice([grey, red, yellow]),
                                 (i.center[0], i.center[1], (i.life + 10) * .04, (i.life + 10) * .04))

    # draw shapes

    mistshape = rotate_triangle(missile1.center, 4, missile1.center + missile1.vel_vector)
    pygame.draw.aaline(win, (10, 90, 20), missile1.center, NewTargetPos, 2)

    pygame.draw.aaline(win, (255, 255, 255), NewTargetPos, target1.center + target1.vel_vector * 20, 2)
    # pygame.draw.line(win, (0,155,0),tpos,new+dpx)
    # pygame.draw.line(win, (0,155,0),tpos,new+dpy)
    pygame.draw.aaline(win, (255, 1, 1), target1.center, NewTargetPos + missile1.perpendicular, 3)
    pygame.draw.circle(win, (0, 0, 255), target1.center + target1.vel_vector, 5)

    pygame.draw.aaline(win, (10, 90, 20), missile1.center, missile1.center + dmp * 40, 1)
    # pygame.draw.line(win, (0,155,0),mpos,mpos+dmpX)
    # pygame.draw.line(win, (0,155,0),mpos,mpos+dmpY)
    pygame.draw.aaline(win, (255, 0, 100), missile1.center, missile1.center + MVP2 * 4000, 3)
    pygame.draw.aaline(win, (0, 200, 255), missile1.center, missile1.center + missile1.vel_vector * 2)
    pygame.draw.polygon(win, (20, 255, 100), mistshape)

    pygame.display.update()
    win.fill((0, 0, 0))
