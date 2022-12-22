
''' Some functions that are usefull in qt gui applications '''
from PyQt5 import QtWidgets

def reconnect(signal ,new_handler=None,old_handler=None):
    try:
        if old_handler is not None:
            while True:
                signal.disconnect(old_handler)
        else:
            signal.disconnect()
    except TypeError:
        pass
    if new_handler is not None:
        # printer(signal)
        signal.connect(new_handler)
        
def insert_into(layout,index,widget):
    items=[]
    for i in reversed(range(index,layout.count())):
        item = layout.takeAt(i)
        if isinstance(item,QtWidgets.QWidgetItem):
            widget_ =item.widget()
            widget_.setParent(None)
            items.append(item)
        elif isinstance(item,QtWidgets.QSpacerItem):
            if  item.sizePolicy().horizontalPolicy()==7:
                horizontalSpacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Expanding,\
                    QtWidgets.QSizePolicy.Minimum) 
                items.append(horizontalSpacer)
            else:
                raise Exception("Error in insert_into")
        else:
            raise Exception("Non handled case in insert_into")
    layout.addWidget(widget)
    for i in reversed(range(len(items))):
        item = items[i]
        if isinstance(item,QtWidgets.QWidgetItem):
            layout.addWidget(item.widget())
        elif isinstance(item,QtWidgets.QSpacerItem):
            layout.addItem(item)
        else:
            raise Exception("Non handled case in insert_into")