

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