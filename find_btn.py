with open('temp.js', 'rb') as f:
    for i, b_line in enumerate(f):
        if b'button class' in b_line:
            line_str = b_line.decode('utf-8', errors='ignore')
            if 'Thích' in line_str or 'Chia' in line_str or '&#9825;' in line_str or '&#10150;' in line_str:
                print(f'{i+1}: {line_str.strip()}')
