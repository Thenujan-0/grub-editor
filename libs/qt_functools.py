
''' Some functions that are usefull in qt gui applications '''


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
        item =layout.itemAt(i).widget()
        item.setParent(None)
        items.append(item)
        
    # printer('widget',widget)
    layout.addWidget(widget)
    for i in reversed(range(len(items))):
        layout.addWidget(items[i])