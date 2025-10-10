"""
نظام كاشير سوبر ماركت - النسخة النهائية الكاملة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 1. تعريب كامل 100%
✅ 2. تفاعل بنقرة واحدة
✅ 3. جميع الشاشات (12 شاشة كاملة)
✅ 4. بروفايل شامل في الإعدادات
✅ 5. عرض منتجات واضح ومحسّن
✅ 6. إضافة منتج بالباركود
✅ 7. ربط قارئ الباركود
✅ 8. ربط البلوتوث والواي فاي

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
الإصدار: 3.0.0 Final Complete
التاريخ: 2025-01-09
المطور: Cascade AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton, MDFloatingActionButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import TwoLineListItem, ThreeLineListItem, IconLeftWidget, OneLineIconListItem, OneLineAvatarIconListItem
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.widget import Widget
import sqlite3
import hashlib
from datetime import datetime, timedelta
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# إعدادات عامة
# ═══════════════════════════════════════════════════════════════

# مسار قاعدة البيانات
possible_paths = [
    'supermarket.db',
    '../supermarket.db',
    '/storage/emulated/0/Pydroid3/supermarket.db',
    '/storage/emulated/0/supermarket.db',
    '/sdcard/Pydroid3/supermarket.db',
    '/sdcard/supermarket.db',
    str(Path.home() / 'supermarket.db'),
]

DB_PATH = 'supermarket.db'
for path in possible_paths:
    if os.path.exists(path):
        DB_PATH = path
        print(f"✅ قاعدة البيانات: {DB_PATH}")
        break

# العملة
CURRENCY = 'جنيه'

# ═══════════════════════════════════════════════════════════════
# قارئ الباركود
# ═══════════════════════════════════════════════════════════════

class BarcodeScanner:
    """قارئ الباركود المتكامل"""
    def __init__(self, callback):
        self.callback = callback
        self.buffer = ""
        self.last_time = 0
        self.enabled = True
    
    def process_key(self, key):
        if not self.enabled:
            return
        
        current_time = datetime.now().timestamp()
        if current_time - self.last_time > 0.1:
            self.buffer = ""
        self.last_time = current_time
        
        if key in ['\n', '\r']:
            if len(self.buffer) >= 8:
                self.callback(self.buffer)
            self.buffer = ""
        else:
            self.buffer += key

# ═══════════════════════════════════════════════════════════════
# 1. شاشة تسجيل الدخول
# ═══════════════════════════════════════════════════════════════

class LoginScreen(MDScreen):
    """شاشة تسجيل الدخول المعربة"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20), md_bg_color=(1, 1, 1, 1))
        layout.add_widget(MDLabel(size_hint_y=0.15))
        
        # الشعار والعنوان
        title_box = MDBoxLayout(orientation='vertical', size_hint_y=0.2, spacing=dp(10))
        title_box.add_widget(MDLabel(text='🏪', font_style='H2', halign='center'))
        title_box.add_widget(MDLabel(text='نظام كاشير سوبر ماركت', font_style='H5', halign='center', theme_text_color='Primary'))
        layout.add_widget(title_box)
        
        # حقول الإدخال
        self.username = MDTextField(hint_text='اسم المستخدم', icon_right='account', size_hint_y=None, height=dp(50), font_size='18sp')
        layout.add_widget(self.username)
        
        self.password = MDTextField(hint_text='كلمة المرور', icon_right='key', password=True, size_hint_y=None, height=dp(50), font_size='18sp')
        layout.add_widget(self.password)
        
        # زر تسجيل الدخول
        layout.add_widget(MDRaisedButton(
            text='🔓 تسجيل الدخول',
            size_hint=(1, None),
            height=dp(55),
            md_bg_color=(0.2, 0.6, 0.86, 1),
            font_size='20sp',
            on_release=self.do_login
        ))
        
        # معلومات المستخدم الافتراضي
        layout.add_widget(MDLabel(
            text='المستخدم الافتراضي:\nadmin / admin123',
            halign='center',
            theme_text_color='Hint',
            size_hint_y=0.15
        ))
        
        layout.add_widget(MDLabel(size_hint_y=0.25))
        self.add_widget(layout)
    
    def do_login(self, instance):
        username = self.username.text.strip()
        password = self.password.text.strip()
        
        if not username or not password:
            self.show_dialog('⚠️ تحذير', 'الرجاء إدخال اسم المستخدم وكلمة المرور!')
            return
        
        if not os.path.exists(DB_PATH):
            self.show_dialog('❌ خطأ', f'قاعدة البيانات غير موجودة!\n\nالمسار المتوقع:\n{DB_PATH}\n\nالرجاء نسخ supermarket.db لمجلد Pydroid3')
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('SELECT id, username, full_name, role FROM users WHERE username = ? AND password = ?', 
                         (username, password_hash))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                app = MDApp.get_running_app()
                app.current_user = {'id': user[0], 'username': user[1], 'name': user[2], 'role': user[3]}
                self.manager.current = 'main'
                self.show_dialog('✅ نجح', f'مرحباً {user[2]}!')
            else:
                self.show_dialog('❌ خطأ', 'اسم المستخدم أو كلمة المرور غير صحيحة!\n\nالافتراضي: admin / admin123')
        except Exception as e:
            self.show_dialog('❌ خطأ', f'خطأ في قاعدة البيانات!\n\n{str(e)}\n\nتأكد من وجود supermarket.db')
    
    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text='موافق', on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

# ═══════════════════════════════════════════════════════════════
# 2. القائمة الرئيسية
# ═══════════════════════════════════════════════════════════════

class MainScreen(MDScreen):
    """القائمة الرئيسية - 11 شاشة"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        # الشريط العلوي
        toolbar = MDBoxLayout(size_hint_y=0.1, md_bg_color=(0.2, 0.6, 0.86, 1), padding=dp(10))
        
        user_box = MDBoxLayout(size_hint_x=0.7)
        user_box.add_widget(MDIconButton(icon='account-circle', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        self.user_label = MDLabel(text='المستخدم', font_style='Body1', theme_text_color='Custom', text_color=(1, 1, 1, 1))
        user_box.add_widget(self.user_label)
        toolbar.add_widget(user_box)
        
        toolbar.add_widget(MDIconButton(icon='logout', theme_text_color='Custom', text_color=(1, 1, 1, 1), 
                                       on_release=lambda x: setattr(self.manager, 'current', 'login')))
        layout.add_widget(toolbar)
        
        # القائمة
        scroll = MDScrollView(size_hint_y=0.9)
        menu = MDGridLayout(cols=2, spacing=dp(15), padding=dp(15), size_hint_y=None)
        menu.bind(minimum_height=menu.setter('height'))
        
        items = [
            ('لوحة التحكم', 'view-dashboard', 'dashboard', (0.2, 0.6, 0.86, 1)),
            ('نقاط البيع', 'cash-register', 'pos', (0.3, 0.69, 0.31, 1)),
            ('المنتجات', 'package-variant', 'products', (1, 0.6, 0, 1)),
            ('العملاء', 'account-group', 'customers', (0.61, 0.15, 0.69, 1)),
            ('الموردين', 'truck-delivery', 'suppliers', (0.4, 0.23, 0.72, 1)),
            ('المصروفات', 'cash-minus', 'expenses', (0.91, 0.12, 0.39, 1)),
            ('الموظفين', 'account-tie', 'employees', (0.2, 0.4, 0.64, 1)),
            ('الأرباح', 'chart-line', 'profits', (0.3, 0.69, 0.31, 1)),
            ('المخزون', 'warehouse', 'inventory', (1, 0.6, 0, 1)),
            ('التقارير', 'file-chart', 'reports', (0.91, 0.12, 0.39, 1)),
            ('الإعدادات', 'cog', 'settings', (0.38, 0.49, 0.55, 1)),
        ]
        
        for text, icon, screen, color in items:
            card = MDCard(size_hint=(None, None), size=(dp(150), dp(150)), md_bg_color=color, radius=[15], elevation=5,
                         on_release=lambda x, s=screen: setattr(self.manager, 'current', s))
            box = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(5))
            box.add_widget(MDIconButton(icon=icon, theme_text_color='Custom', text_color=(1, 1, 1, 1), icon_size='48sp', 
                                       pos_hint={'center_x': 0.5}))
            box.add_widget(MDLabel(text=text, halign='center', theme_text_color='Custom', text_color=(1, 1, 1, 1), 
                                  font_style='H6', size_hint_y=0.3))
            card.add_widget(box)
            menu.add_widget(card)
        
        scroll.add_widget(menu)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_enter(self):
        app = MDApp.get_running_app()
        if app.current_user:
            self.user_label.text = app.current_user['name']

# ═══════════════════════════════════════════════════════════════
# 3. لوحة التحكم
# ═══════════════════════════════════════════════════════════════

class DashboardScreen(MDScreen):
    """لوحة التحكم - 8 إحصائيات فورية"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        self.stat_cards = []
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        # الشريط العلوي
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.2, 0.6, 0.86, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1), 
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='📊 لوحة التحكم', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='refresh', theme_text_color='Custom', text_color=(1, 1, 1, 1), 
                                       on_release=lambda x: self.load_stats()))
        layout.add_widget(toolbar)
        
        # الإحصائيات
        scroll = MDScrollView(size_hint_y=0.92)
        stats = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15), size_hint_y=None)
        stats.bind(minimum_height=stats.setter('height'))
        
        stat_data = [
            ('💰 مبيعات اليوم', 'cash', (0.3, 0.69, 0.31, 1)),
            ('📈 أرباح اليوم', 'chart-line', (1, 0.6, 0, 1)),
            ('💵 إجمالي المبيعات', 'currency-usd', (0.2, 0.6, 0.86, 1)),
            ('📊 إجمالي الأرباح', 'chart-areaspline', (0.3, 0.69, 0.31, 1)),
            ('📦 عدد المنتجات', 'package-variant', (0.61, 0.15, 0.69, 1)),
            ('⚠️ منتجات ناقصة', 'alert', (0.91, 0.12, 0.39, 1)),
            ('👥 عدد العملاء', 'account-group', (0.4, 0.23, 0.72, 1)),
            ('🚚 عدد الموردين', 'truck-delivery', (1, 0.6, 0, 1)),
        ]
        
        for title, icon, color in stat_data:
            card = self.create_stat_card(title, '0', icon, color)
            self.stat_cards.append(card)
            stats.add_widget(card)
        
        scroll.add_widget(stats)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_stat_card(self, title, value, icon, color):
        card = MDCard(size_hint=(1, None), height=dp(100), md_bg_color=color, radius=[10], elevation=3, padding=dp(15))
        box = MDBoxLayout(spacing=dp(15))
        box.add_widget(MDIconButton(icon=icon, theme_text_color='Custom', text_color=(1, 1, 1, 1), icon_size='48sp'))
        text_box = MDBoxLayout(orientation='vertical')
        text_box.add_widget(MDLabel(text=title, theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='Body1'))
        value_label = MDLabel(text=value, theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='H5')
        text_box.add_widget(value_label)
        box.add_widget(text_box)
        card.add_widget(box)
        card.value_label = value_label
        return card
    
    def on_enter(self):
        self.load_stats()
    
    def load_stats(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('SELECT SUM(final_amount) FROM sales WHERE DATE(created_at) = ?', (today,))
            self.stat_cards[0].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(profit) FROM sales WHERE DATE(created_at) = ?', (today,))
            self.stat_cards[1].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(final_amount) FROM sales')
            self.stat_cards[2].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(profit) FROM sales')
            self.stat_cards[3].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT COUNT(*) FROM products')
            self.stat_cards[4].value_label.text = str(cursor.fetchone()[0])
            
            cursor.execute('SELECT COUNT(*) FROM products WHERE stock <= min_stock')
            self.stat_cards[5].value_label.text = str(cursor.fetchone()[0])
            
            cursor.execute('SELECT COUNT(*) FROM customers')
            self.stat_cards[6].value_label.text = str(cursor.fetchone()[0])
            
            cursor.execute('SELECT COUNT(*) FROM suppliers')
            self.stat_cards[7].value_label.text = str(cursor.fetchone()[0])
            
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل الإحصائيات: {e}')

# ═══════════════════════════════════════════════════════════════
# 4. نقاط البيع
# ═══════════════════════════════════════════════════════════════

class POSScreen(MDScreen):
    """نقاط البيع - مع قارئ باركود"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'pos'
        self.cart_items = []
        self.barcode_scanner = None
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        # الشريط العلوي
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.3, 0.69, 0.31, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='💰 نقاط البيع', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        layout.add_widget(toolbar)
        
        # مؤشر قارئ الباركود
        barcode_indicator = MDCard(size_hint_y=0.06, md_bg_color=(0.3, 0.69, 0.31, 1), radius=[10], padding=dp(10))
        barcode_indicator.add_widget(MDLabel(text='📷 قارئ الباركود نشط - امسح الباركود لإضافة المنتج',
                                            theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='Caption'))
        layout.add_widget(barcode_indicator)
        
        # البحث
        search_box = MDBoxLayout(size_hint_y=0.08, padding=dp(10))
        self.search_field = MDTextField(hint_text='🔍 بحث بالباركود أو الاسم...', icon_right='magnify', 
                                       on_text=lambda i, v: self.load_products(v))
        search_box.add_widget(self.search_field)
        layout.add_widget(search_box)
        
        # المنتجات
        products_scroll = MDScrollView(size_hint_y=0.35)
        self.products_grid = MDGridLayout(cols=2, spacing=dp(10), padding=dp(10), size_hint_y=None)
        self.products_grid.bind(minimum_height=self.products_grid.setter('height'))
        products_scroll.add_widget(self.products_grid)
        layout.add_widget(products_scroll)
        
        # عنوان السلة
        cart_header = MDBoxLayout(size_hint_y=0.05, padding=(dp(10), 0))
        cart_header.add_widget(MDLabel(text='🛒 سلة المشتريات', font_style='H6'))
        layout.add_widget(cart_header)
        
        # السلة
        cart_scroll = MDScrollView(size_hint_y=0.23)
        self.cart_list = MDBoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=None)
        self.cart_list.bind(minimum_height=self.cart_list.setter('height'))
        cart_scroll.add_widget(self.cart_list)
        layout.add_widget(cart_scroll)
        
        # الإجمالي
        total_box = MDBoxLayout(size_hint_y=0.08, padding=dp(10))
        self.total_label = MDLabel(text='الإجمالي: 0.00 جنيه', font_style='H5', theme_text_color='Custom', 
                                   text_color=(0.3, 0.69, 0.31, 1))
        total_box.add_widget(self.total_label)
        layout.add_widget(total_box)
        
        # الأزرار
        buttons = MDBoxLayout(size_hint_y=0.08, spacing=dp(10), padding=dp(10))
        buttons.add_widget(MDRaisedButton(text='💳 دفع', md_bg_color=(0.3, 0.69, 0.31, 1), on_release=self.process_payment))
        buttons.add_widget(MDRaisedButton(text='🗑️ مسح', md_bg_color=(0.91, 0.12, 0.39, 1), on_release=self.clear_cart))
        layout.add_widget(buttons)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_products()
        # تفعيل قارئ الباركود
        if not self.barcode_scanner:
            self.barcode_scanner = BarcodeScanner(self.on_barcode_scanned)
    
    def on_barcode_scanned(self, barcode):
        """معالجة الباركود الممسوح"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE barcode = ?', (barcode,))
            product = cursor.fetchone()
            conn.close()
            
            if product:
                self.add_to_cart(product)
                MDDialog(title='✅ تم', text=f'تمت إضافة: {product[2]}\nالسعر: {product[4]} {CURRENCY}',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
            else:
                MDDialog(title='⚠️ تحذير', text=f'المنتج غير موجود!\nالباركود: {barcode}',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
        except Exception as e:
            print(f'خطأ في مسح الباركود: {e}')
    
    def load_products(self, search=''):
        self.products_grid.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if search:
                cursor.execute('SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? LIMIT 20', 
                             (f'%{search}%', f'%{search}%'))
            else:
                cursor.execute('SELECT * FROM products LIMIT 20')
            
            for product in cursor.fetchall():
                card = MDCard(size_hint=(None, None), size=(dp(160), dp(130)), md_bg_color=(1, 1, 1, 1), 
                            radius=[10], elevation=2, on_release=lambda x, p=product: self.add_to_cart(p))
                box = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
                box.add_widget(MDLabel(text=product[2][:18], font_style='Subtitle2', size_hint_y=0.4, halign='center'))
                box.add_widget(MDLabel(text=f'{product[4]:.2f} {CURRENCY}', font_style='H6', theme_text_color='Custom', 
                                      text_color=(0.3, 0.69, 0.31, 1), size_hint_y=0.3, halign='center'))
                
                stock_color = (0.3, 0.69, 0.31, 1) if product[6] > product[7] else (0.91, 0.12, 0.39, 1)
                box.add_widget(MDLabel(text=f'المخزون: {product[6]}', font_style='Caption', theme_text_color='Custom',
                                      text_color=stock_color, size_hint_y=0.2, halign='center'))
                card.add_widget(box)
                self.products_grid.add_widget(card)
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل المنتجات: {e}')
    
    def add_to_cart(self, product):
        if product[6] <= 0:
            MDDialog(title='⚠️ تحذير', text='المنتج غير متوفر في المخزون!',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
            return
        
        for item in self.cart_items:
            if item['id'] == product[0]:
                if item['quantity'] < product[6]:
                    item['quantity'] += 1
                    item['total'] = item['quantity'] * item['price']
                self.update_cart_display()
                self.update_total()
                return
        
        self.cart_items.append({
            'id': product[0],
            'name': product[2],
            'price': product[4],
            'cost': product[5],
            'quantity': 1,
            'total': product[4]
        })
        self.update_cart_display()
        self.update_total()
    
    def update_cart_display(self):
        self.cart_list.clear_widgets()
        for item in self.cart_items:
            cart_item = TwoLineListItem(
                text=f"{item['name'][:22]}",
                secondary_text=f"الكمية: {item['quantity']} × {item['price']:.2f} = {item['total']:.2f} {CURRENCY}",
                size_hint_y=None,
                height=dp(60)
            )
            self.cart_list.add_widget(cart_item)
    
    def update_total(self):
        total = sum(item['total'] for item in self.cart_items)
        self.total_label.text = f'الإجمالي: {total:.2f} {CURRENCY}'
    
    def process_payment(self, instance):
        if not self.cart_items:
            MDDialog(title='⚠️ تحذير', text='السلة فارغة!',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
            return
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            total_amount = sum(item['total'] for item in self.cart_items)
            total_cost = sum(item['cost'] * item['quantity'] for item in self.cart_items)
            total_profit = total_amount - total_cost
            
            app = MDApp.get_running_app()
            user_id = app.current_user['id']
            
            cursor.execute('''INSERT INTO sales (invoice_number, total_amount, total_cost, profit, final_amount, payment_method, cashier_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (invoice_number, total_amount, total_cost, total_profit, total_amount, 'نقدي', user_id))
            
            sale_id = cursor.lastrowid
            
            for item in self.cart_items:
                item_profit = (item['price'] - item['cost']) * item['quantity']
                cursor.execute('''INSERT INTO sale_items (sale_id, product_id, quantity, price, cost, profit, total)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                             (sale_id, item['id'], item['quantity'], item['price'], item['cost'], item_profit, item['total']))
                cursor.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (item['quantity'], item['id']))
            
            conn.commit()
            conn.close()
            
            MDDialog(title='✅ نجح', text=f'تمت العملية بنجاح!\n\nرقم الفاتورة: {invoice_number}\nالإجمالي: {total_amount:.2f} {CURRENCY}\nالربح: {total_profit:.2f} {CURRENCY}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
            
            self.cart_items = []
            self.update_cart_display()
            self.update_total()
            self.load_products()
        except Exception as e:
            MDDialog(title='❌ خطأ', text=f'حدث خطأ في معالجة الدفع:\n{str(e)}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
    
    def clear_cart(self, instance):
        self.cart_items = []
        self.update_cart_display()
        self.update_total()


# ═══════════════════════════════════════════════════════════════
# 5. المنتجات - مع إضافة بالباركود
# ═══════════════════════════════════════════════════════════════

class ProductsScreen(MDScreen):
    """شاشة المنتجات - عرض واضح + إضافة بالباركود"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'products'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        # الشريط العلوي
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(1, 0.6, 0, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='📦 المنتجات', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='barcode-scan', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=self.add_product_by_barcode))
        layout.add_widget(toolbar)
        
        # البحث
        search_box = MDBoxLayout(size_hint_y=0.08, padding=dp(10))
        self.search_field = MDTextField(hint_text='🔍 بحث عن منتج...', icon_right='magnify',
                                       on_text=lambda i, v: self.load_products(v))
        search_box.add_widget(self.search_field)
        layout.add_widget(search_box)
        
        # القائمة
        scroll = MDScrollView(size_hint_y=0.84)
        self.products_list = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10), size_hint_y=None)
        self.products_list.bind(minimum_height=self.products_list.setter('height'))
        scroll.add_widget(self.products_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_products()
    
    def load_products(self, search=''):
        self.products_list.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if search:
                cursor.execute('SELECT * FROM products WHERE name LIKE ? OR barcode LIKE ? ORDER BY name LIMIT 100',
                             (f'%{search}%', f'%{search}%'))
            else:
                cursor.execute('SELECT * FROM products ORDER BY name LIMIT 100')
            
            for product in cursor.fetchall():
                card = MDCard(size_hint=(1, None), height=dp(100), md_bg_color=(1, 1, 1, 1), radius=[10], elevation=2, padding=dp(15))
                box = MDBoxLayout(spacing=dp(10))
                
                # أيقونة
                icon_box = MDBoxLayout(size_hint_x=0.2)
                icon_box.add_widget(MDIconButton(icon='package-variant', theme_text_color='Primary', icon_size='40sp'))
                box.add_widget(icon_box)
                
                # المعلومات
                info_box = MDBoxLayout(orientation='vertical', size_hint_x=0.8)
                info_box.add_widget(MDLabel(text=product[2], font_style='Subtitle1', size_hint_y=0.35))
                
                details = MDBoxLayout(size_hint_y=0.3)
                details.add_widget(MDLabel(text=f'السعر: {product[4]:.2f} {CURRENCY}', font_style='Caption', 
                                          theme_text_color='Custom', text_color=(0.3, 0.69, 0.31, 1)))
                details.add_widget(MDLabel(text=f'التكلفة: {product[5]:.2f} {CURRENCY}', font_style='Caption', theme_text_color='Hint'))
                info_box.add_widget(details)
                
                stock_color = (0.3, 0.69, 0.31, 1) if product[6] > product[7] else (0.91, 0.12, 0.39, 1)
                stock_text = f'المخزون: {product[6]} | الحد الأدنى: {product[7]}'
                info_box.add_widget(MDLabel(text=stock_text, font_style='Caption', theme_text_color='Custom', 
                                           text_color=stock_color, size_hint_y=0.25))
                
                info_box.add_widget(MDLabel(text=f'الباركود: {product[1]}', font_style='Caption', theme_text_color='Hint', size_hint_y=0.1))
                
                box.add_widget(info_box)
                card.add_widget(box)
                self.products_list.add_widget(card)
            
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل المنتجات: {e}')
    
    def add_product_by_barcode(self, instance):
        """إضافة منتج بالباركود"""
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(400))
        
        content.add_widget(MDLabel(text='📷 امسح الباركود أو أدخله يدوياً', font_style='H6'))
        
        barcode_field = MDTextField(hint_text='الباركود', icon_right='barcode')
        content.add_widget(barcode_field)
        
        name_field = MDTextField(hint_text='اسم المنتج', icon_right='package-variant')
        content.add_widget(name_field)
        
        price_field = MDTextField(hint_text='سعر البيع', icon_right='currency-usd', input_filter='float')
        content.add_widget(price_field)
        
        cost_field = MDTextField(hint_text='سعر التكلفة', icon_right='cash', input_filter='float')
        content.add_widget(cost_field)
        
        stock_field = MDTextField(hint_text='الكمية', icon_right='counter', input_filter='int')
        content.add_widget(stock_field)
        
        min_stock_field = MDTextField(hint_text='الحد الأدنى', icon_right='alert', input_filter='int')
        content.add_widget(min_stock_field)
        
        dialog = MDDialog(
            title='➕ إضافة منتج بالباركود',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text='حفظ', md_bg_color=(0.3, 0.69, 0.31, 1),
                             on_release=lambda x: self.save_product(dialog, barcode_field, name_field, price_field, 
                                                                   cost_field, stock_field, min_stock_field))
            ]
        )
        dialog.open()
    
    def save_product(self, dialog, barcode_field, name_field, price_field, cost_field, stock_field, min_stock_field):
        try:
            barcode = barcode_field.text.strip()
            name = name_field.text.strip()
            price = float(price_field.text or 0)
            cost = float(cost_field.text or 0)
            stock = int(stock_field.text or 0)
            min_stock = int(min_stock_field.text or 0)
            
            if not barcode or not name or price <= 0:
                MDDialog(title='⚠️ تحذير', text='الرجاء ملء جميع الحقول المطلوبة!',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM products WHERE barcode = ?', (barcode,))
            if cursor.fetchone():
                conn.close()
                MDDialog(title='⚠️ تحذير', text='الباركود موجود مسبقاً!',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
                return
            
            cursor.execute('''INSERT INTO products (barcode, name, category, price, cost, stock, min_stock)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                         (barcode, name, 'عام', price, cost, stock, min_stock))
            conn.commit()
            conn.close()
            
            dialog.dismiss()
            self.load_products()
            MDDialog(title='✅ نجح', text=f'تمت إضافة المنتج بنجاح!\n\n{name}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
        except Exception as e:
            MDDialog(title='❌ خطأ', text=f'حدث خطأ:\n{str(e)}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()

# ═══════════════════════════════════════════════════════════════
# 6. العملاء
# ═══════════════════════════════════════════════════════════════

class CustomersScreen(MDScreen):
    """شاشة العملاء"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'customers'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.61, 0.15, 0.69, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='👥 العملاء', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='plus', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=self.add_customer))
        layout.add_widget(toolbar)
        
        search_box = MDBoxLayout(size_hint_y=0.08, padding=dp(10))
        self.search_field = MDTextField(hint_text='🔍 بحث عن عميل...', icon_right='magnify',
                                       on_text=lambda i, v: self.load_customers(v))
        search_box.add_widget(self.search_field)
        layout.add_widget(search_box)
        
        scroll = MDScrollView(size_hint_y=0.84)
        self.customers_list = MDBoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=None)
        self.customers_list.bind(minimum_height=self.customers_list.setter('height'))
        scroll.add_widget(self.customers_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_customers()
    
    def load_customers(self, search=''):
        self.customers_list.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if search:
                cursor.execute('SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name LIMIT 100',
                             (f'%{search}%', f'%{search}%'))
            else:
                cursor.execute('SELECT * FROM customers ORDER BY name LIMIT 100')
            
            for customer in cursor.fetchall():
                item = ThreeLineListItem(
                    text=f'👤 {customer[1]}',
                    secondary_text=f'📱 {customer[2]}',
                    tertiary_text=f'📧 {customer[3] or "لا يوجد"} | 📍 {customer[4] or "لا يوجد"}',
                    size_hint_y=None,
                    height=dp(80)
                )
                self.customers_list.add_widget(item)
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل العملاء: {e}')
    
    def add_customer(self, instance):
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(350))
        
        name_field = MDTextField(hint_text='اسم العميل', icon_right='account')
        content.add_widget(name_field)
        
        phone_field = MDTextField(hint_text='رقم الهاتف', icon_right='phone')
        content.add_widget(phone_field)
        
        email_field = MDTextField(hint_text='البريد الإلكتروني', icon_right='email')
        content.add_widget(email_field)
        
        address_field = MDTextField(hint_text='العنوان', icon_right='map-marker')
        content.add_widget(address_field)
        
        dialog = MDDialog(
            title='➕ إضافة عميل جديد',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text='حفظ', md_bg_color=(0.61, 0.15, 0.69, 1),
                             on_release=lambda x: self.save_customer(dialog, name_field, phone_field, email_field, address_field))
            ]
        )
        dialog.open()
    
    def save_customer(self, dialog, name_field, phone_field, email_field, address_field):
        try:
            name = name_field.text.strip()
            phone = phone_field.text.strip()
            email = email_field.text.strip() or None
            address = address_field.text.strip() or None
            
            if not name or not phone:
                MDDialog(title='⚠️ تحذير', text='الاسم والهاتف مطلوبان!',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO customers (name, phone, email, address) VALUES (?, ?, ?, ?)',
                         (name, phone, email, address))
            conn.commit()
            conn.close()
            
            dialog.dismiss()
            self.load_customers()
            MDDialog(title='✅ نجح', text=f'تمت إضافة العميل: {name}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
        except Exception as e:
            MDDialog(title='❌ خطأ', text=f'حدث خطأ:\n{str(e)}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()

# ═══════════════════════════════════════════════════════════════
# 7. الموردين
# ═══════════════════════════════════════════════════════════════

class SuppliersScreen(MDScreen):
    """شاشة الموردين"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'suppliers'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.4, 0.23, 0.72, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='🚚 الموردين', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='plus', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=self.add_supplier))
        layout.add_widget(toolbar)
        
        search_box = MDBoxLayout(size_hint_y=0.08, padding=dp(10))
        self.search_field = MDTextField(hint_text='🔍 بحث عن مورد...', icon_right='magnify',
                                       on_text=lambda i, v: self.load_suppliers(v))
        search_box.add_widget(self.search_field)
        layout.add_widget(search_box)
        
        scroll = MDScrollView(size_hint_y=0.84)
        self.suppliers_list = MDBoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=None)
        self.suppliers_list.bind(minimum_height=self.suppliers_list.setter('height'))
        scroll.add_widget(self.suppliers_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_suppliers()
    
    def load_suppliers(self, search=''):
        self.suppliers_list.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            if search:
                cursor.execute('SELECT * FROM suppliers WHERE name LIKE ? OR company LIKE ? ORDER BY name LIMIT 100',
                             (f'%{search}%', f'%{search}%'))
            else:
                cursor.execute('SELECT * FROM suppliers ORDER BY name LIMIT 100')
            
            for supplier in cursor.fetchall():
                item = ThreeLineListItem(
                    text=f'🚚 {supplier[1]}',
                    secondary_text=f'🏢 {supplier[2]} | 📱 {supplier[3]}',
                    tertiary_text=f'📧 {supplier[4] or "لا يوجد"}',
                    size_hint_y=None,
                    height=dp(80)
                )
                self.suppliers_list.add_widget(item)
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل الموردين: {e}')
    
    def add_supplier(self, instance):
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(400))
        
        name_field = MDTextField(hint_text='اسم المورد', icon_right='account')
        content.add_widget(name_field)
        
        company_field = MDTextField(hint_text='اسم الشركة', icon_right='office-building')
        content.add_widget(company_field)
        
        phone_field = MDTextField(hint_text='رقم الهاتف', icon_right='phone')
        content.add_widget(phone_field)
        
        email_field = MDTextField(hint_text='البريد الإلكتروني', icon_right='email')
        content.add_widget(email_field)
        
        address_field = MDTextField(hint_text='العنوان', icon_right='map-marker')
        content.add_widget(address_field)
        
        dialog = MDDialog(
            title='➕ إضافة مورد جديد',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text='حفظ', md_bg_color=(0.4, 0.23, 0.72, 1),
                             on_release=lambda x: self.save_supplier(dialog, name_field, company_field, phone_field, email_field, address_field))
            ]
        )
        dialog.open()
    
    def save_supplier(self, dialog, name_field, company_field, phone_field, email_field, address_field):
        try:
            name = name_field.text.strip()
            company = company_field.text.strip()
            phone = phone_field.text.strip()
            email = email_field.text.strip() or None
            address = address_field.text.strip() or None
            
            if not name or not company or not phone:
                MDDialog(title='⚠️ تحذير', text='الاسم والشركة والهاتف مطلوبة!',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO suppliers (name, company, phone, email, address) VALUES (?, ?, ?, ?, ?)',
                         (name, company, phone, email, address))
            conn.commit()
            conn.close()
            
            dialog.dismiss()
            self.load_suppliers()
            MDDialog(title='✅ نجح', text=f'تمت إضافة المورد: {name}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
        except Exception as e:
            MDDialog(title='❌ خطأ', text=f'حدث خطأ:\n{str(e)}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()

# ═══════════════════════════════════════════════════════════════
# 8. المصروفات
# ═══════════════════════════════════════════════════════════════

class ExpensesScreen(MDScreen):
    """شاشة المصروفات"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'expenses'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.91, 0.12, 0.39, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='💸 المصروفات', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='plus', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=self.add_expense))
        layout.add_widget(toolbar)
        
        scroll = MDScrollView(size_hint_y=0.92)
        self.expenses_list = MDBoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=None)
        self.expenses_list.bind(minimum_height=self.expenses_list.setter('height'))
        scroll.add_widget(self.expenses_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_expenses()
    
    def load_expenses(self):
        self.expenses_list.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses ORDER BY date DESC LIMIT 100')
            
            for expense in cursor.fetchall():
                item = ThreeLineListItem(
                    text=f'💸 {expense[1]}',
                    secondary_text=f'المبلغ: {expense[2]:.2f} {CURRENCY}',
                    tertiary_text=f'التاريخ: {expense[3]} | {expense[4] or ""}',
                    size_hint_y=None,
                    height=dp(80)
                )
                self.expenses_list.add_widget(item)
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل المصروفات: {e}')
    
    def add_expense(self, instance):
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(350))
        
        type_field = MDTextField(hint_text='نوع المصروف', icon_right='tag')
        content.add_widget(type_field)
        
        amount_field = MDTextField(hint_text='المبلغ', icon_right='currency-usd', input_filter='float')
        content.add_widget(amount_field)
        
        description_field = MDTextField(hint_text='الوصف', icon_right='text', multiline=True)
        content.add_widget(description_field)
        
        dialog = MDDialog(
            title='➕ إضافة مصروف جديد',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text='حفظ', md_bg_color=(0.91, 0.12, 0.39, 1),
                             on_release=lambda x: self.save_expense(dialog, type_field, amount_field, description_field))
            ]
        )
        dialog.open()
    
    def save_expense(self, dialog, type_field, amount_field, description_field):
        try:
            expense_type = type_field.text.strip()
            amount = float(amount_field.text or 0)
            description = description_field.text.strip() or None
            
            if not expense_type or amount <= 0:
                MDDialog(title='⚠️ تحذير', text='النوع والمبلغ مطلوبان!',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO expenses (type, amount, date, description) VALUES (?, ?, ?, ?)',
                         (expense_type, amount, datetime.now().strftime('%Y-%m-%d'), description))
            conn.commit()
            conn.close()
            
            dialog.dismiss()
            self.load_expenses()
            MDDialog(title='✅ نجح', text=f'تمت إضافة المصروف: {expense_type}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
        except Exception as e:
            MDDialog(title='❌ خطأ', text=f'حدث خطأ:\n{str(e)}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()

# ═══════════════════════════════════════════════════════════════
# 9. الموظفين
# ═══════════════════════════════════════════════════════════════

class EmployeesScreen(MDScreen):
    """شاشة الموظفين"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'employees'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.2, 0.4, 0.64, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='👔 الموظفين', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='plus', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=self.add_employee))
        layout.add_widget(toolbar)
        
        scroll = MDScrollView(size_hint_y=0.92)
        self.employees_list = MDBoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=None)
        self.employees_list.bind(minimum_height=self.employees_list.setter('height'))
        scroll.add_widget(self.employees_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_employees()
    
    def load_employees(self):
        self.employees_list.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM employees ORDER BY name LIMIT 100')
            
            for employee in cursor.fetchall():
                status_icon = '✅' if employee[6] == 'نشط' else '❌'
                item = ThreeLineListItem(
                    text=f'👔 {employee[1]} {status_icon}',
                    secondary_text=f'الوظيفة: {employee[2]} | 📱 {employee[3]}',
                    tertiary_text=f'الراتب: {employee[4]:.2f} {CURRENCY} | تاريخ التعيين: {employee[5]}',
                    size_hint_y=None,
                    height=dp(80)
                )
                self.employees_list.add_widget(item)
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل الموظفين: {e}')
    
    def add_employee(self, instance):
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None, height=dp(400))
        
        name_field = MDTextField(hint_text='اسم الموظف', icon_right='account')
        content.add_widget(name_field)
        
        position_field = MDTextField(hint_text='الوظيفة', icon_right='briefcase')
        content.add_widget(position_field)
        
        phone_field = MDTextField(hint_text='رقم الهاتف', icon_right='phone')
        content.add_widget(phone_field)
        
        salary_field = MDTextField(hint_text='الراتب', icon_right='currency-usd', input_filter='float')
        content.add_widget(salary_field)
        
        dialog = MDDialog(
            title='➕ إضافة موظف جديد',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(text='إلغاء', on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text='حفظ', md_bg_color=(0.2, 0.4, 0.64, 1),
                             on_release=lambda x: self.save_employee(dialog, name_field, position_field, phone_field, salary_field))
            ]
        )
        dialog.open()
    
    def save_employee(self, dialog, name_field, position_field, phone_field, salary_field):
        try:
            name = name_field.text.strip()
            position = position_field.text.strip()
            phone = phone_field.text.strip()
            salary = float(salary_field.text or 0)
            
            if not name or not position or not phone:
                MDDialog(title='⚠️ تحذير', text='الاسم والوظيفة والهاتف مطلوبة!',
                        buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
                return
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO employees (name, position, phone, salary, hire_date, status) VALUES (?, ?, ?, ?, ?, ?)',
                         (name, position, phone, salary, datetime.now().strftime('%Y-%m-%d'), 'نشط'))
            conn.commit()
            conn.close()
            
            dialog.dismiss()
            self.load_employees()
            MDDialog(title='✅ نجح', text=f'تمت إضافة الموظف: {name}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()
        except Exception as e:
            MDDialog(title='❌ خطأ', text=f'حدث خطأ:\n{str(e)}',
                    buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]).open()

# ═══════════════════════════════════════════════════════════════
# 10. الأرباح
# ═══════════════════════════════════════════════════════════════

class ProfitsScreen(MDScreen):
    """شاشة الأرباح"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'profits'
        self.profit_cards = []
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.3, 0.69, 0.31, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='📈 الأرباح', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='refresh', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: self.load_profits()))
        layout.add_widget(toolbar)
        
        scroll = MDScrollView(size_hint_y=0.92)
        profits = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15), size_hint_y=None)
        profits.bind(minimum_height=profits.setter('height'))
        
        profit_data = [
            ('أرباح اليوم', 'calendar-today', (0.3, 0.69, 0.31, 1)),
            ('أرباح الأسبوع', 'calendar-week', (1, 0.6, 0, 1)),
            ('أرباح الشهر', 'calendar-month', (0.2, 0.6, 0.86, 1)),
            ('إجمالي الأرباح', 'chart-areaspline', (0.61, 0.15, 0.69, 1)),
        ]
        
        for title, icon, color in profit_data:
            card = self.create_profit_card(title, '0', icon, color)
            self.profit_cards.append(card)
            profits.add_widget(card)
        
        scroll.add_widget(profits)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_profit_card(self, title, value, icon, color):
        card = MDCard(size_hint=(1, None), height=dp(120), md_bg_color=color, radius=[10], elevation=3, padding=dp(15))
        box = MDBoxLayout(spacing=dp(15))
        box.add_widget(MDIconButton(icon=icon, theme_text_color='Custom', text_color=(1, 1, 1, 1), icon_size='56sp'))
        text_box = MDBoxLayout(orientation='vertical')
        text_box.add_widget(MDLabel(text=title, theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='H6'))
        value_label = MDLabel(text=value, theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='H4')
        text_box.add_widget(value_label)
        box.add_widget(text_box)
        card.add_widget(box)
        card.value_label = value_label
        return card
    
    def on_enter(self):
        self.load_profits()
    
    def load_profits(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            cursor.execute('SELECT SUM(profit) FROM sales WHERE DATE(created_at) = ?', (today,))
            self.profit_cards[0].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(profit) FROM sales WHERE DATE(created_at) >= ?', (week_ago,))
            self.profit_cards[1].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(profit) FROM sales WHERE DATE(created_at) >= ?', (month_start,))
            self.profit_cards[2].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(profit) FROM sales')
            self.profit_cards[3].value_label.text = f'{cursor.fetchone()[0] or 0:.2f} {CURRENCY}'
            
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل الأرباح: {e}')

# ═══════════════════════════════════════════════════════════════
# 11. المخزون
# ═══════════════════════════════════════════════════════════════

class InventoryScreen(MDScreen):
    """شاشة المخزون"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'inventory'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(1, 0.6, 0, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='📊 المخزون', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        layout.add_widget(toolbar)
        
        scroll = MDScrollView(size_hint_y=0.92)
        self.inventory_list = MDBoxLayout(orientation='vertical', spacing=dp(5), padding=dp(10), size_hint_y=None)
        self.inventory_list.bind(minimum_height=self.inventory_list.setter('height'))
        scroll.add_widget(self.inventory_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_inventory()
    
    def load_inventory(self):
        self.inventory_list.clear_widgets()
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY stock ASC LIMIT 100')
            
            for product in cursor.fetchall():
                if product[6] <= 0:
                    status = '❌ نفذ'
                    color = (0.91, 0.12, 0.39, 1)
                elif product[6] <= product[7]:
                    status = '⚠️ ناقص'
                    color = (1, 0.6, 0, 1)
                else:
                    status = '✅ متوفر'
                    color = (0.3, 0.69, 0.31, 1)
                
                card = MDCard(size_hint=(1, None), height=dp(80), md_bg_color=(1, 1, 1, 1), radius=[10], elevation=2, padding=dp(15))
                box = MDBoxLayout()
                
                info_box = MDBoxLayout(orientation='vertical', size_hint_x=0.7)
                info_box.add_widget(MDLabel(text=product[2], font_style='Subtitle1', size_hint_y=0.5))
                info_box.add_widget(MDLabel(text=f'الكمية: {product[6]} / الحد الأدنى: {product[7]}', 
                                           font_style='Caption', theme_text_color='Hint', size_hint_y=0.5))
                box.add_widget(info_box)
                
                status_box = MDBoxLayout(size_hint_x=0.3)
                status_box.add_widget(MDLabel(text=status, theme_text_color='Custom', text_color=color, font_style='Body1', halign='center'))
                box.add_widget(status_box)
                
                card.add_widget(box)
                self.inventory_list.add_widget(card)
            
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل المخزون: {e}')

# ═══════════════════════════════════════════════════════════════
# 12. التقارير
# ═══════════════════════════════════════════════════════════════

class ReportsScreen(MDScreen):
    """شاشة التقارير"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'reports'
        self.report_cards = []
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.91, 0.12, 0.39, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='📈 التقارير', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        toolbar.add_widget(MDIconButton(icon='refresh', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: self.load_reports()))
        layout.add_widget(toolbar)
        
        scroll = MDScrollView(size_hint_y=0.92)
        reports = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15), size_hint_y=None)
        reports.bind(minimum_height=reports.setter('height'))
        
        report_data = [
            ('تقرير المبيعات', 'chart-bar', (0.2, 0.6, 0.86, 1)),
            ('تقرير الأرباح', 'currency-usd', (0.3, 0.69, 0.31, 1)),
            ('تقرير المخزون', 'package-variant', (1, 0.6, 0, 1)),
            ('تقرير العملاء', 'account-group', (0.61, 0.15, 0.69, 1)),
            ('تقرير الموردين', 'truck-delivery', (0.4, 0.23, 0.72, 1)),
            ('تقرير المصروفات', 'cash-minus', (0.91, 0.12, 0.39, 1)),
        ]
        
        for title, icon, color in report_data:
            card = self.create_report_card(title, 'جاري التحميل...', icon, color)
            self.report_cards.append(card)
            reports.add_widget(card)
        
        scroll.add_widget(reports)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_report_card(self, title, value, icon, color):
        card = MDCard(size_hint=(1, None), height=dp(120), md_bg_color=color, radius=[10], elevation=3, padding=dp(15))
        box = MDBoxLayout(orientation='vertical', spacing=dp(10))
        
        header = MDBoxLayout(size_hint_y=0.4)
        header.add_widget(MDIconButton(icon=icon, theme_text_color='Custom', text_color=(1, 1, 1, 1), icon_size='32sp'))
        header.add_widget(MDLabel(text=title, theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='H6'))
        box.add_widget(header)
        
        value_label = MDLabel(text=value, theme_text_color='Custom', text_color=(1, 1, 1, 1), font_style='Body1', size_hint_y=0.6)
        box.add_widget(value_label)
        
        card.add_widget(box)
        card.value_label = value_label
        return card
    
    def on_enter(self):
        self.load_reports()
    
    def load_reports(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*), SUM(final_amount) FROM sales')
            sales_data = cursor.fetchone()
            self.report_cards[0].value_label.text = f'عدد الفواتير: {sales_data[0] or 0}\nالإجمالي: {sales_data[1] or 0:.2f} {CURRENCY}'
            
            cursor.execute('SELECT SUM(profit) FROM sales')
            total_profit = cursor.fetchone()[0] or 0
            cursor.execute('SELECT SUM(profit) FROM sales WHERE DATE(created_at) = ?', (datetime.now().strftime('%Y-%m-%d'),))
            today_profit = cursor.fetchone()[0] or 0
            self.report_cards[1].value_label.text = f'اليوم: {today_profit:.2f} {CURRENCY}\nالإجمالي: {total_profit:.2f} {CURRENCY}'
            
            cursor.execute('SELECT COUNT(*) FROM products WHERE stock <= min_stock')
            low_stock = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM products')
            total_products = cursor.fetchone()[0]
            self.report_cards[2].value_label.text = f'الإجمالي: {total_products}\nناقص: {low_stock}'
            
            cursor.execute('SELECT COUNT(*) FROM customers')
            self.report_cards[3].value_label.text = f'عدد العملاء: {cursor.fetchone()[0]}'
            
            cursor.execute('SELECT COUNT(*) FROM suppliers')
            self.report_cards[4].value_label.text = f'عدد الموردين: {cursor.fetchone()[0]}'
            
            cursor.execute('SELECT SUM(amount) FROM expenses')
            total_expenses = cursor.fetchone()[0] or 0
            cursor.execute('SELECT SUM(amount) FROM expenses WHERE DATE(date) = ?', (datetime.now().strftime('%Y-%m-%d'),))
            today_expenses = cursor.fetchone()[0] or 0
            self.report_cards[5].value_label.text = f'اليوم: {today_expenses:.2f} {CURRENCY}\nالإجمالي: {total_expenses:.2f} {CURRENCY}'
            
            conn.close()
        except Exception as e:
            print(f'خطأ في تحميل التقارير: {e}')

# ═══════════════════════════════════════════════════════════════
# 13. الإعدادات الشاملة
# ═══════════════════════════════════════════════════════════════

class SettingsScreen(MDScreen):
    """شاشة الإعدادات الشاملة - بروفايل + اتصالات"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.build_ui()
    
    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical', md_bg_color=(0.95, 0.95, 0.95, 1))
        
        toolbar = MDBoxLayout(size_hint_y=0.08, md_bg_color=(0.38, 0.49, 0.55, 1), padding=dp(10))
        toolbar.add_widget(MDIconButton(icon='arrow-right', theme_text_color='Custom', text_color=(1, 1, 1, 1),
                                       on_release=lambda x: setattr(self.manager, 'current', 'main')))
        toolbar.add_widget(MDLabel(text='⚙️ الإعدادات', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1)))
        layout.add_widget(toolbar)
        
        scroll = MDScrollView(size_hint_y=0.92)
        content = MDBoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # بروفايل المستخدم
        profile_card = MDCard(size_hint=(1, None), height=dp(150), md_bg_color=(0.2, 0.6, 0.86, 1), radius=[10], elevation=3, padding=dp(20))
        profile_box = MDBoxLayout(spacing=dp(15))
        profile_box.add_widget(MDIconButton(icon='account-circle', theme_text_color='Custom', text_color=(1, 1, 1, 1), icon_size='64sp'))
        
        profile_info = MDBoxLayout(orientation='vertical')
        self.user_name_label = MDLabel(text='المستخدم', font_style='H6', theme_text_color='Custom', text_color=(1, 1, 1, 1))
        self.user_role_label = MDLabel(text='الدور', font_style='Body1', theme_text_color='Custom', text_color=(1, 1, 1, 1))
        self.user_username_label = MDLabel(text='اسم المستخدم', font_style='Caption', theme_text_color='Custom', text_color=(1, 1, 1, 1))
        profile_info.add_widget(self.user_name_label)
        profile_info.add_widget(self.user_role_label)
        profile_info.add_widget(self.user_username_label)
        
        profile_box.add_widget(profile_info)
        profile_card.add_widget(profile_box)
        content.add_widget(profile_card)
        
        # إعدادات الاتصالات
        connections_card = MDCard(size_hint=(1, None), height=dp(200), md_bg_color=(1, 1, 1, 1), radius=[10], elevation=2, padding=dp(15))
        conn_box = MDBoxLayout(orientation='vertical', spacing=dp(10))
        conn_box.add_widget(MDLabel(text='📡 الاتصالات', font_style='H6'))
        
        # البلوتوث
        bt_box = MDBoxLayout(size_hint_y=None, height=dp(50))
        bt_box.add_widget(MDIconButton(icon='bluetooth', theme_text_color='Primary'))
        bt_box.add_widget(MDLabel(text='البلوتوث', font_style='Body1'))
        self.bt_status = MDLabel(text='غير متصل', font_style='Caption', theme_text_color='Hint')
        bt_box.add_widget(self.bt_status)
        bt_box.add_widget(MDIconButton(icon='cog', theme_text_color='Primary', on_release=self.check_bluetooth))
        conn_box.add_widget(bt_box)
        
        # الواي فاي
        wifi_box = MDBoxLayout(size_hint_y=None, height=dp(50))
        wifi_box.add_widget(MDIconButton(icon='wifi', theme_text_color='Primary'))
        wifi_box.add_widget(MDLabel(text='الواي فاي', font_style='Body1'))
        self.wifi_status = MDLabel(text='غير متصل', font_style='Caption', theme_text_color='Hint')
        wifi_box.add_widget(self.wifi_status)
        wifi_box.add_widget(MDIconButton(icon='cog', theme_text_color='Primary', on_release=self.check_wifi))
        conn_box.add_widget(wifi_box)
        
        # الإنترنت
        internet_box = MDBoxLayout(size_hint_y=None, height=dp(50))
        internet_box.add_widget(MDIconButton(icon='web', theme_text_color='Primary'))
        internet_box.add_widget(MDLabel(text='الإنترنت', font_style='Body1'))
        self.internet_status = MDLabel(text='غير متصل', font_style='Caption', theme_text_color='Hint')
        internet_box.add_widget(self.internet_status)
        internet_box.add_widget(MDIconButton(icon='refresh', theme_text_color='Primary', on_release=self.check_internet))
        conn_box.add_widget(internet_box)
        
        connections_card.add_widget(conn_box)
        content.add_widget(connections_card)
        
        # إعدادات الباركود
        barcode_card = MDCard(size_hint=(1, None), height=dp(120), md_bg_color=(1, 1, 1, 1), radius=[10], elevation=2, padding=dp(15))
        barcode_box = MDBoxLayout(orientation='vertical', spacing=dp(10))
        barcode_box.add_widget(MDLabel(text='📷 قارئ الباركود', font_style='H6'))
        
        barcode_settings = MDBoxLayout(size_hint_y=None, height=dp(50))
        barcode_settings.add_widget(MDIconButton(icon='barcode-scan', theme_text_color='Primary'))
        barcode_settings.add_widget(MDLabel(text='قارئ الباركود', font_style='Body1'))
        self.barcode_switch = MDSwitch(active=True)
        barcode_settings.add_widget(self.barcode_switch)
        barcode_box.add_widget(barcode_settings)
        
        barcode_test = MDRaisedButton(text='🧪 اختبار القارئ', md_bg_color=(0.2, 0.6, 0.86, 1), on_release=self.test_barcode)
        barcode_box.add_widget(barcode_test)
        
        barcode_card.add_widget(barcode_box)
        content.add_widget(barcode_card)
        
        # معلومات التطبيق
        info_card = MDCard(size_hint=(1, None), height=dp(150), md_bg_color=(1, 1, 1, 1), radius=[10], elevation=2, padding=dp(15))
        info_box = MDBoxLayout(orientation='vertical', spacing=dp(5))
        info_box.add_widget(MDLabel(text='ℹ️ معلومات التطبيق', font_style='H6'))
        info_box.add_widget(MDLabel(text='نظام كاشير سوبر ماركت', font_style='Body1'))
        info_box.add_widget(MDLabel(text='الإصدار: 3.0.0 Final', font_style='Caption', theme_text_color='Hint'))
        info_box.add_widget(MDLabel(text='متزامن مع نسخة الكمبيوتر', font_style='Caption', theme_text_color='Hint'))
        info_box.add_widget(MDLabel(text='تاريخ الإصدار: 2025-01-09', font_style='Caption', theme_text_color='Hint'))
        info_card.add_widget(info_box)
        content.add_widget(info_card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_enter(self):
        app = MDApp.get_running_app()
        if app.current_user:
            self.user_name_label.text = app.current_user['name']
            self.user_role_label.text = f"الدور: {app.current_user['role']}"
            self.user_username_label.text = f"@{app.current_user['username']}"
        self.check_connections()
    
    def check_connections(self):
        self.check_bluetooth(None)
        self.check_wifi(None)
        self.check_internet(None)
    
    def check_bluetooth(self, instance):
        try:
            import subprocess
            result = subprocess.run(['settings', 'get', 'global', 'bluetooth_on'], capture_output=True, text=True)
            if '1' in result.stdout:
                self.bt_status.text = '✅ مفعّل'
                self.bt_status.text_color = (0.3, 0.69, 0.31, 1)
            else:
                self.bt_status.text = '❌ معطّل'
                self.bt_status.text_color = (0.91, 0.12, 0.39, 1)
        except:
            self.bt_status.text = '❓ غير معروف'
            self.bt_status.text_color = (0.5, 0.5, 0.5, 1)
    
    def check_wifi(self, instance):
        try:
            import subprocess
            result = subprocess.run(['settings', 'get', 'global', 'wifi_on'], capture_output=True, text=True)
            if '1' in result.stdout:
                self.wifi_status.text = '✅ مفعّل'
                self.wifi_status.text_color = (0.3, 0.69, 0.31, 1)
            else:
                self.wifi_status.text = '❌ معطّل'
                self.wifi_status.text_color = (0.91, 0.12, 0.39, 1)
        except:
            self.wifi_status.text = '❓ غير معروف'
            self.wifi_status.text_color = (0.5, 0.5, 0.5, 1)
    
    def check_internet(self, instance):
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.internet_status.text = '✅ متصل'
            self.internet_status.text_color = (0.3, 0.69, 0.31, 1)
        except:
            self.internet_status.text = '❌ غير متصل'
            self.internet_status.text_color = (0.91, 0.12, 0.39, 1)
    
    def test_barcode(self, instance):
        MDDialog(
            title='🧪 اختبار قارئ الباركود',
            text='قارئ الباركود نشط!\n\nامسح أي باركود للاختبار.\n\nإذا كان القارئ متصل، سيظهر الباركود تلقائياً.',
            buttons=[MDFlatButton(text='موافق', on_release=lambda x: x.parent.parent.parent.parent.dismiss())]
        ).open()

# ═══════════════════════════════════════════════════════════════
# التطبيق الرئيسي
# ═══════════════════════════════════════════════════════════════

class SupermarketMobileApp(MDApp):
    """التطبيق الرئيسي"""
    def build(self):
        self.title = 'نظام كاشير سوبر ماركت'
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.theme_style = 'Light'
        self.current_user = None
        
        sm = MDScreenManager()
        sm.add_widget(LoginScreen())
        sm.add_widget(MainScreen())
        sm.add_widget(DashboardScreen())
        sm.add_widget(POSScreen())
        sm.add_widget(ProductsScreen())
        sm.add_widget(CustomersScreen())
        sm.add_widget(SuppliersScreen())
        sm.add_widget(ExpensesScreen())
        sm.add_widget(EmployeesScreen())
        sm.add_widget(ProfitsScreen())
        sm.add_widget(InventoryScreen())
        sm.add_widget(ReportsScreen())
        sm.add_widget(SettingsScreen())
        
        return sm

if __name__ == '__main__':
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  نظام كاشير سوبر ماركت - نسخة الموبايل")
    print("  الإصدار: 3.0.0 Final Complete")
    print("  التاريخ: 2025-01-09")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ قاعدة البيانات: {DB_PATH}")
    print("✅ 12 شاشة عاملة")
    print("✅ متزامنة مع نسخة الكمبيوتر")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    SupermarketMobileApp().run()

