import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from utils.tratamento import lowest_per_timestamp
from utils.subscription import COLLECTION as SUBS_COLLECTION
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Load environment variables ---
load_dotenv()
MONGO_USER = os.getenv("mongo_user")
MONGO_PASS = os.getenv("mongo_pass")

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
# EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("app_password")
EMAIL_FROM = os.getenv("email")

# --- MongoDB setup ---
URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@fraldas.1gjvb.mongodb.net/?retryWrites=true&w=majority&appName=fraldas"
CLIENT = MongoClient(URI, server_api=ServerApi('1'))
DATABASE = CLIENT['essentiel']
PRODUCTS_COLLECTION = DATABASE['pourbebe2']

def get_recommendation_label(current_value, df):
    p10 = df['min_value'].quantile(0.1)
    # Only "Excelent" if current_value <= p10
    if current_value <= p10:
        return "Excelente"
    return None

def get_last_two_prices(df):
    if len(df) < 2:
        return None, df['min_value'].iloc[-1] if len(df) > 0 else None
    return df['min_value'].iloc[-2], df['min_value'].iloc[-1]

def fetch_subscriptions():
    return list(SUBS_COLLECTION.find({}))

def fetch_product_history(sub):
    # Returns a DataFrame with timestamp and min_value for the product
    history = lowest_per_timestamp(
        categoria=sub.get("categoria"),
        marca=sub.get("marca"),
        qualidade=sub.get("submarca"),
        tamanho=sub.get("tamanho")
    )
    import pandas as pd
    return pd.DataFrame(history)

def build_email_content(products):
    # products: list of dicts with keys: categoria, marca, submarca, tamanho, price, prev_price, recommendation
    if not products:
        return None
    # Email header with branding and icon
    header = '''
    <div style="display:flex; align-items:center; padding:24px 0 12px 0;">
    <img src="https://img.freepik.com/premium-vector/mother-baby-icon_602006-6401.jpg" alt="Essenciais do Bebê" width="62" height="62" style="margin-right:12px;">
    <div>
        <h1 style="font-family:Arial,sans-serif; color:#228be6; margin:0;">Essenciais do Bebê</h1>
        <div style="font-size:16px; color:#555;">Monitoramento inteligente de preços</div>
    </div>
    </div>

    <hr style="border:none; border-top:1px solid #e9ecef; margin:16px 0;">
    '''

    intro = """
    <p style='font-size:16px;'>Olá! Veja as recomendações de <b>preço excelente</b> para os produtos que você acompanha:</p>
    """

    # Table for product recommendations
    table = [
        "<table style='width:100%; border-collapse:collapse; font-size:15px;'>",
        "<tr style='background:#f8fafc;'>",
        "<th style='padding:8px; border-bottom:1px solid #e9ecef;'>Produto</th>",
        "<th style='padding:8px; border-bottom:1px solid #e9ecef;'>Preço Atual</th>",
        "<th style='padding:8px; border-bottom:1px solid #e9ecef;'>Preço Anterior</th>",
        "<th style='padding:8px; border-bottom:1px solid #e9ecef;'>Recomendação</th>",
        "</tr>"
    ]
    for prod in products:
        table.append(f"<tr>"
            f"<td style='padding:8px; border-bottom:1px solid #e9ecef;'><b>{prod['categoria']} - {prod['marca']} - {prod['submarca']} - {prod['tamanho']}</b></td>"
            f"<td style='padding:8px; border-bottom:1px solid #e9ecef; color:#099268; font-weight:700; text-align:center;'>R$ {prod['price']:.2f}</td>"
            f"<td style='padding:8px; border-bottom:1px solid #e9ecef; text-align:center;'>R$ {prod['prev_price']:.2f}</td>"
            f"<td style='padding:8px; border-bottom:1px solid #e9ecef; text-align:center;'><span style='background:#e6fcf5; color:#099268; padding:2px 8px; border-radius:4px;'>Excelente</span></td>"
            f"</tr>")
    table.append("</table>")

    outro = """
    <p style='font-size:14px; color:#555; margin-top:24px;'>Você está recebendo este e-mail porque se inscreveu para recomendações de preço excelente.</p>
    <hr style='border:none; border-top:1px solid #e9ecef; margin:16px 0;'>
    <div style='text-align:center; font-size:13px; color:#888;'>Essenciais do Bebê &copy; 2025<br>Para cancelar sua inscrição, responda este e-mail.</div>
    """

    return header + intro + "\n".join(table) + outro

def send_email(to_email, subject, html_content):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.sendmail(EMAIL_FROM, to_email, msg.as_string())

def main():
    # 1. Fetch all subscriptions
    subscriptions = fetch_subscriptions()
    if not subscriptions:
        print("No subscriptions found.")
        return

    # 2. Group subscriptions by email
    from collections import defaultdict
    email_products = defaultdict(list)

    for sub in subscriptions:
        df = fetch_product_history(sub)
        df = df.set_index('timestamp').resample('D')['min_value'].min().ffill().reset_index()
        if df.empty or 'min_value' not in df or df['min_value'].isnull().all():
            continue

        prev_price, current_price = get_last_two_prices(df)
        if current_price is None or prev_price is None:
            continue

        recommendation = get_recommendation_label(current_price, df)
        # Only send if recommendation is "Excelente" and price changed
        if recommendation == "Excelente":# and current_price != prev_price:
            email_products[sub['email']].append({
                "categoria": sub.get("categoria"),
                "marca": sub.get("marca"),
                "submarca": sub.get("submarca"),
                "tamanho": sub.get("tamanho"),
                "price": current_price,
                "prev_price": prev_price,
                "recommendation": recommendation
            })

    # 3. Send one email per user with all relevant products
    for email, products in email_products.items():
        if not products:
            continue
        html_content = build_email_content(products)
        subject = "Essenciais do Bebê - Recomendações"
        try:
            send_email(email, subject, html_content)
            print(f"Sent recommendation to {email}")
        except Exception as e:
            print(f"Failed to send to {email}: {e}")

if __name__ == "__main__":
    main()
