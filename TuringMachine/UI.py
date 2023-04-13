from tkinter import *
from tkinter import ttk
from functools import partial
from game import Logic


class TuringUI(Frame):
    def __init__(self, master, root, digit_num=3, max_digit=5):
        super().__init__(master)

        # 基础窗体结构
        self.game_panel = Frame(self)
        self.place(relx=0, rely=0, relheight=1, relwidth=1)
        self.game_panel.place(relx=0.05, rely=0.025, relheight=0.6, relwidth=0.5)
        self.history_panel = Frame(self, highlightbackground="gray", highlightthickness=2)
        self.history_panel.place(relx=0.05, rely=0.675, relheight=0.3, relwidth=0.9)
        self.root = root

        # 基础规则参数
        self.digit_num = digit_num
        self.max_digit = max_digit

        # 初始化逻辑内核
        self.logic = Logic(self.digit_num, self.max_digit)
        self.num = None
        self.rules = []

        # 状态变量
        self.current_digit = [1] * self.digit_num
        self.rule_selection = [False] * 6
        self.validated = [0] * 6
        self.validate_timer = 0
        self.last_click = None
        self.validate_history = []
        self.history_labels = []

        # 大部分的ui对象在此函数内定义
        self.create_widgets()

        # 0: 选单, 1: 主游戏, 2: 教程
        self.display_mode = 0

        self.new_game()

        self.update_display()

    def create_widgets(self):
        # ---选单部分---
        self.menu_frame = Frame()

        # ---主游戏部分---
        # 数字显示和切换数字的箭头
        self.game_components = []
        self.digit_labels = []
        self.digit_arrows = [[] for _ in range(self.digit_num)]
        for i in range(self.digit_num):
            digit_label = Label(self.game_panel, text=self.current_digit[i], height=1, width=2, relief='sunken',
                                font=('黑体', 24))
            digit_label.place(relx=0.1 + (0.8 / self.digit_num) * (i + 0.5), rely=0.1, anchor=CENTER)
            self.digit_labels.append(digit_label)
            self.game_components.append(digit_label)
            for arrow in [1, -1]:
                arrow_text = ''
                if arrow == -1:
                    arrow_text = '-'
                else:
                    arrow_text = '+'
                digit_arrow = Button(self.game_panel, text=arrow_text, height=1, width=1, font=('黑体', 10),
                                     command=partial(self.change_digit, i, arrow))
                digit_arrow.place(relx=0.1 + (0.8 / self.digit_num) * (i + 0.5) + arrow * 0.08, rely=0.1,
                                  anchor=CENTER)
                self.digit_arrows[i].append(digit_arrow)
                self.game_components.append(digit_arrow)

        # 规则显示区
        self.rule_boxes = []
        self.rule_checks = []
        self.rule_check_var = [BooleanVar() for _ in range(6)]
        self.rule_feedbacks = []
        for i in range(6):
            rule_box = Label(self.game_panel, text='', height=1, width=30, relief='ridge', font=('微软雅黑', 14))
            rule_box.place(relx=0.5, rely=0.2 + 0.1 * (i + 0.5), anchor=CENTER)
            rule_box.bind("<Button-1>", partial(self.change_rule_selection, i))
            self.rule_boxes.append(rule_box)
            self.game_components.append(rule_box)
            # rule_feedback = Label(self, text='', height=3, width=50, relief='ridge')
            # rule_feedback.place(relx=0.8, rely=0.2 + 0.08 * (i + 0.5), anchor=CENTER)
            # self.rule_feedbacks.append(rule_feedback)

        # 检查按钮和信息区
        self.check_button = Button(self.game_panel, text='提交验证', height=1, width=10, font=('黑体', 18),
                                   command=self.validate_answer)
        self.check_button.place(relx=0.25, rely=0.9, anchor=CENTER)
        self.submit_button = Button(self.game_panel, text='确认结果', height=1, width=10, font=('黑体', 18),
                                    command=self.check_answer)
        self.submit_button.place(relx=0.75, rely=0.9, anchor=CENTER)
        self.info_box = Text(self, state=DISABLED, height=18, width=30, relief='ridge', font=('微软雅黑', 12))
        self.info_box.place(relx=0.75, rely=0.35, anchor=CENTER)

        self.game_components.append(self.check_button)
        self.game_components.append(self.submit_button)
        self.game_components.append(self.info_box)

    def update_display(self):
        # 主更新函数，每50ms进行一次更新
        # 数字显示
        for i in range(self.digit_num):
            self.digit_labels[i]['text'] = self.current_digit[i]

        # 规则显示
        for i in range(len(self.rules)):
            self.rule_boxes[i]['text'] = self.rules[i].description()
            # 这部分是validation时的动态颜色变化逻辑
            if self.validated[i] == 1:
                self.rule_boxes[i]['bg'] = '#%02x%02x%02x' % (
                    200 - int(128 * self.validate_timer / 60), 240, 200 - int(128 * self.validate_timer / 60))
            elif self.validated[i] == -1:
                self.rule_boxes[i]['bg'] = '#%02x%02x%02x' % (
                    240, 200 - int(128 * self.validate_timer / 60), 200 - int(128 * self.validate_timer / 60))
            else:
                self.rule_boxes[i]['bg'] = '#%02x%02x%02x' % (240, 240, 240)

            # 规则被选中时的边框加粗特效
            if self.rule_selection[i]:
                self.rule_boxes[i]['borderwidth'] = 5
            else:
                self.rule_boxes[i]['borderwidth'] = 2

        # 信息框内容更新
        self.info_box.config(state=NORMAL)
        self.info_box.delete(0.0, END)
        self.info_box.insert(0.0, self.get_info())
        self.info_box.config(state=DISABLED)

        if self.validate_timer > 0:
            self.validate_timer -= 1

        self.root.update()
        self.after(50, self.update_display)

    def clear_history_display(self):
        # 历史验证记录中的label实例销毁
        for label in self.history_labels:
            label.destroy()

    def clear_history(self):
        # 清空历史验证记录
        self.clear_history_display()
        self.validate_history = []
        self.history_labels = []
        self.update_history()

    def update_history(self):
        # 主窗口下方的历史验证记录显示，仅在每次进行validation时才调用
        self.clear_history_display()
        for i in range(len(self.validate_history)):
            num_str = ''
            num, validation = self.validate_history[i]
            for n in num:
                num_str += str(n)
            num_label = Label(self.history_panel, text=num_str, height=1, width=4, relief='groove')
            num_label.place(relx=0.05 + 0.05 * i, rely=0.11, anchor=CENTER)
            self.history_labels.append(num_label)

            color_map = {None: '#F0F0F0',
                         True: '#E0FFE0',
                         False: '#FFE0E0'}

            for j in range(len(self.rules)):
                validation_label = Label(self.history_panel, text='', height=1, width=4, relief='groove',
                                         bg=color_map[validation[j]])
                validation_label.place(relx=0.05 + 0.05 * i, rely=0.27 + 0.12 * j, anchor=CENTER)
                self.history_labels.append(validation_label)

        self.root.update()

    def change_digit(self, idx, delta):
        # 改变当前选中数字的回调函数，绑定到数字显示区的上下箭头
        self.current_digit[idx] += delta
        if self.current_digit[idx] == 0:
            self.current_digit[idx] = self.max_digit
        if self.current_digit[idx] == self.max_digit + 1:
            self.current_digit[idx] = 1
        self.reset_validation()

    def change_rule_selection(self, idx, e):
        # 改变规则选中状态的回调函数，绑定到规则框的被点击事件
        if idx >= len(self.rules):
            return
        self.last_click = idx
        count = 0
        for i in range(len(self.rules)):
            count += self.rule_selection[i]
        if count >= 3 and not self.rule_selection[idx]:
            return
        self.rule_selection[idx] = not self.rule_selection[idx]

    def new_game(self):
        # 生成一局新游戏
        self.num, self.rules = self.logic.pick_rules()
        for i in range(6):
            self.rule_boxes[i]['text'] = ''
            self.rule_boxes[i]['bg'] = '#%02x%02x%02x' % (240, 240, 240)
            self.rule_boxes[i]['borderwidth'] = 2

        self.current_digit = [1] * self.digit_num
        self.rule_selection = [False] * len(self.rules)
        self.validated = [0] * len(self.rules)
        self.validate_timer = 0
        self.last_click = None
        self.clear_history()

    def check_answer(self):
        # 确认当前显示的数字是否正确
        correct = True
        for i in range(self.digit_num):
            if self.num[i] != self.current_digit[i]:
                correct = False
        # self.info_box['text'] = f'{correct}, {self.num}'
        self.new_game()

    def validate_answer(self):
        # 验证当前显示的数字是否符合当前被选中的若干条规则
        validation = [None] * len(self.rules)
        for i in range(len(self.rules)):
            rule = self.rules[i]
            judge = rule.judge(self.current_digit)
            if self.rule_selection[i]:
                validation[i] = judge
                if judge:
                    self.validated[i] = 1
                else:
                    self.validated[i] = -1
            else:
                self.validated[i] = 0
        self.validate_history.append([[d for d in self.current_digit], validation])
        self.update_history()
        self.validate_timer = 60

    def get_info(self):
        # 信息显示，现在是用来显示最后一次点击的规则有几种可能变体
        if self.last_click is None:
            return ''
        else:
            return self.rules[self.last_click].detail()

    def reset_validation(self):
        # 生成新游戏时的复位函数
        for i in range(len(self.validated)):
            self.validated[i] = 0


def main():
    root = Tk()
    root.title("Turing Machine")
    root.geometry("800x600")
    root.resizable(False, False)
    app = TuringUI(root, root, 3, 5)
    root.mainloop()


if __name__ == '__main__':
    main()
