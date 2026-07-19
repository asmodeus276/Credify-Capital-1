import glob

for file in glob.glob('*.html'):
    with open(file, 'r') as f:
        content = f.read()
    
    idx = content.find('<!-- TAB INIT FIX:')
    if idx != -1:
        end_idx = content.find('</script>', idx)
        if end_idx != -1:
            end_idx += len('</script>')
            new_content = content[:idx] + content[end_idx:]
            with open(file, 'w') as f:
                f.write(new_content)
            print(f"Removed from {file}")
