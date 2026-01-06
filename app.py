from flask import Flask
from flask import request, redirect, url_for, abort
from flask import session, flash, get_flashed_messages
from flask import render_template
from datetime import date, datetime
import math
import bcrypt

from src.games import games

from db import get_db_connection

app = Flask(__name__)
app.register_blueprint(games, url_prefix="/games")

app.secret_key = '123'

@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        if 'id' in session:
            first_name = session['fname']
            last_name = session['lname']
            username = session['username']

            player_id = session['id'];

            conn = get_db_connection()
            cursor = conn.cursor()
            query = "SELECT personal_balance FROM players WHERE player_id = %s;"

            cursor.execute(query, (player_id,))
            result = cursor.fetchone()
            
            balance = result['personal_balance'] if result else 0

            conn.close()

            return render_template(
                'home.html',
                username=username,
                fname=first_name,
                lname=last_name,
                accbalance=balance
            )
        else:
            return redirect(url_for('login'))
    # else:
    #     if "logout" in request.form:
    #         return redirect(url_for('login'))

@app.route("/logout")
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for("login"))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()

        player_query = '''
            SELECT player_id, username, first_name, last_name, email, password
            FROM players WHERE username=%s;
        '''

        with conn.cursor() as cursor:       
            cursor.execute(player_query, (username,))
            player = cursor.fetchone()

        conn.close()

        password_bytes = password.encode('utf-8')
        stored_hash = player['password'].encode('utf-8') 
        passbool = bcrypt.checkpw(password_bytes, stored_hash)

        # if player and player['password'] == password:
        if player and passbool:
            session['id'] = player['player_id']
            session['username'] = player['username']
            session['fname'] = player['first_name']
            session['lname'] = player['last_name']
            session['email'] = player['email']
            return redirect(url_for('home'))
        else:
            flash('Username or password is incorrect!', 'warning')
            return redirect(url_for('login'))

    else:
        session.pop('id', None)
        session.pop('username', None)
        session.pop('fname', None)
        session.pop('lname', None)
        return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        uname = request.form['username']
        email = request.form['email']
        dob = request.form['dob']
        password = request.form['password']

        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)

        valid = True

        validation_query = '''
        SELECT
            EXISTS (
                SELECT 1 FROM players WHERE username = %s 
            ) AS username_taken,
            EXISTS (
                SELECT 1 FROM players WHERE email = %s
            ) AS email_taken;
        '''

        insertion_query = '''
            INSERT INTO players (
                first_name,
                last_name,
                username,
                email,
                date_of_birth,
                password
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        '''

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(validation_query, (uname, email))
            row = cursor.fetchone()
            username_taken = bool(row['username_taken'])
            email_taken = bool(row['email_taken'])
            if username_taken or email_taken:
                valid = False
            if username_taken:
                flash('Username is taken! Please try a different one.', 'warning')
            if email_taken:
                flash('Email is associated with an existing account! Please log in.', 'warning')
        if valid:
            with conn.cursor() as cursor:
                cursor.execute(
                    insertion_query,
                    (fname, lname, uname, email, dob, hashed)
                )
                conn.commit()
                conn.close()
                flash('Sign up successful! Please log in.', 'success')
                return redirect(url_for('login'))
        conn.close()
    today = date.today().isoformat()
    return render_template('signup.html', today=today)

@app.route("/friends", methods=['GET', 'POST'])
def friends():
    player_id = session['id']

    if not player_id:
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        submitting_data = request.method == 'POST'
        accepting_frq = submitting_data and 'friend_id' in request.form
        declining_frq = submitting_data and 'reject_id' in request.form
        unfriending_frn = submitting_data and 'unfriend_id' in request.form
        sending_frq = submitting_data and 'username' in request.form

        if accepting_frq:
            insertion_query = '''
                INSERT INTO friendships (befriender_id, befriended_id)
                VALUES (%s, %s);
            '''
            deletion_query = '''
                DELETE FROM friend_requests 
                WHERE sender_id = %s AND receiver_id = %s;
            '''
            sender = request.form["friend_id"]
            receiver = player_id
            with conn.cursor() as cursor:
                cursor.execute(insertion_query, (sender, receiver))
                cursor.execute(deletion_query, (sender, receiver))
                conn.commit()
        elif declining_frq:
            deletion_query = '''
                DELETE FROM friend_requests 
                WHERE sender_id = %s AND receiver_id = %s;
            '''
            sender = request.form["reject_id"]
            receiver = player_id
            with conn.cursor() as cursor:
                cursor.execute(deletion_query, (sender, receiver))
                conn.commit()
        elif unfriending_frn:
            deletion_query = '''
                DELETE FROM friendships 
                WHERE
                    (befriender_id = %s AND befriended_id = %s)
                    OR (befriender_id = %s AND befriended_id = %s);
            '''
            target = request.form["unfriend_id"]
            player = player_id
            with conn.cursor() as cursor:
                cursor.execute(deletion_query, (target, player, player, target))
                conn.commit()
        elif sending_frq:
            target_username = request.form['username']
            locating_query = '''
                SELECT player_id FROM players
                WHERE username = %s;
            '''
            with conn.cursor() as cursor:
                cursor.execute(locating_query, (target_username,))
                match = cursor.fetchone()
                user_exists = bool(match)

            if user_exists:
                target = match['player_id']
                player = player_id

                user_is_self = target == player
                if user_is_self:
                    flash('You cannot add yourself as a friend!', 'warning')
                else:
                    existing_frq_query = '''
                        SELECT sender_id as sender FROM friend_requests
                        WHERE
                            (sender_id = %s AND receiver_id =  %s) OR
                            (sender_id = %s AND receiver_id = %s);
                    '''
                    existing_frn_query = '''
                    SELECT befriender_id as sender FROM friendships
                    WHERE
                        (befriender_id = %s AND befriended_id =  %s) OR
                        (befriender_id = %s AND befriended_id = %s);
                '''
                    with conn.cursor() as cursor:
                        cursor.execute(
                            existing_frq_query,
                            (target, player, player, target)
                        )
                        frq_row = cursor.fetchone()
                        existing_frq = bool(frq_row)

                    with conn.cursor() as cursor:
                        cursor.execute(
                        existing_frn_query,
                        (target, player, player, target)
                    )
                    frn_row = cursor.fetchone()
                    existing_frn = bool(frn_row)
                    if existing_frq:
                        resending = frq_row['sender'] == player
                        accepting = frq_row['sender'] == target
                        if resending:
                            flash('You already sent this person a friend request', 'warning')
                        elif accepting:
                            deletion_query = '''
                                DELETE FROM friend_requests
                                WHERE sender_id = %s AND receiver_id = %s
                            '''
                            insertion_query = '''
                                INSERT INTO friendships (
                                    befriender_id,
                                    befriended_id
                                )
                                VALUES (%s, %s)
                            '''
                            with conn.cursor() as cursor:
                                cursor.execute(deletion_query, (target, player))
                                cursor.execute(insertion_query, (target, player))
                                conn.commit()
                            flash('Friend request accepted', 'success')
                    elif existing_frn:
                        flash('You have already befriended this person!', 'warning')
                    else:    
                        insertion_query = '''
                            INSERT INTO friend_requests (sender_id, receiver_id)
                            VALUES (%s, %s);
                        '''
                        with conn.cursor() as cursor:
                            cursor.execute(insertion_query, (player, target))
                            conn.commit()
                        flash('Friend request sent!', 'success')
            else:
                flash('Player not found!', 'warning')

        return redirect(url_for('friends'))

    with conn.cursor() as cursor:
        frn_query = '''
                SELECT
                    CONCAT(p.first_name, " ", p.last_name) AS name,
                    p.username,
                    p.player_id
                FROM (
                    SELECT befriended_id AS friend_id
                    FROM friendships
                    WHERE befriender_id = %s
            
                    UNION

                    SELECT befriender_id AS friend_id
                    FROM friendships
                    WHERE befriended_id = %s
                ) AS t
                INNER JOIN players p 
                ON p.player_id = t.friend_id
                ORDER BY p.personal_balance DESC;
        '''
        cursor.execute(frn_query, (player_id, player_id))
        frn = cursor.fetchall()

    with conn.cursor() as cursor:
        frq_query = '''
            SELECT
                CONCAT(p.first_name, ' ', p.last_name) as name,
                p.username,
                p.player_id
            FROM players p
            INNER JOIN friend_requests frq ON frq.sender_id = p.player_id
            WHERE frq.receiver_id = %s
        '''
        cursor.execute(frq_query, (player_id,))
        frq = cursor.fetchall()

    conn.close()
    return render_template("friends.html", frn=frn, frq=frq)

@app.route("/player/<username>")
def player_profile(username):
    conn = get_db_connection()
    
    profile_query = '''
        SELECT
            p.username,
            p.player_id,
            p.first_name,
            CONCAT(p.first_name, " ", p.last_name) AS name,
            TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) AS age,
            p.personal_balance,
            b.account_balance,
            b.account_no
        FROM players p
        LEFT JOIN ownership o ON o.player_id = p.player_id
        LEFT JOIN bank_accounts b ON b.account_no = o.account_no
        WHERE p.username=%s;
    '''
    friendship_query = '''
        SELECT EXISTS (
            SELECT 1
            FROM friendships
            WHERE
                (befriender_id = %s AND befriended_id = %s)
                or (befriender_id = %s AND befriended_id = %s)
        ) as is_friend;
    '''
    bank_query = '''
    SELECT SUM(b.account_balance) AS total_balance
    FROM ownership o
    JOIN bank_accounts b ON o.account_no = b.account_no
    WHERE o.player_id = %s;
    '''

    fav_game_query = '''
    WITH game_counts AS (
        SELECT g.game_name, COUNT(*) AS cnt
        FROM game_sessions gs
        JOIN games g ON gs.game_id = g.game_id
        WHERE gs.player_id = %s
        GROUP BY g.game_id, g.game_name
    )
    SELECT game_name
    FROM game_counts
    WHERE cnt = (SELECT MAX(cnt) FROM game_counts);
    '''

    with conn.cursor() as cursor:
        cursor.execute(profile_query, (username,))
        profile_details = cursor.fetchone()
        profile_exists = bool(profile_details)

    if profile_exists:
        player = session['id']
        target = profile_details['player_id']
        mutuals_query = '''
            SELECT
                username,
                CONCAT(first_name, ' ', last_name) AS name
            FROM players
            WHERE
                player_id IN (
                    SELECT befriended_id AS friend_id
                    FROM friendships
                    WHERE befriender_id = %s

                    UNION

                    SELECT befriender_id AS friend_id
                    FROM friendships
                    WHERE befriended_id = %s
                ) AND player_id IN (
                    SELECT befriended_id AS friend_id
                    FROM friendships
                    WHERE befriender_id = %s

                    UNION

                    SELECT befriender_id AS friend_id
                    FROM friendships
                    WHERE befriended_id = %s
                );
        '''

        with conn.cursor() as cursor:
            cursor.execute(mutuals_query, (player, player, target, target))
            mutuals = cursor.fetchall()

        with conn.cursor() as cursor:
            cursor.execute(friendship_query, (player, target, target, player))
            row = cursor.fetchone()
            is_friend = row['is_friend']
            if not is_friend: profile_details.pop('account_no', None)

        with conn.cursor() as cursor:
            cursor.execute(bank_query, (target,))
            row = cursor.fetchone()
            bank_balance = ('$'+str(row['total_balance'])) if row['total_balance'] is not None else "N/A"

            cursor.execute(fav_game_query, (target,))
            rows = cursor.fetchall()

            if not rows:
                fav_game = "N/A"
            else:
                fav_game = ", ".join(r['game_name'] for r in rows)

        moredet = {
            "bank_balance": bank_balance,
            "fav_game": fav_game
        }
    else:
        conn.close()
        abort(404)

    conn.close()
    return render_template(
        'player_profile.html',
        details=profile_details,
        mutuals=mutuals,
        more_details=moredet
        )

@app.route('/bank/')
def bank():
    player_id = session['id']
    conn = get_db_connection()

    ownership_query = '''
        SELECT b.account_no, b.account_balance, b.account_type
        FROM bank_accounts b
        INNER JOIN ownership w ON b.account_no = w.account_no
        INNER JOIN players p ON p.player_id = w.player_id
        WHERE p.player_id = %s
    ''' 
    with conn.cursor() as cursor:
        cursor.execute(ownership_query, (player_id,))
        account = cursor.fetchone()

    if not account:
        return redirect(url_for('create_bank_account'))
    else:
        return render_template('bank.html', account=account)

@app.route('/bank/signup', methods=["POST", "GET"])
def create_bank_account():
    valid = False
    conn = get_db_connection()
    
    type_query = '''
        SELECT DISTINCT account_type
        FROM bank_accounts;
    '''
    validation_query = '''
        SELECT personal_balance
        FROM players
        WHERE player_id = %s;
    '''
    ba_insertion_query = '''
        INSERT INTO bank_accounts (account_no, account_type, account_balance)
        VALUES (%s, %s, %s);
    '''
    ownership_insertion_query = '''
        INSERT INTO ownership (player_id, account_no)
        VALUES (%s, %s)
    '''
    update_query = '''
        UPDATE players
        SET personal_balance = personal_balance - %s
        WHERE player_id = %s
    '''

    with conn.cursor() as cursor:
        cursor.execute(type_query)
        account_types = cursor.fetchall()

    if request.method == "POST":
        deposit = float(request.form.get('initial_deposit'))
        account_type = request.form.get('account_type')


        with conn.cursor() as cursor:
            player_id = session['id']
            cursor.execute(validation_query, (player_id,))
            row = cursor.fetchone()
            balance = row['personal_balance']
            valid = balance >= deposit
    
        if not valid:
            conn.close()
            flash('You do not have that much money!', 'warning')
            return redirect(url_for('create_bank_account'))
        with conn.cursor() as cursor:
            account_no = f'MONEYGAME-{account_type.upper()}-{player_id:05}'
            cursor.execute(
                ba_insertion_query,
                (account_no, account_type, deposit)
            )
            cursor.execute(ownership_insertion_query, (player_id, account_no))
            cursor.execute(update_query, (deposit, player_id))
            conn.commit()
            return redirect(url_for('bank'))
    conn.close()
    return render_template(
        'bank_registration.html',
        account_types=account_types
    )

@app.route('/bank/deposit', methods=["GET", "POST"])
def deposit():
    conn = get_db_connection()
    player_id = session['id']
    if request.method == "POST":
        amount = float(request.form['amount'])
        balance_query = '''
            SELECT personal_balance
            FROM players WHERE player_id = %s
        '''
        update_query = '''
            UPDATE bank_accounts b
            INNER JOIN ownership o ON o.account_no = b.account_no
            INNER JOIN players p ON p.player_id = o.player_id
            SET
                b.account_balance = b.account_balance + %s,
                p.personal_balance = p.personal_balance - %s
            WHERE p.player_id = %s;
        ''' 
        with conn.cursor() as cursor:
            cursor.execute(balance_query, (player_id,))
            row = cursor.fetchone()
            balance = row['personal_balance']
        if amount <= balance:
            with conn.cursor() as cursor:
                cursor.execute(update_query, (amount, amount, player_id))
                conn.commit()
                flash('Deposit successful!', 'success')
        else:
            flash("You don't have that much money!", 'warning')
        
        return redirect(url_for('deposit'))

    profile_query = '''
        SELECT b.account_no, p.personal_balance, b.account_balance
        FROM bank_accounts b
        INNER JOIN ownership w ON b.account_no = w.account_no
        INNER JOIN players p ON p.player_id = w.player_id
        WHERE p.player_id = %s
    '''
    with conn.cursor() as cursor:
        cursor.execute(profile_query, (player_id,))
        row = cursor.fetchone()
        account_no = row['account_no']
        personal_balance = row['personal_balance']
        account_balance = row['account_balance']

    conn.close()
    return render_template(
        'deposit.html',
        account_no = account_no,
        personal_balance = personal_balance,
        bank_balance = account_balance
        )

@app.route('/bank/withdraw', methods=["GET", "POST"])
def withdraw():
    conn = get_db_connection()
    player_id = session['id']
    if request.method == "POST":
        amount = float(request.form['amount'])
        balance_query = '''
            SELECT b.account_balance
            FROM bank_accounts b
            INNER JOIN ownership o ON b.account_no = o.account_no
            WHERE o.player_id = %s
        '''
        update_query = '''
            UPDATE players p
            INNER JOIN ownership o ON p.player_id = o.player_id
            INNER JOIN bank_accounts b ON b.account_no = o.account_no
            SET
                b.account_balance = b.account_balance - %s,
                p.personal_balance = p.personal_balance + %s
            WHERE p.player_id = %s;
        ''' 
        with conn.cursor() as cursor:
            cursor.execute(balance_query, (player_id,))
            row = cursor.fetchone()
            balance = row['account_balance']

        if amount <= balance:
            with conn.cursor() as cursor:
                cursor.execute(update_query, (amount, amount, player_id))
                conn.commit()
                flash('Withdrew successfully!', 'success')
        else:
            flash("You don't have that much money!", 'warning')

        
        return redirect(url_for('withdraw'))

    profile_query = '''
        SELECT b.account_no, p.personal_balance, b.account_balance
        FROM bank_accounts b
        INNER JOIN ownership w ON b.account_no = w.account_no
        INNER JOIN players p ON p.player_id = w.player_id
        WHERE p.player_id = %s
    '''
    with conn.cursor() as cursor:
        cursor.execute(profile_query, (player_id,))
        row = cursor.fetchone()
        account_no = row['account_no']
        personal_balance = row['personal_balance']
        account_balance = row['account_balance']

    conn.close()
    return render_template(
        'withdraw.html',
        account_no = account_no,
        personal_balance = personal_balance,
        bank_balance = account_balance
        )

@app.route('/bank/transfer', methods=["GET", "POST"])
def transfer():
    conn = get_db_connection()
    player_id = session['id']

    profile_query = '''
        SELECT b.account_no, b.account_balance
        FROM bank_accounts b
        INNER JOIN ownership w ON b.account_no = w.account_no
        INNER JOIN players p ON p.player_id = w.player_id
        WHERE p.player_id = %s
    '''
    with conn.cursor() as cursor:
        cursor.execute(profile_query, (player_id,))
        row = cursor.fetchone()

    account_no = row['account_no']
    account_balance = row['account_balance']

    if request.method == "POST":
        amount = float(request.form['amount'])
        receiver_account = request.form['receiver']
        memo = request.form['memo']
        sender_account = account_no
    
        subtraction_query = '''
            UPDATE bank_accounts
            SET account_balance = account_balance - %s
            WHERE account_no = %s;
        ''' 
        addition_query = '''
            UPDATE bank_accounts
            SET account_balance = account_balance + %s
            WHERE account_no = %s;
        ''' 
        logging_query = '''
            INSERT INTO transactions (
                sender_account,
                receiver_account,
                transaction_amount,
                memo
            )
            VALUES (%s, %s, %s, %s)
        '''
        validation_query = '''
        SELECT
            EXISTS (
                SELECT 1 FROM bank_accounts WHERE account_no = %s 
            ) AS ex
        '''

        if sender_account == receiver_account:
            flash("You can't send money to yourself!", 'warning')
            return render_template(
                'transfer.html',
                account_no = account_no,
                bank_balance = account_balance,
                forminfo={"rec": amount, "memo": memo}
                )

        with conn.cursor() as cursor:
            cursor.execute(validation_query, (receiver_account,))
            row = cursor.fetchone()
            exists = bool(row['ex'])

        if not exists:
            flash('Account not found!', 'warning')
            return render_template(
                'transfer.html',
                account_no = account_no,
                bank_balance = account_balance,
                forminfo={"rec": amount, "memo": memo}
                )

        if amount <= account_balance:
            with conn.cursor() as cursor:
                cursor.execute(subtraction_query, (amount, sender_account))
                cursor.execute(addition_query, (amount, receiver_account))
                cursor.execute(
                    logging_query,
                    (sender_account, receiver_account, amount, memo)
                )

                conn.commit()
                conn.close()
                flash('Money sent successfully!', 'success')
                return redirect(url_for('transfer'))
        else:
            flash("You don't have that much money!", 'warning')
            return render_template(
                'transfer.html',
                account_no = account_no,
                bank_balance = account_balance,
                forminfo={"receiver": receiver_account, "memo": memo}
                )

        
        return redirect(url_for('transfer'))

    conn.close()
    return render_template(
        'transfer.html',
        account_no = account_no,
        bank_balance = account_balance,
        forminfo={}
        )

@app.route('/bank/transactions')
def transactions():
    conn = get_db_connection()
    player_id = session['id']
    profile_query = '''
        SELECT b.account_no
        FROM bank_accounts b
        INNER JOIN ownership w ON b.account_no = w.account_no
        INNER JOIN players p ON p.player_id = w.player_id
        WHERE p.player_id = %s
    '''

    history_query = '''
        SELECT
            transaction_date,
            "You" AS sender_account,
            receiver_account,
            transaction_amount,
            memo
        FROM transactions
        WHERE sender_account = %s

        UNION

        SELECT
            transaction_date,
            sender_account,
            "You" AS receiver_account,
            transaction_amount,
            memo
        FROM transactions
        WHERE receiver_account = %s

        ORDER BY transaction_date DESC
        LIMIT 20;
    '''
    with conn.cursor() as cursor:
        cursor.execute(profile_query, (player_id,))
        row = cursor.fetchone()
        account_no = row['account_no']
    
    with conn.cursor() as cursor:
        cursor.execute(history_query, (account_no, account_no))
        rows = cursor.fetchall()
    
    conn.close()
    return render_template('transactions.html', transactions=rows)

stock_funcs = {
    'SIN' : math.sin,
    'COS' : math.cos,
    'TAN' : math.tan,
}

def get_stock_rate(func):
    minute = datetime.now().minute
    degree = minute*6
    rad = (degree/180)*math.pi
    f = stock_funcs[func]
    price = round(min(max(1, abs(f(rad))*1000), 10000000))
    return price

@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    balance_query = 'SELECT personal_balance FROM players WHERE player_id = %s'
    player_id = session['id']
    conn = get_db_connection()
    market_query = '''
        SELECT stock_id, abbreviation, exchange FROM stocks
    '''
    with conn.cursor() as cursor:
        cursor.execute(balance_query, (player_id,))
        row = cursor.fetchone()
        balance = row['personal_balance']
        cursor.execute(market_query)
        stocks = cursor.fetchall()
        for s in stocks:
            rate = get_stock_rate(s['abbreviation'])
            s['rate'] = rate
    investments_query = '''
        SELECT
            s.stock_id,
            s.abbreviation,
            s.exchange,
            i.investment_amount,
            i.investment_date
        FROM investments i
        INNER JOIN players p ON p.player_id = i.player_id
        INNER JOIN stocks s ON s.stock_id = i.stock_id
        WHERE p.player_id = %s;
        ORDER BY i.investment_date DESC;

    '''
    with conn.cursor() as cursor:
        cursor.execute(investments_query, (player_id,))
        invs = cursor.fetchall()
    
    submitting_data = request.method == "POST"
    buying = submitting_data and 'stock' in request.form
    selling = submitting_data and not buying
    
    if buying:
        stock_id = request.form['stock']
        amount = float(request.form['amount'])

        stock_query = '''
            SELECT s.abbreviation FROM stocks s
            WHERE s.stock_id = %s;
        '''
        validation_query = '''
            SELECT personal_balance FROM players
            WHERE player_id = %s
        '''
        insertion_query = '''
            INSERT INTO investments (stock_id, player_id, investment_amount)
            VALUES (%s, %s, %s);
        '''
        update_query = '''
            UPDATE players
            SET personal_balance = personal_balance - %s
            WHERE player_id = %s
        '''
        with conn.cursor() as cursor:
            cursor.execute(stock_query, (stock_id,))
            row = cursor.fetchone()

        abv = row['abbreviation']
        buying_price = get_stock_rate(abv) * amount

        with conn.cursor() as cursor:
            cursor.execute(validation_query, (player_id,))
            row = cursor.fetchone()
        
        balance = row['personal_balance']
        valid = buying_price <= balance

        if valid:
            with conn.cursor() as cursor:
                cursor.execute(insertion_query, (stock_id, player_id, amount))
                cursor.execute(update_query, (buying_price, player_id))

                conn.commit()
                conn.close()
                flash('Stock bought successfully!', 'success')
                return redirect(url_for('stocks'))
        else:
            flash("You don't have enough money to do that!", 'warning')
    elif selling:
        stock_query = '''
            SELECT s.abbreviation, i.investment_amount
            FROM stocks s
            INNER JOIN investments i ON i.stock_id = s.stock_id
            INNER JOIN players p ON p.player_id = i.player_id
            WHERE
                i.stock_id=%s AND
                i.player_id=%s AND
                i.investment_date LIKE %s;
        '''
        deletion_query = '''
            DELETE FROM investments
            WHERE
                stock_id=%s AND
                player_id=%s AND
                investment_date LIKE %s;
        '''
        update_query = '''
            UPDATE players
            SET personal_balance = personal_balance + %s
            WHERE player_id=%s
        '''
        
        selected = request.form.getlist('sell')
        if not selected:
            flash('Please select at least one investment to sell!', 'warning')
            return redirect(url_for('stocks'))
            
        for s in selected:
            stock_id, purchase_date = s.split('|')
            purchase_date = purchase_date + "%"
            stock_id = int(stock_id)
            player_id = player_id

            with conn.cursor() as cursor:
                cursor.execute(
                    stock_query,
                    (stock_id, player_id, purchase_date)
                )
                row = cursor.fetchone()
            abv = row['abbreviation']
            rate = get_stock_rate(abv)
            amount = row['investment_amount']
            selling_price = rate * amount

            
            with conn.cursor() as cursor:
                cursor.execute(
                    deletion_query,
                    (stock_id, player_id, purchase_date)
                )
                cursor.execute(update_query, (selling_price, player_id))
                conn.commit()
        conn.close()
        return redirect(url_for('stocks'))
    
    conn.close()
    return render_template('stocks.html', stocks=stocks, investments=invs, balance=balance)

@app.route('/edit_profile', methods=["GET", "POST"])
def edit_profile():
    conn = get_db_connection()
    player_id = session['id']
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        username = request.form['username']
        email = request.form['email']
        new_password = request.form['new_password']
        old_password = request.form['old_password']

        player_query = '''
            SELECT
                first_name,
                last_name,
                username,
                email,
                password
            FROM players WHERE player_id=%s;
        '''

        with conn.cursor() as cursor:
            cursor.execute(player_query, (player_id,))
            player_details = cursor.fetchone()

        old_password_bytes = old_password.encode('utf-8')
        stored_hash = player_details['password'].encode('utf-8') 
        passbool = bcrypt.checkpw(old_password_bytes, stored_hash)

        if passbool == False:
            flash("Incorrect password!")
            conn.close()
            return redirect(url_for('edit_profile'))



        valid = True

        validation_query = '''
        SELECT
            EXISTS (
                SELECT 1 FROM players WHERE username = %s 
            ) AS username_taken,
            EXISTS (
                SELECT 1 FROM players WHERE email = %s
            ) AS email_taken;
        '''



        update_query = '''
            UPDATE players
            SET
                first_name = %s,
                last_name = %s,
                username = %s,
                email = %s,
                password = %s
            WHERE player_id = %s
        '''

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(validation_query, (username, email))
            row = cursor.fetchone()
            username_taken = bool(row['username_taken'])
            email_taken = bool(row['email_taken'])
            if username_taken or email_taken:
                valid = False
            if username_taken:
                flash('Username is taken! Please try a different one.', 'warning')
            if email_taken:
                flash('Email is associated with an existing account!', 'warning')
        if valid:
            if not fname: fname = player_details['first_name']
            if not lname: lname = player_details['last_name']
            if not username: username = player_details['username']
            if not email: email = player_details['email']
            if not new_password:
                new_password = player_details['password']
            else:
                new_password_bytes = new_password.encode('utf-8')
                salt = bcrypt.gensalt()
                new_password = bcrypt.hashpw(new_password_bytes, salt).decode('utf-8')
            with conn.cursor() as cursor:
                cursor.execute(
                    update_query,
                    (fname, lname, username, email, new_password, player_id)
                )
                conn.commit()
                session['username'] = username
                session['fname'] = fname
                session['lname'] = lname
                session['email'] = email
                flash('Changes saved!', 'success')
                conn.close()
                return redirect(url_for('edit_profile'))

    conn.close()
    return render_template(
        'edit_profile.html'
        )

    
if __name__ == "__main__":
    app.run(debug=True)
