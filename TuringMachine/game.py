import random

from rule import AllRules


class Logic:
    def __init__(self, digit_num, max_digit, n_rules=None, max_group_size=10, min_group_size=3):
        self.digit_num = digit_num
        self.max_digit = max_digit
        self.n_rules = n_rules
        self.max_group_size = max_group_size
        self.min_group_size = min_group_size

        self.all_nums = []
        self.generate_all_nums()
        self.total_nums = len(self.all_nums)

        self.rules = []

    def generate_all_nums(self):
        for i in range(self.max_digit ** self.digit_num):
            num_idx = i
            current_num = []
            for j in range(self.digit_num):
                current_num.append(num_idx % self.max_digit + 1)
                num_idx = num_idx // self.max_digit
            self.all_nums.append(tuple(current_num))

    def pick_rules(self, num=None, blur=True):
        if num is None:
            num = random.choice(self.all_nums)
        rules = []
        while True:
            rule = self.get_random_rule()
            if not rule.judge(num):
                continue
            rules.append(rule)
            passed = self.check_unique(rules)
            if len(passed) == 1:
                break

        while True:
            redundant = self.check_redundant(rules)
            if redundant is None:
                break
            rules.pop(redundant)

        if blur:
            for rule in rules:
                rule.random_blur()

        self.rules = rules

        return num, rules

    def check_unique(self, rules):
        # 检查唯一性
        passed = []
        for num in self.all_nums:
            pass_flag = True
            for rule in rules:
                if not rule.judge(num):
                    pass_flag = False
                    break
            if pass_flag:
                passed.append(num)

        return passed

    def check_redundant(self, rules):
        for i in range(len(rules)):
            rest_rules = rules[:i] + rules[i + 1:]
            passed = self.check_unique(rest_rules)
            if len(passed) == 1:
                return i

    def get_random_rule(self):
        rule = random.choice(AllRules)(self.digit_num, self.max_digit)
        rule.get_random()
        return rule


class Game:
    def __init__(self, digit_num, max_digit, n_rules=None):
        self.digit_num = digit_num
        self.max_digit = max_digit
        self.n_rules = n_rules
        self.logic = Logic(digit_num, max_digit, n_rules)


def main():
    logic = Logic(3, 5)
    logic.pick_rules()
    for rule in logic.rules:
        print(rule.description())


if __name__ == '__main__':
    main()
