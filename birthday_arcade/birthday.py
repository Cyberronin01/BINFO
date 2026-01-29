"""
🎮 ARCADE BIRTHDAY SHOOTER 🎮
Shoot the birthday text to reveal the message!
From Barbie with love 💜
"""

import tkinter as tk
import random
import math
import webbrowser
import threading
import winsound

class Star:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.reset()
        self.y = random.randint(0, height)  # Start anywhere initially
        
    def reset(self):
        self.x = random.randint(0, self.width)
        self.y = 0
        self.speed = random.uniform(2, 6)
        self.size = random.randint(1, 3)
        self.color = random.choice(['#ffffff', '#00ffff', '#ff00ff', '#ffff00'])
        
    def draw(self):
        return self.canvas.create_oval(
            self.x, self.y, self.x + self.size, self.y + self.size,
            fill=self.color, outline=''
        )
    
    def move(self):
        self.y += self.speed
        if self.y > self.height:
            self.reset()

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 15
        self.width = 4
        self.height = 12
        self.active = True
        
    def move(self):
        self.y -= self.speed
        if self.y < -20:
            self.active = False

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 2)
        self.life = random.randint(20, 40)
        self.color = color
        self.size = random.randint(3, 8)
        
    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # gravity
        self.life -= 1
        self.size = max(1, self.size - 0.1)
        return self.life > 0

class TextBlock:
    def __init__(self, char, x, y, block_size):
        self.char = char
        self.x = x
        self.y = y
        self.size = block_size
        self.health = 3
        self.color = '#ff0080'  # Neon pink
        self.crack_colors = ['#ff0080', '#ff3399', '#ff66b2', '#ffffff']
        self.active = True
        self.shake_offset = 0
        
    def hit(self):
        self.health -= 1
        self.shake_offset = random.randint(-3, 3)
        if self.health <= 0:
            self.active = False
            return True  # Destroyed
        return False
    
    def get_color(self):
        idx = 3 - self.health
        return self.crack_colors[min(idx, len(self.crack_colors)-1)]
    
    def collides(self, bullet):
        return (self.active and 
                bullet.x >= self.x and bullet.x <= self.x + self.size and
                bullet.y >= self.y and bullet.y <= self.y + self.size)

class Spaceship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = 8
        self.color = '#00ffff'
        
class ArcadeBirthdayShooter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎮 HAPPY BIRTHDAY SHOOTER 🎮")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # Get screen dimensions
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=self.width, 
            height=self.height, 
            bg='#0a0a1a',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Input tracking
        self.keys = {'Left': False, 'Right': False, 'Up': False, 'Down': False, 'space': False}
        self.root.bind('<KeyPress>', self.key_press)
        self.root.bind('<KeyRelease>', self.key_release)
        self.root.bind('<Motion>', self.mouse_move)
        self.root.bind('<Button-1>', self.mouse_click)
        
        # Game objects
        self.stars = [Star(self.canvas, self.width, self.height) for _ in range(100)]
        self.ship = Spaceship(self.width // 2, self.height - 100)
        self.bullets = []
        self.particles = []
        self.text_blocks = []
        
        # Game state
        self.frame = 0
        self.shoot_cooldown = 0
        self.all_destroyed = False
        self.victory_shown = False
        self.score = 0
        self.call_button = None  # Instagram call button
        self.instagram_url = "https://www.instagram.com/ashveil____/"
        
        # Screen shake
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.shake_intensity = 0
        
        # Letter sequence puzzle
        self.target_word = "DASRUPAYKIPEPSI"  # Her Instagram ID
        self.current_letter_index = 0  # Which letter we're looking for
        self.wrong_letter_flash = 0  # Flash effect when wrong
        
        # Music disabled
        self.music_playing = False
        
        # Create text blocks
        self.create_text_blocks()
        
        # Start animation
        self.animate()
        self.root.mainloop()
    
    def create_text_blocks(self):
        """Create text blocks - JUMBLED!"""
        text = "DASRUPAYKIPEPSI"  # Her Instagram ID
        # Create jumbled version for display
        letters_only = list(text.upper())
        jumbled = letters_only.copy()
        random.shuffle(jumbled)
        
        block_size = 35
        spacing = 5
        total_width = len(jumbled) * (block_size + spacing)
        start_x = (self.width - total_width) // 2
        y = self.height // 3
        
        for i, char in enumerate(jumbled):
            x = start_x + i * (block_size + spacing)
            self.text_blocks.append(TextBlock(char, x, y, block_size))
    
    def key_press(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = True
        # Secret bomb - 'b' key
        if event.keysym.lower() == 'b':
            self.trigger_bomb()
    
    def key_release(self, event):
        if event.keysym in self.keys:
            self.keys[event.keysym] = False
    
    def mouse_move(self, event):
        self.ship.x = max(20, min(event.x, self.width - self.ship.width - 20))
    
    def mouse_click(self, event):
        # Check if clicking on call button
        if self.all_destroyed and self.call_button:
            bx, by, bw, bh = self.call_button
            if bx <= event.x <= bx + bw and by <= event.y <= by + bh:
                webbrowser.open(self.instagram_url)
                return
        self.shoot()
    
    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet = Bullet(self.ship.x + self.ship.width // 2, self.ship.y)
            self.bullets.append(bullet)
            self.shoot_cooldown = 8  # Frames between shots
            # Quick pew sound
            threading.Thread(target=lambda: winsound.Beep(800, 30), daemon=True).start()
    
    def spawn_explosion(self, x, y, color):
        """Spawn cute pixel explosion"""
        for _ in range(15):
            self.particles.append(Particle(x, y, color))
        # Add some sparkles
        sparkle_colors = ['#ffffff', '#ffff00', '#00ffff']
        for _ in range(8):
            self.particles.append(Particle(x, y, random.choice(sparkle_colors)))
    
    def play_chiptune(self):
        """Play retro chiptune music in background"""
        import time
        # Simple retro melody notes (frequency, duration)
        melody = [
            (523, 150), (587, 150), (659, 150), (698, 150),
            (784, 200), (698, 100), (659, 150), (587, 150),
            (523, 200), (0, 100),  # 0 = pause
            (392, 150), (440, 150), (523, 200), (440, 150),
            (392, 200), (349, 150), (330, 200), (0, 200),
        ]
        while self.music_playing:
            for freq, dur in melody:
                if not self.music_playing:
                    break
                try:
                    if freq > 0:
                        winsound.Beep(freq, dur)
                    else:
                        time.sleep(dur / 1000)
                except:
                    pass
            time.sleep(0.5)  # Pause before loop
    
    def trigger_bomb(self):
        """Secret bomb - destroy all blocks at once!"""
        for block in self.text_blocks:
            if block.active:
                block.active = False
                center_x = block.x + block.size // 2
                center_y = block.y + block.size // 2
                # Big explosion for each block
                for _ in range(3):
                    self.spawn_explosion(center_x, center_y, random.choice(['#ff0080', '#ffff00', '#00ffff', '#ff00ff']))
                self.score += 100
        # Massive screen shake for bomb
        self.shake_intensity = 30
        # Big explosion sound
        threading.Thread(target=lambda: winsound.Beep(100, 200), daemon=True).start()
    
    def update(self):
        self.frame += 1
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        
        # Move ship with keyboard
        if self.keys['Left']:
            self.ship.x = max(20, self.ship.x - self.ship.speed)
        if self.keys['Right']:
            self.ship.x = min(self.width - self.ship.width - 20, self.ship.x + self.ship.speed)
        if self.keys['Up']:
            self.ship.y = max(self.height // 2, self.ship.y - self.ship.speed)
        if self.keys['Down']:
            self.ship.y = min(self.height - 50, self.ship.y + self.ship.speed)
        if self.keys['space']:
            self.shoot()
        
        # Move stars
        for star in self.stars:
            star.move()
        
        # Move bullets
        for bullet in self.bullets:
            bullet.move()
        self.bullets = [b for b in self.bullets if b.active]
        
        # Check bullet collisions with text blocks
        for bullet in self.bullets:
            for block in self.text_blocks:
                if block.collides(bullet):
                    bullet.active = False
                    center_x = block.x + block.size // 2
                    center_y = block.y + block.size // 2
                    
                    # Check if this is the correct letter in sequence
                    expected_letter = self.target_word[self.current_letter_index] if self.current_letter_index < len(self.target_word) else None
                    
                    if expected_letter and block.char == expected_letter:
                        # CORRECT letter! Destroy it
                        if block.hit():
                            # Block destroyed - big explosion!
                            self.spawn_explosion(center_x, center_y, block.color)
                            self.score += 100
                            self.shake_intensity = 15
                            self.current_letter_index += 1  # Move to next letter
                            threading.Thread(target=lambda: winsound.Beep(600, 50), daemon=True).start()
                        else:
                            # Block damaged - small sparks
                            for _ in range(5):
                                self.particles.append(Particle(center_x, center_y, '#ffffff'))
                            self.score += 10
                    else:
                        # WRONG letter! Flash and penalty
                        self.wrong_letter_flash = 20
                        self.score = max(0, self.score - 50)  # Penalty
                        block.health = 3  # Reset block health
                        self.shake_intensity = 8
                        # Wrong sound
                        threading.Thread(target=lambda: winsound.Beep(200, 100), daemon=True).start()
                    break
        
        # Move particles
        self.particles = [p for p in self.particles if p.move()]
        
        # Check if all blocks destroyed
        if not self.all_destroyed and all(not b.active for b in self.text_blocks):
            self.all_destroyed = True
    
    def draw(self):
        self.canvas.delete('all')
        
        # Update screen shake
        if self.shake_intensity > 0:
            self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity = max(0, self.shake_intensity - 2)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0
        
        sx, sy = self.shake_offset_x, self.shake_offset_y  # shorthand
        
        # Draw stars
        for star in self.stars:
            self.canvas.create_oval(
                star.x + sx, star.y + sy, star.x + star.size + sx, star.y + star.size + sy,
                fill=star.color, outline=''
            )
        
        # Draw text blocks
        for block in self.text_blocks:
            if block.active:
                x = block.x + block.shake_offset
                block.shake_offset *= 0.8  # Decay shake
                
                # Check if this is the target letter (subtle hint)
                is_target = False
                if self.current_letter_index < len(self.target_word):
                    if block.char == self.target_word[self.current_letter_index]:
                        is_target = True
                
                # Determine border color - blue for target, white for others
                border_color = '#00aaff' if is_target else '#ffffff'
                
                # Draw block background
                self.canvas.create_rectangle(
                    x, block.y, x + block.size, block.y + block.size,
                    fill=block.get_color(), outline=border_color, width=2
                )
                
                # Draw character
                self.canvas.create_text(
                    x + block.size // 2, block.y + block.size // 2,
                    text=block.char, font=('Courier New', 20, 'bold'),
                    fill='#ffffff'
                )
                
                # Draw cracks based on damage
                if block.health < 3:
                    for _ in range(3 - block.health):
                        cx = x + random.randint(5, block.size - 5)
                        cy = block.y + random.randint(5, block.size - 5)
                        self.canvas.create_line(
                            cx - 5, cy - 5, cx + 5, cy + 5,
                            fill='#330022', width=2
                        )
        
        # Draw particles
        for p in self.particles:
            size = int(p.size)
            self.canvas.create_rectangle(
                p.x, p.y, p.x + size, p.y + size,
                fill=p.color, outline=''
            )
        
        # Draw bullets
        for bullet in self.bullets:
            # Neon bullet effect
            self.canvas.create_rectangle(
                bullet.x - 2, bullet.y,
                bullet.x + bullet.width + 2, bullet.y + bullet.height,
                fill='#00ffff', outline=''
            )
            self.canvas.create_rectangle(
                bullet.x, bullet.y + 2,
                bullet.x + bullet.width, bullet.y + bullet.height - 2,
                fill='#ffffff', outline=''
            )
        
        # Draw spaceship
        ship = self.ship
        # Main body
        points = [
            ship.x + ship.width // 2, ship.y,  # Top
            ship.x, ship.y + ship.height,  # Bottom left
            ship.x + ship.width, ship.y + ship.height,  # Bottom right
        ]
        self.canvas.create_polygon(points, fill=ship.color, outline='#ffffff', width=2)
        
        # Cockpit
        self.canvas.create_oval(
            ship.x + ship.width // 2 - 6, ship.y + 10,
            ship.x + ship.width // 2 + 6, ship.y + 22,
            fill='#ff00ff', outline=''
        )
        
        # Draw UI
        self.canvas.create_text(
            100, 30, text=f"SCORE: {self.score}",
            font=('Courier New', 20, 'bold'), fill='#ffff00', anchor='w'
        )
        
        # Show next letter hint
        if self.current_letter_index < len(self.target_word):
            progress = f"[{self.current_letter_index}/{len(self.target_word)}]"
            hint_color = '#ff3333' if self.wrong_letter_flash > 0 else '#666666'
            self.canvas.create_text(
                self.width // 2, 30, text=f"SPELL THE WORD {progress}",
                font=('Courier New', 14, 'bold'), fill=hint_color
            )
            # Show progress - completed letters + underscores for remaining
            completed = self.target_word[:self.current_letter_index]
            remaining = "_" * (len(self.target_word) - self.current_letter_index)
            progress_text = completed + remaining
            # Add spaces between letters for readability
            spaced_progress = " ".join(progress_text)
            self.canvas.create_text(
                self.width // 2, 60, text=spaced_progress,
                font=('Courier New', 18, 'bold'), fill='#00ffcc'
            )
            # Decay flash
            if self.wrong_letter_flash > 0:
                self.wrong_letter_flash -= 1
        else:
            self.canvas.create_text(
                self.width // 2, 30, text="< WORD COMPLETE! >",
                font=('Courier New', 16, 'bold'), fill='#00ff00'
            )
            # Show full word
            spaced_word = " ".join(self.target_word)
            self.canvas.create_text(
                self.width // 2, 60, text=spaced_word,
                font=('Courier New', 18, 'bold'), fill='#00ffcc'
            )
        
        # Draw victory message if all destroyed
        if self.all_destroyed:
            # Pulsing effect
            pulse = abs(math.sin(self.frame * 0.05))
            glow_size = int(3 + pulse * 2)
            
            # Simple elegant gold-green text
            self.canvas.create_text(
                self.width // 2, self.height // 2 - 50,
                text="★ HAPPY BIRTHDAY ★",
                font=('Courier New', 52 + glow_size, 'bold'),
                fill='#bfff00'  # Yellow-green / Lime gold
            )
            
            self.canvas.create_text(
                self.width // 2, self.height // 2 + 30,
                text="You revealed the message!",
                font=('Courier New', 20, 'bold'), fill='#00ffff'
            )
            
            self.canvas.create_text(
                self.width // 2, self.height // 2 + 80,
                text="– From Barbie ♥",
                font=('Courier New', 28, 'bold'), fill='#ff00ff'
            )
            
            # Spawn celebration particles
            if random.random() < 0.2:
                self.spawn_explosion(
                    random.randint(100, self.width - 100),
                    random.randint(100, self.height // 2),
                    random.choice(['#ff0080', '#00ffff', '#ffff00', '#ff00ff'])
                )
            
            # Draw Instagram Call Button
            btn_text = "📞 Call Barbie"
            btn_width = 200
            btn_height = 50
            btn_x = self.width // 2 - btn_width // 2
            btn_y = self.height // 2 + 140
            
            # Store button bounds for click detection
            self.call_button = (btn_x, btn_y, btn_width, btn_height)
            
            # Pulsing glow effect for text
            pulse = abs(math.sin(self.frame * 0.08))
            glow_color = '#ff00ff' if pulse > 0.5 else '#cc66cc'
            
            # Just glowing text, no box
            self.canvas.create_text(
                self.width // 2, btn_y + btn_height // 2,
                text=btn_text,
                font=('Courier New', 16, 'bold'), fill='#ff00ff'
            )
        
        self.canvas.create_text(
            self.width // 2, self.height - 30,
            text="[Arrow Keys to move | SPACE to shoot | ESC to exit]",
            font=('Courier New', 12), fill='#666666'
        )
    
    def animate(self):
        self.update()
        self.draw()
        self.root.after(33, self.animate)

if __name__ == "__main__":
    ArcadeBirthdayShooter()
