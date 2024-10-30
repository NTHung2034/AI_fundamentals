import tkinter as tk
from tkinter import ttk
import time
import os
from typing import List, Dict
import copy
from mazesolver import read_input, MazeSolver

class SokobanGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sokoban Solver")
        
        # GUI state variables
        self.current_step = 0
        self.is_playing = False
        self.animation_speed = 500  # milliseconds
        self.current_maze = []
        self.solution_path = ""
        self.stats = {"steps": 0, "weight": 0, "nodes": 0, "time": 0, "memory": 0}
        
        # Setup GUI components
        self.setup_gui()
        
    def setup_gui(self):
        # Top control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").grid(row=0, column=0, padx=5)
        self.algo_var = tk.StringVar(value="UCS")
        algo_combo = ttk.Combobox(control_frame, textvariable=self.algo_var, 
                                 values=["UCS", "BFS", "DFS", "A*"], state="readonly")
        algo_combo.grid(row=0, column=1, padx=5)
        
        # Test case selection
        ttk.Label(control_frame, text="Test Case:").grid(row=0, column=2, padx=5)
        self.test_var = tk.StringVar(value="01")
        test_combo = ttk.Combobox(control_frame, textvariable=self.test_var,
                                 values=[f"{i:02d}" for i in range(1, 11)], state="readonly")
        test_combo.grid(row=0, column=3, padx=5)
        
        # Solve button
        ttk.Button(control_frame, text="Solve", command=self.solve_maze).grid(row=0, column=4, padx=5)
        
        # Playback controls
        control_frame2 = ttk.Frame(self.root, padding="10")
        control_frame2.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(control_frame2, text="⏮", command=self.reset_animation).grid(row=0, column=0, padx=2)
        ttk.Button(control_frame2, text="⏪", command=self.step_backward).grid(row=0, column=1, padx=2)
        self.play_button = ttk.Button(control_frame2, text="▶", command=self.toggle_play)
        self.play_button.grid(row=0, column=2, padx=2)
        ttk.Button(control_frame2, text="⏩", command=self.step_forward).grid(row=0, column=3, padx=2)
        
        # Speed control
        ttk.Label(control_frame2, text="Speed:").grid(row=0, column=4, padx=5)
        self.speed_scale = ttk.Scale(control_frame2, from_=100, to=1000, orient=tk.HORIZONTAL,
                                   command=self.update_speed)
        self.speed_scale.set(500)
        self.speed_scale.grid(row=0, column=5, padx=5)
        
        # Maze canvas
        self.canvas_frame = ttk.Frame(self.root, padding="10")
        self.canvas_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(self.canvas_frame, width=500, height=500)
        self.canvas.grid(row=0, column=0)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding="10")
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Stats labels
        self.stats_labels = {}
        stats = ["Steps", "Weight", "Nodes", "Time (ms)", "Memory (MB)"]
        for i, stat in enumerate(stats):
            ttk.Label(stats_frame, text=f"{stat}:").grid(row=0, column=i*2, padx=5)
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0")
            self.stats_labels[stat].grid(row=0, column=i*2+1, padx=5)
            
    def solve_maze(self):
        # Get selected algorithm and test case
        algo = self.algo_var.get()
        test_case = self.test_var.get()
        
        # Read input file
        input_file = f"input-{test_case}.txt"
        stone_weights, maze = read_input(input_file)
        
        # Create solver instance
        solver = MazeSolver(maze, stone_weights)
        
        # Solve based on selected algorithm
        if algo == "UCS":
            solution, stats = solver.solve_ucs()
        # Add other algorithms here...
        
        # Store solution and update display
        if solution:
            self.solution_path = ''.join(solution)
            self.stats = stats
            self.current_maze = [list(row) for row in maze]
            self.current_step = 0
            self.update_display()
            self.update_stats()
            
    def update_display(self):
        self.canvas.delete("all")
        if not self.current_maze:
            return
            
        # Calculate cell size
        canvas_width = 500
        canvas_height = 500
        cell_size = min(canvas_width // len(self.current_maze[0]),
                       canvas_height // len(self.current_maze))
        
        # Draw maze
        for i, row in enumerate(self.current_maze):
            for j, cell in enumerate(row):
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                # Set color based on cell type
                color = {
                    '#': 'gray',
                    ' ': 'white',
                    '@': 'blue',
                    '$': 'brown',
                    '.': 'green',
                    '*': 'purple',
                    '+': 'cyan'
                }.get(cell, 'white')
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black')
                self.canvas.create_text((x1 + x2)/2, (y1 + y2)/2, text=cell)
                
    def update_stats(self):
        # Update statistics display
        self.stats_labels["Steps"].config(text=f"{self.current_step}/{self.stats['steps']}")
        self.stats_labels["Weight"].config(text=f"{self.stats['weight']}")
        self.stats_labels["Nodes"].config(text=f"{self.stats['nodes']}")
        self.stats_labels["Time (ms)"].config(text=f"{self.stats['time']:.2f}")
        self.stats_labels["Memory (MB)"].config(text=f"{self.stats['memory']:.2f}")
        
    def step_forward(self):
        if self.current_step < len(self.solution_path):
            move = self.solution_path[self.current_step]
            self.current_maze = self.apply_move(self.current_maze, move)
            self.current_step += 1
            self.update_display()
            self.update_stats()
            
    def step_backward(self):
        if self.current_step > 0:
            self.current_step -= 1
            # Recreate maze up to current step
            self.reset_maze()
            for i in range(self.current_step):
                move = self.solution_path[i]
                self.current_maze = self.apply_move(self.current_maze, move)
            self.update_display()
            self.update_stats()
            
    def reset_animation(self):
        self.is_playing = False
        self.play_button.config(text="▶")
        self.current_step = 0
        self.reset_maze()
        self.update_display()
        self.update_stats()
        
    def toggle_play(self):
        self.is_playing = not self.is_playing
        self.play_button.config(text="⏸" if self.is_playing else "▶")
        if self.is_playing:
            self.play_animation()
            
    def play_animation(self):
        if self.is_playing and self.current_step < len(self.solution_path):
            self.step_forward()
            self.root.after(self.animation_speed, self.play_animation)
        else:
            self.is_playing = False
            self.play_button.config(text="▶")
            
    def update_speed(self, value):
        self.animation_speed = int(float(value))
        
    def reset_maze(self):
        # Reset maze to initial state
        stone_weights, maze = read_input(f"input-{self.test_var.get()}.txt")
        self.current_maze = [list(row) for row in maze]
        
    def apply_move(self, maze, move):
        # Create a deep copy of the maze
        new_maze = copy.deepcopy(maze)
        
        # Get player position
        player_pos = None
        for i in range(len(maze)):
            for j in range(len(maze[i])):
                if maze[i][j] in ['@', '+']:
                    player_pos = (i, j)
                    break
            if player_pos:
                break
                
        # Define move directions
        directions = {
            'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1),
            'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)
        }
        
        # Apply move
        dir_y, dir_x = directions[move]
        new_y, new_x = player_pos[0] + dir_y, player_pos[1] + dir_x
        
        # Handle different move types
        if move.isupper():  # Push move
            # Calculate stone's new position
            stone_y, stone_x = new_y + dir_y, new_x + dir_x
            
            # Update stone position
            new_maze[stone_y][stone_x] = '*' if new_maze[stone_y][stone_x] == '.' else '$'
            
        # Update player position
        new_maze[player_pos[0]][player_pos[1]] = '.' if new_maze[player_pos[0]][player_pos[1]] == '+' else ' '
        new_maze[new_y][new_x] = '+' if new_maze[new_y][new_x] in ['.', '*'] else '@'
        
        return new_maze

def main():
    root = tk.Tk()
    app = SokobanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()