# ===================================================================
# titlebar_keyboard_button.py by enez.houad@free.fr
# ===================================================================
# This script adds a keyboard icon to the titlebar 
# to easely call the script "my_special_key_row.py" 
# wich add a scrolling special key row to the keyboard
# to replace the standard one wich has problem with ios 14.
# ===================================================================
# To launch it at Pythonista startup :
# - rename it to : "pythonista_startup.py"
# - place it in : "site-packages"
# ===================================================================

from objc_util import *
import ui
from ui3.sfsymbol import *

w = ObjCClass('UIApplication').sharedApplication().keyWindow()
main_view = w.rootViewController().view()

def get_toolbar(view):
	# get main editor toolbar, by recursively walking the view
	sv = view.subviews()
	for v in sv:
		if v._get_objc_classname().startswith(b'OMTabViewToolbar'):
			return v
		tb = get_toolbar(v)
		if tb:
			return tb
			
# ———————————————————————————————————————————————————————————————————

def keyboard_btn_action(sender):
	
	def run_script(scriptPath):
		import os
		from objc_util import ObjCInstance,ObjCClass
	
		dir = os.path.expanduser(scriptPath)
		I3=ObjCClass('PYK3Interpreter').sharedInterpreter()
		I3.runScriptAtPath_argv_resetEnvironment_(dir, [''], True)

	iCloudPath = "/private/var/mobile/Library/Mobile Documents/iCloud~com~omz-software~Pythonista3/Documents/"
	iPadPath = '~/Documents/'
	scriptPath = 'PROJETS/KEYBOARD/my_special_key_row.py'
	run_script(iCloudPath + scriptPath)
			
# ———————————————————————————————————————————————————————————————————

def create_keyboard_button(action,index=0):
	global __persistent_views
	
	assert(callable(action))
	tb = get_toolbar(main_view)
		
	try:
		__persistent_views
	except NameError:
		__persistent_views={}
		
	#check for existing button in this index and delete if needed
	remove_toolbar_button(index)	
	btn = ui.Button()
	w = ui.get_window_size()[0]
	btn.frame = (w-(5*48), 24, 40, 40)
	#btn.frame = (110, 24, 40, 40)
	
	if ui.get_ui_style() == 'dark':
		btn.tint_color = 'white' 
	else:
		btn.tint_color = '#0D89B5' 
	btn.image = SymbolImage('keyboard', point_size=14, weight=THIN, scale=SMALL)
	btn.image = btn.image.with_rendering_mode(ui.RENDERING_MODE_AUTOMATIC)
			
	btn.action=action
	btn_obj=ObjCInstance(btn)
	__persistent_views[index]=(btn,action)
	tb.superview().superview().addSubview_(btn_obj) # in front of all buttons
	
	return btn
	
# ———————————————————————————————————————————————————————————————————
	
def remove_toolbar_button(index):
	global __persistent_views
	
	try:
		btn,action = __persistent_views.pop(index)
		btn.action= None
		ObjCInstance(btn).removeFromSuperview()
	except KeyError:
		pass

# ===================================================================

#if __name__=='__main__': # if imported by pythonista startup	
		
create_keyboard_button(keyboard_btn_action)
