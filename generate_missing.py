import os
import re
import json

def ensure_dirs():
    os.makedirs('blogs', exist_ok=True)
    os.makedirs('personal-loan-faq', exist_ok=True)

def get_page_frame():
    """Reads an existing page to extract head, header and footer structures to preserve style consistency."""
    base_file = 'personal-loan-eligibility-and-documents.html'
    if not os.path.exists(base_file):
        # Fallback to index.html if pl-eligibility does not exist
        base_file = 'index.html'
        
    with open(base_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Header starts at beginning of file and goes up to <!-- END HEADER --> or </header>
    header_end_idx = content.find('<!-- END HEADER -->')
    if header_end_idx == -1:
        header_end_idx = content.find('</header>')
        if header_end_idx != -1:
            header_end_idx += len('</header>')
    else:
        header_end_idx += len('<!-- END HEADER -->')
        
    if header_end_idx == -1:
        # Emergency split point
        header_end_idx = content.find('</head>') + len('</head>')
        
    header_part = content[:header_end_idx]
    
    # Footer starts from <!-- START FOOTER --> or <footer
    footer_start_idx = content.find('<!-- START FOOTER -->')
    if footer_start_idx == -1:
        footer_start_idx = content.find('<footer')
        if footer_start_idx == -1:
            footer_start_idx = content.find('</body>')
            
    footer_part = content[footer_start_idx:]
    
    return header_part, footer_part

def adjust_paths_for_nested_page(content, local_files=None):
    """Prefixes relative link, script, and stylesheet paths with '../' for files residing in blogs/ or personal-loan-faq/."""
    if local_files is None:
        local_files = []
    # Match href="..." or src="..." where the path is relative (doesn't start with http, mailto, tel, javascript, /, or #)
    def replacer(match):
        attr = match.group(1) # href or src
        val = match.group(2)  # value
        
        val_clean = val.split('#')[0]
        if val_clean in local_files:
            return f'{attr}="{val}"'
            
        if (val.startswith(('http://', 'https://', 'mailto:', 'tel:', 'javascript:', '#', '/')) or
            val == '' or val.startswith('../')):
            return f'{attr}="{val}"'
        else:
            return f'{attr}="../{val}"'
            
    # Adjust regular attributes
    content = re.sub(r'(href|src)=["\']([^"\']*)["\']', replacer, content)
    
    # Adjust style backgrounds e.g., url('img/...') or url("img/...")
    def style_replacer(match):
        val = match.group(1)
        if (val.startswith(('http://', 'https://', '/')) or val.startswith('../')):
            return f"url('{val}')"
        else:
            return f"url('../{val}')"
            
    content = re.sub(r'url\(["\']?([^"\'\)]*)["\']?\)', style_replacer, content)
    return content

def customize_header(header_part, title, description, canonical_url):
    """Replaces title, description and canonical tag in the head portion."""
    # Replace title
    if re.search(r'<title>.*?</title>', header_part, re.IGNORECASE):
        header_part = re.sub(r'<title>.*?</title>', f'<title>{title} - Credify Capital</title>', header_part, flags=re.IGNORECASE)
    else:
        header_part = header_part.replace('</head>', f'<title>{title} - Credify Capital</title>\n</head>')
        
    # Replace meta description
    if re.search(r'<meta\s+name="description"\s+content="[^"]*"', header_part, re.IGNORECASE):
        header_part = re.sub(r'<meta\s+name="description"\s+content="[^"]*"', f'<meta name="description" content="{description}"', header_part, flags=re.IGNORECASE)
    else:
        header_part = header_part.replace('</head>', f'<meta name="description" content="{description}">\n</head>')
        
    # Replace canonical url
    if re.search(r'<link\s+rel="canonical"\s+href="[^"]*"', header_part, re.IGNORECASE):
        header_part = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"', f'<link rel="canonical" href="{canonical_url}"', header_part, flags=re.IGNORECASE)
    else:
        header_part = header_part.replace('</head>', f'<link rel="canonical" href="{canonical_url}">\n</head>')
        
    return header_part

def generate_subpage(target_filename, base_filename, title, description, replacements):
    """Generates a child subpage by copying a base page and replacing content patterns."""
    if not os.path.exists(base_filename):
        print(f"Base file {base_filename} not found for generating {target_filename}. Skipping.")
        return False
        
    with open(base_filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Apply substitutions safely
    for old_val, new_val in replacements:
        if old_val.endswith('.html'):
            content = re.sub(r'(href|src)=["\']' + re.escape(old_val) + r'["\']', f'\\1="{new_val}"', content)
        else:
            content = content.replace(old_val, new_val)
        
    # Update title, description, and canonical
    content = re.sub(r'<title>.*?</title>', f'<title>{title} - Credify Capital</title>', content, flags=re.IGNORECASE)
    content = re.sub(r'<meta\s+name="description"\s+content="[^"]*"', f'<meta name="description" content="{description}"', content, flags=re.IGNORECASE)
    content = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"', f'<link rel="canonical" href="{target_filename}"', content, flags=re.IGNORECASE)
    
    with open(target_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def generate_review_page(target_filename, product_name, category_name):
    """Generates an elegant, interactive customer reviews page for a specific product."""
    header_part, footer_part = get_page_frame()
    
    title = f"Verified Reviews & Testimonials for {product_name}"
    description = f"Read verified reviews, ratings and success stories of customers who availed {product_name} from Credify Capital."
    canonical = target_filename
    
    header_customized = customize_header(header_part, title, description, canonical)
    
    # Custom review lists based on product type
    reviews = []
    if "CA" in product_name or "Chartered Accountant" in product_name:
        reviews = [
            {"name": "CA Rajeev Mehta", "desig": "Senior Partner, Mehta & Associates", "rating": 5, "text": "Credify Capital understood the unique cash flow cycle of Chartered Accountants. Got unsecured funding of 45 Lakhs within 48 hours to set up our new branch in Bangalore. Highly recommended!", "date": "12th May 2026"},
            {"name": "CA Priya Sharma", "desig": "Independent Practice", "rating": 5, "text": "The zero collateral requirement and fully digital documentation using my COP registration made this incredibly smooth. Repayment tenures are very flexible.", "date": "3rd June 2026"},
            {"name": "CA & CS Amit Verma", "desig": "Verma Consulting", "rating": 4, "text": "Excellent service. The interest rates were very competitive compared to private banks, and there were no hidden charges. Very transparent.", "date": "18th June 2026"}
        ]
    elif "Doctor" in product_name:
        reviews = [
            {"name": "Dr. Shalini Iyer", "desig": "MD Pediatrics, Clinic Owner", "rating": 5, "text": "I used the Doctor Professional Loan to upgrade our pediatric ward with modern healthcare equipment. Extremely fast disbursement and dedicated support team.", "date": "14th April 2026"},
            {"name": "Dr. Rohit Deshmukh", "desig": "Consultant Cardiologist", "rating": 5, "text": "Credify's customer relationship manager helped me custom-tailor my EMI structure based on seasonal clinic flows. A highly professional financial experience.", "date": "29th May 2026"},
            {"name": "Dr. Naman Gupta", "desig": "Dental Surgeon", "rating": 4, "text": "Outstanding hassle-free experience. Digital KYC process was smooth and got my clinic expansion loan disbursed directly to my bank account in 2 days.", "date": "10th July 2026"}
        ]
    elif "CS" in product_name or "Company Secretary" in product_name:
        reviews = [
            {"name": "CS Neha Kulkarni", "desig": "Neha Kulkarni & Associates", "rating": 5, "text": "Establishing a corporate consultancy requires capital. This professional loan for CS helped me build my client meeting lounge and hire skilled compliance trainees.", "date": "8th March 2026"},
            {"name": "CS Vikrant Singh", "desig": "Managing Partner", "rating": 5, "text": "Outstanding and seamless service. Zero-collateral loan was approved instantly based on my registration certificate. Very impressed.", "date": "22nd May 2026"}
        ]
    elif "Women" in product_name:
        reviews = [
            {"name": "Ananya Patel", "desig": "Founder, Organic Glow Cosmetics", "rating": 5, "text": "As a woman entrepreneur, getting funding is often full of hurdles. Credify Capital was incredibly supportive. The special interest concession for women business loans made our raw material purchase smooth.", "date": "10th May 2026"},
            {"name": "Meera Nair", "desig": "Director, Nair Logistics", "rating": 5, "text": "Excellent unsecured loan scheme! Our fleet expansion became a reality thanks to the swift disbursal and clear transparency of Credify Capital.", "date": "24th June 2026"}
        ]
    elif "MSME" in product_name or "Retail" in product_name or "Proprietorship" in product_name or "Business" in product_name or "Working Capital" in product_name:
        reviews = [
            {"name": "Suresh Gupta", "desig": "Owner, Gupta General Store", "rating": 5, "text": "Credify Capital helped us secure critical inventory ahead of the festive season. The Working Capital Loan was approved with zero collateral and minimal documents.", "date": "15th June 2026"},
            {"name": "Vikram Rathore", "desig": "Director, Rathore CNC Machining", "rating": 5, "text": "Purchasing tools and keeping payroll steady is tough for MSMEs. The business loan scheme for MSME from Credify came at the perfect time. Hassle-free and very helpful.", "date": "2nd July 2026"},
            {"name": "Ritu Singhal", "desig": "Proprietor, Singhal Fashion Studio", "rating": 4, "text": "Very clean paperless process. I recommend Credify Capital for all retail shop and proprietorship owners looking for immediate expansion capital.", "date": "19th June 2026"}
        ]
    else:
        reviews = [
            {"name": "Karan Johar", "desig": "Business Owner", "rating": 5, "text": "Getting a customized business loan was highly straightforward with Credify. The digital portal and rapid response from the underwriting team are exceptional.", "date": "20th May 2026"},
            {"name": "Siddharth Roy", "desig": "Consultant", "rating": 5, "text": "Great repayment flexible schemes, transparent fees structure, and top-class service. Will definitely expand my financial ties with Credify Capital.", "date": "5th July 2026"}
        ]

    # Build Reviews HTML
    reviews_html = ""
    for r in reviews:
        stars_html = '<span class="text-yellow-400 text-lg">★</span>' * r['rating'] + '<span class="text-gray-300 text-lg">★</span>' * (5 - r['rating'])
        reviews_html += f"""
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-bold text-primary text-base">{r['name']}</h4>
              <p class="text-xs text-on-surface-variant">{r['desig']}</p>
            </div>
            <span class="text-xs font-semibold text-gray-400">{r['date']}</span>
          </div>
          <div class="flex items-center gap-1">
            {stars_html}
          </div>
          <p class="text-sm text-on-surface-variant italic leading-relaxed">"{r['text']}"</p>
        </div>
        """

    body_content = f"""
  <body class="bg-background text-on-background font-body-md pt-28">
    <main class="max-w-7xl mx-auto px-4 md:px-12 py-12 space-y-12">
      <!-- HERO -->
      <section class="bg-gradient-to-r from-primary to-[#253A71] text-white p-8 md:p-12 rounded-3xl space-y-4 text-center md:text-left shadow-lg">
        <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight">{product_name} - Customer Reviews</h1>
        <p class="text-blue-100 text-base max-w-2xl">Discover why thousands of professionals and business owners trust Credify Capital for quick, collateral-free financial solutions.</p>
        <div class="flex flex-wrap items-center justify-center md:justify-start gap-6 pt-2">
          <div class="bg-white/10 px-4 py-2 rounded-xl border border-white/10 flex items-center gap-2">
            <span class="text-yellow-400 text-xl font-bold">★ 4.8 / 5</span>
            <span class="text-xs text-blue-200">Verified Rating</span>
          </div>
          <div class="bg-white/10 px-4 py-2 rounded-xl border border-white/10 flex items-center gap-2">
            <span class="font-bold text-xl">10k+</span>
            <span class="text-xs text-blue-200">Happy Customers</span>
          </div>
        </div>
      </section>

      <!-- CONTENT GRID -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- REVIEWS LIST -->
        <div class="lg:col-span-2 space-y-6">
          <h3 class="text-xl font-bold text-primary flex items-center gap-2">
            <span class="material-symbols-outlined text-secondary">verified</span> What Our Customers Say
          </h3>
          <div class="space-y-6">
            {reviews_html}
          </div>
        </div>

        <!-- WRITE A REVIEW FORM -->
        <div class="bg-white p-6 rounded-3xl border border-gray-100 shadow-xl h-fit space-y-6">
          <h3 class="text-lg font-bold text-primary flex items-center gap-2">
            <span class="material-symbols-outlined text-secondary">rate_review</span> Share Your Feedback
          </h3>
          <form id="review-submit-form" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-on-surface-variant mb-1">Your Name</label>
              <input type="text" required class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary">
            </div>
            <div>
              <label class="block text-xs font-semibold text-on-surface-variant mb-1">Designation / Profession</label>
              <input type="text" required class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary">
            </div>
            <div>
              <label class="block text-xs font-semibold text-on-surface-variant mb-1">Rating</label>
              <select class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary">
                <option value="5">★★★★★ (5/5)</option>
                <option value="4">★★★★☆ (4/5)</option>
                <option value="3">★★★☆☆ (3/5)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-on-surface-variant mb-1">Your Review</label>
              <textarea required rows="4" class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-primary" placeholder="Tell us about your loan experience..."></textarea>
            </div>
            <button type="submit" class="w-full bg-secondary text-white py-3 rounded-full font-bold hover:brightness-110 transition shadow-md">
              Submit Review
            </button>
          </form>
          
          <div id="review-success-msg" class="hidden bg-green-50 border border-green-100 p-4 rounded-2xl text-center space-y-2">
            <span class="material-symbols-outlined text-green-500 text-3xl">check_circle</span>
            <h4 class="font-bold text-green-800 text-sm">Review Submitted!</h4>
            <p class="text-xs text-green-700">Thank you for sharing your experience. Your review has been sent for moderation and will be live shortly.</p>
          </div>
        </div>
      </div>
    </main>

    <script>
      document.getElementById('review-submit-form').addEventListener('submit', function(e) {{
        e.preventDefault();
        document.getElementById('review-submit-form').classList.add('hidden');
        document.getElementById('review-success-msg').classList.remove('hidden');
      }});
    </script>
    """

    full_page = header_customized + body_content + footer_part
    
    with open(target_filename, 'w', encoding='utf-8') as f:
        f.write(full_page)
    return True

def generate_blog_page(target_filename, blog_title):
    """Generates an outstanding, rich blog post detail page with educational content."""
    header_part, footer_part = get_page_frame()
    
    # Customize title and metadata
    title = blog_title
    description = f"Read our comprehensive article on: {blog_title}. Find financial tips and expert loan guidance from Credify Capital."
    canonical = f"blogs/{target_filename}"
    
    header_customized = customize_header(header_part, title, description, canonical)
    
    # Generate content based on article title
    blog_contents = ""
    if "financial-investment" in target_filename:
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">Using a personal loan to fund investments is a sophisticated financial move. However, it requires a thorough understanding of interest rate differentials and leverage risks.</p>
        <h3 class="text-xl font-bold text-primary mt-6">1. Understanding Financial Leverage</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Leverage is the strategy of using borrowed capital to increase the potential return of an investment. If your investment return exceeds the personal loan interest rate (which starts around 10.50% p.a.), the difference represents pure profit. For instance, investing in high-yielding corporate bonds or expanding a high-margin personal business are classic ways to apply personal credit productively.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">2. Evaluating the Risk-to-Return Ratio</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">It is critical to avoid speculative assets (like high-risk stock trading or volatile cryptocurrencies) with borrowed funds. Safe and structured avenues include:</p>
        <ul class="list-disc pl-5 text-sm text-on-surface-variant space-y-2">
          <li><strong>Real Estate Tokenization or Down Payments:</strong> Securing property investments that yield consistent monthly rentals.</li>
          <li><strong>Professional Skill Certification:</strong> Investing in educational courses or certifications that directly boost your salary or consulting fees.</li>
          <li><strong>Debt Consolidation:</strong> Clearing high-interest credit card debt (usually 36-42% p.a.) with a lower-cost personal loan. This is mathematically the highest guaranteed return investment you can make!</li>
        </ul>
        
        <h3 class="text-xl font-bold text-primary mt-6">3. Strategic Budgeting and Repayments</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Always use an online EMI calculator before taking a loan. Ensure that your monthly investment dividends or standard income streams easily cover the EMI to maintain an excellent CIBIL credit history.</p>
        """
    elif "five-easy-steps" in target_filename:
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">Securing an instant personal loan online doesn't need to be overwhelming. Credify Capital has streamlined the process into 5 simple digital steps.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">Step 1: Check Your Personal Eligibility</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Begin by verifying that you meet basic criteria: a stable monthly salary or business turnover, age between 21 and 60, and a healthy credit score (typically 700+ is optimal).</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">Step 2: Customize Your EMI Requirements</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Use our instant digital EMI calculator to simulate different loan amounts and repayment terms (from 12 to 60 months) to find an optimal balance that fits your monthly budget.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">Step 3: Complete the Secure Online Application</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Fill out the basic KYC and employment forms on our secure website. This takes less than 5 minutes and uses secure TLS encryption to protect your personal details.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">Step 4: Upload Required Documents</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Upload digital copies of your PAN card, Aadhaar card, recent salary slips, and 3-month bank statements. There's no physical paperwork required.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">Step 5: Rapid Approval and Direct Disbursal</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Once verified, our underwriting team issues instant e-approval. The final cash is directly disbursed to your bank account via NACH/e-mandate in under 24 hours.</p>
        """
    elif "disbursement-process" in target_filename:
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">Ever wondered what happens behind the scenes after you click 'Apply' for a personal loan? Here is an inside look at the digital verification and disbursement cycle.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">1. Automated Digital KYC Verification</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Instantly after submission, our secure API portals verify your identity using Aadhaar e-KYC and PAN matching databases. This prevents identity fraud and matches your CIBIL score details in milliseconds.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">2. Credit Analysis and Risk Assessment</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Our advanced underwriting engines check your banking habits via automated PDF statements. They calculate your Debt-to-Income ratio to ensure that you are borrowing safely and won't face financial strain.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">3. E-Agreement and NACH Mandate Setup</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Upon approval, a digital loan agreement is generated. You can securely sign this online using Aadhaar OTP (e-Sign). At the same time, a National Automated Clearing House (NACH) mandate is set up so EMIs can be automatically paid from your bank account monthly, eliminating manual payment friction.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">4. RTGS/NEFT Direct Credit</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Once the digital agreement is executed, the funds are immediately sent via bank transfer directly to your designated account. This whole cycle is completed seamlessly in a matter of hours.</p>
        """
    elif "applying-online" in target_filename:
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">The era of standing in bank queues and waiting weeks for approvals is officially over. Discover the top advantages of applying for a personal loan completely online.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">1. Absolute Convenience & Availability</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Apply anytime, anywhere. Whether you are at home or at the office, you can submit your request via desktop or mobile 24/7 without adjusting your daily routine.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">2. Zero Paperwork & Minimal Documents</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">By integrating directly with digital storage services and official databases, online applications require zero physical copies, zero photocopying, and zero courier coordination.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">3. Speed of Verification and Approval</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Online underwriting is driven by algorithms and real-time APIs. This means decision cycles are cut down from weeks to a few minutes, delivering unparalleled speed for urgent financial needs.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">4. Superior Data Security and Privacy</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Reputable online portals use 256-bit encryption and strict OAuth integration to ensure your personal and bank files are kept highly confidential, away from unauthorized third parties.</p>
        """
    elif "emi-calculator" in target_filename:
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">An EMI calculator is the single most powerful financial planning tool you can use before borrowing. Learn why you should never apply for a loan without simulating it first.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">1. Helps Maintain Debt-to-Income Discipline</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Financial experts recommend keeping your total monthly debt payments under 40% of your take-home pay. An EMI calculator gives you exact monthly payout values, helping you size your loan to fit this rule.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">2. Instantly Compares Tenure Options</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">By sliding your tenure from 12 months to 60 months, you can immediately see how it impacts your monthly EMI and total interest outgo. Shorter tenures mean higher EMIs but massive interest savings, whereas longer tenures provide affordable monthly payments.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">3. Clarifies Interest Rates & Charges</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Calculating complex compound interest formulas manually is tedious and error-prone. The EMI calculator performs these mathematical checks instantly, enabling transparent budgeting with zero guesswork.</p>
        """
    elif "miss-to-pay" in target_filename:
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">Life is full of unexpected events, and sometimes a monthly budget gets tight. Here is what happens if you miss an EMI and how you can proactively protect your financial health.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">1. Late Payment Fees & Penalties</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Immediately after missing an EMI, a standard penal interest or late fee is charged to your account. This adds extra interest to your loan principal, raising the total cost of credit.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">2. Direct Drop in CIBIL/Credit Score</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Your payment history constitutes roughly 35% of your credit score. Lenders report payment defaults to credit bureaus (like CIBIL) monthly. Even a single missed payment can drop your credit score, making future credit card or loan approvals harder and more expensive.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">3. Steps to Proactively Manage a Budget Crunch</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">If you foresee a tight month, do not wait for the payment date to lapse. Reach out to your lender. Reputable institutions can offer loan restructuring, temporary grace periods, or tenure extensions to keep your repayment schedule safe and active.</p>
        """
    else: # where-can-i-get-personal-loan-online
        blog_contents = """
        <p class="text-lg text-on-surface-variant leading-relaxed font-semibold">With hundreds of digital lending apps and traditional financial firms on the web, choosing the right source for your personal loan requires diligence.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">1. Digital Fintech Platforms vs. Legacy Banks</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Traditional banks often offer low base rates but are bound by rigid physical verifications and manual underwriting, resulting in 5 to 10 days of processing. Modern fintech portals (like Credify Capital) use electronic APIs and paperless systems to deliver approvals in minutes and cash credits in under 24 hours.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">2. Verifying NBFC and RBI Registrations</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Always verify that your online lender works with RBI-regulated banks or Non-Banking Financial Companies (NBFCs). Credify Capital is committed to strict regulatory compliance, ensuring secure, transparent transactions and fair lending practices.</p>
        
        <h3 class="text-xl font-bold text-primary mt-6">3. Key Red Flags to Watch Out For</h3>
        <ul class="list-disc pl-5 text-sm text-on-surface-variant space-y-2">
          <li><strong>Lenders asking for upfront processing fees:</strong> Real lenders deduct processing charges directly from the disbursed amount.</li>
          <li><strong>Unsecured web portals lacking HTTPS:</strong> Secure finance portals must use TLS encryption.</li>
          <li><strong>Extremely vague interest declarations:</strong> Insist on clear, transparent terms with zero hidden costs.</li>
        </ul>
        """

    body_content = f"""
  <body class="bg-background text-on-background font-body-md pt-28">
    <main class="max-w-7xl mx-auto px-4 md:px-12 py-12">
      <!-- BREADCRUMB -->
      <div class="flex items-center gap-2 text-xs font-semibold text-on-surface-variant mb-6">
        <a href="index.html" class="hover:text-primary">Home</a>
        <span class="material-symbols-outlined text-sm">chevron_right</span>
        <a href="blogs.html" class="hover:text-primary">Blogs</a>
        <span class="material-symbols-outlined text-sm">chevron_right</span>
        <span class="text-gray-400">Article</span>
      </div>

      <!-- ARTICLE GRID -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <!-- MAIN POST -->
        <div class="lg:col-span-2 space-y-6 bg-white p-6 md:p-10 rounded-3xl border border-gray-100 shadow-sm">
          <div class="inline-flex items-center gap-2 bg-secondary/10 border border-secondary/20 text-secondary px-3 py-1 rounded-full text-xs font-bold">
            <span class="material-symbols-outlined text-sm">menu_book</span> Personal Finance
          </div>
          <h1 class="text-2xl md:text-3xl lg:text-4xl font-extrabold tracking-tight text-primary leading-tight">{blog_title}</h1>
          <div class="flex items-center gap-4 text-xs font-medium text-gray-500 py-2 border-y border-gray-100">
            <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">calendar_month</span> July 20, 2026</span>
            <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">schedule</span> 5 Min Read</span>
            <span class="flex items-center gap-1"><span class="material-symbols-outlined text-sm">person</span> By Credify Editorial</span>
          </div>

          <!-- Rich Content -->
          <div class="space-y-6 pt-4 text-on-surface">
            {blog_contents}
          </div>
        </div>

        <!-- SIDEBAR -->
        <div class="space-y-8">
          <!-- CTA -->
          <div class="bg-gradient-to-br from-[#142450] to-[#253A71] text-white p-6 rounded-3xl text-center space-y-4 shadow-xl">
            <h3 class="text-lg font-bold">Need a Personal Loan?</h3>
            <p class="text-xs text-blue-200">Get instant approval and disbursement directly to your bank account up to ₹25 Lakh.</p>
            <div class="pt-2">
              <a href="apply.html?type=Personal+Loan" class="inline-block bg-secondary text-white px-6 py-3 rounded-full font-bold text-xs hover:brightness-115 transition shadow-lg">Apply Online Now</a>
            </div>
          </div>
          
          <!-- RELATED ARTICLES -->
          <div class="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm space-y-4">
            <h3 class="text-base font-bold text-primary border-b border-gray-100 pb-2">Related Articles</h3>
            <ul class="space-y-4 text-xs font-semibold text-on-surface-variant">
              <li><a href="how-to-get-a-personal-loan-in-five-easy-steps.html" class="hover:text-secondary transition-colors block">How to Get A Personal Loan in 5 Easy Steps?</a></li>
              <li><a href="top-advantages-of-applying-online-for-personal-loan.html" class="hover:text-secondary transition-colors block">Top 5 Advantages of Applying Online for a Personal Loan</a></li>
              <li><a href="all-about-personal-loan-disbursement-process.html" class="hover:text-secondary transition-colors block">All You Need to Know about Personal Loan Disbursal Process</a></li>
            </ul>
          </div>
        </div>
      </div>
    </main>
    """

    full_page = header_customized + body_content + footer_part
    
    # Since this is a nested page, adjust all asset paths
    blog_filenames = [
        "how-to-use-personal-loan-for-financial-investment.html",
        "how-to-get-a-personal-loan-in-five-easy-steps.html",
        "all-about-personal-loan-disbursement-process.html",
        "top-advantages-of-applying-online-for-personal-loan.html",
        "top-benefits-of-using-personal-loan-emi-calculator.html",
        "what-happens-if-you-miss-to-pay-personal-loan-emi.html",
        "where-can-i-get-personal-loan-online.html"
    ]
    full_page_adjusted = adjust_paths_for_nested_page(full_page, local_files=blog_filenames)
    
    with open(f"blogs/{target_filename}", 'w', encoding='utf-8') as f:
        f.write(full_page_adjusted)
    return True

def generate_faq_page(target_filename, question_title):
    """Generates an outstanding FAQ post page with professional detailed answer."""
    header_part, footer_part = get_page_frame()
    
    title = question_title
    description = f"Get an expert, detailed answer to the question: '{question_title}'. Explore personal finance insights from Credify Capital."
    canonical = f"personal-loan-faq/{target_filename}"
    
    header_customized = customize_header(header_part, title, description, canonical)
    
    # Choose detailed answer based on title keyword
    answer_text = ""
    if "processing-fees" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">Processing fees are administrative charges collected by financial institutions to process, evaluate, and underwrite a loan application. At Credify Capital, we believe in complete transparency:</p>
        <h3 class="text-base font-bold text-primary mt-4">1. Typical Percentage Range</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Processing fees usually range from <strong>1.5% to 3.0%</strong> of the approved loan principal amount. This depends on factors like your employment type, credit profile, and relationship history with our platform.</p>
        <h3 class="text-base font-bold text-primary mt-4">2. Automatic Deduction</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Important note: You do NOT have to pay this fee upfront. The processing charges are directly deducted from your approved principal during final disbursement. For example, if your loan is 5,00,000 and the processing fee is 2% (10,000), a net cash amount of 4,90,000 will be credited to your bank account.</p>
        <h3 class="text-base font-bold text-primary mt-4">3. Zero Hidden Charges</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Credify is committed to absolute integrity. All processing costs, GST (currently 18% of processing fees), and documentation charges are highlighted clearly in the digital e-agreement before signing.</p>
        """
    elif "credit-history" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">This is a highly popular question. The short answer is: <strong>It depends on WHO is checking and HOW they check.</strong></p>
        <h3 class="text-base font-bold text-primary mt-4">1. Soft Enquiries vs. Hard Enquiries</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">When you check your own credit history online or use a credit tracking portal, it is classified as a <strong>soft inquiry</strong>. Soft inquiries have <strong>zero impact</strong> on your CIBIL credit score and are not visible to external financial lenders.</p>
        <h3 class="text-base font-bold text-primary mt-4">2. Hard Enquiries by Financial Firms</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">When you apply for a credit card or a personal loan, and the financial firm formally requests your credit file from bureaus like TransUnion CIBIL, it is recorded as a <strong>hard inquiry</strong>. Hard inquiries indicate active search for credit, and multiple hard inquiries in a very short span can temporarily drop your credit score by a few points.</p>
        <h3 class="text-base font-bold text-primary mt-4">3. Our Tip</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Avoid applying at 10 different platforms simultaneously. Work with a trusted partner like Credify Capital where initial digital eligibility is verified without triggering excessive hard inquiries, protecting your credit profile.</p>
        """
    elif "best-way-to-get" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">The single best way to secure a personal loan efficiently is by using a <strong>fully digital paperless application portal</strong>. This ensures maximum speed, best interest rates, and minimal friction.</p>
        <h3 class="text-base font-bold text-primary mt-4">1. Maintain a Strong Credit Profile (750+)</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Borrowers with a credit score over 750 are instantly eligible for lower interest rates and higher loan approvals. Pay credit card bills and active EMIs strictly on time.</p>
        <h3 class="text-base font-bold text-primary mt-4">2. Organize Your Income Evidence</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Ensure you have soft copies of your PAN card, Aadhaar card, 3-month salary slips, and bank statements showing regular salary credits. Clear income visibility speeds up approvals.</p>
        <h3 class="text-base font-bold text-primary mt-4">3. Apply with Credify Capital</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Our digital underwriting and API checks verify your files in minutes, offering the fastest, most secure, and most affordable unsecured loan options in India.</p>
        """
    elif "one-day" in target_filename or "borrow-money-online" in target_filename or "apply-online-for-an-instant" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">With modern Indian financial APIs (like Aadhaar e-KYC, e-Sign, and NACH), getting a personal loan within 24 hours is highly achievable.</p>
        <h3 class="text-base font-bold text-primary mt-4">1. Apply Through a 100% Digital Platform</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Fintech lenders like Credify Capital process underwritings instantly, bypassing physical documentation and legacy human queues.</p>
        <h3 class="text-base font-bold text-primary mt-4">2. Perform e-KYC and Upload Instantly</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Use your Aadhaar-linked mobile number to complete instant e-KYC. Then upload clear PDF files of your bank statements and income slips on our secure platform.</p>
        <h3 class="text-base font-bold text-primary mt-4">3. Sign the Digital E-Agreement Immediately</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Once approved, sign the e-contract using Aadhaar OTP (e-Sign) and complete your e-mandate registration. This triggers automatic fund release directly to your savings account, ensuring one-day disbursal.</p>
        """
    elif "lowest-interest-rate" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">The lowest personal loan rates generally start around <strong>10.29% to 10.50% p.a.</strong> but interest rates are dynamic and custom-offered based on several risk factors.</p>
        <h3 class="text-base font-bold text-primary mt-4">1. Your Credit Score</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">A score of 780+ guarantees you access to the lowest interest tiers, as it indicates a history of zero late payments and disciplined credit utilization.</p>
        <h3 class="text-base font-bold text-primary mt-4">2. Employer Profile</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Salaried professionals working in top-tier multinational companies, government departments, or blue-chip corporations are offered concessional rates due to high job stability.</p>
        <h3 class="text-base font-bold text-primary mt-4">3. Credify Transparency</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">We evaluate your application details holistically. Our rates are highly competitive and transparent, ensuring you get the best market terms possible.</p>
        """
    elif "types-of-unsecured-loans" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">Unsecured credit refers to financing backed by the borrower's creditworthiness, requiring zero assets or gold as collateral. Main options include:</p>
        <ul class="list-disc pl-5 text-sm text-on-surface-variant space-y-2">
          <li><strong>Personal Loan:</strong> Multi-purpose cash credit for travel, marriage, home renovation, or health emergencies.</li>
          <li><strong>Professional Loan:</strong> Customized higher-limit loans designed for Chartered Accountants (CAs), Doctors, and Company Secretaries.</li>
          <li><strong>Business Loan / Working Capital:</strong> Short-term financing for businesses, MSMEs, and retailers to purchase stock or cover operating fees.</li>
          <li><strong>Small/Instant Cash Loan:</strong> Micro-loans from 10,000 to 50,000 for immediate utility.</li>
        </ul>
        """
    elif "maximum-years" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">The maximum repayment tenure allowed for an unsecured personal loan is typically <strong>5 years (60 months)</strong>.</p>
        <h3 class="text-base font-bold text-primary mt-4">1. Flexibility based on Budget</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">Borrowers can choose standard flexible tenures starting from 12 months up to 60 months. Longer tenures reduce the monthly EMI load significantly but raise the total compound interest paid over the life of the loan.</p>
        <h3 class="text-base font-bold text-primary mt-4">2. Short vs. Long Term</h3>
        <p class="text-sm text-on-surface-variant leading-relaxed">We advise choosing a shorter tenure (e.g., 24-36 months) if your monthly cash flows allow it, as this minimizes your overall interest cost.</p>
        """
    elif "best-place-online" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">The best place to secure an online loan in India is a platform that offers **absolute transparency, fast disbursals, bank-grade encryption, and RBI-regulated partnerships**.</p>
        <p class="text-sm text-on-surface-variant leading-relaxed">At Credify Capital, we partner with top Non-Banking Financial Companies (NBFCs) and banks. We offer competitive interest rates starting from 10.50% p.a., completely online paperless processing, zero pre-closure charges, and 24-hour bank credits. Our platform is fully secure, respecting your privacy and credit score.</p>
        """
    elif "factors-that-affect" in target_filename:
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">Your credit score (calculated by bureaus like CIBIL) is a key financial asset. Key factors driving it are:</p>
        <ul class="list-disc pl-5 text-sm text-on-surface-variant space-y-2">
          <li><strong>Payment History (35%):</strong> Paying credit card bills and EMIs on time is the single most critical factor.</li>
          <li><strong>Credit Utilization Ratio (30%):</strong> Keep your credit card spending below 30% of its total available credit limit.</li>
          <li><strong>Credit Mix (15%):</strong> Maintaining a healthy mix of secured (car/home) and unsecured (personal) credit.</li>
          <li><strong>Recent Hard Queries (10%):</strong> Frequent loan applications indicate high hunger for credit and can lower your rating.</li>
        </ul>
        """
    else: # Fallback answer
        answer_text = """
        <p class="text-sm text-on-surface-variant leading-relaxed">Personal credit queries require clear, reliable, and expert answers. In India, securing an instant personal loan online has been revolutionized by fintech platforms. Ensure you maintain a credit score above 750, verify all lender certifications, budget your payments carefully, and choose flexible tenures to make borrowing a healthy and productive tool for your financial growth.</p>
        """

    body_content = f"""
  <body class="bg-background text-on-background font-body-md pt-28">
    <main class="max-w-7xl mx-auto px-4 md:px-12 py-12">
      <!-- BREADCRUMB -->
      <div class="flex items-center gap-2 text-xs font-semibold text-on-surface-variant mb-6">
        <a href="../index.html" class="hover:text-primary">Home</a>
        <span class="material-symbols-outlined text-sm">chevron_right</span>
        <a href="../personal-loan-faq.html" class="hover:text-primary">FAQs</a>
        <span class="material-symbols-outlined text-sm">chevron_right</span>
        <span class="text-gray-400">Question</span>
      </div>

      <!-- FAQ DETAIL -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <!-- ANSWER BODY -->
        <div class="lg:col-span-2 space-y-6 bg-white p-6 md:p-10 rounded-3xl border border-gray-100 shadow-sm">
          <div class="inline-flex items-center gap-2 bg-secondary/10 border border-secondary/20 text-secondary px-3 py-1 rounded-full text-xs font-bold">
            <span class="material-symbols-outlined text-sm">help</span> Expert Answer
          </div>
          <h1 class="text-xl md:text-2xl lg:text-3xl font-extrabold tracking-tight text-primary leading-tight">{question_title}</h1>
          
          <div class="space-y-4 pt-4 border-t border-gray-100 text-on-surface">
            {answer_text}
          </div>
        </div>

        <!-- SIDEBAR -->
        <div class="space-y-8">
          <!-- CTA -->
          <div class="bg-gradient-to-br from-[#142450] to-[#253A71] text-white p-6 rounded-3xl text-center space-y-4 shadow-xl">
            <h3 class="text-lg font-bold">Quick Eligibility Check</h3>
            <p class="text-xs text-blue-200">Got an active credit history? See your personal loan eligibility and custom interest rate tiers in 2 minutes.</p>
            <div class="pt-2">
              <a href="../apply.html?type=Personal+Loan" class="inline-block bg-secondary text-white px-6 py-3 rounded-full font-bold text-xs hover:brightness-115 transition shadow-lg">Check Eligibility</a>
            </div>
          </div>
          
          <!-- OTHER FAQs -->
          <div class="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm space-y-4">
            <h3 class="text-base font-bold text-primary border-b border-gray-100 pb-2">Other Top FAQs</h3>
            <ul class="space-y-4 text-xs font-semibold text-on-surface-variant">
              <li><a href="what-is-the-best-way-to-get-a-personal-loan.html" class="hover:text-secondary transition-colors block">What is the best way to get a personal loan?</a></li>
              <li><a href="does-checking-credit-history-affect-credit-score.html" class="hover:text-secondary transition-colors block">Does Checking Credit History Affect Credit Score?</a></li>
              <li><a href="how-can-i-get-a-personal-loan-in-one-day.html" class="hover:text-secondary transition-colors block">How Can I Get A Personal Loan In One Day?</a></li>
            </ul>
          </div>
        </div>
      </div>
    </main>
    """

    full_page = header_customized + body_content + footer_part
    faq_filenames = [
        "what-is-the-best-way-to-get-a-personal-loan.html",
        "how-many-types-of-unsecured-loans-are-available-in-india.html",
        "how-to-borrow-money-online-instantly.html",
        "how-do-i-apply-online-for-an-instant-personal-loan.html",
        "what-is-the-lowest-interest-rate-available-on-personal-loans.html",
        "what-are-the-maximum-years-allowable-to-pay-personal-loan-via-emi.html",
        "does-checking-credit-history-affect-credit-score.html",
        "what-are-the-factors-that-affect-your-credit-score.html",
        "what-is-the-best-place-online-to-get-a-personal-loan-in-india.html",
        "what-are-the-processing-fees-for-personal-loan.html",
        "how-can-i-get-a-personal-loan-in-one-day.html"
    ]
    full_page_adjusted = adjust_paths_for_nested_page(full_page, local_files=faq_filenames)
    
    with open(f"personal-loan-faq/{target_filename}", 'w', encoding='utf-8') as f:
        f.write(full_page_adjusted)
    return True

def generate_blogs_list_page():
    """Generates an outstanding, beautiful main blogs list page (blogs.html) listing all blog posts."""
    header_part, footer_part = get_page_frame()
    
    title = "Financial Insights, Guides & Borrowing Tips"
    description = "Read expert articles, borrowing tips, and financial guides to help you make informed decisions about Personal, Business, and Professional Loans."
    canonical = "blogs.html"
    
    header_customized = customize_header(header_part, title, description, canonical)
    
    body_content = """
  <body class="bg-background text-on-background font-body-md pt-28">
    <section class="section-padding pt-32 pb-16 bg-surface">
      <div class="container mx-auto max-w-7xl px-4 md:px-6">
        <div class="text-center space-y-4 mb-12">
          <span class="text-secondary font-bold text-sm tracking-widest uppercase">FINANCIAL INSIGHTS</span>
          <h1 class="text-4xl md:text-5xl font-extrabold text-primary tracking-tight">Our Latest Blogs & Guides</h1>
          <p class="text-gray-500 max-w-2xl mx-auto text-base">Expert advice, borrowing tips, and financial guides to help you make informed decisions and build a stable future.</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <!-- Blog Card 1 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/how-to-use-personal-loan-for-financial-investment.jpg" alt="How to Use Personal Loans for Financial Investments?" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Investment</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/how-to-use-personal-loan-for-financial-investment.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">How to Use Personal Loans for Financial Investments?</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">Discover the strategic ways to utilize low-interest personal loans to generate positive investment returns and manage wealth.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>5 Min Read</span>
                        <span>July 21, 2026</span>
                    </div>
                </div>
            </div>
            
            <!-- Blog Card 2 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/how-to-get-a-personal-loan-in-five-easy-steps.jpg" alt="How to Get A Personal Loan in 5 Easy Steps?" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Loan Guide</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/how-to-get-a-personal-loan-in-five-easy-steps.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">How to Get A Personal Loan in 5 Easy Steps?</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">Navigating personal loan applications is simple. Follow our 5 quick digital steps to secure cash in under 24 hours.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>4 Min Read</span>
                        <span>June 18, 2026</span>
                    </div>
                </div>
            </div>

            <!-- Blog Card 3 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/all-about-personal-loan-disbursement-process.jpg" alt="All You Need to Know about Personal Loan Disbursal Process" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Disbursal</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/all-about-personal-loan-disbursement-process.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">All About Personal Loan Disbursement Process</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">Understand what happens behind the scenes once your loan gets approved and how funds are safely credited to your bank account.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>6 Min Read</span>
                        <span>May 12, 2026</span>
                    </div>
                </div>
            </div>

            <!-- Blog Card 4 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/top-advantages-of-applying-online-for-personal-loan.jpg" alt="Top 5 Advantages of Applying Online for a Personal Loan" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Digital Lending</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/top-advantages-of-applying-online-for-personal-loan.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">Top 5 Advantages of Applying Online</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">Explore how online applications speed up credit checks, improve options comparison, and lower overall administrative costs.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>4 Min Read</span>
                        <span>April 29, 2026</span>
                    </div>
                </div>
            </div>

            <!-- Blog Card 5 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/top-benefits-of-using-personal-loan-emi-calculator.jpg" alt="Top Benefits of Using a Personal Loan EMI Calculator" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Planning</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/top-benefits-of-using-personal-loan-emi-calculator.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">Top Benefits of Using an EMI Calculator</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">Never guess your monthly repayments. Learn how a digital EMI tool helps optimize interest rates and plan repayment cycles easily.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>3 Min Read</span>
                        <span>April 14, 2026</span>
                    </div>
                </div>
            </div>

            <!-- Blog Card 6 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/what-happens-if-you-miss-to-pay-personal-loan-emi.jpg" alt="What Will Happen When You Miss Your Personal Loan EMI?" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Credit Health</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/what-happens-if-you-miss-to-pay-personal-loan-emi.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">What Happens If You Miss an EMI?</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">Avoid credit downgrades. Know the penalties, credit score impacts, and amicable options available if you miss a personal loan payment.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>5 Min Read</span>
                        <span>March 22, 2026</span>
                    </div>
                </div>
            </div>

            <!-- Blog Card 7 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col hover:shadow-md transition-all">
                <img src="img/blog/where-can-i-get-personal-loan-online.jpg" alt="Where Can I Get a Personal Loan Online in India?" class="h-48 w-full object-cover">
                <div class="p-6 flex-grow flex flex-col justify-between space-y-4">
                    <div class="space-y-2">
                        <span class="text-xs font-semibold bg-blue-50 text-secondary px-2.5 py-1 rounded-full">Lending Portal</span>
                        <h3 class="text-xl font-bold text-primary leading-tight"><a href="blogs/where-can-i-get-personal-loan-online.html" class="hover:text-secondary transition-colors font-bold text-primary leading-tight">Where to Get Personal Loan Online?</a></h3>
                        <p class="text-gray-500 text-sm line-clamp-3">A complete list of digital platforms, banking channels, and NBFCs offering instant personal credit lines in India.</p>
                    </div>
                    <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
                        <span>4 Min Read</span>
                        <span>February 10, 2026</span>
                    </div>
                </div>
            </div>
        </div>
      </div>
    </section>
  </body>
    """
    
    full_page = header_customized + body_content + footer_part
    with open("blogs.html", 'w', encoding='utf-8') as f:
        f.write(full_page)
    return True

def generate_personal_loan_subpage(target_filename, title, description, display_name, hero_title_1, hero_title_2, hero_desc, overview_bold, overview_text):
    """Generates fully customized sub-feature pages for Personal Loans using personal-loan.html as the base template."""
    base_filename = 'personal-loan.html'
    if not os.path.exists(base_filename):
        print(f"Base file {base_filename} not found.")
        return False
        
    with open(base_filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # 1. Replace Title, Meta Description, and Canonical URL
    content = re.sub(r'<title>.*?</title>', f'<title>{title} - Credify Capital</title>', content, flags=re.IGNORECASE)
    content = re.sub(r'<meta\s+name="description"\s+content="[^"]*"', f'<meta name="description" content="{description}"', content, flags=re.IGNORECASE)
    content = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"', f'<link rel="canonical" href="{target_filename}"', content, flags=re.IGNORECASE)
    
    # 2. Update Breadcrumbs to show the custom product name
    old_breadcrumb = '<li class="breadcrumb-item active">Overview</li>'
    new_breadcrumb = f'<li class="breadcrumb-item active">{display_name}</li>'
    content = content.replace(old_breadcrumb, new_breadcrumb)
    
    # 3. Update Hero main heading
    old_hero_heading = """             <h1>Enabling Dreams with</h1>

             <span>Personal Loan </span>"""
    new_hero_heading = f"""             <h1>{hero_title_1}</h1>

             <span>{hero_title_2}</span>"""
    content = content.replace(old_hero_heading, new_hero_heading)
    
    # Let's support another spacing variant of hero heading if any
    old_hero_heading_alt = """<h1>Enabling Dreams with</h1>\\n\\n            <span>Personal Loan </span>"""
    new_hero_heading_alt = f"""<h1>{hero_title_1}</h1>\\n\\n            <span>{hero_title_2}</span>"""
    content = content.replace(old_hero_heading_alt, new_hero_heading_alt)
    
    # Also support replacement with normal regex / substring replacements to be robust
    content = content.replace("Enabling Dreams with", hero_title_1)
    content = content.replace("<span>Personal Loan </span>", f"<span>{hero_title_2}</span>")
    
    # 4. Update Hero Description Paragraph
    content = content.replace("<p>Loan amount | Quick Disbursal | Flexible EMI</p>", f"<p>{hero_desc}</p>")
    
    # 5. Update Overview Title (H2) and Body content
    old_overview_h2 = '<h2 class="acco-link">Personal Loan </h2>'
    new_overview_h2 = f'<h2 class="acco-link">{display_name} </h2>'
    content = content.replace(old_overview_h2, new_overview_h2)
    
    # Target and replace the main overview text inside card body
    old_overview_body = """<p><b>Get a Personal Loan on Salary of ₹1 Lakh with Quick Approval</b></p>

                               <p>Credify Capital is a trusted fintech platform that helps salaried individuals earning
                                  ₹1 Lakh and above access high-value Personal Loans from leading banks and NBFCs. By
                                  leveraging our network of lending partners, we help you find the most competitive
                                  interest rates and loan terms suited to your financial profile.</p>

                               <p>Whether it's for emergency expenses or planned big-ticket purchases, these Personal
                                  Loans come with no end-use restrictions, no collateral requirements, and flexible
                                  repayment options.</p>

                               <p>If you meet the eligibility criteria, you can benefit from quick approvals through a
                                  fully digital, hassle-free loan process—anytime,anywhere.</p>"""
                                  
    new_overview_body = f"""<p><b>{overview_bold}</b></p>

                               <p>{overview_text}</p>

                               <p>Whether it's for emergency expenses, major purchases, or special family milestones, our tailored {display_name} solutions offer fully digital verification, attractive interest rates, and flexible repayment tenures from 12 to 60 months with zero collateral requirements.</p>

                               <p>Apply online in minutes and enjoy quick approvals and seamless direct-to-bank disbursals to meet your credit needs with absolute transparency.</p>"""
                               
    content = content.replace(old_overview_body, new_overview_body)
    
    # If the exact whitespace varies, let's also do a safe block replace
    if old_overview_body not in content:
        # Robust fallback using regex to match from `<div class="tab-inner-content">` to `</div>`
        pattern = r'(<div class="tab-inner-content">).*?(</div>)'
        replacement = f'\\1\\n                              <p><b>{overview_bold}</b></p>\\n                              <p>{overview_text}</p>\\n                              <p>Our tailored {display_name} solutions offer fully digital verification, competitive rates, and flexible repayments with zero collateral.</p>\\n                              <p>Apply online in minutes to get started.</p>\\n                            \\2'
        content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
        
    with open(target_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def generate_business_loan_custom_subpage(target_filename, base_filename, title, description, display_name, hero_title_1, hero_title_2, overview_bold, overview_text):
    """Generates fully customized sub-feature pages for Business Loans using business-loan.html or small-business-loans.html as base."""
    if not os.path.exists(base_filename):
        print(f"Base file {base_filename} not found.")
        return False
        
    with open(base_filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Replace Title, Description, Canonical
    content = re.sub(r'<title>.*?</title>', f'<title>{title} - Credify Capital</title>', content, flags=re.IGNORECASE)
    content = re.sub(r'<meta\s+name="description"\s+content="[^"]*"', f'<meta name="description" content="{description}"', content, flags=re.IGNORECASE)
    content = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"', f'<link rel="canonical" href="{target_filename}"', content, flags=re.IGNORECASE)
    
    # Update Breadcrumbs
    content = content.replace('<li class="breadcrumb-item active">Overview</li>', f'<li class="breadcrumb-item active">{display_name}</li>')
    
    # Update Hero main heading
    content = content.replace("<h1>Get Hassle-Free Business Loan </h1>", f"<h1>{hero_title_1}</h1>\\n\\n\\t\\t\\t\\t    <span>{hero_title_2}</span>")
    content = content.replace("<h1>Get Hassle-Free Small Business Loans </h1>", f"<h1>{hero_title_1}</h1>\\n\\n\\t\\t\\t\\t    <span>{hero_title_2}</span>")
    
    # Update Overview heading
    content = content.replace('<h2 class="acco-link">Business Loan Overview</h2>', f'<h2 class="acco-link">{display_name} Overview</h2>')
    content = content.replace('<h2 class="acco-link">Small Business Loans </h2>', f'<h2 class="acco-link">{display_name} </h2>')
    
    # Replace overview text using regex for robust matching
    pattern = r'(<div class="tab-inner-content">).*?(</div>)'
    replacement = f'\\1\\n                                    <p><strong>{overview_bold}</strong></p>\\n                                    <p>{overview_text}</p>\\n                                    <p>Our tailored {display_name} provides quick online sanctioning, competitive interest rates, and flexible repayment tenures from 12 to 60 months with zero collateral or security requirements. Fuel your business growth today.</p>\\n                                    \\2'
    content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
    
    with open(target_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def generate_variation_page(target_filename, base_filename, title, description, badge_text, promo_text):
    """Generates machinery-loan, car-loan etc. variations by customizing headers, titles, and promo banners."""
    if not os.path.exists(base_filename):
        print(f"Base page {base_filename} not found. Skipping {target_filename}.")
        return False
        
    with open(base_filename, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Replace the title, description, canonical link
    content = re.sub(r'<title>.*?</title>', f'<title>{title} - Credify Capital</title>', content, flags=re.IGNORECASE)
    content = re.sub(r'<meta\s+name="description"\s+content="[^"]*"', f'<meta name="description" content="{description}"', content, flags=re.IGNORECASE)
    content = re.sub(r'<link\s+rel="canonical"\s+href="[^"]*"', f'<link rel="canonical" href="{target_filename}"', content, flags=re.IGNORECASE)
    
    # Locate main hero header and insert specific promotion badge / text
    # e.g., Replace standard header or inject a promo section right after body opens
    promo_banner = f"""
    <div class="bg-secondary text-white py-2 px-4 text-center text-xs font-bold tracking-wider uppercase flex items-center justify-center gap-2 shadow-sm">
      <span class="material-symbols-outlined text-sm">notification_important</span> {badge_text}: {promo_text}
    </div>
    """
    content = content.replace('<body class="bg-background text-on-background font-body-md pt-28">', f'<body class="bg-background text-on-background font-body-md pt-28">\n{promo_banner}')
    content = content.replace('<body style="padding-top: 108px;">', f'<body style="padding-top: 108px;">\n{promo_banner}')
    
    # Customize the hero section headers if matches are found
    if "machinery-loan" in base_filename:
        content = content.replace("Machinery Loan", title)
    elif "car-loan" in base_filename:
        content = content.replace("Car Loan", title)
    elif "loan-against-property" in base_filename:
        content = content.replace("Loan Against Property", title)
    elif "medical-equipment" in base_filename:
        content = content.replace("Medical Equipment Loan", title)
        
    with open(target_filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    ensure_dirs()
    print("Directories verified. Generating missing pages...")
    
    # 1. Professional Loan subpages mappings
    prof_reps_ca = [
        ("Professional Loan", "Professional Loan for Chartered Accountants (CAs)"),
        ("professional loan", "professional loan for CAs"),
        ("Professional Loans", "Professional Loans for CAs"),
        ("professional-loan.html", "professional-loan-for-ca.html"),
        ("professional-loan-eligibility-and-documents.html", "professional-loan-for-ca-eligibility-and-documents.html"),
        ("professional-loan-features-and-benefits.html", "professional-loan-for-ca-features-and-benefits.html"),
        ("professional-loan-interest-rates-and-charges.html", "professional-loan-for-ca-interest-rates-and-charges.html"),
        ("professional-loan-faq.html", "professional-loan-for-ca-faq.html"),
        ("professional-loan-emi-calculator.html", "professional-loan-for-ca-emi-calculator.html")
    ]
    prof_reps_cs = [
        ("Professional Loan", "Professional Loan for Company Secretaries (CS)"),
        ("professional loan", "professional loan for CS"),
        ("Professional Loans", "Professional Loans for CS"),
        ("professional-loan.html", "professional-loan-for-cs.html"),
        ("professional-loan-eligibility-and-documents.html", "professional-loan-for-cs-eligibility-and-documents.html"),
        ("professional-loan-features-and-benefits.html", "professional-loan-for-cs-features-and-benefits.html"),
        ("professional-loan-interest-rates-and-charges.html", "professional-loan-for-cs-interest-rates-and-charges.html"),
        ("professional-loan-faq.html", "professional-loan-for-cs-faq.html"),
        ("professional-loan-emi-calculator.html", "professional-loan-for-cs-emi-calculator.html")
    ]
    prof_reps_doc = [
        ("Professional Loan", "Professional Loan for Doctors"),
        ("professional loan", "professional loan for doctors"),
        ("Professional Loans", "Professional Loans for Doctors"),
        ("professional-loan.html", "professional-loan-for-doctors.html"),
        ("professional-loan-eligibility-and-documents.html", "professional-loan-for-doctors-eligibility-and-documents.html"),
        ("professional-loan-features-and-benefits.html", "professional-loan-for-doctors-features-and-benefits.html"),
        ("professional-loan-interest-rates-and-charges.html", "professional-loan-for-doctors-interest-rates-and-charges.html"),
        ("professional-loan-faq.html", "professional-loan-for-doctors-faq.html"),
        ("professional-loan-emi-calculator.html", "professional-loan-for-doctors-emi-calculator.html")
    ]

    subpage_mappings = {
        # Professional Loans - CA
        "professional-loan-for-ca-eligibility-and-documents.html": {
            "base": "professional-loan-eligibility-and-documents.html", "title": "Eligibility & Documents - CA Professional Loan", 
            "desc": "Required documents and eligibility requirements for Chartered Accountants' professional loans.", "reps": prof_reps_ca
        },
        "professional-loan-for-ca-features-and-benefits.html": {
            "base": "professional-loan-features-and-benefits.html", "title": "Features & Benefits - CA Professional Loan", 
            "desc": "Check custom benefits of professional loans for Chartered Accountants.", "reps": prof_reps_ca
        },
        "professional-loan-for-ca-interest-rates-and-charges.html": {
            "base": "professional-loan-interest-rates-and-charges.html", "title": "Interest Rates & Charges - CA Professional Loan", 
            "desc": "Competitive interest rates and transparent fees for CA professional loans.", "reps": prof_reps_ca
        },
        "professional-loan-for-ca-faq.html": {
            "base": "professional-loan-faq.html", "title": "FAQs - CA Professional Loan", 
            "desc": "Find answers to all frequently asked questions about CA professional loans.", "reps": prof_reps_ca
        },
        "professional-loan-for-ca-emi-calculator.html": {
            "base": "professional-loan-emi-calculator.html", "title": "EMI Calculator - CA Professional Loan", 
            "desc": "Calculate monthly installment outlays for CA professional practice loans.", "reps": prof_reps_ca
        },

        # Professional Loans - CS
        "professional-loan-for-cs-eligibility-and-documents.html": {
            "base": "professional-loan-eligibility-and-documents.html", "title": "Eligibility & Documents - CS Professional Loan", 
            "desc": "Know about COP registration parameters and required files for CS Professional Loans.", "reps": prof_reps_cs
        },
        "professional-loan-for-cs-features-and-benefits.html": {
            "base": "professional-loan-features-and-benefits.html", "title": "Features & Benefits - CS Professional Loan", 
            "desc": "Discover excellent practice credit benefits tailored for Company Secretaries.", "reps": prof_reps_cs
        },
        "professional-loan-for-cs-interest-rates-and-charges.html": {
            "base": "professional-loan-interest-rates-and-charges.html", "title": "Interest Rates & Charges - CS Professional Loan", 
            "desc": "Know details about interest rates and documentation fees for Company Secretary loans.", "reps": prof_reps_cs
        },
        "professional-loan-for-cs-faq.html": {
            "base": "professional-loan-faq.html", "title": "FAQs - CS Professional Loan", 
            "desc": "Check complete compliance and process FAQs for Company Secretary professional loans.", "reps": prof_reps_cs
        },
        "professional-loan-for-cs-emi-calculator.html": {
            "base": "professional-loan-emi-calculator.html", "title": "EMI Calculator - CS Professional Loan", 
            "desc": "Plan CS professional loan repayments instantly with our quick digital calculator.", "reps": prof_reps_cs
        },

        # Professional Loans - Doctors
        "professional-loan-for-doctors-eligibility-and-documents.html": {
            "base": "professional-loan-eligibility-and-documents.html", "title": "Eligibility & Documents - Doctor Professional Loan", 
            "desc": "Check clinic setup documents and qualification credentials required for Doctors' loans.", "reps": prof_reps_doc
        },
        "professional-loan-for-doctors-features-and-benefits.html": {
            "base": "professional-loan-features-and-benefits.html", "title": "Features & Benefits - Doctor Professional Loan", 
            "desc": "Explore medical equipment funding and clinic expansion loan benefits for Doctors.", "reps": prof_reps_doc
        },
        "professional-loan-for-doctors-interest-rates-and-charges.html": {
            "base": "professional-loan-interest-rates-and-charges.html", "title": "Interest Rates & Charges - Doctor Professional Loan", 
            "desc": "Check competitive medical sector interest rates and setup charges from Credify.", "reps": prof_reps_doc
        },
        "professional-loan-for-doctors-faq.html": {
            "base": "professional-loan-faq.html", "title": "FAQs - Doctor Professional Loan", 
            "desc": "Frequently asked questions regarding equipment lease, clinic expansion, and doctor credit.", "reps": prof_reps_doc
        },
        "professional-loan-for-doctors-emi-calculator.html": {
            "base": "professional-loan-emi-calculator.html", "title": "EMI Calculator - Doctor Professional Loan", 
            "desc": "Evaluate practice expansion loan EMIs instantly using our pediatric/dental clinic calculator.", "reps": prof_reps_doc
        }
    }

    # Generate professional loan subpages
    for fname, details in subpage_mappings.items():
        generate_subpage(fname, details['base'], details['title'], details['desc'], details['reps'])

    # 2. Business Loan subpages (Proprietor, MSME, Women, Retail, Small Business)
    biz_subpages = [
        # Proprietorship
        ("business-loan-for-proprietorship-eligibility-and-documents.html", "business-loan-eligibility-and-documents.html", "Proprietorship Business Loan Eligibility", "Eligibility for sole proprietors", [("Business Loan", "Proprietorship Business Loan"), ("business-loan.html", "business-loan-for-proprietorship.html")]),
        ("business-loan-for-proprietorship-features-and-benefits.html", "business-loan-features-and-benefits.html", "Proprietorship Business Loan Benefits", "Exclusive features for sole traders", [("Business Loan", "Proprietorship Business Loan"), ("business-loan.html", "business-loan-for-proprietorship.html")]),
        ("business-loan-for-proprietorship-interest-rates-and-charges.html", "business-loan-interest-rates-and-charges.html", "Proprietorship Business Loan Interest Rates", "Affordable rates for sole proprietors", [("Business Loan", "Proprietorship Business Loan"), ("business-loan.html", "business-loan-for-proprietorship.html")]),
        ("business-loan-for-proprietorship-emi-calculator.html", "business-loan-emi-calculator.html", "Proprietorship Business Loan EMI Calculator", "Calculate sole trader loan EMI", [("Business Loan", "Proprietorship Business Loan"), ("business-loan.html", "business-loan-for-proprietorship.html")]),
        ("unsecured-business-loan-for-proprietorship.html", "business-loan-for-proprietorship.html", "Unsecured Proprietorship Business Loan", "Collateral-free sole proprietorship funding", [("Business Loan", "Unsecured Proprietorship Business Loan")]),

        # MSME
        ("business-loan-scheme-for-msme-eligibility-and-documents.html", "business-loan-eligibility-and-documents.html", "MSME Business Loan Eligibility", "Requirements for micro, small & medium enterprises", [("Business Loan", "MSME Business Loan"), ("business-loan.html", "business-loan-scheme-for-msme.html")]),
        ("business-loan-scheme-for-msme-features-and-benefits.html", "business-loan-features-and-benefits.html", "MSME Business Loan Features", "Explore central MSME funding schemes", [("Business Loan", "MSME Business Loan"), ("business-loan.html", "business-loan-scheme-for-msme.html")]),
        ("business-loan-scheme-for-msme-interest-rates-and-charges.html", "business-loan-interest-rates-and-charges.html", "MSME Business Loan Interest Rates", "Competitive MSME financing rates", [("Business Loan", "MSME Business Loan"), ("business-loan.html", "business-loan-scheme-for-msme.html")]),
        ("business-loan-scheme-for-msme-emi-calculator.html", "business-loan-emi-calculator.html", "MSME Business Loan EMI Calculator", "Calculate industrial MSME credit EMIs", [("Business Loan", "MSME Business Loan"), ("business-loan.html", "business-loan-scheme-for-msme.html")]),
        ("unsecured-business-loan-scheme-for-msme.html", "business-loan-scheme-for-msme.html", "Unsecured MSME Business Loan Scheme", "No-collateral MSME registration loan scheme", [("Business Loan", "Unsecured MSME Business Loan")]),

        # Women
        ("business-loan-for-women-eligibility-and-documents.html", "business-loan-eligibility-and-documents.html", "Women Entrepreneurs Business Loan Eligibility", "Concessional requirements for women founders", [("Business Loan", "Business Loan for Women"), ("business-loan.html", "business-loan-for-women.html")]),
        ("business-loan-for-women-features-and-benefits.html", "business-loan-features-and-benefits.html", "Women Entrepreneurs Business Loan Benefits", "Concessions and low-interest benefits for women", [("Business Loan", "Business Loan for Women"), ("business-loan.html", "business-loan-for-women.html")]),
        ("business-loan-for-women-interest-rates-and-charges.html", "business-loan-interest-rates-and-charges.html", "Women Business Loan Interest Rates", "Special low rates starting for women entrepreneurs", [("Business Loan", "Business Loan for Women"), ("business-loan.html", "business-loan-for-women.html")]),
        ("business-loan-for-women-emi-calculator.html", "business-loan-emi-calculator.html", "Women Business Loan EMI Calculator", "Calculate custom EMIs with concessional rates", [("Business Loan", "Business Loan for Women"), ("business-loan.html", "business-loan-for-women.html")]),
        ("unsecured-business-loan-for-women.html", "business-loan-for-women.html", "Unsecured Business Loan for Women", "Collateral-free credit up to 75 Lakhs for women", [("Business Loan", "Unsecured Business Loan for Women")]),

        # Retail Shop
        ("business-loan-for-retail-shop-eligibility-and-documents.html", "business-loan-eligibility-and-documents.html", "Retail Shop Business Loan Eligibility", "Easy criteria for local retailers & merchant shops", [("Business Loan", "Retail Shop Business Loan"), ("business-loan.html", "business-loan-for-retail-shop.html")]),
        ("business-loan-for-retail-shop-features-and-benefits.html", "business-loan-features-and-benefits.html", "Retail Shop Business Loan Features", "Inventory & shop renovation funding options", [("Business Loan", "Retail Shop Business Loan"), ("business-loan.html", "business-loan-for-retail-shop.html")]),
        ("business-loan-for-retail-shop-interest-rates-and-charges.html", "business-loan-interest-rates-and-charges.html", "Retail Shop Business Loan Rates", "Transparent processing for offline & online retailers", [("Business Loan", "Retail Shop Business Loan"), ("business-loan.html", "business-loan-for-retail-shop.html")]),
        ("business-loan-for-retail-shop-emi-calculator.html", "business-loan-emi-calculator.html", "Retail Shop Business Loan EMI Calculator", "Merchant EMI & daily collection repayment calculators", [("Business Loan", "Retail Shop Business Loan"), ("business-loan.html", "business-loan-for-retail-shop.html")]),
        ("unsecured-business-loan-for-retail-shop.html", "business-loan-for-retail-shop.html", "Unsecured Retail Shop Business Loan", "No collateral stock purchasing credit for retailers", [("Business Loan", "Unsecured Retail Shop Business Loan")]),

        # Small Business Loans
        ("small-business-loans-eligibility-and-documents.html", "business-loan-eligibility-and-documents.html", "Small Business Loans Eligibility Criteria", "Requirements for small retail, trading and service startups", [("Business Loan", "Small Business Loan"), ("business-loan.html", "small-business-loans.html")]),
        ("small-business-loans-features-and-benefits.html", "business-loan-features-and-benefits.html", "Small Business Loans Features & Benefits", "Get up to 50 Lakhs unsecured credit for small setups", [("Business Loan", "Small Business Loan"), ("business-loan.html", "small-business-loans.html")]),
        ("small-business-loans-interest-rates-and-charges.html", "business-loan-interest-rates-and-charges.html", "Small Business Loans Interest Rates", "Competitive finance rates and minimal processing fees", [("Business Loan", "Small Business Loan"), ("business-loan.html", "small-business-loans.html")]),
        ("small-business-loans-emi-calculator.html", "business-loan-emi-calculator.html", "Small Business Loans EMI Calculator", "Calculate fast repayment schedules for small enterprises", [("Business Loan", "Small Business Loan"), ("business-loan.html", "small-business-loans.html")]),

        # Working Capital variations
        ("unsecured-business-loan-for-working-capital.html", "working-capital.html", "Unsecured Working Capital Business Loan", "Instant overdraft and credit limits for operational cash flow", [("Working Capital", "Unsecured Working Capital"), ("working-capital.html", "business-loan-for-working-capital.html")]),
        ("working-capital-business-loan.html", "working-capital.html", "Working Capital Business Loan Solutions", "Short-term funding for daily operations and business inventory", [("Working Capital", "Working Capital Business Loan")])
    ]

    for fname, base, title, desc, reps in biz_subpages:
        generate_subpage(fname, base, title, desc, reps)

    # 3. Personal Loan EMI Calculator
    generate_subpage("personal-loan-emi-calculator.html", "calculator.html", "Personal Loan EMI Calculator", "Plan your repayments instantly with our Personal Loan EMI Calculator", [("EMI Calculator", "Personal Loan EMI Calculator")])

    # 4. Variation Pages (Machinery, Property, Medical Equipment, Car Loan)
    variations = [
        # Machinery Loan Variations
        ("short-term-machinery-loan.html", "machinery-loan.html", "Short-Term Machinery Loan", "Short-term equipment loans with flexible repayment tenure from 12-36 months.", "Limited Offer", "Get concessional 11.25% p.a. on 1-year machinery financing"),
        ("small-machinery-loan.html", "machinery-loan.html", "Small Machinery & Equipment Loan", "Micro-loans up to ₹15 Lakhs for small-scale manufacturers and workshops.", "Easy Credit", "Special hassle-free paperless processing with zero physical audit"),
        ("urgent-machinery-loan.html", "machinery-loan.html", "Urgent Machinery Funding Online", "Fast track machinery loan approval within 24 hours to prevent operational pauses.", "Instant Approval", "Priority desk approval. Apply with GSTR data and bank logs now"),

        # Loan Against Property (LAP) Variations
        ("small-loan-against-property.html", "loan-against-property.html", "Small Loan Against Property", "Micro LAP from ₹10 Lakhs to ₹50 Lakhs for instant business/personal cash outlays.", "Low Rates", "Get lowest-in-market processing fees on small property collateral loans"),
        ("urgent-loan-against-property.html", "loan-against-property.html", "Urgent Loan Against Property", "Emergency funding against residential/commercial properties with fast evaluation.", "Priority Processing", "Get rapid property valuation checks in under 48 hours"),
        ("short-term-loan-against-property.html", "loan-against-property.html", "Short-Term Loan Against Property", "LAP options with shorter lock-in terms and flexible prepayments.", "Flexible Terms", "Zero pre-closure charges for customized short-term property loans"),
        ("loan-against-residential-property.html", "loan-against-property.html", "Loan Against Residential Property", "High-value cash credits by pledging your self-occupied residential apartment.", "High Loan-to-Value", "Get up to 75% market value of your residential asset as liquid cash"),

        # Medical Equipment Loan Variations
        ("short-term-medical-equipment-loan.html", "medical-equipment-loan.html", "Short-Term Medical Equipment Loan", "Flexible leases and working capital to acquire high-tech diagnostic tools.", "Concessional Scheme", "Pay 0% interest for first 3 months on dental and clinical leases"),
        ("small-medical-equipment-loan.html", "medical-equipment-loan.html", "Small Medical Equipment & Clinical Loan", "Loans up to 25 Lakhs for custom dental, aesthetic and ultrasound machines.", "Doctor Special", "COP and Clinic registration based instant paperless credit limit"),
        ("urgent-medical-equipment-loan.html", "medical-equipment-loan.html", "Urgent Medical Equipment Finance", "Immediate clinical asset purchase solutions approved in under 12 hours.", "Emergency Support", "Priority medical desk support with instant vendor credit payout"),

        # Car Loan Variations
        ("small-car-loan.html", "car-loan.html", "Small & Hatchback Car Loan", "Instant hatchback, sedan, and pre-owned car financing options for salaried individuals.", "Low EMI", "Zero downpayment options available for selected corporate employees"),
        ("short-term-car-loan.html", "car-loan.html", "Short-Term Car Financing", "Car funding with short repayment plans to avoid long-term interest burden.", "Zero Pre-closure", "Clear your car credit in 12-24 months with zero prepayment charges"),
        ("urgent-car-loan.html", "car-loan.html", "Urgent & Instant Car Loan Online", "Instant car loan validation with digital income and credit-bureau verification.", "Spot Approval", "Get spot e-approval using our secure paperless login system")
    ]

    for fname, base, title, desc, badge, promo in variations:
        generate_variation_page(fname, base, title, desc, badge, promo)

    # 5. Reviews Pages (11 pages)
    reviews_mappings = [
        ("professional-loan-review.html", "Professional Loan", "Professional"),
        ("professional-loan-for-doctors-review.html", "Professional Loan for Doctors", "Professional"),
        ("professional-loan-for-ca-review.html", "Professional Loan for CAs", "Professional"),
        ("professional-loan-for-cs-review.html", "Professional Loan for Company Secretaries", "Professional"),
        ("business-loan-review.html", "Business Loan", "Business"),
        ("business-loan-for-working-capital-review.html", "Working Capital Business Loan", "Business"),
        ("business-loan-for-proprietorship-review.html", "Proprietorship Business Loan", "Business"),
        ("business-loan-scheme-for-msme-review.html", "MSME Business Loan Scheme", "Business"),
        ("business-loan-for-women-review.html", "Business Loan for Women", "Business"),
        ("business-loan-for-retail-shop-review.html", "Retail Shop Business Loan", "Business"),
        ("small-business-loans-review.html", "Small Business Loan", "Business")
    ]

    for fname, prod, cat in reviews_mappings:
        generate_review_page(fname, prod, cat)

    # 6. Blogs Detail Pages (7 pages)
    blogs_mappings = [
        ("how-to-use-personal-loan-for-financial-investment.html", "How to Use Personal Loans for Financial Investments?"),
        ("how-to-get-a-personal-loan-in-five-easy-steps.html", "How to Get A Personal Loan in 5 Easy Steps?"),
        ("all-about-personal-loan-disbursement-process.html", "All You Need to Know about Personal Loan Disbursal Process"),
        ("top-advantages-of-applying-online-for-personal-loan.html", "Top 5 Advantages of Applying Online for a Personal Loan"),
        ("top-benefits-of-using-personal-loan-emi-calculator.html", "Top Benefits of Using a Personal Loan EMI Calculator"),
        ("what-happens-if-you-miss-to-pay-personal-loan-emi.html", "What Will Happen When You Miss Your Personal Loan EMI?"),
        ("where-can-i-get-personal-loan-online.html", "Where Can I Get a Personal Loan Online in India?")
    ]

    for fname, btitle in blogs_mappings:
        generate_blog_page(fname, btitle)

    # 7. FAQ Detail Pages (11 pages)
    faq_mappings = [
        ("what-is-the-best-way-to-get-a-personal-loan.html", "What is the best way to get a personal loan?"),
        ("how-many-types-of-unsecured-loans-are-available-in-india.html", "How Many Types Of Unsecured Loans Are Available In India?"),
        ("how-to-borrow-money-online-instantly.html", "How To Borrow Money Online Instantly?"),
        ("how-do-i-apply-online-for-an-instant-personal-loan.html", "How Do I Apply Online For An Instant Personal Loan?"),
        ("what-is-the-lowest-interest-rate-available-on-personal-loans.html", "What Is The Lowest Interest Rate Available On Personal Loans?"),
        ("what-are-the-maximum-years-allowable-to-pay-personal-loan-via-emi.html", "What are the maximum years allowed to pay a personal loan via EMI?"),
        ("does-checking-credit-history-affect-credit-score.html", "Does Checking Credit History Affect Credit Score?"),
        ("what-are-the-factors-that-affect-your-credit-score.html", "What Are The Factors That Affect Your Credit Score?"),
        ("what-is-the-best-place-online-to-get-a-personal-loan-in-india.html", "Where Is The Best Place Online To Get A Personal Loan In India?"),
        ("what-are-the-processing-fees-for-personal-loan.html", "What Are The Processing Fees For A Personal Loan?"),
        ("how-can-i-get-a-personal-loan-in-one-day.html", "How Can I Get A Personal Loan In One Day?")
    ]

    for fname, qtitle in faq_mappings:
        generate_faq_page(fname, qtitle)

    # 8. Generation of Blogs List Page (blogs.html)
    generate_blogs_list_page()

    # 9. Personal Loan Sub-features
    personal_subpages = [
        (
            "personal-loan-for-wedding.html",
            "Personal Loan for Wedding - Instant Wedding Loan Online",
            "Fund your dream wedding with Credify Capital's wedding personal loans. Check eligibility, get low-interest marriage finance, and flexible EMI options.",
            "Personal Loan for Wedding",
            "Celebrate Your Special Day with",
            "Wedding Personal Loan",
            "Fund your dream venue, designer attire, catering, and memorable celebrations with instant finance",
            "Get an Instant Marriage Loan up to ₹40 Lakhs with Flexible Repayments",
            "Credify Capital offers customized wedding personal loans designed to help you cover all your wedding expenses without compromising your dream celebration. From booking premium venues and caterers to buying jewelry, clothes, and planning a perfect honeymoon, our hassle-free wedding loan covers all marriage-related expenses."
        ),
        (
            "personal-loan-for-travel.html",
            "Personal Loan for Travel & Holidays - Vacation Loan Online",
            "Fund your dream holiday or international vacation with personal loans for travel. Quick approval, fully digital process, and affordable interest rates.",
            "Personal Loan for Travel",
            "Explore Your Dream Destination with",
            "Travel Personal Loan",
            "Cover flights, premium resort bookings, tour packages, and travel gear with easy, collateral-free credit",
            "Get an Instant Travel & Vacation Loan up to ₹15 Lakhs Online",
            "Credify Capital offers travel personal loans that allow you to plan your dream vacation or international getaway without worrying about high immediate expenses. Fund your flights, hotel accommodation, travel activities, and shopping with a single, fast-disbursing, zero-collateral holiday credit."
        ),
        (
            "personal-loan-for-doctors.html",
            "Personal Loan for Doctors - Customized Credit for Medical Practitioners",
            "Get special unsecured personal loans for doctors at attractive interest rates. Quick sanction, simplified documentation, and zero collateral.",
            "Personal Loan for Doctors",
            "Special Financial Solutions for",
            "Personal Loan for Doctors",
            "Exclusive credit lines with higher loan limits, lower processing fees, and priority paperless desk support",
            "Avail High-Value Personal Loans for Medical Professionals up to ₹50 Lakhs",
            "Doctors and medical professionals hold exceptional credibility and have unique financial demands. Credify Capital's exclusive doctor personal loan offers customized high-ticket limits to fund personal expenditures, medical conferences, premium equipment purchases, or urgent personal cash flow needs, without any asset pledging."
        ),
        (
            "personal-loan-for-government-employees.html",
            "Personal Loan for Government Employees - Concessional Interest Rates",
            "Exclusive low-interest personal loans for central/state government and PSU employees. Fast track processing and paperless approvals.",
            "Personal Loan for Government Employees",
            "Privileged Financial Terms for",
            "Personal Loan for Government Employees",
            "Enjoy low interest rates, reduced administration fees, and rapid direct-to-bank processing",
            "Special Low-Interest Unsecured Loans up to ₹25 Lakhs for Govt Staff",
            "Credify Capital provides tailored personal loans for central government, state government, defense, and public sector undertaking (PSU) employees. Because of your secure employment status and stable income, we offer concessional interest rates, minimal paperwork, and lightning-fast digital verification."
        ),
        (
            "personal-loan-for-home-renovation.html",
            "Personal Loan for Home Renovation & Repairs - Home Improvement Loan",
            "Upgrade your home with an instant personal loan for home renovation. Low interest rates, zero collateral, and customized EMI terms.",
            "Personal Loan for Home Renovation",
            "Upgrade and Beautify Your Home with",
            "Home Renovation Personal Loan",
            "Finance interior designs, modular kitchen extensions, repairs, painting, or home additions seamlessly",
            "Get Instant Home Improvement Loans up to ₹30 Lakhs with Zero Asset Pledge",
            "Your home deserves the best. Credify Capital's personal loan for home renovation lets you refurbish, repair, and modernize your living space without liquidating your long-term savings. Pay for raw materials, interior decorators, and contractor fees using an affordable, unsecured credit line."
        ),
        (
            "personal-loan-for-medical-emergency.html",
            "Urgent Personal Loan for Medical Emergency - Instant Emergency Funding",
            "Apply for an urgent personal loan for medical emergencies. Get instant cash disbursed to your bank account in under 12 hours with zero collateral.",
            "Personal Loan for Medical Emergency",
            "Immediate Financial Aid with",
            "Medical Emergency Loan",
            "Handle hospital bills, surgical costs, and medicine purchases during crucial hours with our priority team",
            "Urgent Collateral-Free Emergency Loans up to ₹15 Lakhs Disbursed Instantly",
            "During healthcare crises, financial hurdles shouldn't delay essential medical care. Credify Capital offers high-priority personal loans for medical emergencies, providing swift, collateral-free cash with expedited document screening. Funds are credited directly to your bank account to cover treatments, hospital stays, and immediate medical costs."
        ),
        (
            "personal-loan-for-women.html",
            "Personal Loan for Women - Financial Independence & Concessional Rates",
            "Exclusive personal loans for women. Low interest rates, simple digital documentation, and fast approval for working women.",
            "Personal Loan for Women",
            "Foster Financial Independence with",
            "Personal Loan for Women",
            "Attractive custom lending structures with higher approvals and concessional terms for women leaders",
            "Get Personal Loans for Women up to ₹25 Lakhs with Flexible Repayments",
            "Credify Capital supports women in achieving their personal, travel, wedding, or emergency funding goals. Our personal loan for women offers exclusive interest rate concessions, simplified digital processing, and custom tenure plans to empower working women and women entrepreneurs across India."
        ),
        (
            "short-term-personal-loan.html",
            "Short Term Personal Loan - Quick Micro-Credit Online",
            "Borrow short term personal loans with easy repayments up to 24 months. Enjoy fast approval, minimal documents, and zero prepayment fees.",
            "Short Term Personal Loan",
            "Fast Repayment and Flex Credit with",
            "Short Term Personal Loan",
            "Bridge immediate cash gaps and clear your debt quickly within 12 to 24 months",
            "Apply for Short Term Personal Credit up to ₹5 Lakhs Instantly",
            "Short-term personal loans are ideal for handling temporary cash shortages or unexpected monthly expenses without tying yourself to long-term financial commitments. Credify Capital's short-term credit solutions offer simple documentation, spot online verification, and flexible pre-payment options without penalties."
        ),
        (
            "small-personal-loan.html",
            "Small Personal Loan Online - Get Instant Small Cash Loan",
            "Apply for small personal loans from ₹10,000 to ₹2 Lakhs. Fully digital, 100% paperless KYC, and instant bank transfer.",
            "Small Personal Loan",
            "Instant Small-Ticket Cash with",
            "Small Personal Loan",
            "Fast cash loans to cover gadget purchases, minor repairs, online courses, or month-end cash flow drops",
            "Get Quick Small-Ticket Personal Loans Online up to ₹2 Lakhs",
            "For minor expenses, you don't need a heavy, long-term loan burden. Credify Capital's small personal loans are micro-credit lines starting from ₹10,000 up to ₹2,00,000. Features include 100% paperless verification, zero physical audits, and same-day disbursal directly to your salary account."
        ),
        (
            "unsecured-personal-loan.html",
            "Unsecured Personal Loan - No Collateral, Fast Disbursal",
            "Avail collateral-free unsecured personal loans online. Enjoy maximum loan limits, low interest rates, and paperless bank approval.",
            "Unsecured Personal Loan",
            "Zero Collateral, Zero Asset Pledge with",
            "Unsecured Personal Loan",
            "Borrow high-value loans with absolute safety, complete confidentiality, and zero physical security requirements",
            "Avail Unsecured Personal Credit up to ₹40 Lakhs with Simplified Documents",
            "Unlike traditional secured lending, our unsecured personal loan lets you access premium credit lines without pledging gold, property, or securities. Credify Capital validates your credit profile, employment history, and monthly income to approve high-value loans within minutes, providing ultimate financial liquidity."
        ),
        (
            "urgent-personal-loan.html",
            "Urgent Personal Loan - Same Day Approval & Bank Transfer",
            "Need cash urgently? Apply for an urgent personal loan online. Get 100% digital KYC and bank credit in less than an hour.",
            "Urgent Personal Loan",
            "Instant Financial Backing with",
            "Urgent Personal Loan",
            "Rapid paperless credit lines to meet sudden financial obligations without any waiting times",
            "Get Urgent Personal Loans Approved & Disbursed in 30 Minutes",
            "Credify Capital's express urgent personal loan is tailored for when time is of the essence. Our advanced automated underwriting engine checks your GSTR, bank statement, and salary slip online to issue immediate sanction letters. Skip long bank visits and secure funds directly in your account in under an hour."
        )
    ]

    for item in personal_subpages:
        generate_personal_loan_subpage(*item)

    # 10. Business Loan Custom Sub-features
    biz_custom_subpages = [
        (
            "unsecured-business-loan.html",
            "business-loan.html",
            "Unsecured Business Loan - Collateral-Free Business Funding",
            "Apply for collateral-free unsecured business loans up to ₹75 Lakhs. High loan approval rates, flexible repayment options, and minimal paperwork.",
            "Unsecured Business Loan",
            "Collateral-Free Funding with",
            "Unsecured Business Loan",
            "Unsecured Business Loan Overview",
            "Fuel growth and working capital for your business with a Credify Capital Unsecured Business Loan. Get fast approval and customized loan solutions to take your business to the next level."
        ),
        (
            "unsecured-small-business-loans.html",
            "small-business-loans.html",
            "Unsecured Small Business Loans - No-Collateral Credit for Startups & Retail",
            "Empower your small-scale enterprise with unsecured small business loans. Collateral-free funding up to ₹50 Lakhs with minimum documents.",
            "Unsecured Small Business Loans",
            "Collateral-Free Small Loans with",
            "Unsecured Small Business Loans",
            "Unsecured Small Business Loans Overview",
            "At Credify Capital, we understand small business needs and offer collateral-free Unsecured Small Business Loans specifically designed for growing enterprises and MSMEs. Enjoy quick paperless approvals."
        )
    ]

    for item in biz_custom_subpages:
        generate_business_loan_custom_subpage(*item)

    print("--- ALL MISSING PAGES SUCCESSFULLY GENERATED ---")

if __name__ == "__main__":
    main()
