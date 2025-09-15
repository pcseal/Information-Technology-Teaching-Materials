from flask import Flask, render_template, jsonify, redirect, url_for
import random
import matplotlib.pyplot as plt
import os
import time
import glob
import copy

app = Flask(__name__)

# 全局保存迷宫和路径
maze = []
path = []

def generate_maze(width=15, height=15):
    """用DFS生成迷宫，并加外边框"""
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def dfs(x, y):
        maze[y][x] = 0
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                dfs(nx, ny)

    dfs(1, 1)  # 从 (1,1) 开始，不破坏外框

    # 确保外框全是墙
    for x in range(width):
        maze[0][x] = 1
        maze[height-1][x] = 1
    for y in range(height):
        maze[y][0] = 1
        maze[y][width-1] = 1

    # 留入口出口
    maze[1][0] = 0          # 左边入口
    maze[height-2][width-1] = 0  # 右边出口

    return maze

def maze_path(x1, y1, x2, y2):
    maze_copy = copy.deepcopy(maze)
    dirs = [[0, 1], [0, -1], [1, 0], [-1, 0]]
    path = [0] * 1000
    top = -1
    snapshots = []  # 用于保存每一步的图片路径

    top += 1
    path[top] = [x1, y1]
    maze_copy[x1][y1] = 2
    
    # 初始路径图片
    snapshots.append(draw_maze(maze, path[:top+1]))

    while top != -1:
        now_x, now_y = path[top]

        if now_x == x2 and now_y == y2:
            path = path[:top+1]
            snapshots.append(draw_maze(maze, path))  # 最后一帧
            print('已求解')
            return path, snapshots

        for d in dirs:
            new_x, new_y = now_x + d[0], now_y + d[1]
            if maze_copy[new_x][new_y] == 0:
                top += 1
                path[top] = [new_x, new_y]
                maze_copy[new_x][new_y] = 2
                snapshots.append(draw_maze(maze, path[:top+1]))  # 保存每一步的图片路径
                print('已生成路径图片',path[top])
                break
        else:
            top -= 1 # 回退 
            snapshots.append(draw_maze(maze, path[:top+1]))

    return path, snapshots

def draw_maze(maze, path=None):
    
    # 新文件名（毫秒级时间戳）
    filename = f"maze_{int(time.time()*1000)}.png"
    filepath = os.path.join("static", filename)

    # 绘制
    plt.figure(figsize=(6, 6))
    plt.imshow(maze, cmap="gray_r", origin="upper", interpolation="nearest")

    if path:
        # 把 [x,y] 转换成 (x,y)
        path = [tuple(p) for p in path]
        px, py = zip(*[(p[1], p[0]) for p in path])

        # 绘制路径
        plt.plot(px, py, color="red", linewidth=2, marker="o", markersize=4)

        # 起点绿色
        plt.plot(px[0], py[0], "go", markersize=8)
        # 终点蓝色
        plt.plot(px[-1], py[-1], "bo", markersize=8)

    plt.axis("off")
    plt.savefig(filepath, bbox_inches="tight")
    plt.close()

    print(f"Generated image: {filepath}")  # Debugging log

    return filename

@app.route("/")
def index():
    return render_template("index1.html")

@app.route("/generate")
def generate():
    global maze, path
     # 清理旧图片（这里只清理旧的路径图像，不删除当前生成的迷宫图像）
    for f in glob.glob("static/maze_*.png"):
        try:
            # 我们不清除刚刚生成的图片，这里增加了判断条件
            if "maze" in f:  # 清理掉所有以 "maze_" 开头的旧图像文件
                os.remove(f)
        except Exception as e:
            print(f"Error removing file: {e}")
    maze = generate_maze(21, 21)
    path = []
    filename = draw_maze(maze, None)
    return render_template("index1.html", filename=filename)
    

@app.route("/solve", methods=["GET", "POST"])
def solve():
    global maze, path
     # 清理旧图片（这里只清理旧的路径图像，不删除当前生成的迷宫图像）
    for f in glob.glob("static/maze_*.png"):
        try:
            # 我们不清除刚刚生成的图片，这里增加了判断条件
            if "maze" in f:  # 清理掉所有以 "maze_" 开头的旧图像文件
                os.remove(f)
        except Exception as e:
            print(f"Error removing file: {e}")
    if maze:
        h, w = len(maze), len(maze[0])  # 迷宫的高度和宽度
        # 入口在左边 (1,0)
        # 出口在右边 (h-2, w-1)
        path, snapshots = maze_path(1, 0, h-2, w-1)
        return jsonify({"snapshots": snapshots})  # 返回每一步的图片路径
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run()
