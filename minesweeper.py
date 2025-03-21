import pyglet
from pyglet.window import mouse
font_path = "Assets/Font/CinzelDecorative-Bold.ttf"
pyglet.font.add_file(font_path)

import random
import time
import json
from datetime import datetime
import os

if not os.path.exists("statistics.json"):
    with open("statistics.json", "w") as f:
        json.dump([], f)

# Constants
MINE = -1
TILE_SIZE = 40

class Minesweeper:
    def __init__(self, width, height, num_mines):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.minefield = self.create_minefield()
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flags = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.start_time = time.time()
        self.moves = 0
        # Load images
        self.images = {
            "back": pyglet.image.load("Assets/Pictures/tile_back.png"),
            "empty": pyglet.image.load("Assets/Pictures/tile_empty.png"),
            "mine": pyglet.image.load("Assets/Pictures/tile_mine.png"),
            "flag": pyglet.image.load("Assets/Pictures/tile_flag.png"),
            "1": pyglet.image.load("Assets/Pictures/tile_1.png"),
            "2": pyglet.image.load("Assets/Pictures/tile_2.png"),
            "3": pyglet.image.load("Assets/Pictures/tile_3.png"),
            "4": pyglet.image.load("Assets/Pictures/tile_4.png"),
            "5": pyglet.image.load("Assets/Pictures/tile_5.png"),
            "6": pyglet.image.load("Assets/Pictures/tile_6.png"),
            "7": pyglet.image.load("Assets/Pictures/tile_7.png"),
            "8": pyglet.image.load("Assets/Pictures/tile_8.png"),
        }

    def create_minefield(self):
        minefield = [[0 for _ in range(self.width)] for _ in range(self.height)]
        mines_placed = 0

        while mines_placed < self.num_mines:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if minefield[y][x] != MINE:
                minefield[y][x] = MINE
                mines_placed += 1
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if 0 <= x + dx < self.width and 0 <= y + dy < self.height and minefield[y + dy][x + dx] != MINE:
                            minefield[y + dy][x + dx] += 1
        return minefield

    def reveal_tile(self, x, y):
        if self.revealed[y][x] or self.flags[y][x] or self.game_over:
            return
        self.revealed[y][x] = True
        self.moves += 1

        if self.minefield[y][x] == MINE:
            self.game_over = True
            self.end_game(outcome="Lose")
            return

        if self.minefield[y][x] == 0:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if 0 <= x + dx < self.width and 0 <= y + dy < self.height:
                        self.reveal_tile(x + dx, y + dy)

        if self.check_win():
            self.game_over = True
            self.end_game(outcome="Win")

    def check_win(self):
        # Win condition: all non-mine tiles are revealed
        for y in range(self.height):
            for x in range(self.width):
                if self.minefield[y][x] != MINE and not self.revealed[y][x]:
                    return False
        return True

    def end_game(self, outcome):
        duration = (time.time() - self.start_time) / 60  # Convert to minutes
        save_statistics(
            duration=duration,
            moves=self.moves,
            outcome=outcome,
            num_mines=self.num_mines,
            width=self.width,
            height=self.height
        )

    def toggle_flag(self, x, y):
        if not self.revealed[y][x]:
            self.flags[y][x] = not self.flags[y][x]

    def draw(self):
        for y in range(self.height):
            for x in range(self.width):
                tile_x = x * TILE_SIZE
                tile_y = y * TILE_SIZE

                if self.revealed[y][x]:
                    if self.minefield[y][x] == MINE:
                        self.images["mine"].blit(tile_x, tile_y)
                    elif self.minefield[y][x] == 0:
                        self.images["empty"].blit(tile_x, tile_y)
                    else:
                        self.images[str(self.minefield[y][x])].blit(tile_x, tile_y)
                elif self.flags[y][x]:
                    self.images["flag"].blit(tile_x, tile_y)
                else:
                    self.images["back"].blit(tile_x, tile_y)

    def on_mouse_press(self, x, y, button, modifiers):
        tile_x = int(x // TILE_SIZE)
        tile_y = int(y // TILE_SIZE)
        if 0 <= tile_x < self.width and 0 <= tile_y < self.height:
            if button == mouse.LEFT:
                self.reveal_tile(tile_x, tile_y)
            elif button == mouse.RIGHT:
                self.toggle_flag(tile_x, tile_y)

class MinesweeperWindow(pyglet.window.Window):
    def __init__(self, minesweeper):
        super(MinesweeperWindow, self).__init__(minesweeper.width * TILE_SIZE, minesweeper.height * TILE_SIZE)
        self.minesweeper = minesweeper
        self.set_location(100, 100)
        self.push_handlers(self.minesweeper)

    def on_draw(self):
        self.clear()
        self.minesweeper.draw()

        # Check the game state and display appropriate messages
        if self.minesweeper.game_over:
            outcome_text = "You Win!" if self.minesweeper.check_win() else "Game Over!"
            label = pyglet.text.Label(
                outcome_text,
                font_name='Cinzel Decorative',
                font_size=35,
                x=self.width // 2,
                y=self.height // 2,
                anchor_x='center',
                anchor_y='center',
                color=(80, 200, 120, 255) if self.minesweeper.check_win() else (155, 27, 48, 255)
            )
            label.draw()

def view_statistics():
    try:
        with open("statistics.json", "r") as f:
            statistics = json.load(f)

            if not statistics:
                print("No statistics available.")
                return

            print("\n--- Game Statistics ---")
            for entry in statistics:
                print(f"Timestamp: {entry['timestamp']}")
                print(f"Duration: {entry['duration_minutes']} minutes")
                print(f"Moves: {entry['moves']}")
                print(f"Outcome: {entry['outcome']}")
                print(f"Mines: {entry['mines']}")
                print(f"Grid Dimensions: {entry['grid_dimensions']}")
                print("-" * 30)

    except FileNotFoundError:
        print("No statistics file found. Please play a game first.")
    except json.JSONDecodeError:
        print("Error reading the statistics file. The file may be corrupted.")

def save_statistics(duration, moves, outcome, num_mines, width, height):
    stats_entry = {
        "timestamp": str(datetime.now()),  # Store timestamp as string
        "duration_minutes": round(duration, 2),
        "moves": moves,
        "outcome": outcome,
        "mines": num_mines,
        "grid_dimensions": f"{width}x{height}"
    }

    try:
        # Try loading the existing statistics or create an empty list
        try:
            with open("statistics.json", "r") as f:
                statistics = json.load(f)
        except FileNotFoundError:
            statistics = []

        # Append new entry
        statistics.append(stats_entry)

        # Save updated stats back to the file
        with open("statistics.json", "w") as f:
            json.dump(statistics, f, indent=4)

        print("Statistics saved successfully.")
    except Exception as e:
        print(f"Error saving statistics: {e}")

def get_user_input():
    print('\n'+'=-= '*12, "\n=           Welcome to Minesweeper!           =",'\n'+'=-= '*12)

    print("\nPlease choose your grid dimensions:")
    print("\n1. Easy - 10x10, 15 mines")
    print("2. Medium - 16x16, 25 mines")
    print("3. Hard - 18x30, 40 mines")
    print("4. Custom Dimensions & Mines")
    print("5. View Game Statistics")
    print("6. Quit")

    while True:
        try:
            choice = int(input("Enter your choice (1-6): "))
            if choice == 1:
                return 10, 10, 15
            elif choice == 2:
                return 16, 16, 25
            elif choice == 3:
                return 18, 30, 40
            elif choice == 4:
                width = int(input("Enter the width: "))
                height = int(input("Enter the height: "))
                num_mines = int(input("Enter the number of mines: "))
                return width, height, num_mines
            elif choice == 5:
                view_statistics()  # View statistics
                return None, None, None  # Return None to avoid starting a new game
            elif choice == 6:
                print("Thanks for playing!")
                exit()  # Quit the program
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Invalid input, please enter a number between 1 and 6.")

def main():
    while True:
        width, height, num_mines = get_user_input()

        if width is None:  # If None is returned (view stats or quit), skip starting the game
            continue

        # Start the game
        minesweeper = Minesweeper(width, height, num_mines)
        window = MinesweeperWindow(minesweeper)
        pyglet.app.run()

if __name__ == "__main__":
    main()
