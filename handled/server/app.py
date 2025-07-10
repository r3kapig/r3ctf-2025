from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

# Status constants
PENDING = 0      # 待评测
JUDGING = 1     # 评测中
CORRECT = 2     # 评测完成-正确
WRONG = 3       # 评测完成-错误

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS submissions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  team_id TEXT(64) NOT NULL,
                  code TEXT NOT NULL,
                  submit_time TEXT NOT NULL,
                  status INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

# Auth middleware for submit/list
def check_auth_submit():
    auth_header = request.headers.get('Auth')
    return auth_header == '9a8e4619-60f0-46e2-9867-a0a454e0923f'

# Auth middleware for get/result
def check_auth_judge():
    auth_header = request.headers.get('Auth')
    return auth_header == '61d7f983-cba6-45b4-b6ce-88954baf72ba'

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    if not data or 'team_id' not in data or 'code' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    if len(data['code']) > 16384:
        return jsonify({'error': 'Code too large'}), 400
    
    # 检查1分钟提交限制
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    
    # 获取当前时间
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    
    # 检查该团队在过去1分钟内是否有提交
    c.execute("SELECT COUNT(*) FROM submissions WHERE team_id = ? AND submit_time > ?", 
              (data['team_id'], one_minute_ago.isoformat()))
    recent_submissions = c.fetchone()[0]
    
    if recent_submissions > 0:
        conn.close()
        return jsonify({'error': 'Please wait 1 minute between submissions'}), 429
    
    # 插入新提交
    c.execute("INSERT INTO submissions (team_id, code, submit_time, status) VALUES (?, ?, ?, ?)",
              (data['team_id'], data['code'], now.isoformat(), PENDING))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Submission received'}), 200

@app.route('/list', methods=['GET'])
def list_submissions():
    team_id = request.args.get('team_id')
    if not team_id:
        return jsonify({'error': 'Missing team_id'}), 400
    
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    c.execute("SELECT id, team_id, submit_time, status FROM submissions WHERE team_id = ? ORDER BY id DESC LIMIT 10", (team_id,))
    submissions = [dict(zip(['id', 'team_id', 'submit_time', 'status'], row)) for row in c.fetchall()]
    conn.close()
    
    return jsonify(submissions), 200

@app.route('/get', methods=['POST'])
def get_submission():
    if not check_auth_judge():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    sub_id = data.get('id', 0) if data else 0
    
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    
    if sub_id == 0:
        # Get oldest pending submission if id is 0 or not provided
        c.execute("SELECT id, team_id, code FROM submissions WHERE status = ? ORDER BY id ASC LIMIT 1", (PENDING,))
        submission = c.fetchone()
        
        if submission:
            sub_id, team_id, code = submission
            c.execute("UPDATE submissions SET status = ? WHERE id = ?", (JUDGING, sub_id))
            conn.commit()
            conn.close()
            return jsonify({'id': sub_id, 'team_id': team_id, 'code': code}), 200
        else:
            conn.close()
            return jsonify({'message': 'No pending submissions'}), 404
    else:
        # Get specific submission by id
        c.execute("SELECT id, team_id, code FROM submissions WHERE id = ?", (sub_id,))
        submission = c.fetchone()
        
        if submission:
            sub_id, team_id, code = submission
            conn.close()
            return jsonify({'id': sub_id, 'team_id': team_id, 'code': code}), 200
        else:
            conn.close()
            return jsonify({'error': 'Submission not found'}), 404

@app.route('/set', methods=['POST'])
def update_result():
    if not check_auth_judge():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    if not data or 'id' not in data or 'status' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    valid_statuses = [CORRECT, WRONG]
    if int(data['status']) not in valid_statuses:
        return jsonify({'error': 'Invalid status'}), 400
    
    conn = sqlite3.connect('submissions.db')
    c = conn.cursor()
    c.execute("UPDATE submissions SET status = ? WHERE id = ?", (data['status'], data['id']))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Status updated'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=30028, debug=True)