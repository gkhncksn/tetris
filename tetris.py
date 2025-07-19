import tkinter
from tkinter import Canvas, Label, Tk, StringVar, Button, Frame
from random import choice
from collections import Counter
import time

class Game():
    WIDTH = 300
    HEIGHT = 500

    def start(self):
        self.level = 1
        self.score = 0
        self.speed = 500
        self.lines_cleared = 0
        self.create_new_game = True
        self.paused = False
        self.game_over_state = False

        self.root = Tk()
        self.root.title("Tetris")
        self.root.focus_set()

        # Ana frame
        main_frame = Frame(self.root)
        main_frame.pack()

        # Üst bilgi frame'i
        top_frame = Frame(main_frame)
        top_frame.pack(fill='x')

        self.status_var = StringVar() 
        self.status_var.set("Level: 1, Score: 0, Lines: 0")
        self.status = Label(top_frame, 
                textvariable=self.status_var, 
                font=("Helvetica", 10, "bold"))
        self.status.pack(side='left')

        # Oyun alanı frame'i
        game_frame = Frame(main_frame)
        game_frame.pack()

        # Ana oyun canvas'ı
        self.canvas = Canvas(
                game_frame, 
                width=Game.WIDTH, 
                height=Game.HEIGHT,
                bg='black')
        self.canvas.pack(side='left')

        # Sağ panel - Sonraki Şekil
        right_panel = Frame(game_frame)
        right_panel.pack(side='right', padx=10, fill='y')
        next_label = Label(right_panel, text="Sonraki Şekil:", 
                          font=("Helvetica", 10, "bold"))
        next_label.pack()

        # Sonraki Şekil Önizleme
        self.next_canvas = Canvas(right_panel, 
                                width=100, height=100, 
                                bg='black', relief='sunken', bd=2)
        self.next_canvas.pack(pady=5)

        # Yeniden oyna butonu (başlangıçta gizli)
        self.restart_button = Button(main_frame, text="Yeniden Oyna (R)", 
                                   command=self.restart_game,
                                   font=("Helvetica", 12, "bold"),
                                   bg="lightblue")
        
        # Kontrollar etiketi
        controls_text = "Kontroller: ← → ↓ ↑(Döndür) P(Pause) R(Restart)"
        self.controls_label = Label(main_frame, text=controls_text, 
                                  font=("Helvetica", 8))
        self.controls_label.pack()

        self.next_shape_type = choice(Shape.SHAPES)
        self.draw_next_shape()

        self.root.bind("<Key>", self.handle_events)
        self.timer()
        self.root.mainloop()
    
    def timer(self):
        if self.game_over_state:
            return
            
        if self.paused:
            self.root.after(100, self.timer)
            return
            
        if self.create_new_game == True:
            self.current_shape = Shape(self.canvas, self.next_shape_type)
            self.create_new_game = False
            # Yeni next shape seç ve çiz
            self.next_shape_type = choice(Shape.SHAPES)
            self.draw_next_shape()

        if not self.current_shape.fall():
            lines = self.remove_complete_lines()
            if lines:
                self.lines_cleared += lines
                # Skor hesaplama: temizlenen satır sayısına göre
                line_scores = [0, 40, 100, 300, 1200]  # 0, 1, 2, 3, 4 satır için puanlar
                if lines <= 4:
                    self.score += line_scores[lines] * self.level
                else:
                    self.score += 1200 * self.level * (lines - 3)  # 4'ten fazla satır için
                
                # Level artırma: her 10 satır temizlendiğinde
                new_level = (self.lines_cleared // 10) + 1
                if new_level > self.level:
                    self.level = new_level
                    self.speed = max(50, 500 - (self.level - 1) * 50)  # Minimum hız 50ms
                
                self.update_status()

            self.current_shape = Shape(self.canvas, self.next_shape_type)
            # Yeni next shape seç ve çiz
            self.next_shape_type = choice(Shape.SHAPES)
            self.draw_next_shape()
            
            if self.is_game_over(): 
                self.game_over()
                return
        
        self.root.after(self.speed, self.timer)

    def update_status(self):
        self.status_var.set("Level: %d, Score: %d, Lines: %d" % 
                (self.level, self.score, self.lines_cleared))

    def handle_events(self, event):
        if event.keysym == "p" or event.keysym == "P":
            self.toggle_pause()
            return
        
        if event.keysym == "r" or event.keysym == "R":
            self.restart_game()
            return
            
        if self.paused or self.game_over_state:
            return
            
        if hasattr(self, 'current_shape') and self.current_shape:
            if event.keysym == "Left": 
                self.current_shape.move(-1, 0)
            elif event.keysym == "Right": 
                self.current_shape.move(1, 0)
            elif event.keysym == "Down": 
                self.current_shape.move(0, 1)
            elif event.keysym == "Up": 
                self.current_shape.rotate()

    def toggle_pause(self):
        if self.game_over_state:
            return
        self.paused = not self.paused
        if self.paused:
            self.show_pause_message()
        else:
            self.clear_messages()

    def show_pause_message(self):
        self.canvas.create_text(Game.WIDTH // 2, Game.HEIGHT // 2, 
                              text="OYUN DURDURULDU\nDevam etmek için P'ye basın",
                              fill="white", font=("Helvetica", 14, "bold"),
                              justify="center", tags="pause_message")

    def draw_next_shape(self):
        self.next_canvas.delete("all")
        
        if not self.next_shape_type:
            return
            
        color = self.next_shape_type[0]
        shape_points = self.next_shape_type[1:]
        
        # Şeklin boyutlarını hesapla
        min_x = min(point[0] for point in shape_points)
        max_x = max(point[0] for point in shape_points)
        min_y = min(point[1] for point in shape_points)
        max_y = max(point[1] for point in shape_points)
        
        shape_width = (max_x - min_x + 1) * 15  # Küçültülmüş boyut
        shape_height = (max_y - min_y + 1) * 15
        
        # Şekli ortalamak için offset hesapla
        offset_x = (100 - shape_width) // 2 - min_x * 15
        offset_y = (100 - shape_height) // 2 - min_y * 15
        
        # Şeklin her bloğunu çiz
        for point in shape_points:
            x1 = point[0] * 15 + offset_x
            y1 = point[1] * 15 + offset_y
            x2 = x1 + 15
            y2 = y1 + 15
            
            self.next_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=color, outline='white'
            )

    def clear_messages(self):
        self.canvas.delete("pause_message")
        self.canvas.delete("game_over_message")

    def restart_game(self):
        self.canvas.delete("all")
        self.level = 1
        self.score = 0
        self.lines_cleared = 0
        self.speed = 500
        self.create_new_game = True
        self.paused = False
        self.game_over_state = False
        self.restart_button.pack_forget()
        # Yeni next shape seç
        self.next_shape_type = choice(Shape.SHAPES)
        self.draw_next_shape()
        self.update_status()
        self.timer()

    def is_game_over(self):
        if not hasattr(self.current_shape, 'boxes') or not self.current_shape.boxes:
            return False
            
        for box in self.current_shape.boxes:
            if not self.current_shape.can_move_box(box, 0, 1):
                return True
        return False

    def remove_complete_lines(self):
        '''Tamamlanmış satırları görsel efektlerle kaldır ve üstteki blokları aşağı kaydır'''
        all_boxes = self.canvas.find_all()
        if not all_boxes:
            return 0

        rows = {}
        box_coords = {}
        
        for box in all_boxes:
            coords = self.canvas.coords(box)
            if len(coords) == 4:  
                y = int(coords[1])  
                box_coords[box] = coords
                if y not in rows:
                    rows[y] = []
                rows[y].append(box)

        complete_lines = []
        boxes_per_row = Game.WIDTH // Shape.BOX_SIZE
        
        for y, boxes in rows.items():
            if len(boxes) >= boxes_per_row:
                complete_lines.append(y)

        if not complete_lines:
            return 0

        complete_lines.sort()  # Satırları sırala

        # Görsel efektlerle satırları sil
        self.animate_line_clear(complete_lines, rows)

        # Kalan kutuları aşağı kaydır
        remaining_boxes = []
        for box in all_boxes:
            try:
                current_coords = self.canvas.coords(box)
                if len(current_coords) == 4:
                    remaining_boxes.append(box)
            except:
                continue
                
        for box in remaining_boxes:
            try:
                current_coords = self.canvas.coords(box)
                if len(current_coords) == 4:
                    box_y = int(current_coords[1])
                    # Bu kutunun kaç tane tamamlanmış satırın üstünde olduğunu hesapla
                    lines_below = sum(1 for line_y in complete_lines if box_y < line_y)
                    if lines_below > 0:
                        self.canvas.move(box, 0, lines_below * Shape.BOX_SIZE)
            except:
                continue

        return len(complete_lines)

    def animate_line_clear(self, complete_lines, rows):
        '''Satır temizleme animasyonu - soldan sağa doğru patlatma'''
        for line_y in complete_lines:
            line_boxes = rows[line_y]
            # Kutuları x koordinatına göre sırala (soldan sağa)
            line_boxes.sort(key=lambda box: self.canvas.coords(box)[0])
            
            # Her kutuyu soldan sağa doğru patlatma efektiyle sil
            for i, box in enumerate(line_boxes):
                self.root.after(i * 30, lambda b=box: self.explode_box(b))

        # Tüm animasyon bitene kadar bekle
        total_delay = len(line_boxes) * 30 + 100
        self.root.after(total_delay, lambda: None)

    def explode_box(self, box):
        '''Tek bir kutuyu patlatma efektiyle sil'''
        try:
            coords = self.canvas.coords(box)
            if len(coords) == 4:
                x1, y1, x2, y2 = coords
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Patlatma efekti - küçük parçacıklar oluştur
                colors = ['white', 'yellow', 'orange', 'red']
                for i in range(4):
                    particle = self.canvas.create_oval(
                        center_x - 2, center_y - 2,
                        center_x + 2, center_y + 2,
                        fill=choice(colors), outline=""
                    )
                    # Parçacıkları dağıt
                    dx = (i - 1.5) * 10
                    dy = (i - 1.5) * 5
                    self.canvas.move(particle, dx, dy)
                    # Parçacıkları 100ms sonra sil
                    self.root.after(100, lambda p=particle: self.canvas.delete(p))
                
                # Orijinal kutuyu sil
                self.canvas.delete(box)
        except:
            pass

    def game_over(self):
        self.game_over_state = True
        game_over_text = f"OYUN BİTTİ!\n\nSkor: {self.score}\nSeviye: {self.level}\nTemizlenen Satır: {self.lines_cleared}\n\nYeniden oynamak için R'ye basın"
        
        # Yarı şeffaf arka plan
        overlay = self.canvas.create_rectangle(0, 0, Game.WIDTH, Game.HEIGHT,
                                             fill="black", stipple="gray50",
                                             tags="game_over_message")
        
        # Ana mesaj
        self.canvas.create_text(Game.WIDTH // 2, Game.HEIGHT // 2 - 50,
                              text=game_over_text,
                              fill="white", font=("Helvetica", 12, "bold"),
                              justify="center", tags="game_over_message")
        
        # Yeniden oyna butonunu göster
        self.restart_button.pack(pady=10)

class Shape:
    '''Defines a tetris shape.'''
    BOX_SIZE = 20
    # START_POINT relies on screwy integer arithmetic to approximate the middle
    # of the canvas while remaining correctly on the grid.
    START_POINT = Game.WIDTH // 2 // BOX_SIZE * BOX_SIZE - BOX_SIZE
    SHAPES = (
            ("yellow", (0, 0), (1, 0), (0, 1), (1, 1)),     # square
            ("lightblue", (0, 0), (1, 0), (2, 0), (3, 0)),  # line
            ("orange", (2, 0), (0, 1), (1, 1), (2, 1)),     # right el
            ("blue", (0, 0), (0, 1), (1, 1), (2, 1)),       # left el
            ("green", (0, 1), (1, 1), (1, 0), (2, 0)),      # right wedge
            ("red", (0, 0), (1, 0), (1, 1), (2, 1)),        # left wedge
            ("purple", (1, 0), (0, 1), (1, 1), (2, 1)),     # symmetrical wedge
            )

    def __init__(self, canvas, shape_type=None):
        self.boxes = [] # the squares drawn by canvas.create_rectangle()
        self.shape = shape_type if shape_type else choice(Shape.SHAPES) # a random shape or provided shape
        self.color = self.shape[0]
        self.canvas = canvas

        for point in self.shape[1:]:
            box = canvas.create_rectangle(
                point[0] * Shape.BOX_SIZE + Shape.START_POINT,
                point[1] * Shape.BOX_SIZE,
                point[0] * Shape.BOX_SIZE + Shape.BOX_SIZE + Shape.START_POINT,
                point[1] * Shape.BOX_SIZE + Shape.BOX_SIZE,
                fill=self.color,
                outline='white')
            self.boxes.append(box)
      
    def move(self, x, y):
        '''Moves this shape (x, y) boxes.'''
        if not self.can_move_shape(x, y): 
            return False         
        else:
            for box in self.boxes: 
                self.canvas.move(box, x * Shape.BOX_SIZE, y * Shape.BOX_SIZE)
            return True

    def fall(self):
        '''Moves this shape one box-length down.'''
        if not self.can_move_shape(0, 1):
            return False
        else:
            for box in self.boxes:
                self.canvas.move(box, 0, Shape.BOX_SIZE)
            return True

    def rotate(self):
        '''Rotates the shape clockwise.'''
        if len(self.boxes) < 3:
            return False
            
        boxes = self.boxes[:]
        pivot = boxes.pop(2)

        def get_move_coords(box):
            '''Return (x, y) boxes needed to rotate a box around the pivot.'''
            box_coords = self.canvas.coords(box)
            pivot_coords = self.canvas.coords(pivot)
            x_diff = box_coords[0] - pivot_coords[0]
            y_diff = box_coords[1] - pivot_coords[1]
            x_move = (- x_diff - y_diff) / Shape.BOX_SIZE
            y_move = (x_diff - y_diff) / Shape.BOX_SIZE
            return x_move, y_move

        # Check if shape can legally move
        for box in boxes:
            x_move, y_move = get_move_coords(box)
            if not self.can_move_box(box, x_move, y_move): 
                return False
            
        # Move shape
        for box in boxes:
            x_move, y_move = get_move_coords(box)
            self.canvas.move(box, 
                    x_move * Shape.BOX_SIZE, 
                    y_move * Shape.BOX_SIZE)

        return True

    def can_move_box(self, box, x, y):
        '''Check if box can move (x, y) boxes.'''
        try:
            x = x * Shape.BOX_SIZE
            y = y * Shape.BOX_SIZE
            coords = self.canvas.coords(box)
            
            if len(coords) != 4:
                return False
            
            # Returns False if moving the box would overrun the screen
            if coords[3] + y > Game.HEIGHT: return False
            if coords[0] + x < 0: return False
            if coords[2] + x > Game.WIDTH: return False

            # Returns False if moving box (x, y) would overlap another box
            overlap = set(self.canvas.find_overlapping(
                    (coords[0] + coords[2]) / 2 + x, 
                    (coords[1] + coords[3]) / 2 + y, 
                    (coords[0] + coords[2]) / 2 + x,
                    (coords[1] + coords[3]) / 2 + y
                    ))
            other_items = set(self.canvas.find_all()) - set(self.boxes)
            if overlap & other_items: return False

            return True
        except:
            return False

    def can_move_shape(self, x, y):
        '''Check if the shape can move (x, y) boxes.'''
        if not self.boxes:
            return False
        for box in self.boxes:
            if not self.can_move_box(box, x, y): 
                return False
        return True

if __name__ == "__main__":
    game = Game()
    game.start()
