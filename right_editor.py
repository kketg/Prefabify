from PyQt5.QtWidgets import * 
from PyQt5.QtGui import *
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import *
import data
from data import Package
import os

# List Widget for image_list
class ImageListItem(QListWidgetItem):
    def __init__(self, name, bytes):
        super().__init__()
        self.image_tuple = (name,bytes)
        self.setText(name)

# Right half of Editor GUI
class RightLayout(QVBoxLayout):
    data_changed_signal = QtCore.pyqtSignal()
    def __init__(self, package : Package):
        super().__init__()
        self.image_label = QLabel("Image")
        self.addWidget(self.image_label)

        self.selected_item = -1

        # Add text box under image with scroll bar
        self.image_list = QListWidget()
        for tuple in package.images:
            self.image_list.addItem(ImageListItem(tuple[0], tuple[1]))

        self.image_list.itemClicked.connect(self.image_clicked)



        # attempting to load images as bytes & sets up list widget
        self.pixmap = QPixmap()
        self.image_display = QLabel()
        self.image_display.resize(256,256)
        self.addWidget(self.image_display)
        self.render_image(0)
        self.image_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.image_list.itemDoubleClicked.connect(self.render_widget)
        self.addWidget(self.image_list)

        # Create HBox for buttons
        right_button_container = QHBoxLayout()
        right_new = QPushButton("New")
        right_new.clicked.connect(self.open_image_button)
        right_new.setToolTip("Opens a new image")
        right_setdef = QPushButton("Set As Default")
        right_setdef.clicked.connect(self.set_as_default_button)
        right_setdef.setToolTip("Sets selected image as default")
        right_rename = QPushButton("Rename")
        right_rename.clicked.connect(self.rename_image_button)
        right_rename.setToolTip("Renames selected image")
        right_delete = QPushButton("Delete")
        right_delete.clicked.connect(self.delete_image_button)
        right_delete.setToolTip("Deletes selected image")
        right_button_container.addWidget(right_new)
        right_button_container.addWidget(right_setdef)
        right_button_container.addWidget(right_rename)
        right_button_container.addWidget(right_delete)
        r_spacer = QSpacerItem(60, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # add spacer to move buttons to left side
        right_button_container.addItem(r_spacer)
        self.addLayout(right_button_container)

        self.error = QMessageBox()
        self.error.setIcon(3)
        self.error.setWindowTitle("Error")

    def image_clicked(self, item):
        self.selected_item = self.image_list.row(item)

    def open_image_button(self):
        name, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Portable Network Graphics (*.png)")
        if name == "":
            return
        with open(name, "rb") as f:
            b = bytearray(f.read())
            image_name = os.path.basename(name).split('.')[0]
            ili = ImageListItem(image_name, b)
            self.image_list.addItem(ili)
        self.data_changed_signal.emit()

    def set_as_default_button(self):
        i = self.selected_item
        if i < 0:
            self.error.setText("GUI Error\n\nPlease Select an Image")
            self.error.show()
        else:
            item = self.image_list.item(i)
            self.image_list.takeItem(i)
            self.image_list.insertItem(0,item)
            self.render_image(0)
            self.selected_item = 0
            self.data_changed_signal.emit()
    
    def rename_image_button(self):
        if self.selected_item < 0:
            self.error.setText("GUI Error\n\nPlease Select an Image")
            self.error.show()
        else:
            text, okPressed = QInputDialog.getText(None, "Rename Image", "New Name:")
            if okPressed and text != "":
                item = self.image_list.item(self.selected_item)
                item.setText(text)
                self.data_changed_signal.emit()
            else:
                self.error.setText("GUI Error\n\nPlease Enter a Valid Name")
                self.error.show()

    def delete_image_button(self):
        if self.selected_item < 0:
            self.error.setText("GUI Error\n\nPlease Select an Image")
            self.error.show()
        else:
            name = self.image_list.item(self.selected_item).text()
            box = QMessageBox
            ret = box.question(None, "", f"Are you sure you want to delete {name}?", box.Yes | box.No)
            if ret == box.No:
                return
            else:
                self.delete_image(self.selected_item)
                self.data_changed_signal.emit()
                self.selected_item = -1


    # Converts image list into list for comparison to Package
    def to_list(self):
        l = []
        for i in range(self.image_list.count()):
            item : ImageListItem = self.image_list.item(i)
            l.append(item.image_tuple)
        return l

    # Renders image by index in list
    def render_image(self, index):
        self.pixmap.loadFromData(self.image_list.item(index).image_tuple[1])
        self.image_display.setPixmap(self.pixmap.scaledToWidth(256))
    
    # Renders image contained in ImageListItem
    def render_widget(self, widget : ImageListItem):
        self.pixmap.loadFromData(widget.image_tuple[1])
        self.image_display.setPixmap(self.pixmap.scaledToWidth(256))
    
    # Deletes image by index
    def delete_image(self,index):
        # Probably gonna change this to be like in data_table, using selectedRow
        self.image_list.takeItem(index)


