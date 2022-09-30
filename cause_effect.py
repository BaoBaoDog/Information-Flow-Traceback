import re
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller
import info_flow as iffl

class ContentHandler():
    def __init__(self):
        self.segmentor = Segmentor("./ltp_data/cws.model")
        self.postagger = Postagger("./ltp_data/pos.model")
        self.parser = Parser("./ltp_data/parser.model")
        self.recognizer = NamedEntityRecognizer("./ltp_data/ner.model")
        self.labeller = SementicRoleLabeller("./ltp_data/pisrl_win.model")

    def sentence_split(self, content):
        return [sentence for sentence in re.split(r'[？?！!。；;\n\r]', content) if sentence and len(sentence) > 1]

    def main_handle(self, content):
        sentence_list = self.sentence_split(content)
        parse_list = []
        for sentence in sentence_list:
            words = list(self.segmentor.segment(sentence))
            postags = list(self.postagger.postag(words))
            arcs = self.parser.parse(words, postags)
            roles = self.labeller.label(words, postags, arcs)
            roles_dict = {}
            for role in roles:
                roles_dict[role[0]] = {arg[0]: [arg[0], arg[1][0], arg[1][1]] for arg in role[1]}
            parse_list.append([sentence, words, postags, arcs, roles_dict])
            '''print("sentence", sentence)
            print("words", words)
            print("postags", postags)
            print("arcs", arcs)
            print("rols_dict", roles_dict)'''
        return parse_list

class CauseEffectExtractor():
    def __init__(self):
        pass

    def rule_ce1(self, sentence):
        match_list = []

        ce_pair = [
            ['因为', '所以'], ['因为', '为此'], ['因为', '从而'], ['因为', '以至于'], ['因为', '故而'], ['因为', '故此'],
            ['因为', '故'], ['因为', '就此'], ['因为', '以致'], ['由于', '所以'], ['由于', '为此'], ['由于', '从而'],
            ['由于', '以至于'], ['由于', '故而'], ['由于', '故此'], ['由于', '故'], ['由于', '因而'], ['由于', '以致'],
            ['由于', '导致'], ['因为', '导致'], ['因', '而'], ['由于', '因此'], ['既然', '那么'], ['因为', '于是'],
        ]

        invalid_cause_suffix = {'，', }
        invalid_effect_suffix = {'，', '了'}

        for ce in ce_pair:
            data = {}
            mode = re.compile(r'(%s)(.*)(%s)(.*)' % (ce[0], ce[1]))
            match = mode.findall(sentence)
            if len(match) > 0:
                match = list(match[0])
                if match[1][-1] in invalid_cause_suffix:
                    match[1] = match[1][:-1]
                if match[3][-1] in invalid_effect_suffix:
                    match[1] = match[1][:-3]
                print(match)
                data['tag'] = ce[0] + '-' + ce[1]
                data['cause'] = match[1]
                data['effect'] = match[3]
                match_list.append(data)
        return match_list

    def rule_ce2():
        pass



if __name__ == '__main__':
    content1 = '''
    中新社北京9月24日电 综合消息：据相关媒体近期报道，俄罗斯外交部副部长谢尔盖·里亚布科夫表示，俄罗斯没有用核武器威胁任何人。乌克兰撤销伊朗驻乌大使的相关证件。芬兰将限制俄罗斯公民持申根签证过境。
    俄副外长称没有用核武器威胁任何人。
    俄罗斯卫星通讯社23日援引俄副外长谢尔盖·里亚布科夫的表态称，俄罗斯没有用核武器威胁任何人。他警告说，西方干涉俄罗斯在乌克兰实施特别军事行动将面临相应风险。
    谢尔盖·里亚布科夫指出，与美国和北约进行公开对抗不符合俄罗斯的利益。俄罗斯希望美国政府认清乌克兰冲突升级失控的危险性。
    俄罗斯卫星通讯社23日援引俄国防部的消息说，为了保障俄罗斯个别高科技领域、金融系统的正常运转，决定在局部动员期间不征召相应专业的高学历专家服役。主流媒体等领域的工作人员也将免于被征召。
    据塔斯社23日报道，俄罗斯克里姆林宫发言人表示，关于俄罗斯局部动员令将征召120万俄罗斯人的说法其实是“谣言”。
    乌克兰撤销伊朗驻乌大使证件
    据乌通社23日报道，乌克兰外交部已通知伊朗驻乌克兰大使馆临时代办，由于俄军使用了伊朗制造的武器，决定撤销伊朗驻乌克兰大使的相关证件，并减少该大使馆内外交人员的额定人数。
    路透社报道称，乌克兰将降低与伊朗的外交关系级别。乌克兰总统泽连斯基此前表示，乌方已击落8架俄军使用的伊朗制无人机。
    美国有线电视新闻网23日援引乌军方的消息说，伊朗制造的无人机已被用来袭击敖德萨地区。
    据乌通社23日消息，泽连斯基指出，西方国家提供的多管火箭发射系统以及火炮对乌军进攻产生了决定性影响。乌克兰将继续要求合作伙伴提供更多武器。
    芬兰将限制俄罗斯公民持申根签证过境
    据俄罗斯卫星通讯社报道，当地时间23日，芬兰外交部长哈维斯托在新闻发布会上表示，芬兰近期将限制持有申根签证的俄罗斯人过境，同时也将限制俄罗斯游客入境。
    据俄罗斯卫星通讯社24日消息，匈牙利外长西雅尔多在接受采访时表示，当前首要任务是避免俄罗斯与北约发生直接冲突。
    西雅尔多认为，如果俄罗斯和美国不达成协议、不进行磋商，那么乌克兰危机就无法得到解决。要想解决当前局势，俄美必须尽快展开对话。
    中新社北京9月23日电 综合消息：据俄罗斯媒体22日报道，俄罗斯联邦安全会议副主席梅德韦杰夫表示，对于新加入俄罗斯的领土，包括战略核武器和新型武器在内的任何俄罗斯武器都可以用于防御。联合国秘书长古特雷斯称俄乌冲突没有平息迹象。俄罗斯禁止87名加拿大公民入境。
    梅德韦杰夫称或可使用核武器保护新加入俄罗斯的地区。
    当地时间9月22日，梅德韦杰夫通过社交媒体表示，俄罗斯已经宣布，对于新加入俄罗斯的领土，包括战略核武器和新型武器在内的任何俄罗斯武器都可以用于防御。
    俄罗斯武装力量总参谋部动员局发言人弗拉基米尔·齐姆良斯基表示，俄罗斯秋季开展的征兵活动将征召12万人入伍。该征兵活动与特别军事行动没有关联，应征入伍的俄罗斯公民也不会被派往乌克兰参加特别军事活动。
    齐姆良斯基还介绍说，按照局部动员令被征召入伍的俄公民将获得与合同兵等同的社会保障、报酬和身份。“宣布实施局部动员第一天以来，已经有1万名公民等不及征召，自行抵达兵役委员会报到。”
    俄罗斯卫星通讯社23日援引俄外交部的消息说，俄罗斯外交部长拉夫罗夫在向阿拉伯国家联盟联络小组各国外长通报乌克兰局势时指出，乌克兰危机是由2014年在一些西方国家的支持下发生的政变造成的。俄罗斯无条件的优先事项是保护顿巴斯的平民、乌克兰的非军事化和去纳粹化。
    拉夫罗夫还在稍早前的联合国安理会会议上指出，西方国家向乌克兰提供武器从而成为冲突的参与方。
    乌军方通报战况
    乌通社23日援引乌克兰武装部队总参谋部的声明说，在过去1天里，敌方对乌克兰实施了4次导弹袭击、27次空袭，并对乌克兰境内目标使用多管火箭系统超过75次。空袭和导弹袭击的威胁在乌克兰各地持续存在。
    该通报还称，乌克兰空军22日摧毁了7个空中目标，并发动了10次集体空袭等。
    乌克兰政府官员表示，自军事冲突开始到9月20日，乌克兰共有349座能源基础设施受到破坏。
    联合国秘书长称俄乌冲突没有平息迹象。
    据联合国官网22日消息，联合国秘书长古特雷斯在有关乌克兰局势的会议上表示，“战争到现在仍然没有平息的迹象。”他强调，近期的局势发展让和平的前景进一步远去，“这场毫无意义的战争可能会给乌克兰乃至整个世界造成无尽的伤害”。
    古特雷斯介绍说，国际原子能机构正在就确保扎波罗热核电站及周边地区安全的措施与有关各方进行磋商。他强调，必须停止对核设施的所有攻击，必须重新确立此类核电站的纯民用性质。他说：“世界承受不起一场核灾难。”
    俄罗斯禁止87名加拿大公民入境
    俄罗斯卫星通讯社22日援引俄外交部的消息说，俄罗斯禁止87名加拿大公民入境，以回应反俄制裁。
    俄外交部介绍称，上述87人包括加拿大各省和地区的领导人、军队成员、为基辅政权提供武器和军民两用技术的公司负责人等。
    俄外交部指出，考虑到加拿大对俄制裁名单显然会扩大，依据对等原则，俄罗斯方面将继续发布制裁加拿大公民名单的新公告。'''

    content2 = '俄罗斯卫星通讯社23日援引俄副外长谢尔盖·里亚布科夫的表态称，俄罗斯没有用核武器威胁任何人。'
    content3 = '乌通社23日援引乌克兰武装部队总参谋部的声明说，在过去1天里，敌方对乌克兰实施了4次导弹袭击、27次空袭，并对乌克兰境内目标使用多管火箭系统超过75次'
    content4 = '据乌通社23日消息，西方国家提供的多管火箭发射系统以及火炮对乌军进攻产生了决定性影响。'
    content5 = '俄外交部介绍称，上述87人包括加拿大各省和地区的领导人、军队成员、为基辅政权提供武器和军民两用技术的公司负责人等。'\
               '俄外交部指出，考虑到加拿大对俄制裁名单显然会扩大，依据对等原则，俄罗斯方面将继续发布制裁加拿大公民名单的新公告。'
    content6 = '俄罗斯卫星通讯社23日援引俄外交部的消息说，俄罗斯外交部长拉夫罗夫在向阿拉伯国家联盟联络小组各国外长通报乌克兰局势时指出，乌克兰危机是由2014年在一些西方国家的支持下发生的政变造成的。'
    content7 = '他说：“世界承受不起一场核灾难。”'

    handler = ContentHandler()
    cee = CauseEffectExtractor()
    parse_list = handler.main_handle(content1)
    neo_graph = iffl.FlowGragh()

    for sent in parse_list:
        cee.rule_ce1(sent[0])
        flow_graph = iffl.Information_Flow()
        flow_graph.gen_source(sent)
        neo_graph.add_source(flow_graph.sources)
    neo_graph.graph.commit()