from flask import Flask, render_template
from flask import request
import nltk
import re
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

color_dic = {'yellow':'\033[43m', 'red':'\033[31m', 'blue':'\033[34m', 'end':'\033[0m'}


tag=[]
tag.append("a ")
tag.append("")
tag.append("")
space=" "

gname=""
v_set=[]


app = Flask(__name__)

def print_hl(text, keyword, color="yellow"):
    for kw in keyword:
        bef = kw
        aft = color_dic[color] + kw + color_dic["end"]
        text = re.sub(bef, aft, text)
    #print("plain: "+text.capitalize())
    rtext=text.capitalize()
    print(rtext)
    return rtext
    #Quote -> https://qiita.com/yuto16/items/5618e4147b749177bd15

def tense_check(word):
    s=word.lower()
    s=s.replace('i ','I ')
    verbs=[]
    i=0
    tense=-1
    tofound=0 #usage: skip phrases such as "to play", "to be" and etc.                                           

    words=nltk.word_tokenize(s)
    pos=nltk.pos_tag(words)
    #print(pos)     #usage: check tags                                                                            
    for w in pos:
        if w[1]=="TO" and tofound==0:
            tofound=1
            print("tofound")
            i+=1

        elif w[0]=="will":
            tense=0
            tag[0]="Futute "
            verbs=aspect_check(pos,i,tense)
            break
        elif w[1]=="VBD":
            tense=1
            tag[0]="Past "
            verbs=aspect_check(pos,i,tense)
            break
        elif w[1]=="VB" or w[1]=="VBP" or w[1]=="VBZ":
            if tofound==1:
                i+=1
                tofound=0
                continue
            tense=2
            tag[0]="Present "
            verbs=aspect_check(pos,i,tense)
            break
        else:
            if tofound==1:
                tofound=0
            i+=1
    if tense==-1:
        tag[0]="..."
        tag[1]=""
        tag[2]=""
        return ""
    else:
       #v_col=print_hl(word.lower(), verbs)
       return verbs 
    
def aspect_check(pos,i,tense):
    phrase=[]
    befound=False
    if tense==0:
        phrase.append("will")
        for j in range(i+1,len(pos)):
            #print(pos[j][0])                                                                                      
            if pos[j][1]=="RB" or pos[j][1]=="NN" or pos[j][1]=="NNS" or pos[j][1]=="NNP" or pos[j][1]=="NNPS" or pos[j][1]=="PRP":
                continue
            elif pos[j][0]=="have":
                tag[1]="perfect "
                phrase.append(pos[j][0])
            elif pos[j][1]=="VBN":
                if pos[j][0]=="been" and pos[j+1][1]=="VBG":
                    tag[2]="progressive"
                    phrase.append(pos[j][0])
                    phrase.append(pos[j+1][0])
                else:
                    tag[2]="simple"
                    phrase.append(pos[j][0])
                break
            elif pos[j][0]=="be" and pos[j+1][1]=="VBG":
                tag[2]="progressive"
                phrase.append(pos[j][0])
                phrase.append(pos[j+1][0])
                break
            else:
                tag[1]=""
                tag[2]="simple"
                phrase.append(pos[j][0])
                break
            
    elif tense==1:
        for j in range(i,len(pos)):
           # print(pos[j][0])                                                                                               
            if pos[j][1]=="RB" or pos[j][1]=="NN" or pos[j][1]=="NNS" or pos[j][1]=="NNP" or pos[j][1]=="NNPS" or pos[j][1]\
=="PRP":
                continue
            elif pos[j][0]=="was" or pos[j][0]=="were":
                tag[1]=""
                tag[2]="progressive"
                phrase.append(pos[j][0])
                befound=True
            elif pos[j][1]=="VBG":
                if befound:
                    phrase.append(pos[j][0])
                break

            elif pos[j][0]=="had":
                tag[1]="perfect "
                phrase.append(pos[j][0])

            elif pos[j][1]=="VBN":
                if pos[j][0]=="been":
                    tag[2]="progressive"
                    phrase.append(pos[j][0])
                    befound=True
                else:
                    tag[2]="simple"
                    phrase.append(pos[j][0])
                    break

            else:
                tag[1]=""
                tag[2]="simple"
                if befound==False and pos[j][0]!=".":
                    phrase.append(pos[j][0])
                if j!=0:
                    break
                else:
                    continue
    elif tense==2:
        for j in range(i,len(pos)):
            #print(pos[j][0]+tag[1])                                                                                        
            if pos[j][1]=="RB" or pos[j][1]=="NN" or pos[j][1]=="NNS" or pos[j][1]=="NNP" or pos[j][1]=="NNPS" or pos[j][1]\
=="PRP":
                continue
            elif pos[j][0]=="am" or pos[j][0]=="is" or pos[j][0]=="are":
                tag[1]=""
                tag[2]="progressive"
                phrase.append(pos[j][0])
                befound=True
            elif pos[j][1]=="VBG":
                if befound:
                    phrase.append(pos[j][0])
                break

            elif pos[j][0]=="have" or pos[j][0]=="has":
                tag[1]="perfect "
                phrase.append(pos[j][0])

            elif pos[j][1]=="VBN" or pos[j][1]=="VBD":
                if pos[j][0]=="been":
                    tag[2]="progressive"
                    phrase.append(pos[j][0])
                    befound=True
                else:
                    tag[2]="simple"
                    phrase.append(pos[j][0])
                    break

            else:
                tag[1]=""
                tag[2]="simple"
                if befound==False and pos[j][0]!=".":
                    phrase.append(pos[j][0])
                if j!=0:
                    break
    return phrase

# トップ画面
@app.route('/')
def index():
    return render_template('index.html',sentence="I study Python.",v_set=["study"],gname="Present simple")


# getでの入力情報処理
@app.route("/receive_get", methods=["GET"])
def receive_get():
    name = request.args["my_name"]
    word=str(name)
    v_set=tense_check(word)
    gname=f"{tag[0]}{tag[1]}{tag[2]}"
    return render_template('index.html',sentence=word,v_set=v_set,gname=gname)

if __name__ == '__main__':
    app.run(host="0.0.0.0")
