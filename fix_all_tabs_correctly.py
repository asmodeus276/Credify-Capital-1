import os
import glob
import re

html_files = glob.glob('*.html')

# Base names and their paths
def get_base_name(filename):
    # If the file is a sub-page, it has suffixes like -features-and-benefits
    suffixes = ['-features-and-benefits', '-eligibility-and-documents', '-interest-rates-and-charges', '-emi-calculator', '-faq', '-review']
    base = filename.replace('.html', '')
    for suf in suffixes:
        if base.endswith(suf):
            base = base[:-len(suf)]
            break
    return base

groups = {}
for f in html_files:
    base = get_base_name(f)
    if base not in groups:
        groups[base] = []
    groups[base].append(f)

for base, files in groups.items():
    # Only if this looks like a loan page with tabs
    # Some pages might not have tabs, but we'll check inside the file
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
            
        nav_match = re.search(r'<ul[^>]*id="tabs"[^>]*>(.*?)</ul>', content, re.DOTALL)
        if nav_match:
            # We construct the correct nav links based on what files exist for this base
            links_to_create = [
                ('Overview', f'{base}.html'),
                ('Features & Benefits', f'{base}-features-and-benefits.html'),
                ('Eligibility & Documents', f'{base}-eligibility-and-documents.html'),
                ('Interest Rate & Charges', f'{base}-interest-rates-and-charges.html'),
                ('EMI Calculator', f'{base}-emi-calculator.html'),
                ('FAQs', f'{base}-faq.html'),
                ('Reviews', f'{base}-review.html')
            ]
            
            nav_inner_html = ""
            for title, target in links_to_create:
                if os.path.exists(target):
                    active_class = "active" if target == file else ""
                    nav_inner_html += f'''
                        <li class="nav-item">
                            <a href="{target}" class="nav-link {active_class}">{title}</a>
                        </li>'''
            
            # Add Apply Now
            nav_inner_html += '''
                        <li class="nav-item">
                            <a href="apply-now.html" class="nav-link applynow">Apply Now</a>
                        </li>'''
                        
            # Replace the ul
            new_ul = f'<ul id="tabs" class="nav nav-tabs tab-fixed" role="tablist">{nav_inner_html}\n</ul>'
            content = re.sub(r'<ul[^>]*id="tabs"[^>]*>.*?</ul>', new_ul, content, flags=re.DOTALL)
            
            # We also need to fix the display of the tab-pane!
            # Since we hid tab-pane B, C, D in some files
            content = re.sub(r'<!-- hidden -->', '', content)
            content = re.sub(r'<style> .*? { display: none !important; } </style>', '', content)
            
            with open(file, 'w') as f:
                f.write(content)
            print(f"Fixed tabs in {file}")
