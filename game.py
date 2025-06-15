import pygame
import sys
import win32gui
import win32con
import win32api
import math


class StickMan:
    def __init__(self, x, y, size=40):
        self.x = x
        self.y = y
        self.size = size
        self.direction = 1  # 1 for right, -1 for left
        self.speed = 2
        self.step = 0
        self.max_step = 10

    def update(self):
        # 移动火柴人
        self.x += self.speed * self.direction

        # 更新动画步长
        self.step = (self.step + 1) % self.max_step

        # 边界检测，到达边界时改变方向
        if self.x > 200 - self.size // 2:
            self.direction = -1
        elif self.x < self.size // 2:
            self.direction = 1

    def draw(self, surface):
        # 计算身体各部分的位置
        head_radius = self.size // 6
        body_length = self.size // 2
        leg_length = self.size // 3
        arm_length = self.size // 3

        # 头部
        pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y - body_length - head_radius), head_radius)

        # 身体
        pygame.draw.line(surface, (255, 255, 255),
                         (self.x, self.y - body_length),
                         (self.x, self.y), 2)

        # 腿部动画
        leg_angle = math.sin(self.step * 0.3) * 0.5

        # 左腿
        pygame.draw.line(surface, (255, 255, 255),
                         (self.x, self.y),
                         (self.x - math.sin(leg_angle) * leg_length,
                          self.y + math.cos(leg_angle) * leg_length), 2)

        # 右腿
        pygame.draw.line(surface, (255, 255, 255),
                         (self.x, self.y),
                         (self.x + math.sin(leg_angle + math.pi) * leg_length,
                          self.y + math.cos(leg_angle + math.pi) * leg_length), 2)

        # 手臂动画
        arm_angle = math.sin(self.step * 0.3 + math.pi) * 0.5

        # 左臂
        pygame.draw.line(surface, (255, 255, 255),
                         (self.x, self.y - body_length // 2),
                         (self.x - math.sin(arm_angle) * arm_length,
                          self.y - body_length // 2 + math.cos(arm_angle) * arm_length), 2)

        # 右臂
        pygame.draw.line(surface, (255, 255, 255),
                         (self.x, self.y - body_length // 2),
                         (self.x + math.sin(arm_angle + math.pi) * arm_length,
                          self.y - body_length // 2 + math.cos(arm_angle + math.pi) * arm_length), 2)


class Widget:
    def __init__(self, width=300, height=100, title="火柴人小组件", transparent=True):
        # 初始化Pygame
        pygame.init()

        # 设置窗口
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        pygame.display.set_caption(title)

        # 获取窗口句柄并设置属性
        hwnd = pygame.display.get_wm_info()["window"]

        # 设置窗口置顶
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        # 设置透明背景
        if transparent:
            # 设置窗口透明
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
            # 设置透明颜色 (这里使用黑色作为透明色)
            win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(0, 0, 0), 0, win32con.LWA_COLORKEY)

        # 窗口移动相关变量
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        # 创建火柴人对象，位于屏幕底部中间
        self.stick_man = StickMan(width // 2, height - 10)

        # 主循环控制变量
        self.running = True

        # 时钟对象，控制帧率
        self.clock = pygame.time.Clock()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.dragging = True
                    self.offset_x = event.pos[0]
                    self.offset_y = event.pos[1]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 左键释放
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    hwnd = pygame.display.get_wm_info()["window"]
                    x, y = win32gui.GetCursorPos()
                    win32gui.SetWindowPos(hwnd, None,
                                          x - self.offset_x,
                                          y - self.offset_y,
                                          0, 0,
                                          win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        # 更新火柴人状态
        self.stick_man.update()

    def render(self):
        # 清空屏幕（使用黑色作为透明色）
        self.screen.fill((0, 0, 0))

        # 绘制火柴人
        self.stick_man.draw(self.screen)

        # 绘制底部横线作为地面
        pygame.draw.line(self.screen, (255, 255, 255), (0, self.height - 5), (self.width, self.height - 5), 2)

        # 更新显示
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(30)  # 限制帧率为30FPS

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    widget = Widget(width=300, height=100, title="火柴人小组件")
    widget.run()
