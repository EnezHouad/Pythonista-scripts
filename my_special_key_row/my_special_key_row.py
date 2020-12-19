# coding: utf-8
# =================================================================
# my_special_key_row.py by enez.houad@free.fr
# =================================================================
# This script adds a scrolling special key row to the keyboard
# to replace the standard one wich has problem with ios 14.
# This script is a mix between @cvpe's script AddButtonsToPythonistaKeyboard 
# https://github.com/cvpe/Pythonista-scripts/blob/master/AddButtonsToPythonistaKeyboard.py
# and my own work.
# It uses module ui3.sfsymbol of @mikaelho
# https://github.com/mikaelho/ui3
# Thanks for all their work for Pythonista's community.
# =================================================================

import ui, editor, keyboard
from objc_util import *
from ui3.sfsymbol import *
from ui3.menu import *

@on_main_thread
def tv_find(tv):
	import console, re
	
	tv.find = console.input_alert('Expression à rechercher :', '', tv.find, hide_cancel_button=True)
	txt = tv.find
	
	for sv in tv.subviews():
		if 'SUIButton_PY3' in str(sv._get_objc_classname()):
			sv.removeFromSuperview()
	if txt == '':
		return
	t = str(tv.text())
	
	for m in re.finditer(txt, t):
		st,en = m.span()
		p1 = tv.positionFromPosition_offset_(tv.beginningOfDocument(), st)
		p2 = tv.positionFromPosition_offset_(tv.beginningOfDocument(), en)
		rge = tv.textRangeFromPosition_toPosition_(p1,p2)
		rect = tv.firstRectForRange_(rge)
		x,y = rect.origin.x,rect.origin.y
		w,h = rect.size.width,rect.size.height
		
		l = ui.Button()
		l.frame = (x,y,w,h)
		if '|' not in txt:
			l.background_color = (1,0,0,0.2)
		else:
			# search multiple strings
			wrds = txt.split('|')
			idx = wrds.index(t[st:en])
			cols = [(1,0,0,0.2), (0,1,0,0.2), (0,0,1,0.2), (1,1,0,0.2), (1,0,1,0.2), (0,1,1,0.2)]
			col = cols[idx % len(cols)]
			l.background_color = col
		l.corner_radius = 4
		l.border_width = 1
		tv.addSubview_(l)		
	
# -------------------------------------------------------------------

def lineAction(sender, action):
	tv = sender.objc_instance.firstResponder() # associated TextView 
	firstWord = action.title.split('\t')[0]
	strDict = {'Simple':'# '+65*'-', 'Double':'# '+65*'=', 'Dièse':67*'#'}
	tv.insertText_(strDict[firstWord])
	
# -----------------------------------------------------------------

def key_pressed(sender):
	import clipboard
	
	tv = sender.objc_instance.firstResponder() # associated TextView  
	
	cursor = tv.offsetFromPosition_toPosition_(tv.beginningOfDocument(),     tv.selectedTextRange().start()) # get actual cursor position

	if sender.name == 'tab':
		tv.insertText_('\t')
	
	elif sender.name == 'paste':
		tv.insertText_(clipboard.get())	
		
	elif sender.name == 'undo':
		tv.undoManager().undo()
		
	elif sender.name == 'redo':
		tv.undoManager().redo()
	
	elif sender.name == 'del_right':
		# delete at right = delete at left of next or selection
		if cursor == (len(str(tv.text()))-1): # already after last character
			return
		if tv.selectedTextRange().length() == 0:
			cursor_position = tv.positionFromPosition_offset_(tv.beginningOfDocument(), cursor+1)
			tv.selectedTextRange = tv.textRangeFromPosition_toPosition_(cursor_position, cursor_position)
		tv.deleteBackward()		
		
	elif sender.name == 'find':
		tv_find(tv)
		
	else: # all other keys > insert button title
		tv.insertText_(sender.title)
	
# ===================================================================

class SpecialKeyRow(ui.View):
	
	def __init__(self, pad, *args, **kwargs):
		import keyboard
		
		self.pad = pad
	
		sw, sh = ui.get_screen_size()	
		self.uiStyle = ui.get_ui_style()
		
		self.buttonsList = []
		self.buttonWidth = (sw - (2*8) - (24*4)) / 25
		self.buttonHeight = 40

		# -------------------------------------------------------------------
		# MAIN VIEW	
	
		self.width, self.height = sw, 50
		self.alpha = 0.98
		
		# -------------------------------------------------------------------
		# SCROLL VIEW
		
		sv = ui.ScrollView(name='scrollview')
		sv.width, sv.height = (sw, 50)
		sv.content_size = (2*sw, 50)
		sv.bounces = False
		sv.shows_horizontal_scroll_indicator = False
		sv.paging_enabled = True
		sv.x, sv.y = (0, 0)
		colorDict = {'light':'#D6D8DD', 'dark':'#343639'}
		sv.background_color = colorDict[self.uiStyle]
		
		self.add_subview(sv)
		
		# -------------------------------------------------------------------
		# BUTTONS IN SCROLL VIEW
		# -------------------------------------------------------------------

		for pad_elem in self.pad:
			if not 'style' in pad_elem: bStyle = 'light'
			else: bStyle = pad_elem['style']
			if 'title' in pad_elem:
				b = self.add_text_button(name=pad_elem['key'], title=pad_elem['title'], style=bStyle)
			elif 'symbol' in pad_elem:
				b = self.add_symbol_button(name=pad_elem['key'], symbol_name=pad_elem['symbol'], style=bStyle)
			elif 'menu' in pad_elem:
				b = self.add_text_button(name=pad_elem['key'], title=pad_elem['menu'], style=bStyle)
				set_menu(b, pad_elem['options'], long_press=False)
			self.add_scrollview_button(b)			
		
	# ===================================================================
		 
	def add_scrollview_button(self, b):
		b.y = 10
		if self.buttonsList == []: b.x = 8 # 1er bouton
		else:
			lastButton = self.buttonsList[-1]
			b.x = lastButton.x + lastButton.width + 4 # intervalle 4 px
			if len(self.buttonsList) == 25: b.x += 12 # 2e page
		b.action = key_pressed
		retain_global(b)
		self['scrollview'].add_subview(b)
		self.buttonsList.append(b)
			
	# -------------------------------------------------------------------
	
	def add_text_button(self, name='', title='', width=40, style='light'):
		b = self.add_button(name, style)
		b.title = title
		b.font = ('<system>', 18)
		if width == None: b.width = ui.measure_string(b.title,font=b.font)[0] + 28
		else: b.width = self.buttonWidth		
		return b
		
	# -------------------------------------------------------------------
	
	def add_symbol_button(self, name='', symbol_name='', style='light'):
		b = self.add_button(name, style)
		symbol_image = SymbolImage(symbol_name, point_size=11, weight=LIGHT, scale=SMALL)
		b.image = symbol_image	
		b.width = self.buttonWidth	
		return b
		
	# -------------------------------------------------------------------
	
	def add_button(self, name='', backgroundStyle='light'):		
		b = ui.Button(name=name)
		b.corner_radius = 8
		
		colorsDict = {	'light'	:({'light':'#FFFFFF', 'dark':'#B4B9C1'}, 'black'), 
						'dark'	:({'light':'#717274', 'dark':'#4D4F50'}, 'white') }
		b.background_color = colorsDict[self.uiStyle][0][backgroundStyle]
		b.tint_color = colorsDict[self.uiStyle][1]
		
		b.alpha = self.alpha
		
		b.font = ('<system>', 18)
		b.height = self.buttonHeight		
		return b
		
# ===================================================================
		
@on_main_thread
def display_keyboard():
	# @cvp
	from editor import _get_editor_tab
	
	tab = _get_editor_tab()
	if tab:
		tab.editorView().textView().becomeFirstResponder()
				
# ===================================================================

@on_main_thread
def add_buttons_to_Pythonista_keyboard(pad=None):
	
	def numeric_keys(): 
		list = []
		for i in range(1, 10):
			list.append({'key':str(i), 'title':str(i)})
		list.append({'key':'0', 'title':'0'})
		return list
		
	if not pad:	
		padPage1 = [
				{'key':'tab', 'symbol':'arrow.right.to.line.alt'},				
			
				{'key':'undo', 'symbol':'arrow.uturn.left', 'style':'dark'},
				{'key':'redo','symbol':'arrow.uturn.right', 'style':'dark'},
				
				{'key':'paste', 'symbol':'doc.on.clipboard'},
			
				{'key':'#', 'title':'#'},
				{'key':'_', 'title':'_'},
			
				{'key':"'", 'title':"'"},
				{'key':'"', 'title':'"'},
				{'key':"'''", 'title':"'''"},
			
				{'key':'(', 'title':'('},
				{'key':')', 'title':')'},			
				{'key':'[', 'title':'['},
				{'key':']', 'title':']'},
				{'key':'{', 'title':'{'},
				{'key':'}', 'title':'}'},
			
				{'key':'+', 'title':'+'},
				{'key':'-', 'title':'-'},
				{'key':'*', 'title':'*'},
				{'key':'/', 'title':'/'},
				{'key':"\\", 'title':"\\"},
			
				{'key':'<', 'title':'<'},
				{'key':'>', 'title':'>'},
				{'key':'=', 'title':'='},
				{'key':':', 'title':':'},
			
				{'key':'del_right', 'symbol':'delete.right', 'style':'dark'},
				
				{'key':'tab', 'symbol':'arrow.right.to.line.alt'}
				]		

		padPage2 = [	
				{'key':'undo', 'symbol':'arrow.uturn.left', 'style':'dark'},
				{'key':'redo','symbol':'arrow.uturn.right', 'style':'dark'},				
				{'key':'paste', 'symbol':'doc.on.clipboard'},
				{'key':'#', 'title':'#'},				
				]
				
		padPage2 += numeric_keys() 
		
		padPage2 += [
				{'key':'+', 'title':'+'},
				{'key':'-', 'title':'-'},
				{'key':'*', 'title':'*'},
				{'key':'/', 'title':'/'},
				{'key':'<', 'title':'<'},
				{'key':'>', 'title':'>'},
				{'key':'=', 'title':'='},
				
				{'key':'lines', 'menu':'---', 'options':[('Simple\t\t————————', lineAction),
				('Double\t\t============', lineAction),
				('Dièse\t\t############', lineAction)]},
			
				{'key':'find', 'symbol':'magnifyingglass', 'style':'dark'},
				{'key':'del_right', 'symbol':'delete.right', 'style':'dark'}			
				]			
				
		pad = padPage1 + padPage2

	editorTab = editor._get_editor_tab()
	
	if editorTab != None:
		tv = editorTab.editorView().textView()
		
		v = SpecialKeyRow(pad)                        
		vo = ObjCInstance(v)  
	
		retain_global(v)
		
		tv.setInputAccessoryView_(vo)   # attach accessory to textview
		tv.endEditing(True)
		tv.find = ''
		
		cursor = tv.offsetFromPosition_toPosition_(tv.beginningOfDocument(),     tv.selectedTextRange().start()) # get actual cursor position
		
		display_keyboard()

# ===================================================================
	
#if __name__ == '__main__':
add_buttons_to_Pythonista_keyboard()
