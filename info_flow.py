#coding=utf-8
import re, py2neo

class Information_Flow():
    def __init__(self):
        self.sources = {}

        self.convey_dict = [
            '表示', '指出', '援引', '说', '报道', '电讯', '称', '声明', '宣布', '宣称', '消息',
            '引用', '证实', '印证', '告诉', '告知', '解释', '阐述', '说道', '强调', '转达', '介绍'
            # '', '', '', '', '', '', '', '', '', ''
        ]
        self.convey_dict = {key: None for key in self.convey_dict}

        self.quote_dict = [
            '援引', '转达', '引用'
        ]
        self.quote_dict = {key: None for key in self.quote_dict}

        self.cutsuffix_dict = [
            '消息', '情报', '讲话', '演讲', '讯息', '资讯', '声明'
        ]
        self.cutsuffix_dict = {key: None for key in self.cutsuffix_dict}

    def gen_source(self, parse):
        sentence, words, postags, roles = parse[0], parse[1], parse[2], parse[4]
        current_svb = ''
        current_vob = ''
        current_convey = ''
        for key_index in roles:
            if 'MNR' in roles[key_index].keys():
                for word in words[roles[key_index]['MNR'][1]:roles[key_index]['MNR'][2]+1]:
                    if word in self.convey_dict:
                        comb_key = ''
                        for i in range(roles[key_index]['MNR'][2]+1 - roles[key_index]['MNR'][1]):
                            if postags[i] in {'ni', 'u', 'nl', 'nh'}:
                                comb_key += words[i]
                        self.sources[word] = [comb_key,]
                        break

            if words[key_index] in self.convey_dict:
                if 'A0' in roles[key_index].keys():
                    #print("in A0")
                    if current_convey in self.quote_dict:
                        print("quote")
                        self.sources[words[key_index]] = [current_vob]
                    else:
                        self.sources[words[key_index]] = [''.join(words[roles[key_index]['A0'][1]:roles[key_index]['A0'][2]+1]),]
                    current_svb = self.sources[words[key_index]][0]
                if 'A1' in roles[key_index].keys():
                    if words[key_index]  not in self.sources.keys():
                        #print("A1 with A0")
                        if current_convey in self.quote_dict:
                            self.sources[words[key_index]] = [current_vob]
                        else:
                            self.sources[words[key_index]] = [current_svb]
                    pre_vob = ''.join(words[roles[key_index]['A1'][1]:roles[key_index]['A1'][2] + 1])
                    if len(pre_vob) > 3 and pre_vob[-3] == '的' and pre_vob[-2:] in self.cutsuffix_dict:
                        pre_vob = pre_vob[:-3]
                    self.sources[words[key_index]].append(pre_vob)
                    current_vob = self.sources[words[key_index]][1]
                else:
                    if key_index + 1 < len(words) and words[key_index + 1] == '，':
                        self.sources[words[key_index]].append(''.join(words[key_index + 2:]))
                    elif key_index + 2 < len(words) and words[key_index + 2] == '，':
                        self.sources[words[key_index]].append(''.join(words[key_index + 3:]))
                current_convey = words[key_index]
        #print(self.sources)

class FlowGragh():
    def __init__(self):
        self.url = 'bolt://localhost:xxxx'
        self.pw = 'xxxxxxxxxx'
        self.graph_engine = py2neo.Graph(self.url, username='usrname', password='pw')
        self.graph = self.graph_engine.begin()

    def add_source(self, flow_dict):
        flow= [[key, flow_dict[key]] for key in flow_dict]
        print(flow)
        flow_stack = []
        for i in range(len(flow)):
            if i != len(flow) - 1:
                station = py2neo.Node('station', name=flow[i][1][0])
                flow_stack.append(station)
                self.graph.create(station)
            elif len(flow) > 1:
                print(flow[i][1])
                station = py2neo.Node('station', name=flow[i][1][0])
                text = py2neo.Node('text', name=flow[i][1][1])
                flow_stack.append(station)
                flow_stack.append(text)
                self.graph.create(station)
                self.graph.create(text)
        for i in range(1, len(flow_stack)):
            convex = py2neo.Relationship(flow_stack[i], 'flow', flow_stack[i-1])
            self.graph.create(convex)

        ''''   cause = py2neo.Node('cause', name=''.join(
                [word.split('/')[0] for word in data['cause'].split(' ') if word.split('/')[0]]))
            effect = py2neo.Node('effect', name=''.join(
                [word.split('/')[0] for word in data['effect'].split(' ') if word.split('/')[0]]))
            graph.create(cause)
            graph.create(effect)
            convex = py2neo.Relationship(cause, data['tag'], effect)
            graph.create(convex)'''

