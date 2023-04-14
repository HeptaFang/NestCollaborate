class Battle:
    # 运行在NC端的战斗逻辑核心，负责处理整个战斗相关逻辑。
    def __init__(self):
        self.players = []
        self.enemies = []

        # 动态变量
        self.round = 0
        self.tick = 0
        self.max_tick = 0

    def main_loop(self):
        while True:
            self.enemy_action()
            self.player_action()

            self.tick -= 1
            if self.tick == 0:
                self.end_round()

            if self.end_battle():
                break

    def enemy_action(self):
        pass

    def player_action(self):
        pass

    def end_round(self):
        pass

    def calc_max_tick(self):
        pass

    def end_battle(self):
        pass
