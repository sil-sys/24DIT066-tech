"""
Dataset Generator for Practical 11: SMS Spam Collection Dataset
Generates an authentic, high-quality, balanced/imbalanced SMS spam dataset
modeled on the UCI Machine Learning Repository SMS Spam Collection.
"""

import csv
import random
import os

HAM_TEMPLATES = [
    "Hey {name}, are we still meeting for the project discussion at {time} today?",
    "Ok, I will reach college by {time}. Please save a seat for me.",
    "Did you complete the Big Data Analytics practical assignment for this week?",
    "Can you share the lecture slides from yesterday's distributed computing class?",
    "Thanks for the help earlier! Really appreciate your quick response.",
    "I am stuck in traffic near the circle, will be delayed by 15 minutes.",
    "Please find attached the updated project report and data pipeline code.",
    "Are you coming to the seminar on Cloud Computing and Spark in the auditorium?",
    "Happy Birthday {name}! Wishing you a wonderful and successful year ahead.",
    "Call me whenever you get free, need to discuss the weekend plans.",
    "The exam schedule has been released on the university student portal.",
    "Just reached home safely. Let me know when you reach your hostel.",
    "Where should we order lunch from today? Pizza or sandwiches?",
    "I checked the PySpark MLlib documentation, the parameter is elasticNetParam.",
    "Your OTP for net banking login is {otp}. Valid for 10 minutes. Do not share.",
    "Your order #{order_id} has been delivered successfully. Thank you for shopping with us.",
    "The library book 'Introduction to Algorithms' is due for return on Friday.",
    "Good morning! Remember to submit the lab record before 5 PM today.",
    "Don't worry about the presentation, we have prepared all the slides well.",
    "Let's catch up over coffee this evening at the student cafeteria.",
    "Can you please review the merge request I raised on the repository?",
    "The bus is arriving at platform 4 in five minutes.",
    "Yes, I already verified the cluster configuration on Spark master node.",
    "Mom asked if you will be coming home for dinner tonight.",
    "Please send me the PDF notes for Unit 4 data visualization.",
    "Hi {name}, hope you are doing well! It's been a while since we talked.",
    "The results for the midterm examination will be announced next Monday.",
    "Got your email with the dataset CSV. Loading it into Spark DataFrame now.",
    "I'll bring my laptop charger with me so we can work on the lab assignment.",
    "See you tomorrow at 9 AM sharp in the computer lab."
]

SPAM_TEMPLATES = [
    "CONGRATULATIONS! You have won a cash prize of ${amount} in the National Telecom Lottery! Call {phone} or visit {url} to claim now. T&C apply.",
    "URGENT! Your bank account ending in {acc} has been suspended due to suspicious activity. Verify immediately at {url} to avoid permanent freeze.",
    "WINNER! As a valued customer, you have been selected to receive a FREE iPhone 15 Pro. Reply CLAIM to {shortcode} or click {url} today only!",
    "Instant Personal Loan approved up to ${loan_amount} with 0% processing fee and minimal documentation! Apply within 2 hours at {url}.",
    "Exclusive Offer! Get 85% discount on top designer watches and luxury perfumes. Shop now at {url}. Limited stocks available!",
    "ALERT: Unclaimed lottery reward of ${amount} waiting for your mobile number. Call {phone} now to transfer funds to your bank account.",
    "You have won a free 4-night luxury holiday voucher to Bali! Reply YES to {shortcode} to receive your booking code immediately.",
    "Special promotional offer: 100 GB High Speed 5G Data for just $1.99! Recharge now at {url} before the offer expires at midnight.",
    "Dear Customer, your electricity connection will be disconnected tonight at 9:30 PM due to unpaid bill. Call helpline {phone} immediately.",
    "Get rich quick with guaranteed daily returns of 25% on crypto trading! Join our VIP Telegram channel at {url}. No prior experience needed.",
    "FREE entry into our weekly ${amount} sweepstakes! Text WIN to {shortcode} now to register your free lucky draw ticket.",
    "URGENT NOTICE: Your package delivery has been put on hold due to missing delivery address. Pay $1.50 redelivery fee at {url}.",
    "Congratulations! You qualify for debt forgiveness and credit score repair. Call our financial counselor now at {phone} to eliminate debt.",
    "Hot singles in your area want to meet you tonight! Click {url} to chat live and browse profiles for free.",
    "Double your mobile balance today! Send FREE to {shortcode} and get instant 200% bonus talktime and data packs."
]

NAMES = ["Rahul", "Priya", "Amit", "Sneha", "Karan", "Ananya", "Rohan", "Neha", "Vikram", "Pooja", "Arjun", "Tanvi"]
TIMES = ["10:30 AM", "2:00 PM", "4:15 PM", "11:00 AM", "3:30 PM", "5:00 PM"]
URLS = ["http://spam-claim.biz", "http://secure-verify.net", "http://promo-deal.info", "http://gift-portal.com", "http://fast-loan-app.co"]
PHONES = ["+1-800-555-0199", "+44-20-7946-0921", "+1-888-920-1144", "+1-800-419-7820"]
SHORTCODES = ["55444", "88202", "77331", "99100"]

def generate_message(template, is_spam):
    msg = template
    name = random.choice(NAMES)
    time_val = random.choice(TIMES)
    otp = str(random.randint(100000, 999999))
    order_id = str(random.randint(10000, 99999))
    amount = f"{random.choice([1000, 5000, 10000, 50000, 100000]):,}"
    loan_amount = f"{random.choice([25000, 50000, 75000]):,}"
    phone = random.choice(PHONES)
    url = random.choice(URLS)
    shortcode = random.choice(SHORTCODES)
    acc = str(random.randint(1000, 9999))
    
    msg = msg.replace("{name}", name)
    msg = msg.replace("{time}", time_val)
    msg = msg.replace("{otp}", otp)
    msg = msg.replace("{order_id}", order_id)
    msg = msg.replace("{amount}", amount)
    msg = msg.replace("{loan_amount}", loan_amount)
    msg = msg.replace("{phone}", phone)
    msg = msg.replace("{url}", url)
    msg = msg.replace("{shortcode}", shortcode)
    msg = msg.replace("{acc}", acc)
    return msg

def main():
    random.seed(42)
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, "sms_spam_collection.csv")
    
    total_records = 6000
    spam_ratio = 0.20  # Realistic telecom spam ratio (~20% spam, 80% ham)
    
    records = []
    num_spam = int(total_records * spam_ratio)
    num_ham = total_records - num_spam
    
    for _ in range(num_ham):
        tmpl = random.choice(HAM_TEMPLATES)
        text = generate_message(tmpl, is_spam=False)
        records.append(("ham", text))
        
    for _ in range(num_spam):
        tmpl = random.choice(SPAM_TEMPLATES)
        text = generate_message(tmpl, is_spam=True)
        records.append(("spam", text))
        
    random.shuffle(records)
    
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "message_text"])
        for label, text in records:
            writer.writerow([label, text])
            
    print(f"Generated {total_records} SMS records to {output_file}")
    print(f"Ham records: {num_ham}, Spam records: {num_spam}")

if __name__ == "__main__":
    main()
