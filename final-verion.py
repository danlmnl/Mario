import pygame
import sys
import random

pygame.init()
size = [1500, 800]
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
world_extra = 400
world_width = size[0] + world_extra

BROWN = (150, 75, 0)
GREEN = (135, 147, 1)
BLUE = (66, 170, 255)
YELLOW = (255, 255, 0)
ANOTHERORANGE = (254, 154, 35)
WHITE = (255, 255, 255)

mario_right = pygame.image.load('mario__right.png')
mario_left = pygame.image.load('mario__left.png')
live_image = pygame.image.load('live.png')
enemy1_right = pygame.image.load("enemy1right.png")
enemy1_left = pygame.image.load("enemy1left.png")
enemy2_right = pygame.image.load("enemy2right.png")
enemy2_left = pygame.image.load("enemy2left.png")

mario_right = pygame.transform.scale(mario_right, (60, 80))
mario_left = pygame.transform.scale(mario_left, (60, 80))
live_image = pygame.transform.scale(live_image, (50, 50))
enemy1_right = pygame.transform.scale(enemy1_right, (60, 80))
enemy1_left = pygame.transform.scale(enemy1_left, (60, 80))
enemy2_right = pygame.transform.scale(enemy2_right, (60, 80))
enemy2_left = pygame.transform.scale(enemy2_left, (60, 80))

platform_h = 70
platform_w = 300
overlap = 100
count_pl_max = 5
platforms_y = [740, 570, 400, 230]
count_rows = len(platforms_y)

camera_x = 0

mario_speed = 10
gravity = 0.6
jumpsp = 17

enemy1_speed = 3
enemy2_speed = 1
enemy2_jumpsp = 16
enemy2_cooldownjump = 2000

pause = 1000
win_pause = 2000
count_win_games = 0

coin_r = 20
coin_hit = 36
coin_up = 30
coin_ch = 0.8
coin_min = 6
coin_min_row = 1

font = pygame.font.Font(None, 36)
resfont1 = pygame.font.Font(None, 150)
resfont2 = pygame.font.Font(None, 125)

ground = rows = money = takedmoney = None
goal1 = goal2 = None
mario = None
mario_pos = mario_v = None
enemy1 = enemy2 = None
enemy1_pos = enemy2_pos = enemy2_v = None
lives = 0
hitted = 0
gameres = None
win_timer = 0

def restart():
    global ground, rows, money, takedmoney, goal1, goal2
    global mario, mario_pos, mario_v, ontheground, mariod, enemy1, enemy2
    global enemy1_pos, enemy1d, enemy2_pos, enemy2_v, enemy2_ontheground, enemy2_lastjump, enemy2d
    global lives, hitted, gameres, win_timer, tmp1, tmp2, camera_x

    ground, rows = generate_level()
    goal1, goal2, pl = generate_goal(rows)
    money = generate_money(rows, pl)
    takedmoney = []
    camera_x = 0

    mario = pygame.Rect(0, 0, 50, 70)
    mario_pos = pygame.Vector2(50, 670)
    mario_v = pygame.Vector2(0, 0)
    ontheground = True
    mariod = 1


    enemy1 = pygame.Rect(0, 0, 50, 70)
    enemy1_pos, enemy2_pos = generate_enemy_positions(rows)
    tmp1 = enemy1_pos.copy()
    tmp2 = enemy2_pos.copy()
    enemy1d = 1

    enemy2 = pygame.Rect(0, 0, 40, 60)
    enemy2_v = pygame.Vector2(0, 0)
    enemy2_ontheground = False
    enemy2_lastjump = 0
    enemy2d = 1

    lives = 3
    hitted = 0
    gameres = None
    win_timer = 0

def generate_level():
    rows = [[pygame.Rect(0, platforms_y[0], world_width, platform_h)]]
    for r in range(1, count_rows):
        previous_row = rows[r - 1]
        count = random.randint(2, count_pl_max)
        placed = []
        attempts = 0

        while len(placed) < count and attempts < 1000:
            attempts+=1
            i = random.randint(0, len(previous_row) - 1)
            pr_pl = previous_row[i]
            spread = 50
            min_x = max(0, pr_pl.x - platform_w + overlap - spread)
            max_x = min(world_width-platform_w, pr_pl.x + pr_pl.width - overlap + spread)
            if min_x > max_x:
                continue
            x = random.randint(min_x, max_x)
            new_rect = pygame.Rect(x, platforms_y[r], platform_w, platform_h)

            gap = 60
            s = sum(1 for platform in placed if new_rect.colliderect(platform) or abs(new_rect.left - platform.right) < gap or abs(platform.left - new_rect.right) < gap)
            if s>0:
                continue
            placed.append(new_rect)

        if len(placed) == 0:
            placed.append(pygame.Rect((world_width-platform_w) // 2, platforms_y[r], platform_w, platform_h))
        rows.append(placed)

    flat = [p for row in rows for p in row]
    return flat, rows

def coin_rect(center):
    return pygame.Rect(center[0] - coin_hit//2, center[1] - coin_hit//2, coin_hit, coin_hit)

def coin_y_for(plat):
    return plat.y - 70 - coin_up - coin_hit//2

def try_add(plat, coins):
    center = (plat.x + plat.width // 2, coin_y_for(plat))
    r = coin_rect(center)
    if any(r.colliderect(p) for p in ground):
        return False
    if any(r.colliderect(coin_rect(c[0])) for c in coins):
        return False
    coins.append((center, True))
    return True

def generate_money(rows, finish):
    coins = []

    for r in range(0, count_rows):
        row_coins = 0
        for plat in rows[r]:
            if plat == finish or row_coins >= coin_min_row:
                continue
            if try_add(plat, coins):
                row_coins+=1

    for r in range(count_rows):
        for plat in rows[r]:
            if plat == finish:
                continue
            if random.random() < coin_ch:
                try_add(plat, coins)

    attempts = 0
    while len(coins) < coin_min and attempts < 2000:
        attempts+=1
        r = random.randint(1, count_rows - 2)
        plat = random.choice(rows[r])
        if plat == finish:
            continue
        try_add(plat, coins)
    return coins

def generate_goal(rows):
    toprow = rows[count_rows - 1]
    top_pl = toprow[random.randint(0, len(toprow) - 1)]

    goal_x = top_pl.centerx - 50
    goal_y = platforms_y[count_rows - 1] - 200
    goal1 = pygame.Rect(goal_x, goal_y, 100, 200)
    goal2 = pygame.Rect(goal_x+20, goal_y+25, 60, 150)
    return goal1, goal2, top_pl

def generate_enemy_positions(rows):
    e1x = random.randint(300, world_width - 200)
    e1_pos = pygame.Vector2(e1x, platforms_y[0] - 70)
    r = random.randint(0, count_rows-1)
    row = rows[r]
    plat = row[random.randint(0, len(row) - 1)]
    e2_pos = pygame.Vector2(plat.centerx - 20, plat.y - 60)
    return e1_pos, e2_pos

def draw_money():
    for circle in money:
        if circle[1]:
            pygame.draw.circle(screen, ANOTHERORANGE, (circle[0][0] - camera_x, circle[0][1]), coin_r)
            pygame.draw.circle(screen, YELLOW, (circle[0][0] - camera_x, circle[0][1]), coin_r-4)

def draw_grow_with_grass():
    for block in ground:
        pygame.draw.rect(screen, BROWN, (block.x - camera_x, block.y, block.width, block.height))

        grass = pygame.Rect(block.x - camera_x, block.y, block.width, 30)
        pygame.draw.rect(screen, GREEN, grass)

def draw_goals(goal1, goal2):
    pygame.draw.rect(screen, BROWN, (goal1.x - camera_x, goal1.y, goal1.width, goal1.height))
    pygame.draw.rect(screen, YELLOW, (goal2.x - camera_x, goal2.y, goal2.width, goal2.height))

def func_of_gravity(pos, v, rect, ground):
    oldgr = pos.y + rect.height
    v.y += gravity
    pos.y += v.y
    rect.x = round(pos.x)
    rect.y = round(pos.y)
    onthegroundl = False

    for block in ground:
        if (v.y > 0 and oldgr <= block.y and rect.y + rect.height >= block.y and rect.x + rect.width > block.x and rect.x < block.x + block.width):
            pos.y = block.y - rect.height
            v.y = 0
            onthegroundl = True

    rect.x = round(pos.x)
    rect.y = round(pos.y)
    return onthegroundl

restart()
while True:
    clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if gameres is None:

        data = pygame.key.get_pressed()

        if data[pygame.K_r]:
            mario_pos = pygame.Vector2(50, 670)
            mario_v = pygame.Vector2(0, 0)
            ontheground = True
            mariod = 1
            for circle in takedmoney:
                for i in range(len(money)):
                    if (circle[0], False) == money[i]:
                        money[i] = (circle[0], True)
            takedmoney = []
            lives = 3

            enemy1_pos = tmp1.copy()
            enemy2_pos = tmp2.copy()

            enemy1.x = round(enemy1_pos.x)
            enemy1.y = round(enemy1_pos.y)

            enemy2.x = round(enemy2_pos.x)
            enemy2.y = round(enemy2_pos.y)

            enemy2_v = pygame.Vector2(0, 0)
            enemy2_ontheground = False
            enemy2_lastjump = 0

            enemy1d = enemy2d = 1

        if ontheground:
            if data[pygame.K_LEFT]:
                mario_pos.x -= mario_speed
                mariod = -1

            if data[pygame.K_RIGHT]:
                mario_pos.x += mario_speed
                mariod = 1

            if data[pygame.K_UP]:
                mario_v.y = -jumpsp
                ontheground = False

        ontheground = func_of_gravity(mario_pos, mario_v, mario, ground)

        if mario_pos.x < 0:
            mario_pos.x = 0

        if mario_pos.x > world_width - mario.width:
            mario_pos.x = world_width - mario.width

        camera_right = camera_x + 600
        camera_left = camera_x + 300

        if mario_pos.x > camera_right:
            camera_x += mario_pos.x - camera_right
        elif mario_pos.x < camera_left:
            camera_x -= camera_left - mario_pos.x

        camera_x = max(0, min(camera_x, world_width - size[0]))

        for i, circle in enumerate(money):
            if circle[1] and mario.colliderect(coin_rect(circle[0])):
                money[i] = (circle[0], False)
                takedmoney.append([circle[0]])

        enemy1_pos.x += enemy1_speed * enemy1d

        if enemy1_pos.x + enemy1.width >= world_width:
            enemy1_pos.x = world_width- enemy1.width
            enemy1d = -1

        if enemy1_pos.x <= 0:
            enemy1_pos.x =0
            enemy1d = 1

        enemy1.x = round(enemy1_pos.x)
        enemy1.y = round(enemy1_pos.y)

        if mario.centerx > enemy2.centerx:
            enemy2d = 1
        elif mario.centerx < enemy2.centerx:
            enemy2d = -1

        enemy2_pos.x += enemy2_speed*enemy2d

        if (mario.centery < enemy2.centery - 30 and enemy2_ontheground and now - enemy2_lastjump >= enemy2_cooldownjump):
            enemy2_v.y = -enemy2_jumpsp
            enemy2_ontheground = False
            enemy2_lastjump = now

        enemy2_ontheground = func_of_gravity(enemy2_pos, enemy2_v, enemy2, ground)

        if enemy2_pos.x + enemy2.width >= world_width:
            enemy2_pos.x = world_width - enemy2.width
            enemy2d = -1

        if enemy2_pos.x <=0:
            enemy2_pos.x = 0
            enemy2d = 1


        if now - hitted >= pause and (mario.colliderect(enemy1) or mario.colliderect(enemy2)):
            lives -= 1
            hitted = now

        if lives <= 0:
            gameres = "YOU LOSE"
        elif mario.colliderect(goal1) and len(takedmoney) == len(money):
            gameres = "YOU WON"
            win_timer = now


    screen.fill(BLUE)
    draw_goals(goal1, goal2)
    draw_grow_with_grass()
    draw_money()

    if mariod == 1:
        screen.blit(mario_right, (mario.x - camera_x, mario.y))
    else:
        screen.blit(mario_left, (mario.x - camera_x, mario.y))

    if enemy1d == 1:
        screen.blit(enemy1_right, (enemy1.x - camera_x, enemy1.y))
    else:
        screen.blit(enemy1_left, (enemy1.x - camera_x, enemy1.y))

    if enemy2d == 1:
        screen.blit(enemy2_right, (enemy2.x - camera_x, enemy2.y))
    else:
        screen.blit(enemy2_left, (enemy2.x - camera_x, enemy2.y))

    pygame.draw.circle(screen, ANOTHERORANGE, (1090, 40), 20)
    pygame.draw.circle(screen, YELLOW, (1090, 40), 15)
    screen.blit(font.render(f"{len(takedmoney)} / {len(money)}", True, YELLOW), (1120, 30))

    for i in range(lives):
        screen.blit(live_image, (900 + i * 50, 20))

    if gameres == "YOU WON" and count_win_games == 2:

        text1 = resfont1.render("YOU WON", True, WHITE)
        text2 = resfont2.render("IN EVERY LEVEL", True, WHITE)
        screen.blit(text1, ((size[0] - text1.get_width()) // 2, 250))
        screen.blit(text2, ((size[0] - text2.get_width()) // 2, 430))

    elif gameres == "YOU WON":
        text1 = resfont1.render("YOU", True, WHITE)
        text2 = resfont1.render("WON", True, WHITE)
        screen.blit(text1, ((size[0] - text1.get_width()) // 2, 200))
        screen.blit(text2, ((size[0] - text2.get_width()) // 2, 380))

        if now - win_timer >= win_pause:
            count_win_games+=1
            restart()

    if gameres == "YOU LOSE":
        text1 = resfont1.render("YOU", True, WHITE)
        text2 = resfont1.render("LOSE", True, WHITE)
        screen.blit(text1, ((size[0] - text1.get_width()) // 2, 200))
        screen.blit(text2, ((size[0] - text2.get_width()) // 2, 380))

    pygame.display.flip()
