PKG_DIR=
DESKTOP_FILE=grub-editor.desktop
INSTALL_PATH=$(PKG_DIR)/opt/grub-editor
DESKTOP_PATH=$(PKG_DIR)/usr/share/applications
LICENSE_PATH=$(PKG_DIR)/usr/share/licenses/grub-editor
ICON_PATH=$(PKG_DIR)/usr/share/pixmaps
install:
		find . -type f -exec install -Dm 755 "{}" "$(INSTALL_PATH)/{}" \;
		install $(DESKTOP_FILE) -D $(DESKTOP_PATH)/$(DESKTOP_FILE)
		# install README -D $(DOCPATH)/README
		# install $(DOC)/CHANGES -D $(DOCPATH)/CHANGES
		install LICENSE -D $(LICENSE_PATH)/LICENSE
		install -D grub-editor.png $(ICON_PATH)/grub-editor.png

uninstall:
		rm -f $(DESKTOP_PATH)/$(DESKTOP_FILE)
		rm -rf $(INSTALL_PATH)