#coding=utf8
import json
with open('../output/checkpoint-100/generated_predictions.txt','r') as m,open('../data/submit.txt','w') as n:
    for line in m.readlines():
        line_json = json.loads(line)
        predict_label = line_json['predict']
        n.write(predict_label+'\n')