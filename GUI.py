from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QModelIndex, QObject, QPoint, QRect, QSortFilterProxyModel, QSignalMapper, Qt, QThread, QTimer)
from PyQt5.QtWidgets import (QAction, QApplication, QButtonGroup, QCheckBox, QComboBox, QFileDialog, QGridLayout,  QHBoxLayout, QHeaderView, QInputDialog, QMainWindow, QMenu, QLineEdit, QLabel, QPlainTextEdit, QPushButton, QRadioButton, QSpinBox, QTableView, QVBoxLayout, QWidget)
from PyQt5.QtGui import QFont, QStandardItemModel
import pandas as pd
import numpy as np
import threading, queue, os, time

#import server
import client
import PandasModel
import CustomProxyModel
import TableView
import main


#NUMBER_OF_L4s = 7
#Recieve_Status_Get_Commands = True 


data_on_queue_for_GUI = queue.Queue()

client_thread = threading.Thread(target = client.main)

class DataThread(QObject):
    progress = pyqtSignal()
    
    def get_data(self):
        #create client and server threads
        #server_thread = threading.Thread(target = server.main)
        #server_thread.start()
        #client_thread = threading.Thread(target = client.main)
        client_thread.start()
        while True:
            #once we put data on a queue send the emit signal to connect with on the UI side 
            clientelem = client.get_data()
            data_on_queue_for_GUI.put(clientelem)
            self.progress.emit()
            time.sleep(0.5)
            

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.width = 1000
        self.height = 800
        self.setFixedWidth(self.width)
        self.setFixedHeight(self.height)

        self.version_of_board = main.version_of_board
        self.number_of_L4s = main.number_of_L4s

        '''
        #Choose version of firware that you are running
        self.button_group = QButtonGroup()
        self.radio_button1 = QRadioButton('P1A')
        self.radio_button2 = QRadioButton('P1B')
        self.button_group.addButton(self.radio_button1)
        self.radio_button1.toggled.connect(self.p1a_settings)
        self.button_group.addButton(self.radio_button2)
        self.radio_button2.toggled.connect(self.p1b_settings)
        
        #close window
        self.close_window_button = QPushButton("Close Window")
        self.close_window_button.pressed.connect(self.close_session)


        #Radio_buttons
        button_layout_top = QGridLayout()
        button_layout_top.addWidget(self.radio_button1, 0, 0)
        button_layout_top.addWidget(self.radio_button2, 0, 1)

        button_layout_top.addWidget(self.close_window_button, 0, 3)
        main_layout.addLayout(button_layout_top)
        '''


        #data
        self.column_names = []
        if self.version_of_board.lower() == "p1a":
            self.column_names = ['Time', 'Source', 'Destination', 'Device', 'Status']
        if self.version_of_board.lower() == "p1b":
            self.column_names = ['Time', 'Source', 'Destination', 'Device', 'Command', 'Status']
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
        self.start_btn.setStyleSheet("background-color : lawngreen")
        self.start_data_collection = False
        self.start_btn.pressed.connect(self.start_process)
        self.time_started = None
        self.time = time.time()
        self.completed_execution = False
        buttons_layout.addWidget(self.start_btn)
        #stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background-color : red")
        self.stop_btn.pressed.connect(self.stop_process)
        buttons_layout.addWidget(self.stop_btn)
        #save button
        self.save_btn = QPushButton("Save")
        self.save_btn.setStyleSheet("background-color : lightskyblue")
        self.save_btn.pressed.connect(self.saveFile)
        buttons_layout.addWidget(self.save_btn)
        #load button
        self.load_btn = QPushButton("Open", self)
        self.load_btn.setStyleSheet("background-color : burlywood")
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
        
        next_line = QHBoxLayout()
        #Execution Tag
        self.status = QLabel()
        next_line.addWidget(self.status)

        '''
        #Number_of_L4s
        self.number_of_L4s = QSpinBox()
        #self.number_of_L4s.setText("Number of L4s:")
        self.number_of_L4s.setRange(1,20)
        self.number_of_L4s.valueChanged.connect(self.number_of_L4_changed)
        next_line.addWidget(self.number_of_L4s)
        '''

        #Filter checkbox for the status_get command
        self.status_get_command_checkbox = QCheckBox()
        self.status_get_command_checkbox.setText("See Status-get Commands")
        #self.status_get_command_checkbox.stateChanged.connect(self.filter_command)
        next_line.addWidget(self.status_get_command_checkbox)
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
        self.list_byte_code_text = ['--']
        self.byte_code.setStyleSheet("border: 1px solid black;")
        main_layout.addWidget(self.byte_code)
        
        #entire window layout
        w = QWidget()
        w.setLayout(main_layout)
        self.setCentralWidget(w)
    '''
    def p1a_settings(self):
        self.column_names = ['Time', 'Source', 'Destination', 'Device', 'Status']
        self.dictionary_data = dict()
        for elem in self.column_names:
            self.dictionary_data[elem] = ['']
        self.data = pd.DataFrame.from_dict(self.dictionary_data)
        self.combobox.addItems(self.column_names)

    def p1b_settings(self):
        self.column_names = ['Time', 'Source', 'Destination', 'Device', 'Command', 'Status']
        self.dictionary_data = dict()
        for elem in self.column_names:
            self.dictionary_data[elem] = ['']
        self.data = pd.DataFrame.from_dict(self.dictionary_data)
        self.combobox.addItems(self.column_names)

    def close_session(self):
        client.close_connection()
        self.close()
        main.close_session()
    '''

    def closeEvent(self, event):
        client.close_connection()
        self.close()
        main.close_session()
        event.accept()

    '''
    def number_of_L4_changed(self):
        client.NUMBER_OF_L4s = self.number_of_L4s.value()
    '''

    def get_data(self):
        #get data from queue
        while not data_on_queue_for_GUI.empty():
            data = self.data
            TDM_data = data_on_queue_for_GUI.get()
            
            #check if we have a status from our recieving end
            if TDM_data[0][-2] != '--':
                self.completed_execution = True
            
            #concat with original dataframe
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
                
            #once we started data collection update them
            if self.start_data_collection:
                '''
                if self.status_get_command_checkbox.isChecked():
                    #self.datatable.clear()
                    self.filter_command()
                else:
                    #self.datatable.clear()
                    self.update_datatable()
                '''
                self.update_datatable()

        self.completed_execution = False
   
    
    def filter_command(self):
        if self.status_get_command_checkbox.isChecked():
            client.Recieve_Status_Get_Commands = True 
        else: 
            client.Recieve_Status_Get_Commands = False
        '''
        #if self.status_get_command_checkbox.isChecked():
        keep_rows = self.data.index[self.data['Status'] != "COMMAND_status_get"]

        self.filtered_data = self.data.loc[keep_rows]
        df_as_pandas_model2 = PandasModel.PandasModel(self.filtered_data)
        self.model2 = df_as_pandas_model2
        self.proxy2 = CustomProxyModel.CustomProxyModel()
        self.proxy2.setSourceModel(self.model2)
        #self.proxy.setFilterKeyColumn(1)
        self.datatable.setModel(self.proxy2)

        self.filtered_list_of_explanations = []
        self.filtered_list_of_byte_code = []
        for index in range(len(keep_rows.values.tolist())):
            self.filtered_list_of_explanations += [self.list_of_explanations[index]]
            self.filtered_list_of_byte_code += [self.list_byte_code_text[index]]
        
        else:
            df_as_pandas_model = PandasModel.PandasModel(self.data)
            self.model = df_as_pandas_model
            self.proxy = CustomProxyModel.CustomProxyModel(self)
            self.proxy.setSourceModel(self.model)
            #self.proxy.setFilterKeyColumn(1)
            self.datatable.setModel(self.proxy)
        '''   
         

    def create_and_store_explanations(self, raw_row_value):
        #each time you get data you put it on a list to store to reference later
        output_text = ""
        row_value = raw_row_value.iloc[0]
        if str(row_value['Source'])[:4] == 'Host':
            self.source = 'Host'
            if self.version_of_board.lower() == "p1a":
                output_text = str(row_value['Source']) + ' sent a command to ' + str(row_value['Destination'][:len(row_value['Destination'])-1]) + '.'
            if self.version_of_board.lower() == "p1b":
                output_text = str(row_value['Source']) + ' sent ' + str(row_value['Command'][8:]) + ' ' + str(row_value['Device'][7:]) + ' command to ' + str(row_value['Destination'][:len(row_value['Destination'])-1]) + '.'
        if str(row_value['Source'][:4]) == 'node':
            self.source = 'Node'
            if self.version_of_board.lower() == "p1a":
                output_text = str(row_value['Source']) + 'began execution of the command from ' + str(row_value['Destination']) + ' and had ' + str(row_value['Status'][7:]) + "."
            if self.version_of_board.lower() == "p1b":
                output_text = str(row_value['Source']) + 'began execution of the ' + str(row_value['Command'][8:]) + ' ' + str(row_value['Device'][7:]) + ' command from ' + str(row_value['Destination']) + ' and had ' + str(row_value['Status'][7:]) + "."
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
        self.data_thread = DataThread()
        self.data_thread.moveToThread(self.thread)
        #data has been added to the queue
        self.thread.started.connect(self.data_thread.get_data)
        #get the data once this occurs
        self.data_thread.progress.connect(self.get_data)
        self.thread.start()

    def start_process(self):
        self.status.setText("Running...")
        #data collection begins
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
        data_table = self.data 
        #initial_time = str(0.0000)
        time_dataframe = pd.DataFrame([[""]], columns = ['Time'])
        if "Time" not in data_table.columns:
            self.data = pd.concat([time_dataframe, data_table], axis = 1)
            self.data = self.data.reindex(columns = self.column_names)
        
        
        df_as_pandas_model = PandasModel.PandasModel(self.data)
        self.model = df_as_pandas_model
        self.proxy = CustomProxyModel.CustomProxyModel(self)
        self.proxy.setSourceModel(self.model)
        #self.proxy.setFilterKeyColumn(1)
        self.datatable.setModel(self.proxy)

        #add initial entry
        self.list_of_explanations += ['']

    def update_datatable(self):
        df_as_pandas_model = PandasModel.PandasModel(self.data)
        self.model = df_as_pandas_model
        self.proxy = CustomProxyModel.CustomProxyModel()
        self.proxy.setSourceModel(self.model)
        #self.proxy.setFilterKeyColumn(1)
        self.datatable.setModel(self.proxy)

    def stop_process(self):
        print("trying to stop")
        #stop data collection
        self.start_data_collection = False
        self.status.setText("All execution has been stopped")
    

    def change_explanation(self, list_of_explanation, dataframe_idx):
        #explanation textbox
        self.explanation.setText(list_of_explanation[dataframe_idx])                                     
    
    def change_byte_code(self, list_of_byte_code, dataframe_idx):
        #byte code textbox
        text = ""
        if list_of_byte_code[dataframe_idx] == "--":
            text = ""
        else:
            byte_code_elem = list_of_byte_code[dataframe_idx]
            until_enter = 0
            for elem in byte_code_elem:
                elem_in_list = str(elem).split('x')
                for i in range(1,len(elem_in_list)):
                    text += str(elem_in_list[i][:2]) + " "
                text += "\t"
                until_enter += 1
                if self.source == "Host":
                    if until_enter == 8:
                        text += '\n'
                        until_enter = 0
                if self.source == "Node":
                    if until_enter == 6:
                        text += '\n'
                        until_enter = 0
        self.byte_code.setText(text)
    
    def summary(self):
        #initiate the summary of the results by calling the explanation and the byte code
        dataframe_idx = self.datatable.dataframe_idx
        if dataframe_idx > 0 and dataframe_idx < self.data.shape[0]:
            list_of_explanations = []
            list_of_byte_code = []
            
            if self.status_get_command_checkbox.isChecked():
                list_of_explanations = self.filtered_list_of_explanations
                list_of_byte_code = self.filtered_list_of_byte_code
            else:
                list_of_explanations = self.list_of_explanations
                list_of_byte_code = self.list_byte_code_text

            self.change_explanation(list_of_explanations, dataframe_idx)
            self.change_byte_code(list_of_byte_code, dataframe_idx)
        

    def saveFile(self):
        #save the dataframe
        name, _ = QInputDialog.getText(self, 'Input Dialog', 'Enter file name:')
        path = str(os.path.dirname(os.path.abspath(__file__))) + "/" + str(name) + '.csv'
        self.add_explanation_to_csv()
        self.add_byte_code_to_csv()
        self.data.to_csv(path, index = False)
    
    def add_explanation_to_csv(self):
        self.data['Explanations'] = self.list_of_explanations
    
    def add_byte_code_to_csv(self):
        self.data['Byte Code'] = self.list_byte_code_text
        
    def loadFile(self):
        #load a saved dataframe 
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)");
        df = pd.read_csv(fileName)

        self.list_of_explanations = df['Explanations']
        self.list_byte_code_text = df['Byte Code']

        data = df.drop(columns = ['Explanations', 'Byte Code'], axis = 1)
        data.fillna('', inplace=True)
        self.data = data

        load_model = PandasModel.PandasModel(self.data)
        self.model = load_model
        self.datatable.setModel(self.model)
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
        self.proxy.setFilter("", filterColumn)

    @pyqtSlot(int)
    def on_signalMapper_mapped(self, i):
        #set the respective filter accordingly
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        self.proxy.setFilter(stringAction, filterColumn)

    @pyqtSlot(str)
    def on_lineEdit_textChanged(self, searchtext):
        #choosing what to filter on the line
        self.proxy.setFilter(searchtext, self.combobox.currentIndex())
