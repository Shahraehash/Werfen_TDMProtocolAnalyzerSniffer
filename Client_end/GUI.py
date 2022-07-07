from re import T
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QObject, QPoint, QSignalMapper, QThread)
from PyQt5.QtWidgets import (QAction, QCheckBox, QComboBox, QFileDialog, QGridLayout,  QHBoxLayout, QHeaderView, QInputDialog, QMainWindow, QMenu, QLineEdit, QLabel, QPushButton, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np
import queue, os, threading, time

import CustomProxyModel, global_variables, PandasModel, recieving_client, sending_client, TableView, TDMArgumentParsing


data_on_queue_for_GUI = queue.Queue()

class DataThread(QObject):
    progress = pyqtSignal()
    
    def __init__(self, number_of_L4s, version_of_board):
        super().__init__()
        self.number_of_L4s = number_of_L4s
        self.version_of_board = version_of_board

    def get_data(self):
        HOST = global_variables.HOST

        print("Starting Clients...")
        sending_client_thread = threading.Thread(target = sending_client.main, args = (HOST, self.version_of_board, self.number_of_L4s))
        sending_client_thread.start()

        recieving_client_thread = threading.Thread(target = recieving_client.main, args = (HOST,))
        recieving_client_thread.start()
        while global_variables.message == 'keep running':
            #once we put data on a queue send the emit signal to connect with on the UI side 
            clientelem = recieving_client.get_data()
            data_on_queue_for_GUI.put(clientelem)
            self.progress.emit()
            time.sleep(0.05)
            

class MainWindow(QMainWindow):
    
    def __init__(self, version_of_board, number_of_L4s):
        super().__init__()
        self.width = 1500
        self.height = 1000
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)

        self.version_of_board = version_of_board
        self.number_of_L4s = number_of_L4s

        #data
        self.column_names = ['Time', 'Source', 'Destination', 'Device', 'Command', 'Status', 'Argument 0', 'Argument 1', 'Argument 2']
        self.dictionary_data = dict()
        for elem in self.column_names:
            self.dictionary_data[elem] = ['']
        self.data = pd.DataFrame(self.dictionary_data)
        self.datatable = TableView.TableViewer(self)
        self.number_of_entries = 0
        self.data_indices = []
        
        #main pane
        main_layout = QVBoxLayout()

        #Buttons:
        buttons_layout = QHBoxLayout()
        #start button
        self.start_btn = QPushButton("Run")
        self.start_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.start_btn.setStyleSheet("background-color : lawngreen")
        self.start_data_collection = False
        self.start_btn.pressed.connect(self.start_process)
        self.time_started = None
        self.time = time.time()
        self.completed_execution = False
        buttons_layout.addWidget(self.start_btn)
        
        '''
        #pause button
        self.pause_btn = QPushButton("Pause")
        self.display_data_collection = False
        self.pause_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pause_btn.setStyleSheet("background-color : yellow")
        self.pause_btn.pressed.connect(self.pause_process)
        buttons_layout.addWidget(self.pause_btn)
        '''
        
        #stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_btn.setStyleSheet("background-color : red")
        self.stop_btn.pressed.connect(self.stop_process)
        buttons_layout.addWidget(self.stop_btn)
        #save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_btn.setStyleSheet("background-color : lightgrey")
        self.save_btn.pressed.connect(self.saveFile)
        buttons_layout.addWidget(self.save_btn)
        #load button
        self.load_btn = QPushButton("Open")
        self.load_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.load_btn.setStyleSheet("background-color : lightgrey")
        self.load_btn.clicked.connect(self.loadFile)
        buttons_layout.addWidget(self.load_btn)
        main_layout.addLayout(buttons_layout)
        
        #Filter pane
        filter_line = QGridLayout()
        self.label = QLabel()
        self.label.setText("Filter:")
        self.combobox = QComboBox()
        self.combobox.addItems(self.column_names)
        self.filter_pane = QLineEdit()
        self.filter_pane.textChanged.connect(self.on_lineEdit_textChanged)
        self.horizontalHeader = self.datatable.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)
        filter_line.addWidget(self.label, 0, 0, 1, 1)
        filter_line.addWidget(self.combobox, 0, 1, 1,1)
        filter_line.addWidget(self.filter_pane, 0, 3, 1, 1)
        main_layout.addLayout(filter_line)
        
        next_line = QGridLayout()
        #Execution Tag
        self.status = QLabel()
        next_line.addWidget(self.status, 0, 0)

        #Filter checkbox for the status_get command
        self.status_get_command_checkbox = QCheckBox()
        self.status_get_command_checkbox.setText("Hide Status-Get Command")
        self.status_get_command_checkbox.setChecked(True)
        self.status_get_command_checkbox.stateChanged.connect(self.filter_command)
        #self.status_get_command_checkbox.setAlignment(Qt.Right)
        next_line.addWidget(self.status_get_command_checkbox, 0, 3)
        main_layout.addLayout(next_line)

        self.filtered_data = pd.DataFrame()
        self.filtered_list_of_explanations = []
        self.filtered_list_of_byte_code = []
         
        #Datatable
        self.datatable.clicked.connect(self.summary)
        main_layout.addWidget(self.datatable)
        
        #Explanation of command
        self.explanation = QLabel()
        self.explanation.setFont(QFont('Arial', 16))
        #self.explanation.setAlignment(Qt.AlignCenter)
        self.source = ""
        self.list_of_explanations = []
        self.explanation.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.explanation)
        

        #Byte Code 
        self.byte_code = QLabel()
        #self.byte_code.setAlignment(Qt.AlignCenter)
        self.list_byte_code_text = []
        self.byte_code.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.byte_code)
        
        #entire window layout
        w = QWidget()
        w.setLayout(main_layout)
        self.setCentralWidget(w)

    def closeEvent(self, event):
        #big red X
        global_variables.Close_Session = True
        self.close()
        event.accept()
        self.thread.quit()
        self.start_data_collection = False

    def get_data(self):
        #get data from queue
        while not data_on_queue_for_GUI.empty():
            data = self.data
            TDM_data = data_on_queue_for_GUI.get()
            if TDM_data != ["empty string"]:

                #check if we have a status from our recieving end
                if TDM_data[0][-2] != '--':
                    self.completed_execution = True
            
                #once we started data collection update them
                if self.display_data_collection:
                    data_from_queue = pd.DataFrame([TDM_data[0][:-1]], columns = self.column_names[1:])
                    time_dataframe = pd.DataFrame([[str(time.time()-self.time)[:5] + " seconds"]], columns = ['Time'])
                    data_to_add = pd.concat([time_dataframe, data_from_queue], axis = 1)
                    self.data = pd.concat([data, data_to_add])
                    self.data = self.data.reindex(columns = self.column_names)

                    #store explanations
                    self.create_and_store_explanations(data_to_add)

                    #byte code from the queue
                    self.list_byte_code_text.append(TDM_data[0][-1])

                    #add buffer once we have recieved a status
                    if self.completed_execution:
                        self.add_buffer()

                    self.update_datatable()
                
                

        self.completed_execution = False
   
    
    def filter_command(self):
        if self.status_get_command_checkbox.isChecked():
            global_variables.Hide_Status_Get_Commands = True 
        else: 
            global_variables.Hide_Status_Get_Commands = False
         

    def create_and_store_explanations(self, raw_row_value):
        #each time you get data you put it on a list to store to reference later
        output_text = ""
        row_value = raw_row_value.iloc[0]
        if str(row_value['Source'])[:4] == 'Host':
            argument_clause = " with no arguments"
            arguments = TDMArgumentParsing.decoding_arguments(TDMArgumentParsing.Host_Frame_Argument_Types, row_value) 
            if arguments != "":
                argument_clause = " with arguments" + arguments
            output_text = str(row_value['Source']) + ' sent ' + str(row_value['Command'][8:]) + ' ' + str(row_value['Device'][7:]) + ' command to ' + str(row_value['Destination'][:len(row_value['Destination'])-1]) + argument_clause + '.'
        if str(row_value['Source'][:4]) == 'node':
            argument_clause = " with no arguments"
            arguments = TDMArgumentParsing.decoding_arguments(TDMArgumentParsing.Node_Frame_Argument_Types, row_value) 
            if arguments != "":
                argument_clause = " with arguments" + arguments
            output_text = str(row_value['Source']) + 'began execution of the ' + str(row_value['Command'][8:]) + ' ' + str(row_value['Device'][7:]) + ' command from ' + str(row_value['Destination']) + argument_clause + ' and had ' + str(row_value['Status'][7:]) + "."
        self.list_of_explanations += [output_text]


    def add_buffer(self):
        #buffer between entries
        data_on_GUI = self.data
        buffer = pd.DataFrame.from_dict(self.dictionary_data)
        self.data = pd.concat([data_on_GUI, buffer])
        self.data = self.data.reindex(columns = self.column_names)
        self.list_byte_code_text += ["--"]
        self.list_of_explanations += [""]

        
    def invoke_data_collection_process(self):
        #invoke threads to put data on the queue
        self.thread = QThread()
        self.data_thread = DataThread(version_of_board = self.version_of_board, number_of_L4s = self.number_of_L4s)
        self.data_thread.moveToThread(self.thread)
        #data has been added to the queue
        self.thread.started.connect(self.data_thread.get_data)
        #get the data once this occurs
        self.data_thread.progress.connect(self.get_data)
        self.thread.start()

    def start_process(self):
        self.status.setText("Running...")
        self.display_data_collection = True
        if self.start_data_collection != True:
            self.invoke_data_collection_process()
            self.start_data_collection = True
        #initiate the time
        self.time = time.time()
        #create the initial datatable template
        self.initial_datatable()
        header = self.datatable.horizontalHeader()
        for i in range(len(self.data.columns)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def initial_datatable(self):
        #add initial entry
        self.list_of_explanations += [""]
        self.list_byte_code_text += ["--"]
        
        df_as_pandas_model = PandasModel.PandasModel(self.data)
        self.model = df_as_pandas_model
        self.proxy = CustomProxyModel.CustomProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.datatable.setModel(self.proxy)

    def update_datatable(self):
        df_as_pandas_model = PandasModel.PandasModel(self.data)
        self.model = df_as_pandas_model
        self.proxy = CustomProxyModel.CustomProxyModel()
        self.proxy.setSourceModel(self.model)
        self.datatable.setModel(self.proxy)

    '''
    def pause_process(self):
        self.status.setText("Execution is paused")
        self.display_data_collection = False
    '''

    def stop_process(self):
        #stop data collection
        self.display_data_collection = False
        self.status.setText("All execution has been stopped")
    

    def change_explanation(self, list_of_explanation, dataframe_idx):
        #explanation textbox
        self.explanation.setText(list_of_explanation[dataframe_idx])                                     
    
    def change_byte_code(self, list_of_byte_code, dataframe_idx):
        #byte code textbox
        text = '<font color="black">'
        if list_of_byte_code[dataframe_idx] == "--":
            text = ""
        else:
            byte_code_elem = list_of_byte_code[dataframe_idx]
            tab_space_character = '&nbsp;'*8
            break_point_character = '<br>'

            #host frame
            if len(byte_code_elem) == 111:
                for elem in byte_code_elem[:4]:
                    text += global_variables.conv_byte(elem)
                text += break_point_character
                for i in range(int(self.number_of_L4s)):
                    tab_separator = 0
                    first_three_ids = True
                    first_node_values = False
                    for elem in byte_code_elem[15*i+4:15*(i+1)+4]:
                        text += global_variables.conv_byte(elem)
                        tab_separator += 1
                        if first_three_ids:
                            if tab_separator == 3:
                                text += tab_space_character
                                tab_separator = 0
                                first_three_ids = False
                                first_node_values = True
                        else:
                            if tab_separator == 4:
                                text += tab_space_character
                                tab_separator = 0
                    if first_node_values:
                        text += '</font><font color="gray">'
                        first_node_values = False
                    text += break_point_character
                text += '</font><font color = "black">'
                for elem in byte_code_elem[-2:]:
                    text += global_variables.conv_byte(elem)
                text += '</font>'

            #node frame
            elif len(byte_code_elem) == 18:
                tab_separator = 0
                for elem in byte_code_elem:
                    text += global_variables.conv_byte(elem)
                    tab_separator += 1
                    if tab_separator == 4:
                        text += tab_space_character
                        tab_separator = 0
                text += '</font>'
        self.byte_code.setText(text) 
    
    def summary(self):
        #initiate the summary of the results by calling the explanation and the byte code
        dataframe_idx = self.datatable.dataframe_idx

        self.filtered_list_of_byte_code = self.list_byte_code_text
        self.filtered_list_of_explanations = self.list_of_explanations
        if self.proxy.list_kept_indices != []:
            self.filtered_list_of_explanations = []
            self.filtered_list_of_byte_code = []
            for idx in self.proxy.list_kept_indices:       
                self.filtered_list_of_explanations += [self.list_of_explanations[idx]]
                self.filtered_list_of_byte_code += [self.list_byte_code_text[idx]]

        if dataframe_idx >= 0 and dataframe_idx < self.data.shape[0]:
            self.change_explanation(self.filtered_list_of_explanations, dataframe_idx)
            self.change_byte_code(self.filtered_list_of_byte_code, dataframe_idx)
        

    def saveFile(self):
        #save the dataframe
        name, _ = QInputDialog.getText(self, 'Input Dialog', 'Enter file name:')
        path = str(os.path.dirname(os.path.abspath(__file__))) + "/" + str(name) + '.csv'
        self.add_explanation_to_csv()
        self.add_byte_code_to_csv()
        self.data.to_csv(path, index = False)
    
    def add_explanation_to_csv(self):
        self.data['Explanations'] = list(self.list_of_explanations)
    
    def add_byte_code_to_csv(self):
        self.data['Byte Code'] = list(self.list_byte_code_text)
        
    def loadFile(self):
        #load a saved dataframe 
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)");
        df = pd.read_csv(fileName)

        self.list_of_explanations = df['Explanations'].replace(np.nan, "").tolist()

        raw_byte_code_from_df = df['Byte Code'].tolist()
        list_byte_code_input = []
        for elem in raw_byte_code_from_df:
            if elem == "--":
                list_byte_code_input += ["--"]
            else:
                elem_list = []
                for item in elem.split(","):
                    elem_list += [item]
                list_byte_code_input += [elem_list]
        self.list_byte_code_text = list_byte_code_input


        data = df.drop(columns = ['Explanations', 'Byte Code'], axis = 1)
        data.fillna('', inplace=True)
        self.data = data

        load_model = PandasModel.PandasModel(self.data)
        self.model = load_model
        self.proxy = CustomProxyModel.CustomProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.datatable.setModel(self.proxy)
        header = self.datatable.horizontalHeader()
        for i in range(len(self.data.columns)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
    
    
    @pyqtSlot(int)
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        #drop down from each header of the table
        self.logicalIndex   = logicalIndex
        self.menuValues     = QMenu(self)
        self.signalMapper   = QSignalMapper(self)

        valuesUnique = self.model._data.iloc[:, self.logicalIndex].unique()

        #add the values to the drop down
        actionAll = QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()
        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):
            action = QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)
            action.triggered.connect(self.signalMapper.map)
            self.menuValues.addAction(action)
        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)
        headerPos = self.datatable.mapToGlobal(self.horizontalHeader.pos())
        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QPoint(posX, posY))

    @pyqtSlot()
    def on_actionAll_triggered(self):
        #the all option in the drop down
        filterColumn = self.logicalIndex
        self.proxy.list_kept_indices = []
        self.proxy.setFilter("", filterColumn)

    @pyqtSlot(int)
    def on_signalMapper_mapped(self, i):
        #set the respective filter according to dropdown
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        self.proxy.setFilter(stringAction, filterColumn)

    @pyqtSlot(str)
    def on_lineEdit_textChanged(self, searchtext):
        #setting filter based on text entered on the line
        self.proxy.setFilter(searchtext, self.combobox.currentIndex())

