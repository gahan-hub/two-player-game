import os
import sys
import wx
import pygame
import json
# Assuming SpriteSheet is available in a local module named 'SpriteSheet'
from SpriteSheet import Sprite__Sheet

# -------------------------------------------------------
# 1. CONFIGURATION / GLOBALS
# -------------------------------------------------------
# --- Game Constants ---
GAME_TITLE = "DOUX AND FRIENDS ADVENTURES"
SCREEN_WIDTH = 1296
SCREEN_HEIGHT = 720
FPS = 60
WIN_SCORE = 100
COLLISION_PAUSE_DURATION_MS = 3000
GAME_END_TIME_MS = 100 * 1000 # 100 seconds
GROUND_Y_LEVEL = SCREEN_HEIGHT - 96 # Base ground level

# --- Asset Paths ---
P1_DEFAULT_FN = os.path.join(r'Assets/DinoSprites - doux.png') #ppp
P2_DEFAULT_FN = os.path.join(r'Assets/DinoSprites - mort.png') #ppp

# --- UI Colors (Enhanced) ---
COLOR_GREEN = '#00CC66' # Slightly darker, more pleasing green
COLOR_DARK_GRAY = "#1E1E1E" # Almost black, modern background
COLOR_MEDIUM_GRAY = "#3A3A3A" # New color for menu backgrounds/buttons
COLOR_P1_TEXT = "#33CCFF" # Cyan/light blue
COLOR_P2_TEXT = "#FF6666" # Soft red
COLOR_TEXT_WHITE = "white"
COLOR_TEXT_BLACK = "black"

# --- Pygame Globals (will be initialized later) ---
Screen = None
GAME_END = pygame.USEREVENT + 1
EVT_PLAY_AGAIN = pygame.USEREVENT + 2
CUSTOM_FONT = None # For a more stylized look

# --- Game State ---
Game_Active = True
play = False
rect_colours = [COLOR_GREEN, COLOR_GREEN, COLOR_DARK_GRAY, COLOR_DARK_GRAY]
P1FN = P1_DEFAULT_FN
P2FN = P2_DEFAULT_FN
R1_Score = 0
R2_Score = 0
EPA = 0 # Elapsed time for Play Again countdown

# -------------------------------------------------------
# 2. WX APP / PANELS / UI SETUP
# -------------------------------------------------------
app = wx.App(False)
frame = wx.Frame(None, title=GAME_TITLE, size=(1920, 1080))
frame.ShowFullScreen(True)
icon = wx.Icon(wx.Bitmap("Assets/Icon.png"))
frame.SetIcon(icon)
# Main game panel (pygame will draw into this)
panel = wx.Panel(frame, size=(SCREEN_WIDTH, SCREEN_HEIGHT), style=wx.NO_FULL_REPAINT_ON_RESIZE)
panel.SetBackgroundColour(COLOR_DARK_GRAY)

# Right UI panel
panel2 = wx.Panel(frame, size=(1920 - SCREEN_WIDTH, 1080), pos=(SCREEN_WIDTH, 0))
panel2.SetBackgroundColour(COLOR_MEDIUM_GRAY)
panel2.SetDoubleBuffered(True)

# Bottom UI panel
panel3 = wx.Panel(frame, size=(SCREEN_WIDTH, 1080 - SCREEN_HEIGHT), pos=(0, SCREEN_HEIGHT))
panel3.SetBackgroundColour(COLOR_MEDIUM_GRAY)
panel3.SetDoubleBuffered(True)

# Exit button
exitbtn = wx.Button(panel3, label='Exit Game', pos=(600, 20), size=(100, 30))
exitbtn.SetBackgroundColour(COLOR_P2_TEXT)
exitbtn.SetForegroundColour(COLOR_TEXT_WHITE)
exitbtn.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

def ExitGame(event):
    try: pygame.quit()
    except Exception: pass
    frame.Destroy()
    try: wx.GetApp().ExitMainLoop()
    except Exception: pass

exitbtn.Bind(wx.EVT_BUTTON, ExitGame)

# Title + labels
title = wx.StaticText(panel2, label="CHARACTER \n SELECTION", pos=(30, 10), size=(180, 50), style=wx.ALIGN_CENTER)
title.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
title.SetForegroundColour(COLOR_TEXT_WHITE)

p1_label = wx.StaticText(panel2, label="PLAYER 1", pos=(35, 70))
p1_label.SetForegroundColour(COLOR_P1_TEXT)
p1_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

p2_label = wx.StaticText(panel2, label="PLAYER 2", pos=(145, 70))
p2_label.SetForegroundColour(COLOR_P2_TEXT)
p2_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

def get_bitmap(name):
    bmp = wx.Bitmap(name)
    try:
        # Use top-left pixel for mask (for transparent background)
        bmp.SetMask(wx.Mask(bmp, bmp.GetPixel(0, 0))) 
    except Exception:
        pass
    return bmp

# Character bitmap buttons
B1 = wx.BitmapButton(panel2, bitmap=get_bitmap(os.path.join(r'Assets\Doux.bmp')), pos=(30, 95), size=(50, 50)) #ppp
B2 = wx.BitmapButton(panel2, bitmap=get_bitmap(os.path.join(r'Assets\Mort.bmp')), pos=(140, 95), size=(50, 50))#ppp
B3 = wx.BitmapButton(panel2, bitmap=get_bitmap(os.path.join(r'Assets\Tard.bmp')), pos=(30, 165), size=(50, 50))#ppp
B4 = wx.BitmapButton(panel2, bitmap=get_bitmap(os.path.join(r'Assets\Vita.bmp')), pos=(140, 165), size=(50, 50))#ppp

# Draw coloured selection rectangles in paint event (Updated positions)
def on_paint(event):
    global rect_colours
    dc = wx.PaintDC(panel2)
    dc.SetPen(wx.Pen(wx.Colour(COLOR_DARK_GRAY), 2))
    
    positions = [(25, 90), (135, 90), (25, 160), (135, 160)]
    for i in range(4):
        dc.SetBrush(wx.Brush(wx.Colour(rect_colours[i])))
        dc.DrawRectangle(positions[i][0], positions[i][1], 60, 60)

panel2.Bind(wx.EVT_PAINT, on_paint)

# Runner checkboxes
RS1 = wx.CheckBox(panel2, label='Runner', pos=(35, 240))
RS1.SetForegroundColour(COLOR_TEXT_WHITE)
RS2 = wx.CheckBox(panel2, label='Runner', pos=(145, 240))
RS2.SetForegroundColour(COLOR_TEXT_WHITE)

# Play / Restart buttons
btn = wx.Button(panel2, label='START GAME', pos=(30, 290), size=(170, 50))
btn.SetBackgroundColour(COLOR_GREEN)
btn.SetForegroundColour(COLOR_TEXT_BLACK)
btn.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

btnrs = wx.Button(panel2, label='RESTART GAME', pos=(30, 350), size=(170, 50))
btnrs.SetBackgroundColour(COLOR_P2_TEXT)
btnrs.SetForegroundColour(COLOR_TEXT_WHITE)
btnrs.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

frame.Show()

# -------------------------------------------------------
# 3. WX UI BINDINGS AND GAME STATE MANAGEMENT
# -------------------------------------------------------
def Play(event=None):
    """Start the game if a runner is selected. Does NOT reset score."""
    global play, Game_Active, R1_Score, R2_Score
    music_control(r'Assets\Confused and Angry Robots.mp3',0.3)
    if not RS1.GetValue() and not RS2.GetValue():
        wx.MessageBox('Select a Runner')
        return

    Game_Active = True
    play = True
    
    # Set the game-end timer only on start
    pygame.time.set_timer(GAME_END, GAME_END_TIME_MS)
    pygame.time.set_timer(EVT_PLAY_AGAIN, 0) # Clear collision timer
    
    # Re-initialize players to reset position/sprite if needed
    try:
        player_1.empty()
        player_1.add(Player_1(P1FN))
        player_2.empty()
        player_2.add(Player_2(P2FN))
    except Exception:
        pass 

def Set_Player(sprite_group, filename, rect_indices, highlight_index):
    """Generic function to set player sprite file and selection highlight."""
    global P1FN, P2FN, rect_colours, play
    
    # Determine if it's player 1 or 2
    if sprite_group is player_1:
        P1FN = filename
        rect_colours[rect_indices[0]] = COLOR_GREEN if highlight_index == 1 or highlight_index == 3 else COLOR_DARK_GRAY
        rect_colours[rect_indices[1]] = COLOR_GREEN if highlight_index == 1 or highlight_index == 3 else COLOR_DARK_GRAY
        Player_Class = Player_1
    else:
        P2FN = filename
        rect_colours[rect_indices[0]] = COLOR_GREEN if highlight_index == 2 or highlight_index == 4 else COLOR_DARK_GRAY
        rect_colours[rect_indices[1]] = COLOR_GREEN if highlight_index == 2 or highlight_index == 4 else COLOR_DARK_GRAY
        Player_Class = Player_2
        
    # Re-update the specific selection boxes that were clicked
    # Highlight index 1/3 means P1 (B1 or B3 was clicked)
    # Highlight index 2/4 means P2 (B2 or B4 was clicked)
    
    # If the current player (P1 or P2) selection changed, make sure the other player's highlights are kept.
    if sprite_group is player_1:
        # Un-highlight the P1 column other than the selected one
        rect_colours[0] = COLOR_GREEN if highlight_index == 1 else COLOR_DARK_GRAY
        rect_colours[2] = COLOR_GREEN if highlight_index == 3 else COLOR_DARK_GRAY
    else:
        # Un-highlight the P2 column other than the selected one
        rect_colours[1] = COLOR_GREEN if highlight_index == 2 else COLOR_DARK_GRAY
        rect_colours[3] = COLOR_GREEN if highlight_index == 4 else COLOR_DARK_GRAY

    # If game not playing, update displayed sprite for preview
    if not play:
        try:
            sprite_group.empty()
            sprite_group.add(Player_Class(filename))
        except Exception:
            pass

    panel2.Refresh()

def On_check(runner_checkbox, other_checkbox):
    """Ensure only one Runner checkbox is selected at a time."""
    if runner_checkbox.GetValue():
        other_checkbox.SetValue(False)

def Restart(event=None):
    """Full game reset (resets position, scores, and selection state)."""
    global play, Game_Active, R1_Score, R2_Score, P1FN, P2FN,flip
    music_control(r'Assets\Space Knights.mp3',0.3)
    pygame.time.set_timer(GAME_END, 0)
    pygame.time.set_timer(EVT_PLAY_AGAIN, 0)
    flip=0
    Game_Active = True
    play = False
    R1_Score, R2_Score = 0, 0 # RESET SCORE HERE
    RS1.SetValue(False)
    RS2.SetValue(False)
    
    # Reset players to update their state based on current P1FN/P2FN
    # Reset P1FN/P2FN to defaults (Doux and Mort)
    P1FN = P1_DEFAULT_FN
    P2FN = P2_DEFAULT_FN
    
    # Reset highlights to defaults (Doux and Mort)
    global rect_colours
    rect_colours = [COLOR_GREEN, COLOR_GREEN, COLOR_DARK_GRAY, COLOR_DARK_GRAY]
    panel2.Refresh()

    try:
        player_1.empty()
        player_1.add(Player_1(P1FN))
        player_2.empty()
        player_2.add(Player_2(P2FN))
    except Exception:
        pass

# Bind UI actions
# The rect indices for P1 are [0, 2]. 0 is B1 (Doux), 2 is B3 (Tard).
B1.Bind(wx.EVT_BUTTON, lambda evt: Set_Player(player_1, P1_DEFAULT_FN, [0, 2], 1)) 
B3.Bind(wx.EVT_BUTTON, lambda evt: Set_Player(player_1, os.path.join( r'Assets\DinoSprites - vita.png'), [0, 2], 3)) # Note: Tard.bmp filename refers to vita.png sprite sheet, keeping original intent.

# The rect indices for P2 are [1, 3]. 1 is B2 (Mort), 3 is B4 (Vita).
B2.Bind(wx.EVT_BUTTON, lambda evt: Set_Player(player_2, P2_DEFAULT_FN, [1, 3], 2)) 
B4.Bind(wx.EVT_BUTTON, lambda evt: Set_Player(player_2, os.path.join( r'Assets\DinoSprites - tard.png'), [1, 3], 4)) # Note: Vita.bmp filename refers to tard.png sprite sheet, keeping original intent.


btn.Bind(wx.EVT_BUTTON, Play)
btnrs.Bind(wx.EVT_BUTTON, Restart)
RS1.Bind(wx.EVT_CHECKBOX, lambda evt: On_check(RS1, RS2))
RS2.Bind(wx.EVT_CHECKBOX, lambda evt: On_check(RS2, RS1))

def on_close(event):
    try: pygame.quit()
    except Exception: pass
    try: wx.GetApp().ExitMainLoop()
    except Exception: pass
    frame.Destroy()

frame.Bind(wx.EVT_CLOSE, on_close)

# WX timer to refresh UI
wx_timer = wx.Timer(frame)
# The timer forces wx to repaint and update the panels, showing selection changes
wx_timer.Bind(wx.EVT_TIMER, lambda evt: (frame.Refresh(), frame.Update(), panel2.Refresh(), panel2.Update()))
wx_timer.Start(5)

# -------------------------------------------------------
# 4. PYGAME CLASSES
# -------------------------------------------------------
class GameTextRenderer:
    """Handles all dynamic text rendering in Pygame window."""
    def __init__(self):
        # Use a system font or default if custom is not found
        try:
            self.font_small = pygame.font.SysFont('Consolas', 30, bold=True)
            self.font_medium = pygame.font.SysFont('Consolas', 48, bold=True)
            self.font_large = pygame.font.SysFont('Consolas', 72, bold=True)
        except Exception:
            self.font_small = pygame.font.Font(None, 30)
            self.font_medium = pygame.font.Font(None, 48)
            self.font_large = pygame.font.Font(None, 72)
            
    def draw_score(self, screen, r1_score, r2_score, is_p1_runner, is_p2_runner):
        # Runner status
        runner_text = ""
        runner_color = COLOR_TEXT_WHITE
        if is_p1_runner:
            runner_text = "Runner: P1"
            runner_color = COLOR_P1_TEXT
        elif is_p2_runner:
            runner_text = "Runner: P2"
            runner_color = COLOR_P2_TEXT
        
        if runner_text:
            runner_surf = self.font_medium.render(runner_text, False, runner_color)
            screen.blit(runner_surf, runner_surf.get_rect(center=(SCREEN_WIDTH // 2, 30)))

        # Individual scores
        r1_score_color = COLOR_P1_TEXT
        r2_score_color = COLOR_P2_TEXT

        # Draw scores at bottom corners, slightly adjusted for better visibility
        r1_surf = self.font_small.render(f'P1: {int(r1_score)}', False, r1_score_color)
        r2_surf = self.font_small.render(f'P2: {int(r2_score)}', False, r2_score_color)
        
        screen.blit(r1_surf, (20, SCREEN_HEIGHT - 60))
        screen.blit(r2_surf, (SCREEN_WIDTH - r2_surf.get_width() - 20, SCREEN_HEIGHT - 60))


    def draw_game_over(self, screen, r1_score, r2_score):
        # Use a background image for this screen for better visuals
        screen.blit(s, (0, 0)) # Redraw the background/floor

        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Win condition check
        if int(r1_score) >= WIN_SCORE or int(r2_score) >= WIN_SCORE:
            # Final Score Screen
            if int(r1_score) >= WIN_SCORE:
                winner_text = 'PLAYER 1 WINS!'
                color = COLOR_P1_TEXT
            else:
                winner_text = 'PLAYER 2 WINS!'
                color = COLOR_P2_TEXT

            winner_font = self.font_large.render(winner_text, False, color)
            score_font = self.font_medium.render(f'Final Score: P1={int(r1_score)} | P2={int(r2_score)}', False, COLOR_TEXT_WHITE)
            restart_font = self.font_small.render('Press RESTART GAME on the side panel.', False, COLOR_TEXT_WHITE)
            
            # Draw a darker box behind text for contrast
            rect_height = winner_font.get_height() + score_font.get_height() + restart_font.get_height() + 60
            rect_surf = pygame.Surface((SCREEN_WIDTH - 200, rect_height), pygame.SRCALPHA)
            rect_surf.fill((30, 30, 30, 200)) # Dark transparent background
            screen.blit(rect_surf, rect_surf.get_rect(center=(center_x, center_y)))

            screen.blit(winner_font, winner_font.get_rect(center=(center_x, center_y - 40)))
            screen.blit(score_font, score_font.get_rect(center=(center_x, center_y + 20)))
            screen.blit(restart_font, restart_font.get_rect(center=(center_x, center_y + 70)))
            
        else:
            # Collision screen (Play Again countdown)
            time_left = COLLISION_PAUSE_DURATION_MS / 1000 - (pygame.time.get_ticks() / 1000 - EPA)
            
            # Draw a darker box behind text for contrast
            rect_surf = pygame.Surface((SCREEN_WIDTH - 200, 200), pygame.SRCALPHA)
            rect_surf.fill((30, 30, 30, 200)) # Dark transparent background
            screen.blit(rect_surf, rect_surf.get_rect(center=(center_x, center_y)))

            if time_left > 0:
                text_surf = self.font_medium.render('COLLISION! Changing Roles...', False, COLOR_TEXT_WHITE)
                # Ensure countdown shows 3, 2, 1, then disappears
                time_surf = self.font_large.render(f'{int(time_left) + 1}', False, COLOR_GREEN) 
                screen.blit(text_surf, text_surf.get_rect(center=(center_x, center_y - 30)))
                screen.blit(time_surf, time_surf.get_rect(center=(center_x, center_y + 40)))
            else:
                text_surf = self.font_large.render('ROUND STARTING!', False, COLOR_GREEN)
                screen.blit(text_surf, text_surf.get_rect(center=(center_x, center_y)))

    def draw_start_screen(self, screen):
        # Use a background image for this screen for better visuals
        #screen.blit(s, (0, 0)) # Redraw the background/floor
        screen.fill(COLOR_MEDIUM_GRAY)
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Draw a darker box behind text for contrast
        rect_surf = pygame.Surface((SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), pygame.SRCALPHA)
        rect_surf.fill(COLOR_MEDIUM_GRAY) # Dark transparent background
        screen.blit(rect_surf, rect_surf.get_rect(center=(center_x, center_y)))

        # Title
        title_surf = self.font_large.render(GAME_TITLE, False, COLOR_GREEN)
        screen.blit(title_surf, title_surf.get_rect(center=(center_x, 50)))
        
        # Rules and Instructions
        
        # Controls for Player 1
        p1_controls = [
            'P1 Controls (Blue):',
            'Movement: WASD',
            'Dash (Runner only): Q',
            'Double Jump (Catcher only): E'
        ]
        
        # Controls for Player 2
        p2_controls = [
            'P2 Controls (Red):',
            'Movement: IJKL',
            'Dash (Runner only): U',
            'Double Jump (Catcher only): O'
        ]

        y_pos = 150
        
        # Render Player 1 Controls
        for i, line in enumerate(p1_controls):
            color = COLOR_P1_TEXT if i == 0 else COLOR_TEXT_WHITE
            line_surf = self.font_small.render(line, False, color)
            screen.blit(line_surf, (50, y_pos))
            y_pos += 40

        y_pos += 20 # Spacing between player controls
        
        # Render Player 2 Controls
        for i, line in enumerate(p2_controls):
            color = COLOR_P2_TEXT if i == 0 else COLOR_TEXT_WHITE
            line_surf = self.font_small.render(line, False, color)
            screen.blit(line_surf, (50, y_pos))
            y_pos += 40
            
        # Call to action
        start_surf = self.font_medium.render('SELECT YOUR CHARACTERS AND PRESS START', False, COLOR_TEXT_WHITE)
        rule_surf = self.font_medium.render(f'First to a Score of {WIN_SCORE} wins!', False, COLOR_GREEN)

        screen.blit(start_surf, start_surf.get_rect(center=(center_x, SCREEN_HEIGHT - 150)))
        screen.blit(rule_surf, (center_x - rule_surf.get_width() // 2, SCREEN_HEIGHT - 80))


class Background:
    def __init__(self):
        # NOTE: Assumes 'tilemap-backgrounds.png' exists
        self.back=pygame.image.load(r'Assets\Nature-5.png').convert_alpha()
        sheet = Sprite__Sheet(os.path.join(r'Assets\tilemap-backgrounds.png'))#ppp
        self.Back_tile_list = []
        for i in range(0, 8):
            for j in range(0, 3):
                # get_sprite parameters: x, y, width, height, scale
                self.Back_tile_list.append(sheet.get_sprite(i * 25, j * 25, 24, 24, 2))


class Player_1(pygame.sprite.Sprite):
    def __init__(self, filename):
        super().__init__()
        # NOTE: Assumes Sprite__Sheet is correctly implemented
        SS = Sprite__Sheet(filename)
        self.Doux_Frames = []
        for i in range(0, 24):
            self.Doux_Frames.append(SS.get_sprite(i * 24, 0, 24, 24, 2))
        
        self.image = self.Doux_Frames[0]
        self.rect = self.image.get_rect(midbottom=(0, GROUND_Y_LEVEL))
        self.rect.size = (19 * 2, 20 * 2 + 1) # Hitbox adjustment
        
        self.X_vel = 4
        self.Y_vel = 0
        self.jump = 20
        self.Animation_index = 0
        self.a = 0 # 0 for not flipped (right), 1 for flipped (left)
        self.prev_rect = self.rect.copy()

        # Ability State
        self.is_runner = False
        self.dash_timer = 0 	 # How long the dash lasts
        self.dash_cooldown = 0 	# Time until next dash
        self.double_jump_avail = False # Logic flag
        self.double_jump_timer = 0 # Cooldown for double jump
        self.e_key_pressed = False 	 # Input flag

    def collide_with_terrain(self, terrain_rects):
        keys = pygame.key.get_pressed()
        for block in terrain_rects:
            if self.rect.colliderect(block):
                # Vertical collision (handle first for accurate gravity reset)
                if self.rect.bottom > block.top and self.prev_rect.bottom <= block.top:
                    self.rect.bottom = block.top
                    self.double_jump_avail = True 
                    # Check for jump input immediately after landing
                    if keys[pygame.K_w]:
                        self.Y_vel = -self.jump
                        jump_S.play()
                    else: self.Y_vel=0 
                elif self.rect.top < block.bottom and self.prev_rect.top >= block.bottom:
                    self.rect.top = block.bottom
                    self.Y_vel = 0
                
                # Horizontal collision
                elif self.rect.right > block.left and self.prev_rect.right <= block.left:
                    self.rect.right = block.left
                elif self.rect.left < block.right and self.prev_rect.left >= block.right:
                    self.rect.left = block.right

    def user_input(self):
        keys = pygame.key.get_pressed()
        
        # --- MOVEMENT ---
        # If Dashing, force movement in facing direction
        if self.dash_timer > 0:
            self.dash_timer -= 1
            direction = -1 if self.a == 1 else 1
            self.rect.x += 15 * direction # High speed dash
            self.Y_vel = 0 # Defy gravity slightly during dash
        else:
            # Normal Movement
            if keys[pygame.K_a] and not keys[pygame.K_d]:
                self.rect.x -= self.X_vel
            if keys[pygame.K_d] and not keys[pygame.K_a]:
                self.rect.x += self.X_vel

            # Normal Jump (W) - only on ground
            if keys[pygame.K_w] and self.rect.bottom >= GROUND_Y_LEVEL:
                self.Y_vel = -self.jump
                jump_S.play()

        # --- DASH ABILITY (Key: Q) ---
        if self.dash_cooldown > 0: 
            self.dash_cooldown -= 1
            
        if keys[pygame.K_q] and self.is_runner and self.dash_cooldown == 0:
            dash_S.play()
            Trail.Dash()
            self.dash_timer = 10 	# Dash lasts 10 frames
            self.dash_cooldown = 120 # 2 Seconds cooldown

        # --- DOUBLE JUMP ABILITY (Key: E) ---
        if self.double_jump_timer > 0:
            self.double_jump_timer -= 1

        # Only for Catcher, requires being mid-air, ability available, and cooldown finished
        if not self.is_runner:
            if keys[pygame.K_e]:
                if not self.e_key_pressed and self.double_jump_avail and self.double_jump_timer == 0:
                    self.Y_vel = -self.jump
                    jump_S.play()
                    self.double_jump_avail = False # Consume jump
                    self.double_jump_timer = 120 	 # 2 Second Cooldown (same as dash)
                self.e_key_pressed = True
            else:
                self.e_key_pressed = False

    def Gravity(self):
        # Apply gravity only if not currently dashing
        if self.dash_timer == 0:
            self.Y_vel += 1
        
        self.rect.y += self.Y_vel
        if self.rect.bottom >= GROUND_Y_LEVEL:
            self.rect.bottom = GROUND_Y_LEVEL
            self.Y_vel = 0
            self.double_jump_avail = True # Reset double jump on floor

    def set_vx(self):
        self.is_runner = RS1.GetValue()
        if self.is_runner:
            self.X_vel = 4.0 # Runner is slightly slower
            self.jump = 22
        else:
            self.jump = 20
            self.X_vel = 4.5 # Catcher is slightly faster

    def ends(self):
        # Prevents player from leaving the screen horizontally
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)
        self.rect.left = max(self.rect.left, 0)

    def Animation(self, T):
        keys = pygame.key.get_pressed()
        self.Animation_index += 0.3
        if self.Animation_index > 23: self.Animation_index = 0

        # Facing direction
        if keys[pygame.K_d] and not keys[pygame.K_a]:
            self.a = 0
        elif keys[pygame.K_a] and not keys[pygame.K_d]:
            self.a = 1

        # Running animation index range (17-23)
        if (keys[pygame.K_d] or keys[pygame.K_a]) and not (keys[pygame.K_d] and keys[pygame.K_a]):
            if self.Animation_index < 17 or self.Animation_index > 23:
                self.Animation_index = 17
            frame = self.Doux_Frames[int(self.Animation_index)]
            self.image = pygame.transform.flip(frame, self.a, 0)
        else:
            # Idle frame (0)
            self.image = pygame.transform.flip(self.Doux_Frames[0], self.a, 0)

    def update(self, terrain):
        self.prev_rect = self.rect.copy()
        self.set_vx()
        self.user_input()
        self.Gravity()
        self.ends()
        self.collide_with_terrain(terrain)
        self.Animation(terrain)


class Player_2(pygame.sprite.Sprite):
    """
    Controls: I (Up), J (Left), L (Right), K (Down - unused)
    Abilities: U (Dash), O (Double Jump)
    """
    def __init__(self, filename):
        super().__init__()
        SS = Sprite__Sheet(filename)
        self.Doux_Frames = []
        for i in range(0, 24):
            self.Doux_Frames.append(SS.get_sprite(i * 24, 0, 24, 24, 2))
            
        # Initial image is flipped to face Player 1
        self.image = pygame.transform.flip(self.Doux_Frames[0], 1, 0)
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH, GROUND_Y_LEVEL)) # Start on the right
        self.rect.size = (19 * 2, 20 * 2 + 1)
        
        self.X_vel = 4.5
        self.Y_vel = 0
        self.jump = 20
        self.Animation_index = 0
        self.a = 1 # Start flipped (left)
        self.prev_rect = self.rect.copy()

        # Ability State
        self.is_runner = False
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.double_jump_avail = False
        self.double_jump_timer = 0
        self.o_key_pressed = False

    def collide_with_terrain(self, terrain_rects):
        keys = pygame.key.get_pressed()
        for block in terrain_rects:
            if self.rect.colliderect(block):
                # Vertical collision
                if self.rect.bottom > block.top and self.prev_rect.bottom <= block.top:
                    self.rect.bottom = block.top
                    self.double_jump_avail = True 
                    # Check for jump input immediately after landing
                    if keys[pygame.K_i]:
                        self.Y_vel = -self.jump
                        jump_S.play()
                    else:self.Y_vel=0  
                elif self.rect.top < block.bottom and self.prev_rect.top >= block.bottom:
                    self.rect.top = block.bottom
                    self.Y_vel = 0
                
                # Horizontal collision
                elif self.rect.right > block.left and self.prev_rect.right <= block.left:
                    self.rect.right = block.left
                elif self.rect.left < block.right and self.prev_rect.left >= block.right:
                    self.rect.left = block.right

    def user_input(self):
        keys = pygame.key.get_pressed()
        
        # --- MOVEMENT (IJKL) ---
        if self.dash_timer > 0:
            self.dash_timer -= 1
            direction = -1 if self.a == 1 else 1
            self.rect.x += 15 * direction 
            self.Y_vel = 0
        else:
            if keys[pygame.K_j] and not keys[pygame.K_l]: # J is Left
                self.rect.x -= self.X_vel
            if keys[pygame.K_l] and not keys[pygame.K_j]: # L is Right
                self.rect.x += self.X_vel

            # Jump (I)
            if keys[pygame.K_i] and self.rect.bottom >= GROUND_Y_LEVEL:
                self.Y_vel = -self.jump
                jump_S.play()

        # --- DASH ABILITY (Key: U) ---
        if self.dash_cooldown > 0: 
            self.dash_cooldown -= 1
            
        if keys[pygame.K_u] and self.is_runner and self.dash_cooldown == 0:
            dash_S.play()
            Trail2.Dash()
            self.dash_timer = 10 
            self.dash_cooldown = 120 

        # --- DOUBLE JUMP ABILITY (Key: O) ---
        if self.double_jump_timer > 0:
            self.double_jump_timer -= 1

        if not self.is_runner:
            if keys[pygame.K_o]:
                if not self.o_key_pressed and self.double_jump_avail and self.double_jump_timer == 0:
                    self.Y_vel = -self.jump
                    jump_S.play()
                    self.double_jump_avail = False
                    self.double_jump_timer = 120
                self.o_key_pressed = True
            else:
                self.o_key_pressed = False

    def Gravity(self):
        if self.dash_timer == 0:
            self.Y_vel += 1
        
        self.rect.y += self.Y_vel
        if self.rect.bottom >= GROUND_Y_LEVEL:
            self.rect.bottom = GROUND_Y_LEVEL
            self.Y_vel = 0
            self.double_jump_avail = True

    def set_vx(self):
        self.is_runner = RS2.GetValue()
        if self.is_runner:
            self.X_vel = 4.0 # Runner is slightly slower
            self.jump = 22
        else:
            self.jump = 20
            self.X_vel = 4.5 # Catcher is slightly faster

    def ends(self):
        # Prevents player from leaving the screen horizontally
        self.rect.right = min(self.rect.right, SCREEN_WIDTH)
        self.rect.left = max(self.rect.left, 0)

    def Animation(self, T):
        keys = pygame.key.get_pressed()
        self.Animation_index += 0.3
        if self.Animation_index > 23: self.Animation_index = 0

        # Facing direction
        if keys[pygame.K_l] and not keys[pygame.K_j]:
            self.a = 0
        elif keys[pygame.K_j] and not keys[pygame.K_l]:
            self.a = 1

        # Running animation index range (17-23)
        if (keys[pygame.K_l] or keys[pygame.K_j]) and not (keys[pygame.K_l] and keys[pygame.K_j]):
            if self.Animation_index < 17 or self.Animation_index > 23:
                self.Animation_index = 17
            frame = self.Doux_Frames[int(self.Animation_index)]
            self.image = pygame.transform.flip(frame, self.a, 0)
        else:
            # Idle frame (0)
            self.image = pygame.transform.flip(self.Doux_Frames[0], self.a, 0)

    def update(self, terrain):
        self.prev_rect = self.rect.copy()
        self.set_vx()
        self.user_input()
        self.Gravity()
        self.ends()
        self.collide_with_terrain(terrain)
        self.Animation(terrain)


class Tiles:
    def __init__(self):
        # NOTE: Assumes 'tilemap.png' exists
        sheet = Sprite__Sheet(os.path.join(r'Assets\tilemap.png'))#ppp
        self.Tile_list = []
        for i in range(0, 20):
            for j in range(0, 9):
                # get_sprite parameters: x, y, width, height, scale
                self.Tile_list.append(sheet.get_sprite(i * 19, j * 19, 18, 18, 48 / 18))

        self.Tile_list.append(pygame.surface.Surface((48, 48))) # Placeholder for empty/air
        
        # Combine terrain tiles (0-180) and background tiles (181+)
        self.Tile_back_list = self.Tile_list + Background().Back_tile_list

    def S(self, indexes):
        """Creates a static surface for the background."""
        Super_Surface = pygame.surface.Surface((27 * 48, 15 * 48))
        a = 0
        for i in range(0, 27):
            for j in range(0, 15):
                Super_Surface.blit(self.Tile_back_list[indexes[a]], (i * 48, j * 48))
                a += 1
        return Super_Surface


class Terrain(Tiles):
    with open('Map_json.json','r') as file:
        map_data=json.load(file)

    pad = [(int(k.split(',')[0]), int(k.split(',')[1])) for k in map_data]

    def __init__(self):
        super().__init__()
        self.Elements = list(self.Tile_back_list)
        self.rect_list = [] # Rects for collision

    def Block(self, type_index, x, y, offgrid):
        r = pygame.rect.Rect(48 * x, 48 * y, 48, 48)
        if not offgrid:
            self.rect_list.append(r)
        Screen.blit(self.Elements[type_index], (48 * x, 48 * y))

    def draw_all(self, dic, l):
        for x, y in l:
            self.Block(dic[f'{x},{y}'], x, y, False)
            
    def draw_terrain(self):
        self.rect_list = [] # Clear rects before drawing new ones
        self.draw_all(self.map_data, self.pad)

class Animations:
    def __init__(self,Name):
        self.name=Name
        sprshet=Sprite__Sheet(r'Assets\Free Smoke Fx  Pixel 06.png')  #64*64
        self.dash=[]
        self.jump=[]
        self.fr=0
        self.tmr=0                          #17,18
        self.dur=0
        self.flag=0
        self.flag1=0
        self.x,self.y=0,0
        for i in range (0,12):
            self.dash.append(sprshet.get_sprite(i*64,64,64,64,2))
            self.jump.append(sprshet.get_sprite(i*64,64*17,64,64,2))
    def update(self):
        if pygame.time.get_ticks() - self.tmr<self.dur:
            if self.flag==1:
                self.animate(self.dash)
            else:
                self.flag=0
            if self.flag1==1:self.animate(self.jump)
            else:self.flag1=0
        else:pass

    def animate(self,img_list):
        if int(self.fr)<12:
            self.x=self.name.sprite.rect.x
            self.y=self.name.sprite.rect.y-80
            Screen.blit(img_list[int(self.fr)],(self.x-50,self.y+57))
            self.fr+=0.25
        else: self.fr=0
    def Dash(self):
        # self.x=player_1.sprite.rect.x
        # self.y=player_1.sprite.rect.y-80
        self.tmr=pygame.time.get_ticks()
        self.dur=800
        self.flag=1
    def Jump(self):
        self.tmr=pygame.time.get_ticks()
        self.dur=800
        self.flag1=1
# -------------------------------------------------------
# 5. PYGAME INITIALIZATION AND GAME LOOP
# -------------------------------------------------------
# Pygame initialization
# Set the window to use the wxPanel's handle
os.environ['SDL_VIDEODRIVER'] = 'windib'
os.environ['SDL_WINDOWID'] = str(panel.GetHandle())

pygame.init()
pygame.mixer.init()
jump_S=pygame.mixer.Sound(r'Assets\Retro Jump Classic 08.wav')
jump_S.set_volume(0.05)
dash_S=pygame.mixer.Sound(r'Assets\Retro Swooosh 02.wav')
dash_S.set_volume(0.05)
coll_S=pygame.mixer.Sound(r'Assets\Retro Impact Punch 07.wav')
coll_S.set_volume(0.5)
def music_control(FN,V):
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()
    pygame.mixer.music.load(FN)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(V)
music_control(r'Assets\Space Knights.mp3',0.3)
Screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)
try:
    icon = pygame.image.load(os.path.join(r'Assets\Icon.png')).convert_alpha()#ppp
    pygame.display.set_icon(icon)
except Exception:
    pass

# Game Objects Setup
player_1 = pygame.sprite.GroupSingle()
player_2 = pygame.sprite.GroupSingle()
# Add default players
player_1.add(Player_1(P1FN))
player_2.add(Player_2(P2FN))

Trail=Animations(player_1)
Trail2=Animations(player_2)

Tile = Tiles()
Terra = Terrain()
text_renderer = GameTextRenderer()
clock = pygame.time.Clock()

# Background rendering setup (Using the static surface)
# Using tile 182 which looks like a darker background grass for better contrast
floor_indexes = [182] * (27 * 15) 
s = Tile.S(floor_indexes)
BACK=Background().back
flip=0
flag=0
def P1_P2_collision():
    """Checks for collision and handles game state change (Runner vs Catcher)."""
    global play, EPA, Game_Active, R1_Score, R2_Score
    try:
        if pygame.sprite.spritecollide(player_1.sprite, player_2, False):
            # Collision happened: Stop play, stop game-end timer, start play-again timer
            coll_S.play()
            # Check if scores are already at win condition (shouldn't happen in play state but safety check)
            if R1_Score >= WIN_SCORE or R2_Score >= WIN_SCORE:
                return False # Skip state change if game already won

            Game_Active = False
            play = False
            pygame.time.set_timer(GAME_END, 0)
            
            # Record time for countdown and start restart timer
            global EPA
            EPA = pygame.time.get_ticks() / 1000
            pygame.time.set_timer(EVT_PLAY_AGAIN, COLLISION_PAUSE_DURATION_MS)
            
            # The players must be emptied to prevent drawing during the collision state
            # This is crucial for the Game Over screen rendering
            player_1.empty()
            player_2.empty()

            # Toggle runner state (Runner becomes Catcher, Catcher becomes Runner)
            is_p1_runner = RS1.GetValue()
            RS1.SetValue(RS2.GetValue())
            RS2.SetValue(is_p1_runner)
            return False
        return True
    except Exception:
        # Happens if one or both groups are empty (e.g., during collision pause)
        return True


# Main loop
try:
    while True:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == GAME_END:
                pygame.mixer.music.stop()
                # Timer ran out (Runner wins)
                Game_Active = False
                play = False
            if event.type == EVT_PLAY_AGAIN:
                # Collision pause finished, start a new round
                Play(None)

        # 2. Game Logic
        if play and Game_Active:
            # Update Scores
            score_increment = 1.0 / FPS
            if RS1.GetValue():
                R1_Score += score_increment
            if RS2.GetValue():
                R2_Score += score_increment

            # Check win condition
            if R1_Score >= WIN_SCORE or R2_Score >= WIN_SCORE:
                Game_Active = False
                play = False
                pygame.time.set_timer(GAME_END, 0)
                pygame.time.set_timer(EVT_PLAY_AGAIN, 0)

            # Update Player state (only if sprites exist)
            if player_1.sprite and player_2.sprite:
                player_1.update(Terra.rect_list)
                player_2.update(Terra.rect_list)
                
                # Check for collision
                P1_P2_collision()

        # 3. Rendering
        if play:
            Screen.fill('Black')
            Screen.blit(BACK, (0, 0)) # Draw background surface
            Terra.draw_terrain() # Draw terrain blocks (and update rect_list)
            player_1.draw(Screen)
            player_2.draw(Screen)
            Trail.update()
            Trail2.update()
            text_renderer.draw_score(Screen, R1_Score, R2_Score, RS1.GetValue(), RS2.GetValue())
        elif not Game_Active:
            # Game Over or Collision Pause Screen
            text_renderer.draw_game_over(Screen, R1_Score, R2_Score)
        else: # Game_Active is True, play is False (Start Screen / Pre-Game)
            text_renderer.draw_start_screen(Screen)
            # Players still need to be drawn for preview on start screen
            player_1.sprite.rect.x=370
            player_1.sprite.rect.y=135
            if flip==0:
                player_2.sprite.image=pygame.transform.flip(player_2.sprite.image,1,0)
                flip=1
            else:pass
            player_2.sprite.rect.x=350
            player_2.sprite.rect.y=315
            player_1.draw(Screen) 
            player_2.draw(Screen) 

        pygame.display.update()
        clock.tick(FPS)
except:pass