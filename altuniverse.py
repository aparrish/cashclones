import re
import random

from jinja2 import Template

tmpls = [
    "<WOWPHRASE><INFOSRC> {{subj_prop}} is {{real_prop_val}}<QP> <SWORNPHRASE>it was {{alt_prop_val}}<QP>",

    "<PFFTORNOT>Don't <BUY> <ORG>'s <LIES>. {{ucfirst(subj_prop)}} is {{alt_prop_val}}, not {{real_prop_val}}<WOWPUNC><SHEEPLE>",

    "<PFFTORNOT>Don't <BUY> <ORG>'s {{aster(\"<LIES>\")}}. {{ucfirst(subj_prop)}} is {{real_prop_val}}, not {{alt_prop_val}}<WOWPUNC><SHEEPLE>",

    "{{ucfirst('<LIARS>')}} would have you <THINK><THATORNOT> {{subj_prop}} is {{real_prop_val}}. Don't be fooled. It's {{alt_prop_val}}.",

    "My <NEW> <MEDIA> <ADVERBORNOT>argues that, <CONTRARY> <BELIEF>, {{subj_prop}} is {{alt_prop_val}}, not {{real_prop_val}}.",

    "I must have ~phased into the alternate universe~ where {{subj_prop}} is {{real_prop_val}}. Shouldn't it be {{alt_prop_val}}?",

    "<DISBELIEF>You expect me to believe<THATORNOT> {{subj_prop}} is {{real_prop_val}}? <EVERYONE> it's {{alt_prop_val}}. Just common sense.",

    "I've discovered <EVIDENCE> that {{subj_prop}} is {{alt_prop_val}} and not<ASSUMEDORNOT> {{real_prop_val}}.",

    "<BETPREF> <BETWITH> says that {{subj_prop}} is {{real_prop_val}}, but I think it's {{alt_prop_val}}. Which is it?",

    "<WISTFULORNOT>Sometimes I <WONDER> what <LIFE> <WOULDBELIKE> if {{subj_prop}} had been {{alt_prop_val}}, <INSTEADOF> {{real_prop_val}}.",

    "<QSTPHRASE><CRAZYORNOT>Does anyone else remember {{subj_prop}} as being {{alt_prop_val}}, <INSTEADOF> {{real_prop_val}}?<JUSTMEORNOT>",

    "My <NEWORNOT>alternate <HISTORY> <NOVEL> begins with <THISSIMPLE> premise: what if {{subj_prop}} had been {{alt_prop_val}}, <INSTEADOF> {{real_prop_val}}?",

    '<INITPHRASE>{{subj_prop}} is "{{real_prop_val}}"? <MUSTBE> a typo. <SURELYTHEY> {{alt_prop_val}}.',

    "<ACTUALLY>, and <PEOPLE> people <KNOW> this, {{alt_prop_val}} is {{subj_prop}}, not {{real_prop_val}}.<FYIORNOT>",

    "<WOWPHRASE>All my life I thought {{alt_prop_val}} was {{subj_prop}}. But apparently it's {{real_prop_val}}. <MINDBLOWN><TILORNOT>",

    "<UGH>. {{aster(ucfirst(alt_prop_val))}} is {{subj_prop}}, not {{real_prop_val}}. <CANT> <BELIEVE> <OUTLET> got this wrong.",

    "<ALLIASK> consider the {{aster('possibility')}} that {{subj_prop}} is {{alt_prop_val}} and not {{real_prop_val}}.",

    "<MANYBELIEVE><THATORNOT> {{real_prop_val}} is {{subj_prop}}. But you can't prove it's {{aster('NOT')}} {{alt_prop_val}}.",

    u"Everyone knows<THATORNOT> {{subj_prop}} is {{real_prop_val}}. What this book {{aster('presupposes')}} is\u2026 maybe it's {{alt_prop_val}}?",
  
    "{{aster('Why')}} would <YOUANYONE> <GOAROUNDTELLING><THATORNOT> {{real_prop_val}} is {{subj_prop}}, when it's so <CLEARLY> {{alt_prop_val}}?",

    "I <STRONGLY> believe<THATORNOT> schools should teach <OURORNOT>kids the truth: {{alt_prop_val}} is {{subj_prop}}, not {{real_prop_val}}.", 

    "{{ucfirst(subj_prop)}} isn't {{real_prop_val}}. {{aster('Quite')}} the contrary<SEMIDASH>it's {{alt_prop_val}}.",

    u"I <JUSTLAST>\u2014<DREAMANECORNOT>{{alt_prop_val}} was {{subj_prop}}, not {{real_prop_val}}.<SOWEIRDORNOT>",

    "<PODCAST> just did an episode about how {{alt_prop_val}} is {{subj_prop}}, not {{real_prop_val}}. <PODCASTEVAL>"
]

grammar = {
        '<WOWPHRASE>': ['{{ucfirst("<EXCL><WOWPUNC>")}}'],
        '<EXCL>': ["oh wow", "wait", "wow", "huh"],
        '<DISBELIEF>': ['Really. ', 'Really? ', '{{ucfirst("<EXCL>")}}. ', ''],
        '<WOWPUNC>': ['! ', '. '],
        '<QSTPHRASE>': ['{{ucfirst("<QST><QSTPUNC>")}}'],
        '<QST>': ['huh', 'wait what', 'what'],
        '<QSTPUNC>': ['? ', '?? ', '?! '],
        '<INITPHRASE>': ['<WOWPHRASE>', '<QSTPHRASE>'],
        '<INFOSRC>': ['I just read that',
            'Someone just told me<THATORNOT>', 'It says here<THATORNOT>'],
        '<SWORN>': ['I could have sworn', 'I was so convinced', 'I was sure',
            'I thought {{aster("everyone")}} believed'],
        '<SWORNPHRASE>': ['But <SWORN><THATORNOT> ', '<SWORN><THATORNOT> '],
        '<THATORNOT>': [' that', ''],
        '<QP>': ['?', '.'],
        '<BUY>': ['believe', 'buy', 'listen to'],
        '<ORG>': ['Big Brother', 'Big Pharma', "the government", "Big Oil",
            "Halliburton", "the Illuminati"],
        '<LIES>': ['lies', 'claims', 'propaganda'],
        '<SHEEPLE>': ['Wake up, sheeple!',
            'WAKE UP<CORNOT> SHEEPLE<WOWPUNC>'],
        '<CORNOT>': [',', ''],
        '<PFFTORNOT>': ['<PFFT>', ''],
        '<PFFT>': ['P<F>t. '],
        '<F>': ['{{rmult("f",1,6)}}'],
        '<NEW>': ['new', 'upcoming', 'forthcoming'],
        '<MEDIA>': ['book', 'film', 'documentary', 'essay', 'opera',
            'folk song', 'musical', 'doctoral thesis'],
        '<ADVERBORNOT>': ['', '{{aster("<ADVERB>")}} '],
        '<ADVERB>': ['persuasively', 'definitively', 'stridently',
            'incontrovertibly'],
        '<BELIEF>': ['popular beliefs', 'common misconceptions',
            'the received wisdom', 'what THEY say'],
        '<CONTRARY>': ['contrary to', 'despite', 'regardless of'],
        '<EVERYONE>': ['{{aster("Everyone")}} knows',
            'We {{aster("all")}} know',
            "It's obvious<THATORNOT>"],
        '<EXPECT>': ['seriously <EXPECTWANT>', '<EXPECTWANT>'],
        '<EXPECTWANT>': ['expect', 'want'],
        '<EVIDENCE>': ['<EVIDADJ> evidence', 'evidence'],
        '<EVIDADJ>': ['surprising', 'shocking', 'astounding', 'weird new',
            'incontrovertible', 'conclusive'],
        '<ASSUMEDPHRASE>': ['commonly assumed', 'previously believed'],
        '<ASSUMEDORNOT>': [', as <ASSUMEDPHRASE>,', ''],
        '<BETPREF>': ['{{ucfirst("<BETCOMBO>")}}:'],
        '<BETCOMBO>': ['<OKAYSO>settle a bet', '<OKAYSO>help me out here'],
        '<OKAYSO>': ['', 'Okay, so... ', 'So ', 'OK, '],
        '<BETWITH>': ['My girlfriend', 'My boyfriend', 'My buddy',
            'This guy at the bar', 'My brother', 'My sister'],
        '<WISTFULORNOT>': ['<WISTFUL> ', ''],
        '<WISTFUL>': ['Sigh.', '*sigh*', 'Hmm.'],
        '<WONDER>': ['wonder', 'like to imagine', 'daydream about',
            'contemplate', 'seriously contemplate'],
        '<LIFE>': ['life', 'my life', 'this country', 'our world',
            'the Internet'],
        '<WOULDBELIKE>': ['would be like', 'would have been like',
                'would look like', 'would have looked like'],
        '<INSTEADOF>': ['instead of', 'and not', 'not'],
        '<NEWORNOT>': ['<NEW> ', ''],
        '<HISTORY>': ['history', 'universe', 'timeline'],
        '<NOVEL>': ['novel', 'epic', 'saga', 'romance', 'novella', 'dystopia',
                'trilogy', 'fanfic', 'slashfic', 'text adventure'],
        '<THISSIMPLE>': ['the simple', 'a simple', 'this simple'],
        '<MUSTBE>': ['Must be', "Pretty sure that's", "I think that's",
                "Probably"],
        '<SURELYTHEY>': ['Surely they meant', 'They probably meant',
            'They {{aster("must")}} have meant', 'It should <REALLYORNOT>say'],
        '<REALLYORNOT>': ['really ', 'actually ', 'probably ', ''],
        '<AMICRAZY>': ['Am I going crazy?', 'Am I nuts?', 'Really?'],
        '<CRAZYORNOT>': ['<AMICRAZY> ', ''],
        '<JUSTMEORNOT>': [' Or is it just me?', ' So {{aster("weird.")}}', ''],
        '<ACTUALLY>': ['Actually', 'A{{rmult("a",1,5)}}ctually', 'FYI', 'Just FYI',
                'Just so you know'],
        '<PEOPLE>': ['not many', 'very few', 'only a handful of'],
        '<KNOW>': ['know', 'are aware of', 'really understand',
            'have any idea about', 'truly grok'],
        '<FYIORNOT>': [' Just FYI.', ' FYI.', '', ''],
        '<ALLMYLIFE>': ['All my life I thought<THATORNOT>',
            'In school we learned<THATORNOT>',
            '<AUTHORITYFIGURE> always told me<THATORNOT>'],
        '<AUTHORITYFIGURE>': ['My teacher', 'My mom', 'My dad', 'My grandpa',
                'My grandmother', 'My friends'],
        '<MINDBLOWN>': ["MIND BLOWN<WOWPUNC> ", 'Mind blown<WOWPUNC> ',
                "You learn something new every day<WOWPUNC> ", ''],
        '<TILORNOT>': ['#TIL', ''],
        '<CANT>': ["I can't", "I cannot", "Can't", "I can NOT"],
        '<BELIEVE>': ['{{aster("believe")}}<THATORNOT>', "understand how"],
        '<OUTLET>': ["Wikipedia", "the NY Times", "my professor"],
        '<UGHPHRASE>': ["<UGH>.", "<UGH>. No."],
        '<UGH>': ["Ugh", "UGH", "Wow"],
        '<LIARS>': ['"Scientists"', 'the "mainstream" media',
                'those ivory tower pencil-necks', 'government shills'],
        '<THINK>': ["think", "believe"],
        '<ALLIASK>': ["All I ask is<THATORNOT> you", "I only ask<THATORNOT> you",
                "I only want for you to", "The only think I ask is<THATORNOT> you"],
        '<MANYBELIEVE>': ["Many believe", "Some believe", "You say"],
        '<CLEARLY>': ["clearly", "obviously", "plainly"],
        '<STRONGLY>': ["strongly", "fervently"],
        '<OURORNOT>': ["our ", ""],
        '<GOAROUNDTELLING>': ["go around telling people",
                "{{aster('publicly')}} claim"],
        '<YOUANYONE>': ["you", "anyone", "you (or anyone)"],
        '<SEMIDASH>': ["; ", u"\u2014"],
        '<JUSTLAST>': ["just had the {{aster(caps('<WEIRD>'))}} dream",
                "had the {{aster(caps('<WEIRD>'))}} dream last night"],
        '<WEIRD>': ["weirdest", "strangest", "most unusual"],
        '<DREAMANEC>': ["I was naked", "I was late for class",
            "A bear was chasing me", "I had a <PET>",
            "I was getting married", "I got a new phone"],
        '<PET>': ["cat", "dog", "puppy", "kitten", "pet frog"],
        '<DREAMANECORNOT>': ["<DREAMANEC>, and ", ""],
        '<SOWEIRD>': ["So weird.", "So. Weird.", "Bizarre.",
                "What does it mean?"],
        '<SOWEIRDORNOT>': ["", " {{caps('<SOWEIRD>')}}"],
        '<PODCAST>': ["Radiolab", "This American Life", "99% Invisible",
                "Savage Lovecast", "Slate's Political Gabfest"],
        '<PODCASTEVAL>': ["{{caps('So good')}}.", "Amazing!",
                "You should<TOTALLYORNOT> subscribe."],
        '<TOTALLYORNOT>': [" totally", ""]
}

def ucfirst(s):
    return s[0].upper() + s[1:]

def expand(grammar, axiom):
    expansions = list()
    replacethese = re.findall(r'<[^>]+>', axiom)
    if len(replacethese) > 0:
        for to_replace in replacethese:
            possibles = grammar[to_replace]
            if len(possibles) > 1:
                at_least = 1
            else:
                at_least = 1
            for replacement in random.sample(possibles, at_least):
                replaced = re.sub(to_replace, replacement, axiom)
                expanded = expand(grammar, replaced)
                if len(expanded) > 1:
                    expansions.extend(random.sample(expanded, 1))
                else:
                    expansions.extend(random.sample(expanded, 1))
    else:
        expansions.append(axiom)
    return expansions

def rmult(item, rstart, rend):
    return item * random.randrange(rstart, rend)

def aster(item):
    if random.randrange(2) == 0:
        return "*" + item + "*"
    else:
        return item

def caps(item):
    if random.randrange(2) == 0:
        return item.upper()
    else:
        return item

def alternate_universe(subject, prop, real_prop_val, alt_prop_val):
    if prop.isupper(): prop = prop.lower()
    if re.search(r"^[a-zA-Z ]+[^s]$", subject):
        subj_prop = subject + "'s " + prop
    else:
        subj_prop = "the " + prop + " of " + subject
    possibles = list()
    for tmpl_str in tmpls:
        possibles_this = list()
        expansions = expand(grammar, tmpl_str)
        for expansion in expansions:
            tmpl = Template(expansion)
            res = tmpl.render(subj_prop=subj_prop, real_prop_val=real_prop_val,
                alt_prop_val=alt_prop_val, ucfirst=ucfirst, rmult=rmult,
                aster=aster, caps=caps)
            possibles_this.append(res)
        possibles.append(random.choice(possibles_this))
    #print "\n".join(possibles)
    return ucfirst(random.choice(possibles))

if __name__ == '__main__':
    # Everyone knows Halle Berry's birth year is 1966. What this book
    # presupposes is... maybe it's 2039? http://en.wikipedia.org/wiki/Halle_Berry
    while True:
        print alternate_universe("Halle Berry", "birth year", "1966", "2039")

"""
    if sum(map(len, [subj_prop, real_prop_val, alt_prop_val])) <= 47:
        tmpl_str = u"Everyone knows {{subj_prop}} is {{real_prop_val}}. What this book presupposes is\u2026 maybe it's {{alt_prop_val}}?"
    else:
        tmpl_str = u"Everyone knows {{subj_prop}} is {{real_prop_val}}. This book presupposes\u2026 maybe it's {{alt_prop_val}}?"
    tmpl = Template(tmpl_str)
    return tmpl.render(subj_prop=subj_prop, real_prop_val=real_prop_val,
            alt_prop_val=alt_prop_val)
"""
