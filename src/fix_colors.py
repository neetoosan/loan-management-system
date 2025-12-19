#!/usr/bin/env python
"""Fix Flet colors in all project files"""
import os

def fix_colors(content):
    """Replace invalid Flet colors with valid ones"""
    replacements = {
        'ft.Colors.LIGHT_BLUE_400': 'ft.Colors.BLUE_200',
        'ft.Colors.GREY_850': '"#2a2a2a"',
        'ft.Colors.GREY_900': '"#1a1a1a"',
        'ft.Colors.GREY_400': 'ft.Colors.GREY',
        'ft.Colors.GREY_700': 'ft.Colors.GREY',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    return content

# Files to update
files = [
    'components/navigation.py',
    'views/loan_screen.py',
    'views/contribution_screen.py',
    'views/member_dialog.py',
    'views/settings_screen.py',
]

base_path = os.path.dirname(os.path.abspath(__file__))

for file_path in files:
    full_path = os.path.join(base_path, file_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_content = fix_colors(content)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f'✓ Updated: {file_path}')
    else:
        print(f'✗ File not found: {file_path}')

print('Color fixes complete!')
