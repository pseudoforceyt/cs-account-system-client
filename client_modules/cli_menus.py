import os, sys
from . import packet_handler as p

def cls():
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

def main_menu():
    while True:
        cls()
        print(
"""                                                     ......  .   ..
   -======+++**##%+                                  %*---%::%   @-
  +@#+++*@@+=--:-%%.                                 %.  .% *= .+% 
  *@-   :@#     .%%.                                :@+++*- -+==#= 
  #@:   -@#..:::-%%.                                =*    .%.   %. 
 .%%.   :%%%%#####=  :*-       =-    :%%###%%%%%+   *:    +%+++*=  
 .@%                 *@-      :@#  ..-@@=:-@%:..                   
 -@*     .=++++***:. %@:      :@# .#@%%@@%%%@@###***=              
 =@+    .%@+===-=%%- %%.      -@* :@# -@*  -@#:*@*--.              
 +@=    .%%.     *@+ @#       :@# :@# =@+  -@* =@+                 
 #@:   .:%%======#@* @#-----==*@* -@%+#@#+=#@= +@=                 
.#@%%%%%%##*+++++=:. =******+++=.  :===+==++-  +@=            CHAT""")
        print("Welcome!")
        print("Choose an operation:")
        print("1. Sign up")
        print("2. Log in")
        print("3. Exit")
        c = int(input("> "))
        match c:
            case 1:
                signup()
            case 2:
                login()
            case 3:
                print("Goodbye!")
                sys.exit()

def signup():
    p.signup()