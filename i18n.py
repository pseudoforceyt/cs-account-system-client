class firstrun:
    prompt1 = "Could not determine client's "
    empty_config = "Client configuration is empty. Deleting..."
    prompt2 = "Is this the first time you are running the client?"
    config_not_found = "Configuration file not found!"
    exec = "Client will now run its configuration process"
    fix_missing = "Please enter the Client's"
    welcome_message = "Welcome to the Account System Demonstration Frontend"
    setup_client_dir = "Please enter the path to a folder where the Client can store its files"
    keypair_setup = "Setting up Client Keypair..."
    initialize_db = "Setting up Databases for use..."
    exit = "Client will now exit. Please run it again!"
    config_modinfo = "You will be able to change these later"
    hs_addr = "Enter Homeserver Address: "
    hs_port = "Enter Homeserver Port: "


class savedata:
    gui = "Opening file chooser dialog..."
    nogui = "Cannot open file chooser! Enter the path manually:"
    error = "An error occurred"
    write_error = "An error occurred while trying to write client files.\nPlease choose another path"
    not_a_dir = "Please enter path to a folder!"
    creating = "Folder not accessible."
    input_writable = "Please enter a writeable folder path"
    created = "Written Client files successfully."
    created_new = "Created Client folder successfully."
    data_exists = "Previous Installation Detected! Please delete the files or choose another folder."


class demo:
    captcha_p = "Open the captcha.png in the client folder and enter the digits here:"
    user_p = "Enter your username: "
    email_p = "Enter your email: "
    name_p = "Enter your full name: "
    dob_p = "Enter your date of birth in the format {}: "
    pass_p = "Enter your password: "
    pass_confirm = "Confirm your password: "
    pass_mismatch = "Passwords don't match. Try again"
    error_i = "An error occurred:"
    signup_success = "Signup complete! Login with your credentials."
    id_p = "Enter username/email: "
    save_p = "Save login? No need to re-login for 30 days"
    token_got = "Successfully acquired token."
    token_fail = "Token generation failed. Please try again. Error:\n{}"
    token_nf = "You have to login first! Token not found."
    auth_err = "Token authentication failed. Please login again. Error:\n{}"
    logout_p = "Are you sure you want to log out?\nThis will reset your token and you will have to login again."
    logout_success = "Successfully logged out. Token has been reset"
    end = "You have been logged in successfully.\nYour session is now active and this concludes the demonstration.\nIf you exit the app and decide to login again, you can use > auth to do it."


class log:
    class tags:
        info = '[INFO] '
        warn = '[WARN] '
        error = '[ERR] '
        debug = '[DEBUG] '

    client_start = "Client starting from path {0}...."
    handle_packet = "Handling packet {}..."


sig_map = {
    'CONN_OK': "Connection to the server was successful",
    'CAPTCHA_WRONG': "The CAPTCHA code you entered was wrong. Try performing the action again",
    'SIGNUP_MISSING_CREDS': 'A field in your signup form is empty. Please signup again properly',
    'SIGNUP_USERNAME_ABOVE_LIMIT': 'Username exceeds 32 character limit',
    'SIGNUP_USERNAME_ALREADY_EXISTS': 'Username already exists',
    'SIGNUP_EMAIL_ABOVE_LIMIT': 'Your email ID is abnormally long. Are you sure its a valid address?',
    'SIGNUP_NAME_ABOVE_LIMIT': 'Your name is abnormally long. Are you Jugemu?',
    'SIGNUP_DOB_INVALID': 'Date of birth is Invalid. Please enter it in YYYY-MM-DD or DD-MM-YYYY format.',
    'SIGNUP_PASSWORD_ABOVE_LIMIT': 'No way in heaven will you remember the password. Choose a smaller one.',
    'SIGNUP_ERR': 'Unexpected error while signing up, please try again.',
    'LOGIN_MISSING_CREDS': 'A field in your form is empty. Please fill it again properly',
    'LOGIN_INCORRECT_PASSWORD': 'The password you entered is incorrect. Check your password',
    'LOGIN_ACCOUNT_NOT_FOUND': 'The requested account does not exist. Check your username/email',
    'TOKEN_EXPIRED': 'Your session has expired. Login again',
    'TOKEN_INVALID': 'Login again to fix this.',
    'LOGOUT_ERR': 'Unexpected error while logging out, please try again.',
    'NOT_LOGGED_IN': 'You need to be logged in to do that!',
    'TOKEN_NOT_FOUND': 'The provided auth token does not exist on the server. Log in again',
    'ACCOUNT_DNE': 'No such account found. Check your username/email'
}
