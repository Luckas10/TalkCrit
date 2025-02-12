from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Item, Campaign, Donation, DonationItem, obter_conexao


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SUPERSECRETO'


login_manager = LoginManager()
login_manager.login_view = 'login_and_register'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/loginandregister', methods=['GET', 'POST'])
def login_and_register():
    errors = {}         # Armazena erros específicos de cada campo
    active_form = None  # Indica qual form deve estar ativo (login ou register)
    
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'login':
            active_form = 'login'  # Indica que estamos tratando o login
            
            email = request.form['l_email']
            senha = request.form['l_password']
            user = User.get_by_email(email)

            # Verifica se o usuário existe
            if not user:
                # Mostra erro específico no campo de e-mail de login
                errors['l_email'] = 'E-mail não cadastrado!'
            # Se existe, verifica se a senha está correta
            elif not check_password_hash(user.password, senha):
                # Mostra erro específico no campo de senha de login
                errors['l_password'] = 'Senha incorreta!'
            else:
                # Login bem-sucedido: redireciona
                login_user(user)
                return redirect(url_for('index'))

        elif action == 'register':
            active_form = 'register'  # Indica que estamos tratando o registro
            
            name = request.form['r_name']
            email = request.form['r_email']
            telephone = request.form['r_telefone']
            password = request.form['r_password']
            confirm_password = request.form['r_confirmpassword']

            # Verifica se as senhas batem
            if password != confirm_password:
                errors['r_confirmpassword'] = 'As senhas não coincidem!'
            else:
                # Verifica se já existe um usuário com esse email
                existing_user = User.get_by_email(email)
                if existing_user:
                    errors['r_email'] = 'Este e-mail já está cadastrado!'
                else:
                    # Cria o usuário e redireciona
                    hashed_password = generate_password_hash(password)
                    User.create(
                        name=name, 
                        email=email, 
                        telephone=telephone, 
                        password=hashed_password,
                        itemDonations=0,
                        valueDonations=0,
                        engagedCampaigns=0
                    )
                    return redirect(url_for('index'))
        
        # Se chegamos até aqui, houve algum erro => renderiza o template mostrando os erros
        return render_template('login_register.html', errors=errors, active_form=active_form)
    
    # Se for GET, não exibe erro nenhum (errors vazio) e não força nenhum formulário ativo
    return render_template('login_register.html', errors={}, active_form=None)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('login_and_register'))


@app.context_processor
def utility_processor():
    return dict(min=min)


if __name__ == '__main__':
    app.run(debug=True)

