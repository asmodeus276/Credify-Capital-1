import re

with open('business-loan.html', 'r') as f:
    content = f.read()

# Replace the inner content
new_content = re.sub(
    r'<h2 class="acco-link">Business Loan Features &amp; Benefits</h2>\s*<div class="acco-body">\s*<div class="tab-inner-content">.*?</div>',
    r'''<h2 class="acco-link">Business Loan Overview</h2>
    <div class="acco-body">
        <div class="tab-inner-content">
            <p><strong>Unlocking your business potential</strong></p>
            <p>Fuel growth and working capital for your business with a Credify Capital Business Loan. Get fast approval and customized loan solutions to take your business to the next level.</p>
            <p>We offer customized business loan solutions to help small and medium enterprises achieve their business goals without putting up collateral. With instant approvals and quick disbursals, you can ensure your business always stays ahead.</p>
        </div>''',
    content,
    flags=re.DOTALL
)

# Also fix the nav-tabs active state
# Currently it points to Features & Benefits as active because we copied it
new_content = new_content.replace(
    '<a href="business-loan-features-and-benefits.html" class="nav-link active">Features & Benefits</a>',
    '<a href="business-loan-features-and-benefits.html" class="nav-link ">Features & Benefits</a>'
)
new_content = new_content.replace(
    '<a href="business-loan.html" class="nav-link ">Overview</a>',
    '<a href="business-loan.html" class="nav-link active">Overview</a>'
)

# Replace the <title> tag
new_content = re.sub(r'<title>.*?</title>', '<title>Business Loan - Credify Capital</title>', new_content)

with open('business-loan.html', 'w') as f:
    f.write(new_content)
print("Fixed overview")
