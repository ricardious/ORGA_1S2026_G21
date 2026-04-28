import re
with open('lib/main.dart', 'r') as f:
    code = f.read()

code = re.sub(r'LiquidGlassLayer\(\s*settings:', 'LiquidGlassLayer(\n      fake: true,\n      settings:', code)
code = re.sub(r'LiquidGlass\.withOwnLayer\(\s*settings:', 'LiquidGlass.withOwnLayer(\n      fake: true,\n      settings:', code)
code = code.replace('fake: !isBluetoothConnected,', 'fake: true,')

with open('lib/main.dart', 'w') as f:
    f.write(code)
