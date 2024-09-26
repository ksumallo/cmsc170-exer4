from os import listdir, path

import typing, pathlib
from math import prod
from functools import reduce
from decimal import Decimal
from tkinter import Label, Button, Scrollbar, Frame, Tk
from tkinter import filedialog


def cleanse(str):
    new_str = ""
    for c in str.lower():
        if (ord(c) <= ord('z') and ord(c) >= ord('a')):
            new_str += c
    return new_str

class BagOfWords:
    def __init__(self):
        #-------------# GUI #-------------#
        self.root = Tk()
        self.root.title = "Bag-of-Words"

        self.frame = Frame(self.root, padx=32, pady=32)
        self.frame.pack()

        self.title = Label(self.frame, text="Bag-of-Words", font=("Arial", "16", "bold"))
        self.title.pack()
        
        self.subtitle = Label(self.frame, text="CMSC 170 – GH-4L", font=("Arial", "12"))
        self.subtitle.pack()

        self.name = Label(self.frame, text="Kurt Princip Gavryl T. Sumallo", font=("Arial", "12"))
        self.name.pack()

        self.btn_select_folder = Button(self.frame, text="Select folder", command=self.pick_folder)
        self.btn_select_folder.pack()

        self.text_dict_size = Label(self.frame, text="Dictionary Size:", padx=4, pady=4)
        self.text_dict_size.pack()

        self.text_word_count = Label(self.frame, text="Total Word Count:", padx=4, pady=4)
        self.text_word_count.pack()

    def start(self):
        self.root.mainloop()

    def pick_folder(self):
        parent = filedialog.askdirectory()

        folders = []
        if parent:
            folders = listdir(parent)

        self.read_files(parent)
        
    def read_files(self, parent):
        ham = {}
        spam = {}

        # Create BOW model
        for folder in ("ham", "spam"):
            dict = {}
            files = listdir(f"{parent}/{folder}")
            for filename in files:
                file = open(f"{parent}/{folder}/{filename}", encoding="latin1")

                while True:
                    line = file.readline()
                    if not line: break # EOF
                    else: 
                        words = [cleanse(word) for word in line.split() if word is not None or len(word) > 0]

                        if len(words) > 0:
                            for word in words:
                                if word not in dict.keys():
                                    dict[word] = 1
                                else: dict[word] += 1
                file.close()
            del dict[""]
            if (folder == "ham"):
                ham = dict
            elif (folder == "spam"):
                spam = dict

        
        ham_m_count = len(listdir(f"{parent}/ham"))
        spam_m_count = len(listdir(f"{parent}/spam"))
        threshold = 0.5
        k = 0.01 # TODO: Determine domain
        messages = {}
        messages_new_words = {}
        for file in listdir(f"{parent}/classify"):
            new_words = set()
            print(f"Analyzing {file}")
            message = {}

            # Create BOW per message
            _file = open(f"{parent}/classify/{file}", encoding="latin1")
            while True:
                line = _file.readline()
                if not line: break # EOF
                else: 
                    words = [cleanse(word) for word in line.split() if word is not None or len(word) > 0]

                    if len(words) > 0:
                        for word in words:
                            if word not in message.keys():
                                message[word] = 1
                            else: message[word] += 1

                            if word not in spam.keys() and word not in ham.keys() and word != "":
                                new_words.add(word)
            del message[""]
            messages_new_words[file] = len(new_words)
            _file.close()

            dict_size = len(set(list(ham.keys()) + list(spam.keys())))
            new_words_count = messages_new_words[file]

            P_Ham = (ham_m_count + k)/(ham_m_count + spam_m_count + 2*k)
            P_Spam = (spam_m_count + k)/(ham_m_count + spam_m_count + 2*k)

            total_H = sum(ham.values())
            total_S = sum(spam.values())

            P_w_Ham = reduce(lambda a, b: a*b, [Decimal(ham.get(word, 0) + k)/Decimal(len(ham) + (k*dict_size*messages_new_words[file])) for word in message]) # prod()
            P_w_Spam = reduce(lambda a, b: a*b, [Decimal(spam.get(word, 0) + k)/(Decimal(len(spam) + (k*dict_size*messages_new_words[file]))) for word in message]) # prod([Decimal(spam.get(word, 0))/Decimal(total_S) for word in message])

            # for word in message:
            #     print("%s : %f" % (word, Decimal(spam.get(word, 0))/Decimal(len(spam))))

            print("Dictionary Size:", dict_size, "  New Words:", new_words_count)
            print("P(Ham)=%.15f ; P(Spam)=%.15f" % (P_Ham, P_Spam))
            print("P(w|Ham)=%.25f ; P(w|Spam)=%.25f\n" % (P_w_Ham, P_w_Spam))
            P_Spam_m = (Decimal(P_w_Spam) * Decimal(P_Spam)) / (Decimal(P_w_Spam) * Decimal(P_Spam) + Decimal(P_w_Ham) * Decimal(P_Ham))

            messages[file] = P_Spam_m

        # Export
        # del dict[""]    # Workaround to remove empty strings in the dictionary
        out_file_name = "classify.out"
        all_words = sorted(messages.keys())

        with open(out_file_name, "w+") as out_file: 
            total_words = sum(messages.values())
            dict_size = len(messages.keys())
            out_file.write("SPAM\n")
            out_file.write(f"Total Words: {sum(spam.values())}\n")
            out_file.write(f"Dictionary Size: {len(spam)}\n\n")

            out_file.write("HAM\n")
            out_file.write(f"Total Words: {sum(ham.values())}\n")
            out_file.write(f"Dictionary Size: {len(ham)}\n\n")

            for file in all_words:
                out_file.write(f"%s\t%s\t%s\n" % (file, "SPAM" if messages[file] > 0.5 else "HAM", messages[file]))
                    

BagOfWords().start()
