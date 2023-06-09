import random

mask = '■'


class Rule:
    # 规则基础类，定义每种规则的必要参量
    def __init__(self, digit_num, max_digit):
        # 规则名，以及规则所作用的数字范围
        self.name = None
        self.digit_num = digit_num
        self.max_digit = max_digit

    def get_random(self):
        # 随机将自身进行初始化
        raise NotImplementedError()

    def generate_from(self, num):
        # 生成一个让num符合的规则实例
        raise NotImplementedError()

    def judge(self, num):
        # 输入num，判断是否符合此规则
        raise NotImplementedError()

    def description(self, *args, **kwargs):
        # 规则的文本化说明
        raise NotImplementedError()

    def detail(self, *args, **kwargs):
        # 在有blur参数时，给出所有可能的规则。
        raise NotImplementedError()


class SingleCompare(Rule):
    def __init__(self, digit_num, max_digit, item1=None, item2=None, operator=None):
        """
        item1（小于/等于/大于）item2。
        item:1-5,或-1, -2, -3代表下标123
        operator:-1:小于，0:等于，1:大于
        """
        super().__init__(digit_num, max_digit)
        self.name = 'SingleCompare'

        # 每种情况出现的概率
        self.weight = [2, 1, 2]

        self.item1 = item1
        self.operator = operator
        self.item2 = item2

        self.blur = [False, False, False]

    def get_random(self):
        self.item1 = -random.randint(1, self.digit_num)
        if random.randint(0, 1) == 0:
            self.item2 = self.item1 + random.randint(1, self.digit_num - 1)
            if self.item2 >= 0:
                self.item2 -= self.digit_num
        else:
            self.item2 = random.randint(1, self.max_digit)
        self.operator = random.choices((-1, 0, 1), weights=self.weight)[0]

    def generate_from(self, num):
        raise NotImplementedError()

    def judge(self, num):
        digit1 = num[-self.item1 - 1]
        digit2 = self.item2
        if self.item2 < 0:
            digit2 = num[-self.item2 - 1]
        return (digit1 < digit2 and self.operator == -1) or \
               (digit1 == digit2 and self.operator == 0) or \
               (digit1 > digit2 and self.operator == 1)

    def description(self):
        item1_str = -self.item1
        operator_str = ['小', '等', '大'][self.operator + 1]
        if self.item2 > 0:
            item2_str = self.item2
        else:
            item2_str = -self.item2

        if self.blur[0]:
            item1_str = mask
        if self.blur[1]:
            operator_str = mask
        if self.blur[2]:
            item2_str = mask

        if self.item2 > 0:
            return f'第{item1_str}位{operator_str}于{item2_str}'
        else:
            return f'第{item1_str}位{operator_str}第{item2_str}位'

    def detail(self):
        all_possible = []
        if self.item2 > 0:
            possible_choice = [list(range(1, self.digit_num + 1)),
                               ['小', '等', '大'],
                               list(range(1, self.max_digit + 1))]
        else:
            possible_choice = [list(range(1, self.digit_num + 1)),
                               ['小', '等', '大'],
                               list(range(1, self.digit_num + 1))]

        possible_num = 1
        for i in range(len(self.blur)):
            if self.blur[i]:
                possible_num *= len(possible_choice[i])

        item_str = [-self.item1, ['小', '等', '大'][self.operator + 1], 0]
        if self.item2 > 0:
            item_str[2] = self.item2
        else:
            item_str[2] = -self.item2

        for i in range(possible_num):
            a = i
            for j in range(len(self.blur)):
                if self.blur[j]:
                    item_str[j] = possible_choice[j][a % len(possible_choice[j])]
                    a = a // len(possible_choice[j])

            if self.item2 > 0:
                all_possible.append(f'第{item_str[0]}位{item_str[1]}于{item_str[2]}')
            else:
                all_possible.append(f'第{item_str[0]}位{item_str[1]}第{item_str[2]}位')

        info_str = '所有可能的规则：'
        for info in all_possible:
            info_str += '\n' + info

        return info_str

    def random_blur(self):
        blur_idx = 1
        if random.random() < 0.2:
            blur_idx = 2 * random.randint(0, 1)
        self.blur[blur_idx] = True


class SingleJudge(Rule):
    def __init__(self, digit_num, max_digit, idx=None, judge_type=None):
        """
        检测第idx位数字是否满足某要求：
        judge_type:
        0:偶数, 1:奇数, 2:最小值, 3:最大值, 4:并列最小值, 5:并列最大值
        """
        super().__init__(digit_num, max_digit)
        self.idx = idx
        self.judge_type = judge_type

        self.blur = [False]

    def get_random(self):
        self.idx = random.randint(0, self.digit_num - 1)
        self.judge_type = random.randint(0, 5)

    def generate_from(self, num):
        raise NotImplementedError()

    def judge(self, num):
        flag = True
        if self.judge_type in (0, 1):
            return num[self.idx] % 2 == self.judge_type
        elif self.judge_type == 2:
            for i in range(len(num)):
                if i != self.idx and num[self.idx] >= num[i]:
                    flag = False
        elif self.judge_type == 3:
            for i in range(len(num)):
                if i != self.idx and num[self.idx] <= num[i]:
                    flag = False
        elif self.judge_type == 4:
            for i in range(len(num)):
                if i != self.idx and num[self.idx] > num[i]:
                    flag = False
        elif self.judge_type == 5:
            for i in range(len(num)):
                if i != self.idx and num[self.idx] < num[i]:
                    flag = False
        return flag

    def description(self):
        idx_str = self.idx + 1
        judge_str = ['偶数', '奇数', '唯一最小值', '唯一最大值', '最小值或并列最小值', '最大值或并列最大值'][self.judge_type]

        if self.blur[0]:
            idx_str = mask
        return f'第{idx_str}位为{judge_str}'

    def detail(self):
        all_possible = []
        possible_choice = [list(range(1, self.digit_num + 1))]

        possible_num = 1
        for i in range(len(self.blur)):
            if self.blur[i]:
                possible_num *= len(possible_choice[i])

        item_str = [self.idx + 1, ['偶数', '奇数', '唯一最小值', '唯一最大值', '最小值或并列最小值', '最大值或并列最大值'][self.judge_type]]

        for i in range(possible_num):
            a = i
            for j in range(len(self.blur)):
                if self.blur[j]:
                    item_str[j] = possible_choice[j][a % len(possible_choice[j])]
                    a = a // len(possible_choice[j])

            all_possible.append(f'第{item_str[0]}位为{item_str[1]}')

        info_str = '所有可能的规则：'
        for info in all_possible:
            info_str += '\n' + info

        return info_str

    def random_blur(self):
        self.blur[0] = True


class PlusJudge(Rule):
    def __init__(self, digit_num, max_digit, idx1=None, idx2=None, judge_type=None):
        """
        检测某两位数字之和是否满足某要求：
        judge_type:
        0:偶数, 1:奇数, 2:大于最大值+1, 3:等于最大值+1, 4:大于最大值+1
        """
        super().__init__(digit_num, max_digit)
        self.idx1 = idx1
        self.idx2 = idx2
        self.judge_type = judge_type

        self.blur = [False, False, False]

    def get_random(self):
        raise NotImplementedError()

    def generate_from(self, num):
        raise NotImplementedError()

    def judge(self, num):
        s = num[self.idx1] + num[self.idx2]
        if self.judge_type == 0:
            return s % 2 == 0
        elif self.judge_type == 1:
            return s % 2 == 1
        elif self.judge_type == 2:
            return s < self.max_digit + 1
        elif self.judge_type == 3:
            return s == self.max_digit + 1
        elif self.judge_type == 4:
            return s > self.max_digit + 1

    def description(self, *args, **kwargs):
        str_idx1 = self.idx1
        str_idx2 = self.idx2
        str_type = ['偶', '奇', '小', '等', '大'][self.judge_type]

        if self.blur[0]:
            str_idx1 = mask
        if self.blur[1]:
            str_idx2 = mask
        if self.blur[2]:
            str_type = mask

        if self.judge_type in [0, 1]:
            return f'第{str_idx1}位和第{str_idx2}位之和为{str_type}数'
        elif self.judge_type in [2, 3, 4]:
            return f'第{str_idx1}位和第{str_idx2}位之和{str_type}于{self.max_digit + 1}'

    def detail(self, *args, **kwargs):
        raise NotImplementedError()


class SumJudge(Rule):
    def __init__(self, digit_num, max_digit, judge_type=None):
        """
        检测所有数字之和是否满足某要求：
        judge_type:
        0:偶数, 1:奇数, 2:3的倍数, 3:4的倍数, 4:5的倍数
        """
        super().__init__(digit_num, max_digit)
        self.judge_type = judge_type

        self.blur = [False]

    def get_random(self):
        raise NotImplementedError()

    def generate_from(self, num):
        raise NotImplementedError()

    def judge(self, num):
        s = 0
        for digit in num:
            s += digit

        if self.judge_type == 0:
            return s % 2 == 0
        elif self.judge_type == 1:
            return s % 2 == 1
        elif self.judge_type == 2:
            return s % 3 == 0
        elif self.judge_type == 3:
            return s % 4 == 0
        elif self.judge_type == 4:
            return s % 5 == 0

    def description(self, *args, **kwargs):
        str_type = ['偶', '奇', '3', '4', '5'][self.judge_type]

        if self.blur[0]:
            str_type = mask

        if self.judge_type in [0, 1]:
            return f'所有数字之和为{str_type}数'
        elif self.judge_type in [2, 3, 4]:
            return f'所有数字之和为{str_type}的倍数'

    def detail(self, *args, **kwargs):
        raise NotImplementedError()


class StructureJudge(Rule):
    def __init__(self, digit_num, max_digit, judge_type_major=None, judge_type_minor=None):
        """
        检测数字结构是否满足某要求：
        judge_type:
        0: 单调性 [0: 升序, 1: 降序, 2: 无序]
        1: 重复数字最多出现 [i次]
        2: 最长连续数字长度为 [i位]
        """
        super().__init__(digit_num, max_digit)
        self.judge_type_major = judge_type_major
        self.judge_type_minor = judge_type_minor

        self.blur = [False]

    def get_random(self):
        raise NotImplementedError()

    def generate_from(self, num):
        raise NotImplementedError()

    def judge(self, num):
        if self.judge_type_major == 0:
            order_state = -1
            for i in range(1, self.digit_num):
                if num[i] > num[i - 1]:
                    if order_state in [1, 2]:
                        order_state = 2
                    else:
                        order_state = 0
                elif num[i] < num[i - 1]:
                    if order_state in [0, 2]:
                        order_state = 2
                    else:
                        order_state = 1
                else:
                    order_state = 2
            return order_state == self.judge_type_minor

        elif self.judge_type_major == 1:
            digit_count = [0] * self.digit_num
            for digit in num:
                digit_count[digit - 1] += 1
            max_count = max(digit_count)
            return max_count == self.judge_type_minor

        elif self.judge_type_major == 2:
            max_len = 1
            current_len = 1
            current_direction = 'none'
            for i in range(1, self.digit_num):
                if num[i] == num[i - 1] + 1:
                    if current_direction == 'up':
                        current_len += 1
                    else:
                        current_direction = 'up'
                        current_len = 2
                elif num[i] == num[i - 1] - 1:
                    if current_direction == 'down':
                        current_len += 1
                    else:
                        current_direction = 'down'
                        current_len = 2
                else:
                    current_len = 1
                    current_direction = 'none'
                if current_len > max_len:
                    max_len = current_len
            return max_len == self.judge_type_minor

    def description(self, *args, **kwargs):
        if self.judge_type_major == 0:
            str_type = ['升', '降', '无'][self.judge_type_minor]
            if self.blur[0]:
                str_type = mask
            return f'数字序列为{str_type}序'

        elif self.judge_type_major == 1:
            str_type = self.judge_type_minor
            if self.blur[0]:
                str_type = mask
            return f'重复数字最多出现{str_type}次'

        elif self.judge_type_major == 2:
            str_type = self.judge_type_minor
            if self.blur[0]:
                str_type = mask
            return f'最长连续序列长度为{str_type}'

    def detail(self, *args, **kwargs):
        raise NotImplementedError()


class Counting(Rule):
    def __init__(self, digit_num, max_digit, digit=None, count=None):
        """
        检测数字digit是否出现了count次：
        """
        super().__init__(digit_num, max_digit)
        self.digit = digit
        self.count = count

        self.blur = [False]

    def get_random(self):
        raise NotImplementedError()

    def generate_from(self, num):
        raise NotImplementedError()

    def judge(self, num):
        count = 0
        for digit in num:
            if digit == self.digit:
                count += 1
        return count == self.count

    def description(self, *args, **kwargs):
        str_digit = self.digit
        str_count = self.count

        if self.blur[0]:
            str_digit = mask
        if self.blur[1]:
            str_count = mask

        return f'数字{str_digit}出现了{str_count}次'

    def detail(self, *args, **kwargs):
        raise NotImplementedError()


# 用一个list包装所有的rule对象
AllRules = [SingleCompare, SingleJudge]
