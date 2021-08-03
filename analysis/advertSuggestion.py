import json
import random as r
import collections
import ast


class Suggestion:
    def __init__(self, local=1):
        if local == 1:
            a = open('advert_data.json', 'r')
        else:
            a = open('analysis/advert_data.json', 'r')
        self.data = json.load(a)
        a.close()
        self.total = {'male': {'cat': {}, 'subcat': {}}, 'female': {'cat': {}, 'subcat': {} }}
        self.image_base = 'static/bank_image'
        self.cal_total()

    def cal_total(self):
        for i in ['male', 'female']:
            for j in ['cat', 'subcat']:
                for k in self.data[i][j]:
                    self.total[i][j][k] = sum(list(self.data[i][j][k].values()))

    def initialize(self, age, gender):
        cat_dict = self.data[gender]['cat'][age]
        sub_dict = self.data[gender]['subcat'][age]

        total = self.total[gender]['cat'][age]
        sub_total = self.total[gender]['subcat'][age]

        return cat_dict, sub_dict, total, sub_total

    @staticmethod
    def format_age(age):
        age = ast.literal_eval(age)
        return f'{age[0]}-{age[1]}'

    def suggest_top(self, age, gender):
        if age not in ['(15, 24)', '(25, 37)', '(38, 47)']:
            age = r.choice(['(15, 24)', '(25, 37)', '(38, 47)'])
        items = []  # gender, percentage, item, age
        cat_dict, sub_dict, total, sub_total = self.initialize(age, gender)

        for i in self.top(sub_dict):
            items.append({'gender': gender, 'item': i, 'age': self.format_age(age),
                          'image': f'{self.image_base}/{i}.jpg',
                          'percent': self.get_percentage(sub_dict[i], sub_total)})

        for i in self.top(cat_dict):
            items.append({'gender': gender, 'item': i, 'age': self.format_age(age),
                          'image': f'{self.image_base}/{i}.jpg',
                          'percent': self.get_percentage(cat_dict[i], total)})

        return items

    def suggest_random(self, age, gender):
        if age not in ['(15, 24)', '(25, 37)', '(38, 47)']:
            age = r.choice(['(15, 24)', '(25, 37)', '(38, 47)'])
        items = []  # gender, percentage, item, age

        cat_dict, sub_dict, total, sub_total = self.initialize(age, gender)
        for i in self.rand_select(list(sub_dict)):
            items.append({'gender': gender, 'item': i, 'age': self.format_age(age),
                          'image': f'{self.image_base}/{i}.jpg',
                          'percent': self.get_percentage(sub_dict[i], sub_total)})

        for i in self.rand_select(list(cat_dict)):
            items.append({'gender': gender, 'item': i, 'age': self.format_age(age),
                          'image': f'{self.image_base}/{i}.jpg',
                          'percent': self.get_percentage(cat_dict[i], total)})

        return items

    @staticmethod
    def top(my_dict, no=2):
        return list(collections.OrderedDict(my_dict))[-no:]

    @staticmethod
    def rand_select(my_list, no=2):
        selected = []
        for i in range(no):
            s = r.choice(my_list)
            my_list.remove(s)
            selected.append(s)
        return selected

    @staticmethod
    def get_percentage(value, total):
        return round((value/total)*100)


if __name__ == '__main__':
    obj = Suggestion()
    print(obj.suggest_random('(15, 24)', 'male'))
