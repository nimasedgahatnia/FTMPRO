from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football_manager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    founded_year = db.Column(db.Integer, default=datetime.now().year)
    budget = db.Column(db.Float, default=1000000.0)
    division = db.Column(db.Integer, default=5)
    points = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    goals_for = db.Column(db.Integer, default=0)
    goals_against = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    players = db.relationship('Player', backref='team', lazy=True)
    stadium = db.relationship('Stadium', backref='team', uselist=False)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(20), nullable=False)
    overall_rating = db.Column(db.Integer, default=50)
    potential = db.Column(db.Integer, default=70)
    market_value = db.Column(db.Float, default=50000.0)
    wage = db.Column(db.Float, default=1000.0)
    contract_expires = db.Column(db.DateTime)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    nationality = db.Column(db.String(50))
    stamina = db.Column(db.Integer, default=100)
    form = db.Column(db.Integer, default=50)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Stadium(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, default=5000)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), unique=True)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    home_score = db.Column(db.Integer, nullable=True)
    away_score = db.Column(db.Integer, nullable=True)
    match_date = db.Column(db.DateTime, default=datetime.utcnow)
    played = db.Column(db.Boolean, default=False)
    week = db.Column(db.Integer, default=1)
    
    home_team = db.relationship('Team', foreign_keys=[home_team_id], backref='home_matches')
    away_team = db.relationship('Team', foreign_keys=[away_team_id], backref='away_matches')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_player_name():
    first_names = ['Ali', 'Reza', 'Mohammad', 'Hossein', 'Ahmad', 'Mehdi', 'Saeed', 'Javad', 'Mostafa', 'Amir',
                   'Carlos', 'Juan', 'Pedro', 'Luis', 'Marco', 'Diego', 'Jose', 'Antonio', 'David', 'Daniel']
    last_names = ['Karimi', 'Hosseini', 'Rashidi', 'Mohammadi', 'Ahmadi', 'Niknam', 'Parsa', 'Rad', 'Pour', 'Zadeh',
                  'Silva', 'Garcia', 'Martinez', 'Rodriguez', 'Lopez', 'Sanchez', 'Perez', 'Gonzalez', 'Fernandez', 'Diaz']
    return random.choice(first_names), random.choice(last_names)

def generate_players(count=20, team_id=None):
    positions = ['GK', 'DEF', 'DEF', 'DEF', 'DEF', 'MID', 'MID', 'MID', 'MID', 'FWD', 'FWD']
    nationalities = ['Iran', 'Spain', 'Brazil', 'Argentina', 'Germany', 'France', 'Italy', 'England', 'Portugal', 'Netherlands']
    
    players = []
    for _ in range(count):
        first_name, last_name = generate_player_name()
        player = Player(
            first_name=first_name,
            last_name=last_name,
            age=random.randint(18, 35),
            position=random.choice(positions),
            overall_rating=random.randint(40, 85),
            potential=random.randint(60, 95),
            market_value=random.uniform(20000, 500000),
            wage=random.uniform(500, 5000),
            contract_expires=datetime.now() + timedelta(days=random.randint(180, 1000)),
            team_id=team_id,
            nationality=random.choice(nationalities),
            stamina=random.randint(70, 100),
            form=random.randint(30, 80)
        )
        players.append(player)
    return players

def create_computer_teams(count=9):
    teams = []
    team_names = ['شیراز FC', 'تهران United', 'اصفهان City', 'مشهد Athletic', 'تبریز Rovers', 
                  'اهواز Sport', 'رشت Rangers', 'کرمانشاه FC', 'یزد United']
    
    for i in range(count):
        team = Team(
            name=team_names[i],
            founded_year=random.randint(1950, 2020),
            budget=random.uniform(500000, 2000000),
            division=random.randint(4, 5),
            stadium=Stadium(name=f"ورزشگاه {team_names[i]}", capacity=random.randint(5000, 50000))
        )
        db.session.add(team)
        db.session.flush()
        
        players = generate_players(15, team.id)
        for player in players:
            db.session.add(player)
        
        teams.append(team)
    
    db.session.commit()
    return teams

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        team_name = request.form.get('team_name')
        
        if User.query.filter_by(username=username).first():
            flash('نام کاربری قبلاً استفاده شده است', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('ایمیل قبلاً ثبت شده است', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        team = Team(name=team_name, budget=1500000, user_id=user.id)
        db.session.add(team)
        db.session.flush()
        
        user.team_id = team.id
        
        stadium = Stadium(name=f"ورزشگاه {team_name}", capacity=10000, team_id=team.id)
        db.session.add(stadium)
        
        players = generate_players(18, team.id)
        for player in players:
            db.session.add(player)
        
        db.session.add(user)
        db.session.commit()
        
        flash('ثبت نام با موفقیت انجام شد! حالا وارد شوید.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('نام کاربری یا رمز عبور اشتباه است', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    team = Team.query.get(current_user.team_id)
    players = Player.query.filter_by(team_id=team.id).order_by(Player.position, Player.overall_rating.desc()).all()
    
    next_match = Match.query.filter(
        ((Match.home_team_id == team.id) | (Match.away_team_id == team.id)) & 
        (Match.played == False)
    ).order_by(Match.match_date).first()
    
    all_teams = Team.query.order_by(Team.points.desc(), (Team.goals_for - Team.goals_against).desc()).all()
    
    return render_template('dashboard.html', team=team, players=players[:5], next_match=next_match, league_table=all_teams)

@app.route('/players')
@login_required
def players():
    team = Team.query.get(current_user.team_id)
    position_filter = request.args.get('position')
    
    if position_filter:
        players = Player.query.filter_by(team_id=team.id, position=position_filter).order_by(Player.overall_rating.desc()).all()
    else:
        players = Player.query.filter_by(team_id=team.id).order_by(Player.position, Player.overall_rating.desc()).all()
    
    return render_template('players.html', team=team, players=players)

@app.route('/transfers')
@login_required
def transfers():
    available_players = Player.query.filter(
        (Player.team_id != current_user.team_id) & 
        (Player.contract_expires < datetime.now() + timedelta(days=90))
    ).order_by(Player.overall_rating.desc()).limit(20).all()
    
    return render_template('transfers.html', available_players=available_players)

@app.route('/buy_player/<int:player_id>', methods=['POST'])
@login_required
def buy_player(player_id):
    player = Player.query.get_or_404(player_id)
    team = Team.query.get(current_user.team_id)
    
    if team.budget >= player.market_value:
        player.team_id = team.id
        team.budget -= player.market_value
        db.session.commit()
        flash(f'{player.full_name} با موفقیت خریداری شد!', 'success')
    else:
        flash('بودجه کافی نیست!', 'error')
    
    return redirect(url_for('transfers'))

@app.route('/sell_player/<int:player_id>', methods=['POST'])
@login_required
def sell_player(player_id):
    player = Player.query.get_or_404(player_id)
    
    if player.team_id == current_user.team_id:
        computer_teams = Team.query.filter(Team.user_id.is_(None)).all()
        if computer_teams:
            buying_team = random.choice(computer_teams)
            if buying_team.budget >= player.market_value:
                player.team_id = buying_team.id
                buying_team.budget -= player.market_value * 0.9
                current_user_team = Team.query.get(current_user.team_id)
                current_user_team.budget += player.market_value * 0.9
                db.session.commit()
                flash(f'{player.full_name} فروخته شد!', 'success')
            else:
                flash('هیچ تیمی توانایی خرید این بازیکن را ندارد!', 'error')
        else:
            flash('خطا در فروش بازیکن', 'error')
    
    return redirect(url_for('players'))

@app.route('/matches')
@login_required
def matches():
    team = Team.query.get(current_user.team_id)
    all_matches = Match.query.filter(
        (Match.home_team_id == team.id) | (Match.away_team_id == team.id)
    ).order_by(Match.match_date.desc()).all()
    
    return render_template('matches.html', team=team, matches=all_matches)

@app.route('/simulate_week')
@login_required
def simulate_week():
    current_week = Match.query.filter_by(played=False).order_by(Match.week).first()
    if not current_week:
        flash('همه مسابقات انجام شده است!', 'info')
        return redirect(url_for('dashboard'))
    
    week_number = current_week.week
    matches = Match.query.filter_by(week=week_number, played=False).all()
    
    for match in matches:
        home_team = Team.query.get(match.home_team_id)
        away_team = Team.query.get(match.away_team_id)
        
        home_strength = sum([p.overall_rating for p in home_team.players]) / len(home_team.players) if home_team.players else 50
        away_strength = sum([p.overall_rating for p in away_team.players]) / len(away_team.players) if away_team.players else 50
        
        home_advantage = 5
        home_score = max(0, int((home_strength + home_advantage) / 20 + random.gauss(0, 1)))
        away_score = max(0, int(away_strength / 20 + random.gauss(0, 1)))
        
        match.home_score = home_score
        match.away_score = away_score
        match.played = True
        
        home_team.matches_played += 1
        away_team.matches_played += 1
        home_team.goals_for += home_score
        home_team.goals_against += away_score
        away_team.goals_for += away_score
        away_team.goals_against += home_score
        
        if home_score > away_score:
            home_team.points += 3
            home_team.wins += 1
            away_team.losses += 1
        elif home_score < away_score:
            away_team.points += 3
            away_team.wins += 1
            home_team.losses += 1
        else:
            home_team.points += 1
            away_team.points += 1
            home_team.draws += 1
            away_team.draws += 1
        
        db.session.add(home_team)
        db.session.add(away_team)
        db.session.add(match)
    
    db.session.commit()
    flash(f'هفته {week_number} شبیه‌سازی شد!', 'success')
    return redirect(url_for('matches'))

@app.route('/league_table')
@login_required
def league_table():
    teams = Team.query.order_by(Team.points.desc(), (Team.goals_for - Team.goals_against).desc()).all()
    return render_template('league_table.html', teams=teams)

def init_db():
    with app.app_context():
        db.create_all()
        
        if Team.query.filter(Team.user_id.is_(None)).count() == 0:
            create_computer_teams(9)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
