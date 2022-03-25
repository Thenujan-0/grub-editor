
DESKTOP_FILE=grub-editor.desktop
INSTALL_PATH=/opt/grub-editor
DESKTOP_PATH=/usr/share/applications
LICENSE_PATH=/usr/share/licenses/grub-editor
install:
		find . -type f -exec install -Dm 755 "{}" "$(INSTALL_PATH)/{}" \;
		install $(DESKTOP_FILE) -D $(DESKTOP_PATH)/$(DESKTOP_FILE)
		# install README -D $(DOCPATH)/README
		# install $(DOC)/CHANGES -D $(DOCPATH)/CHANGES
		install LICENSE -D $(LICENSEPATH)/LICENSE

uninstall:
		rm -f $(DESKTOP_PATH)/$(DESKTOP_FILE)
		rm -rf $(INSTALL_PATH)