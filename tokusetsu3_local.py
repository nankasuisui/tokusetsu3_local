#tokusetsu3 templateからindex.htmlの生成
#%%
import csv,re,os,shutil
from pathlib import Path
#import pprint

#%%
#ディレクトリ指定,設定

os.chdir(Path().resolve('__file__'))

source_path = "src"
input_path = "input"
dest_path = "dest"

index_template_path = source_path+'/'+"index_local.html"
templatecsv_path = source_path+'/'+"convert.csv"
ifrule_path = source_path+'/'+"ifrule.csv"
assets_src_path = source_path+'/'+"assets"
assets_dest_path = dest_path+'/'+"assets"
usercsv_path = input_path+'/'+"convert.csv"
out_html_path = dest_path+'/'+"index.html"

#%%
#assetsフォルダ(imgフォルダ),stylesheetをdestフォルダに配置
if not os.path.exists(dest_path):
    os.mkdir(dest_path)
if not os.path.exists(assets_dest_path):
    os.mkdir(assets_dest_path)
if not os.path.exists(assets_dest_path+"/img"):
    os.mkdir(assets_dest_path+"/img")
for f in ["/scripts.js","/style-dark.css","/style-light.css"]:
    if not os.path.exists(assets_dest_path+f):
        shutil.copyfile(assets_src_path+f,assets_dest_path+f)

#input/convert.csvが存在しない場合は該当ディレクトリにsrcのテンプレートを複製し編集を促し終了
if not os.path.exists(input_path):
    os.mkdir(input_path)
if not os.path.exists(usercsv_path):
    shutil.copyfile(templatecsv_path,usercsv_path)
    print("please edit csv file @ "+ usercsv_path)
    exit()

#%%
#index_template読み込み
with open(index_template_path,encoding='utf-8') as f:
    index_template = f.read()

#置換csv読み込み
with open(usercsv_path,encoding='utf-8') as f:
    reader = csv.reader(f)
    userinput = [row for row in reader if len(row) == 2]

#ifrule読み込み
with open(ifrule_path,encoding='utf-8') as f:
    reader = csv.reader(f)
    ifrule = [row for row in reader if len(row) == 2]


#%%
#ファイル名のみの場合userinput内の画像系の指定についてディレクトリ情報を追加
#また¥(JIS),\を/に置換
userinput_tmp = []
for usrinput in userinput:
    usrinput_tmp = [usrinput[0],usrinput[1].replace("\\",'/')]
    if re.search("image:",usrinput_tmp[0]) or re.search("Favicon",usrinput_tmp[0]):
        if usrinput_tmp[1] != "":
            if not re.search("/",usrinput_tmp[1]):
                userinput_tmp.append([usrinput_tmp[0],"assets/img/"+usrinput_tmp[1]])
                continue
    userinput_tmp.append(usrinput_tmp)

userinput = userinput_tmp

#%%
#IfBlockの判定
#最初に0で初期化
ifrule_tmp = []
tmp_flag = 0
for rule in ifrule:
    matchOB = re.search("{block:If(?!Not)(.*)}",rule[0])
    if matchOB:
        tmp_flag = 0
        for usrinput in userinput:
            if (len(usrinput) != 0) and re.search(matchOB.group(1) if len(rule) == 2 else rule[2],usrinput[0].replace(' ','')):
                if usrinput[1] != "":
                    tmp_flag = 1
                break

        ifrule_tmp.append([rule[0],tmp_flag])
        continue

    else:
        matchOB = re.search("{block:IfNot(.*)}",rule[0])
        if matchOB:
            tmp_flag = 1
            for usrinput in userinput:
                if (len(usrinput) != 0) and re.search(matchOB.group(1) if len(rule) == 2 else rule[2],usrinput[0].replace(' ','')):
                    if usrinput[1] != "":
                        tmp_flag = 0

            ifrule_tmp.append([rule[0],tmp_flag])
            continue
    
    if ifrule_tmp != [] and ifrule_tmp[-1][0] != rule[0]:
        print("exception:",rule[0])
        print(matchOB.group(1))
        exit()
            
ifrule = ifrule_tmp
#pprint.pprint(ifrule)

#%%
#ifBlock全体,もしくは{}のみを削除
for ifpatterns in ifrule:
    if ifpatterns[1] == False:
        index_template = re.sub(ifpatterns[0]+'.+?'+'{/'+ifpatterns[0][1:],
        "",index_template,flags=re.DOTALL)
    
    elif ifpatterns[1] == True:
        index_template = re.sub(ifpatterns[0],"",index_template,flags=re.DOTALL)
        index_template = re.sub('{/'+ifpatterns[0][1:],"",index_template,flags=re.DOTALL)

#各文字列等の置換
for patterns in userinput:
    print(patterns)
    index_template = re.sub('{'+patterns[0]+'}',patterns[1],index_template)

#%%
#気に入らない空白行の削除
index_template = '\n'.join(filter(lambda x: x.strip(), index_template.split('\n')))

#%%
#outフォルダに最終的なファイルを出力
with open(out_html_path,'w',encoding='utf-8') as f:
    f.write(index_template)