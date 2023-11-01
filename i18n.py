class firstrun():
    prompt1 = "Could not determine client's "
    empty_config = "client configuration is empty. Deleting..."
    prompt2 = "Is this the first time you are running the client?"
    config_not_found = "Configuration file not found!"
    exec = "client will now run its configuration process"
    fix_missing = "Please enter the client's"
    welcome_message = "Welcome to PesuPy Chat client Software!"
    setup_client_dir = "Please enter the path to a folder where the client can store its files"
    keypair_setup = "Setting up client Keypair..."
    initialize_db = "Setting up Databases for use..."
    security = "For security reasons, enter client launch password again."
    exit = "Client will now exit. Please run it again!"
    class savedata():
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
    class passwd():
        explain = "\
         \
        "
        input = "Enter the client's launch password: "
        confirm = "Enter it again to confirm: "
        retry = "Passwords do not match!"
class log():
    class tags():
        info = '[INFO] '
        warn = '[WARN] '
        error = '[ERR] '
    client_start = "Client starting from path {0}...."