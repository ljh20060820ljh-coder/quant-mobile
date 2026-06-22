import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import math
import datetime

print("="*50)
print("🤖 启动量化中枢 V5.0 (DeepSeek 驱动版)")
print("="*50)

# ==========================================
# ⚙️ 核心配置区 (请填入你自己的信息)
# ==========================================
DEEPSEEK_API_KEY = "sk-fd994623c92e4cbaa4d0c07271c35650" # 换成你的 DeepSeek 密钥
EMAIL_SENDER = "2183089849@qq.com"             # 发件邮箱
EMAIL_AUTH_CODE = "rczpdigubvhgdhgf"             # 邮箱 SMTP 授权码
EMAIL_RECEIVER = "2183089849@qq.com"           # 收件邮箱 (可以发给自己)
SMTP_SERVER = "smtp.qq.com"                    # QQ邮箱服务器 (163邮箱请改为 smtp.163.com)

# ==========================================
# 🧠 模块一：DeepSeek 首席风控师 (AI 情报分析)
# ==========================================
def ask_deepseek_risk(match_name, news_text):
    print(f"\n📡 正在呼叫 DeepSeek 分析 [{match_name}] 场外情报...")
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    prompt = f"""
    你是一个冷酷、顶级的足彩风控师。
    当前比赛：{match_name}。
    最新场外情报："{news_text}"
    请评估该情报对【主队】实战胜率的影响。
    规则：只允许输出一个介于 -15 到 +15 之间的纯数字（代表胜率波动的百分点，例如主队绝对主力受伤，你输出 -8；主队利好，你输出 5）。
    绝对不允许输出任何其他文字、符号或解释！
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1 # 温度设低，保证数字的稳定性
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        modifier = int(result['choices'][0]['message']['content'].strip())
        print(f"🤖 DeepSeek 判定修正值: {modifier:+} %")
        return modifier / 100.0
    except Exception as e:
        print(f"❌ DeepSeek 调用失败，启用 0 修正: {e}")
        return 0.0

# ==========================================
# 🧮 模块二：泊松矩阵核算引擎 (简版演示)
# ==========================================
def calculate_ev(lambda_a, lambda_b, ai_modifier, odds):
    # 计算基础胜率 (全场独赢)
    win_prob = 0
    def fact(n): return 1 if n <= 1 else n * fact(n-1)
    def poisson(k, l): return (math.pow(l, k) * math.exp(-l)) / fact(k)
    
    for i in range(8):
        for j in range(8):
            if i > j: win_prob += poisson(i, lambda_a) * poisson(j, lambda_b)
            
    # 注入 AI 修正值
    final_prob = win_prob + ai_modifier
    final_prob = max(0.01, min(final_prob, 0.99)) # 保证概率在合理区间
    
    ev = (final_prob * odds) - 1
    return final_prob, ev

# ==========================================
# 📧 模块三：军情处 (发送自动战报)
# ==========================================
def send_email_report(report_content):
    print("\n📨 正在将战报加密发送至手机邮箱...")
    message = MIMEText(report_content, 'plain', 'utf-8')
    message['From'] = Header("AI 交易中枢", 'utf-8')
    message['To'] = Header("操盘手", 'utf-8')
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    message['Subject'] = Header(f"📊 {today_str} 0:00 量化开盘指令", 'utf-8')
    
    try:
        smtpObj = smtplib.SMTP_SSL(SMTP_SERVER, 465)
        smtpObj.login(EMAIL_SENDER, EMAIL_AUTH_CODE)
        smtpObj.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], message.as_string())
        smtpObj.quit()
        print("✅ 战报发送成功！请检查手机。")
    except smtplib.SMTPException as e:
        print(f"❌ 邮件发送失败: {e}")

# ==========================================
# 🚀 主运行程序 (每日 0:00 自动执行的部分)
# ==========================================
if __name__ == "__main__":
    # 【模拟抓取当日赛事与赔率】(实战中这里会接入 API 或爬虫)
    match = "阿根廷 vs 奥地利"
    goal_a, goal_b = 2.00, 0.71
    app_odds = 1.65
    
    # 【模拟抓取外网情报】
    news = "阿根廷队已经提前出线，主教练斯卡洛尼在发布会上表示，为了准备淘汰赛，本场比赛梅西、迪马利亚将不会首发出战，后防线也将轮换3人。"
    
    # 1. 呼叫 AI 进行情报降维
    ai_mod = ask_deepseek_risk(match, news)
    
    # 2. 融合核算
    final_prob, ev = calculate_ev(goal_a, goal_b, ai_mod, app_odds)
    
    # 3. 生成报告
    report = f"""
    📅 量化中枢 V5.0 每日作战简报
    =================================
    【目标赛事】: {match}
    【盘口项目】: 全场独赢 - 主胜
    【机构赔率】: {app_odds}
    
    🧠 AI 情报分析:
    抓取情报: {news}
    DeepSeek 胜率修正: {ai_mod*100:+.1f}%
    
    📊 最终核算:
    泊松基准胜率: 66.5%
    修正后真实胜率: {final_prob*100:.1f}%
    期望值 (EV): {ev:+.4f}
    """
    
    if ev > 0:
        report += f"\n✅ 指令：发现正期望，建议建仓！"
    else:
        report += f"\n🚫 指令：负期望陷阱盘，坚决放弃！"
        
    print(report)
    
    # 4. 发送邮件
    send_email_report(report)
    print("\n任务结束，系统休眠。")
