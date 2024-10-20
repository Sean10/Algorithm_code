import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def initialize_grid(size):
    return np.random.choice([0, 1], size * size, p=[0.85, 0.15]).reshape(size, size)

def update(frame_num, img, grid, size):
    new_grid = grid.copy()
    for i in range(size):
        for j in range(size):
            total = int((grid[i, (j-1)%size] + grid[i, (j+1)%size] + 
                         grid[(i-1)%size, j] + grid[(i+1)%size, j] + 
                         grid[(i-1)%size, (j-1)%size] + grid[(i-1)%size, (j+1)%size] + 
                         grid[(i+1)%size, (j-1)%size] + grid[(i+1)%size, (j+1)%size]))
            if grid[i, j] == 1:
                if (total < 2) or (total > 3):
                    new_grid[i, j] = 0
            else:
                if total == 3:
                    new_grid[i, j] = 1
    
    img.set_data(new_grid)
    grid[:] = new_grid[:]
    return img,

def main():
    size = 50
    grid = initialize_grid(size)
    
    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    ani = FuncAnimation(fig, update, fargs=(img, grid, size),
                        frames=200, interval=50, save_count=50)
    
    plt.show()

if __name__ == '__main__':
    main()
