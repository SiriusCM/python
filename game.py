import pygame
import sys
import win32gui
import win32con
import win32api

# 初始化 Pygame
pygame.init()

# ------------------ 配置参数 ------------------
WINDOW_WIDTH = 800  # 窗口宽度
WINDOW_HEIGHT = 600  # 窗口高度
SPRITE_SHEET_PATH = "R-C.png"  # 精灵表路径
FPS = 15  # 播放帧率


# ------------------ 工具函数 ------------------
def create_transparent_window(width, height, title="Sprite Widget"):
    """创建透明、置顶、可拖动的窗口"""
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    pygame.display.set_caption(title)

    hwnd = pygame.display.get_wm_info()["window"]

    # 设置窗口置顶
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                          win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    # 设置透明（黑色为透明色）
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

    return screen, hwnd


def load_sprite_sheet(path, frame_width=80, frame_height=80):
    """加载精灵表并按行分割为不同动作"""
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"无法加载精灵表: {e}")
        sys.exit(1)

    sheet_width, sheet_height = sheet.get_width(), sheet.get_height()
    rows = sheet_height // frame_height
    cols = sheet_width // frame_width

    print(f"精灵表尺寸: {sheet_width}x{sheet_height}")
    print(f"每帧尺寸: {frame_width}x{frame_height}")
    print(f"可容纳帧数: {rows}行 x {cols}列")

    # 假设第一行为向右移动，第二行为向左移动
    animations = {
        'right': [],
        'left': []
    }

    for row in range(rows):
        direction = 'right' if row == 0 else 'left'
        for col in range(cols):
            x = col * frame_width
            y = row * frame_height
            if x + frame_width <= sheet_width and y + frame_height <= sheet_height:
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                animations[direction].append(frame)
            else:
                print(f"警告: 忽略超出边界的帧: ({x}, {y})")

    return animations


# ------------------ 角色类 ------------------
class Character:
    def __init__(self, animations, x, y, speed=5):
        self.animations = animations
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = 'right'  # 初始方向
        self.current_frame = 0
        self.frame_count = len(animations['right'])
        self.animation_speed = 0.2  # 动画播放速度
        self.frame_timer = 0

    def update(self, screen_width):
        # 移动角色
        if self.direction == 'right':
            self.x += self.speed
            if self.x > screen_width:  # 到达右边界，转向左
                self.x = screen_width
                self.direction = 'left'
        else:  # 向左移动
            self.x -= self.speed
            if self.x < 0:  # 到达左边界，转向右
                self.x = 0
                self.direction = 'right'

        # 更新动画帧
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.frame_timer = 0

    def draw(self, surface):
        current_animation = self.animations[self.direction]
        current_frame = current_animation[self.current_frame]
        # 绘制在屏幕最下方
        surface.blit(current_frame, (
            self.x - current_frame.get_width() // 2,
            self.y - current_frame.get_height()
        ))


# ------------------ 主逻辑 ------------------
def main():
    screen, hwnd = create_transparent_window(WINDOW_WIDTH, WINDOW_HEIGHT)

    # 加载精灵表（默认帧大小80x80）
    animations = load_sprite_sheet(SPRITE_SHEET_PATH)

    # 创建角色（放在屏幕底部中央）
    character = Character(
        animations=animations,
        x=WINDOW_WIDTH // 2,
        y=WINDOW_HEIGHT,  # 底部位置
        speed=3
    )

    clock = pygame.time.Clock()
    dragging = False
    offset_x, offset_y = 0, 0

    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    offset_x = event.pos[0]
                    offset_y = event.pos[1]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    x, y = win32gui.GetCursorPos()
                    win32gui.SetWindowPos(hwnd, None,
                                          x - offset_x, y - offset_y,
                                          0, 0,
                                          win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 更新角色
        character.update(WINDOW_WIDTH)

        # 绘制
        screen.fill((0, 0, 0))  # 填充黑色（透明色）
        character.draw(screen)  # 绘制角色

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()