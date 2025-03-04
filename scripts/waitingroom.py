from tkinter import *
from tkinter.filedialog import askopenfile
import os, requests, threading, random, json, shutil, cv2

#os.chdir("..")

ws = Tk()
ws.title('Waiting Room')
ws.geometry('475x320')
ws.config(bg='#c9c9c9')
ws.resizable(False, False)

server_link = open("data\\current_server.txt", "r").read()
player_name = open("data\\player.txt", "r").read().strip().replace("\n", "")

port = open("data\\server_id.txt", "r").read()

delay_between_download = 3000
not_downloaded = True
initial_upload = False

players = []

noquit = True
admin = False

for x in range(4):
    if os.path.exists(f"assets\\interface\\{str(x)}.png"):
        os.remove(f"assets\\interface\\{str(x)}.png")

if os.path.exists("assets\\interface\\flag.png"):
    os.remove("assets\\interface\\flag.png")
shutil.copyfile("assets\\flag.png", "assets\\interface\\flag.png")

# 213 x 128

"""
Base JSON : 

{"Countrys": [{"Georgian Republic": "['n', [163, 59, 42], 0, 0, 1, 0]", "Armenian Republic": "['n', [207, 174, 43], 0, 0, 1, 0]"}], "Map": [{"Georgian Republic": [], "Armenian Republic": []}], "Data": [{"turn": 1, "mri": false}], "Forts": [{"1": [], "2": [], "3": []}]}


"""

def open_flag():
    file = askopenfile(filetypes =[('Photos', '*.png')])

    if os.path.exists("assets\\interface\\flag.png"):
        os.remove("assets\\interface\\flag.png")
    
    shutil.copyfile(file.name, "assets\\interface\\flag.png")

    image = cv2.imread("assets\\interface\\flag.png")

    resized_image = cv2.resize(image, (213, 128))

    cv2.imwrite("assets\\interface\\flag.png", resized_image)

    flag_upload()

    


def start():
    global noquit
    noquit = False

    server_data_file = open(f'data\\server_data.json')
    server_data_file = json.load(server_data_file)

    for i in server_data_file['Server Data']:
        if i == 'started':
            server_data_file['Server Data'][i] = True
            print(server_data_file['Server Data'][i])

    with open("data\\server_data.json", 'w') as fp:
        json.dump(server_data_file, fp)

    upload_server_json()

    ws.destroy()
    #os.system("start main")

    for player in players:
        if player != player_name:
            id = players.index(player)
            download_flags(id)
    import main
    #os.system("python scripts\\main.py")
    quit()

def initial_base_upload():
    url = f'{server_link}/{port}/upload_redirect'
    nm = 'data\\info.json'

    f = open("data\\infobase.txt")

    with open(nm, 'w') as fp:
        fp.write(f.read())
    
    nmrb = open(nm, 'rb')

    files = [('file', nmrb)]

    r = requests.post(url, files=files)

    if r.ok:
        print("Uploaded JSON Succesfully")
    else:
        print("Error when trying to upload JSON to server !!!")

def flag_upload():
    global image, image_label
    url = f'{server_link}/1/upload_flag'
    nm = f'assets\\interface\\{players.index(player_name)}.png'

    os.system(f'copy assets\\interface\\flag.png assets\\interface\\{players.index(player_name)}.png')
    
    nmrb = open(nm, 'rb')

    files = [('file', nmrb)]

    r = requests.post(url, files=files)

    image = PhotoImage(file="assets\\interface\\flag.png")
    image_label.config(image=image)

    if r.ok:
        print("Uploaded JSON Succesfully")
    else:
        print("Error when trying to upload JSON to server !!!")

def download_flags(flag):
    
    url = f'{server_link}1/download_flag/{str(flag)}'

    print("Downloading Country Flags")
    
    os.system(f'del assets\\interface\\{str(flag)}.png')

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(f'assets\\interface\\{str(flag)}.png', 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def upload_base_info_json():

    url = f'{server_link}/{port}/upload_redirect'
    nm = 'data\\info.json'

    fp = open(nm)

    js = json.load(fp)

    random.randrange(200)

    for player in players:
        js["Countrys"][0][player] = f"['n', [{str(random.randrange(200))}, {str(random.randrange(200))}, {str(random.randrange(200))}], 1, 0, 1, 0]"
        js["Map"][0][player] = []

    with open(nm, 'w') as fpp:
        json.dump(js, fpp)


    nmrb = open(nm, 'rb')

    files = [('file', nmrb)]

    r = requests.post(url, files=files)

    if r.ok:
        print("Uploaded JSON Succesfully")
    else:
        print("Error when trying to upload JSON to server !!!")

    nmrb.close()

def upload_server_json():
    url = f'{server_link}/upload_server_data'
    nm = 'data\\server_data.json'


    nmrb = open(nm, 'rb')

    files = [('file', nmrb)]

    r = requests.post(url, files=files)

    if r.ok:
        print("Uploaded JSON Succesfully")
    else:
        print("Error when trying to upload JSON to server !!!")

    nmrb.close()

def update_list():
    global players, admin, added_to_lb, admin_label

    print("BOOM")

    server_data_file = open(f'data\\server_data.json')
    server_data_file = json.load(server_data_file)

    for i in server_data_file['Server Data']:
        if i == 'players':
            players = server_data_file['Server Data'][i]

    i = 0

    lb.delete(0,END)

    for player in players:
        i += 1
        
        lb.insert(i, f"{i}. " + player)

    if players == [player_name]:
        admin = True

    if admin:
        admin_label.config(text = "You are Admin", fg = "green")
    else:
        admin_label.config(text = "You are NOT Admin", fg = "red")

    if len(players) > 1 and admin:
        btn["state"] = "active"
    if len(players) > 5 and admin:
        btn["state"] = "disabled"

def real_download():
    global not_downloaded
    not_downloaded = True

    url = f'{server_link}/return_data'

    while not_downloaded:
        if not os.path.isfile("data\\server_data.json"):

            with requests.get(url, stream=True) as r: # for downloading server data ONCE
                r.raise_for_status()
                with open('data\\server_data.json', 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

        else:
            not_downloaded = False
        
        print(not_downloaded)

def download_server_json_periodicaly():
    global not_downloaded, initial_upload

    print("Downloading Server Data")
    
    os.system('del data\\server_data.json')

    upload_base_info_json()

    t1 = threading.Thread(target=real_download)
    t1.start()
    t1.join()

    if not not_downloaded:

        server_data_file = open(f'data\\server_data.json')
        server_data_file = json.load(server_data_file)

        for i in server_data_file['Server Data']:
            if i == 'started':
                if server_data_file['Server Data'][i] == True:
                    global noquit
                    noquit = False

                    for player in players:
                        if player != player_name:
                            id = players.index(player)
                            download_flags(id)

                    ws.destroy()
                    #os.system("start main")
                    #os.system("python scripts\\main.py")
                    import main
        
        update_list()
    
    if not initial_upload:
        flag_upload()
        initial_upload = True

    ws.after(delay_between_download,download_server_json_periodicaly)

initial_base_upload()

btn = Button(ws, text = 'Start Game', bd = '1', command = start, font=('Consolas 9'),height = 2, width = 15, )
btn2 = Button(ws, text = 'Upload Flag', bd = '1', command = open_flag, font=('Consolas 9'),height = 1, width = 12, )
btn["state"] = "disabled"

var = StringVar()
email = Label(ws, textvariable=var)
var.set("Game may start once 2-5 players are in the waiting room")

label = Label(ws, text = " Players : ") 
admin_label = Label(ws, text = "You are NOT Admin", fg = "red") 

lb = Listbox(ws, height = 10, 
                  width = 15, 
                  bg = "lightgrey",
                  activestyle = 'dotbox',
                  fg = "black")

image = PhotoImage(file="assets\\interface\\flag.png")

image_label = Label(ws, image=image)
image_label.place(x=120, y=60)

lb.place(x=10, y=60)
label.place(x=10, y=40)
admin_label.place(x=350, y=40)

btn.place(x=350, y=275)
btn2.place(x=120, y=200)
email.place(x=12, y=288)

def on_closing():
    global noquit
    noquit = False
    server_data_file = open(f'data\\server_data.json')
    server_data_file = json.load(server_data_file)

    for i in server_data_file['Server Data']:
        if i == 'players':
            players_in_lobby = server_data_file['Server Data'][i]

    c = -1

    for player in players_in_lobby:
        c += 1
        if player == player_name:
            print("WOA", player, player_name)
            del server_data_file['Server Data'][i][c]

            with open("data\\server_data.json", 'w') as fp:
                json.dump(server_data_file, fp)

    upload_server_json()

    ws.destroy()
    quit()

ws.after(100,download_server_json_periodicaly)
ws.protocol("WM_DELETE_WINDOW", on_closing)

ws.mainloop()
