import os
import beyond.Reaper
import time
import sys
import random
import csv
import copy
import PySimpleGUI as sg   

Song_Item = 0 # 0, 1, 2, 3 ------------------------------------------------------------------------------>change

folder_list = ['Song1-InTheMeantime', 'Song2-PouringRoom', 'Song3-RedToBlue', 'Song4-LeadMe'] #歌单
KEY_WORD = 'Balance'
Translation = {'Balance':'平衡感'}
base_path = base_path = sys.path[0]
last_path = os.path.abspath(os.path.dirname(os.getcwd()))

def WAV(path):
    wavlist = []
    files = os.listdir(path)
    for file in files:
        if '.wav' in file and '.reapeaks' not in file:
            wavlist.append(file)
    return wavlist,len(wavlist)

def CheckEmpty(List):
    if 'X' in List:
        return True
    return False

def ReOrderDict(List,Data): #List是乱序后的音频文件顺序，Data是分数数据
    Dict = {}
    for i,item in enumerate(Data):
        Dict[List[i]] = item
    return Dict

def Dict2List(OrderList,Dict): #List乱序后的音频文件名称保存在表格中的顺序
    List = []
    for item in OrderList:
        List.append(str(Dict[item]))
    return List

def GenerateScoreList(data):
    symbol = 'Slider'
    Score_list = []
    for i in range(1,8):
        temp_symbol = symbol + str(i)
        Score_list.append(data[temp_symbol])
    return Score_list

def create_csv(filename, title, data):
    path = filename
    with open(path,'w' ,newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(title)
        csv_write.writerow(data)

def edit_csv(filename, data):
    path  = filename
    with open(path,'a+',newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(data)

print('------------------------------------------------欢迎您来到{}测试系统---------------------------------------------------'.format(Translation[KEY_WORD]))
print('------------------------------------------------------V0.600-------------------------------------------------------------')
print('--------------------------------------------- -当前歌曲:{}----------------------------------------------------------'.format(folder_list[Song_Item]))

temp_WAV_path = os.path.join(last_path,'Final_Stimuli',folder_list[Song_Item])
WAV_list, WAV_list_len = WAV(temp_WAV_path)
Original_WAV_list = copy.deepcopy(WAV_list)
random.shuffle(WAV_list)

os.system('start D:/Reaper-Win-Portable/reaper.exe') #start是为了让os进程不会中止，可以继续
time.sleep(2)
Reaper.Main_openProject(os.path.join(base_path,'2.rpp'))
time.sleep(2)

track_num = 0

for i in range(WAV_list_len): #有多少个Stimuli
    Reaper.InsertTrackAtIndex(Reaper.GetNumTracks(), True)
    reaper_media_track = Reaper.GetTrack(0, i) #第二个参数，0是第一个，1是第二个
    print('请稍等,正在载入音频，加载进度：{}%.'.format(round(((i+1)/WAV_list_len)*100,2)))
    track_num += 1

    Reaper.SetOnlyTrackSelected(reaper_media_track) #选中
    Reaper.InsertMedia(os.path.join(temp_WAV_path, WAV_list[i]), 0)

    if i != WAV_list_len-1:
        Reaper.CSurf_GoStart()  #转移光标位置

#     clip_start_time_sec = Reaper.TimeMap2_QNToTime(0, 0)

# Reaper.MoveEditCursor(clip_start_time_sec, False)
reaper_media_track = Reaper.GetTrack(0, 0) #第二个参数，0是第一个，1是第二个
Reaper.SetOnlyTrackSelected(reaper_media_track) #选中
Reaper.RPR_Main_OnCommand(7,0)# Solo

sg.theme('DarkGreen5')

layout = [  [sg.Text("请问您是否有混音经验？"),sg.Spin( values =['是','否'])],
            [sg.Text("以下共有来自同一首歌曲的7个混音版本，请根据"+Translation[KEY_WORD]+"进行0-100的打分！。\n ",size=(30, 2))],     # Part 2 - The Layout
            [sg.Text("评分标准如下：\n 0-20    很差\n 20-40   较差\n 40-60   一般\n 60-80   较好\n 80-100  很好",size=(30, 6))],
            [sg.Text("本测试通过选择按钮1-7切换音频信号\n请先按下播放按钮：",size=(30, 2))],     # Part 2 - The Layout
            [sg.Button('播放',size=(10, 1))],
            [sg.Slider(orientation ='horizontal', key='Slider1',range=(0,100)), sg.Button('1',size=(3,1))],
            [sg.Slider(orientation ='horizontal', key='Slider2',range=(0,100)), sg.Button('2',size=(3,1))],
            [sg.Slider(orientation ='horizontal', key='Slider3',range=(0,100)), sg.Button('3',size=(3,1))],
            [sg.Slider(orientation ='horizontal', key='Slider4',range=(0,100)), sg.Button('4',size=(3,1))],
            [sg.Slider(orientation ='horizontal', key='Slider5',range=(0,100)), sg.Button('5',size=(3,1))],
            [sg.Slider(orientation ='horizontal', key='Slider6',range=(0,100)), sg.Button('6',size=(3,1))],
            [sg.Slider(orientation ='horizontal', key='Slider7',range=(0,100)), sg.Button('7',size=(3,1))],
            [sg.Text("提示:测试结束后请一定记得保存！",size=(25, 1))],     # Part 2 - The Layout
            [sg.Button(button_text='保存', size=(10, 1))] ]

# Create the window
sg.popup('欢迎您来到'+Translation[KEY_WORD]+'测试界面！')
window = sg.Window(Translation[KEY_WORD]+'测试', layout)      # Part 3 - Window Defintion

play_trigger = False
tempt_track_index = 0
accident_trigeer = False

while True:
    event, values = window.read()                   # Part 4 - Event loop or Window.read call
    # print(event)
    # print(values)
    if event == '保存':      #保存结果
        sg.popup('感谢参与！')
        Reaper.CSurf_OnPause()
        temp = values
        break
    elif event == '播放' and play_trigger == False:
        Reaper.CSurf_OnPlay()
        play_trigger = True
    elif event in ('1','2','3','4','5','6','7'):
        if tempt_track_index == int(event):
            continue
        Reaper.CSurf_OnPause()
        Reaper.RPR_Main_OnCommand(7,0)# unsolo
        tempt_track_index = int(event)
        reaper_media_track = Reaper.GetTrack(0, tempt_track_index-1)
        Reaper.SetOnlyTrackSelected(reaper_media_track) #选中
        Reaper.RPR_Main_OnCommand(7,0)# Solo
        Reaper.CSurf_OnPlay()
        
    elif event == sg.WIN_CLOSED:
        accident_trigeer = True
        sg.popup('点击错误，请重新开始测试！')
        break
    else:
        continue
# Do something with the information gathered

# Finish up by removing from the screen
window.close() 
os.system('taskkill /f /t /im reaper.exe')

if not accident_trigeer:

    First_title = 'E-' if temp[0] == '是' else 'U-' 

    ### 读写模块
    ScoreList = GenerateScoreList(temp)
    temp_dict = ReOrderDict(WAV_list,ScoreList)
    temp_data = Dict2List(Original_WAV_list, temp_dict)

    temp_csv_filename = First_title + folder_list[Song_Item] + '-' + KEY_WORD + '.csv'
    if os.path.exists(temp_csv_filename):
        edit_csv(temp_csv_filename, temp_data)
    else:
        create_csv(temp_csv_filename, Original_WAV_list, temp_data)
