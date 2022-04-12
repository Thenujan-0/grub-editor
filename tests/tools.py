
def change_comboBox_current_index(mw):
    curr_ind = mw.comboBox_grub_default.currentIndex()
    
    for i in  range(len(mw.all_entries)):
        if i!= curr_ind:
            grub_default_ind = i
            break
    
    mw.comboBox_grub_default.setCurrentIndex(grub_default_ind)
    
    return grub_default_ind